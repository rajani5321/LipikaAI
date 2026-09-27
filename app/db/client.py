import json
import uuid
import os
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
import pymongo
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from app.config import MONGODB_URL, DATABASE_NAME, MONGO_TIMEOUT_MS, FALLBACK_DB_FILE

class EmbeddedCollection:
    """A thread-safe in-memory and JSON-backed document store mimicking PyMongo Collection."""
    def __init__(self, name: str, parent_db: "JsonDocumentDB"):
        self.name = name
        self.parent_db = parent_db

    def _get_data(self) -> List[Dict[str, Any]]:
        return self.parent_db.data.setdefault(self.name, [])

    def _matches(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        if not query:
            return True
        for k, v in query.items():
            if k == "_id" or k == "id":
                doc_id = doc.get("id") or doc.get("_id")
                if str(doc_id) != str(v):
                    return False
            elif isinstance(v, dict):
                # Simple Mongo operators like $in, $gte, etc.
                field_val = doc.get(k)
                if "$in" in v:
                    if field_val not in v["$in"] and not (isinstance(field_val, list) and any(x in v["$in"] for x in field_val)):
                        return False
                if "$gte" in v and (field_val is None or field_val < v["$gte"]):
                    return False
                if "$lte" in v and (field_val is None or field_val > v["$lte"]):
                    return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    def find(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query = query or {}
        with self.parent_db.lock:
            docs = [dict(d) for d in self._get_data() if self._matches(d, query)]
        return docs

    def find_one(self, query: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        query = query or {}
        with self.parent_db.lock:
            for d in self._get_data():
                if self._matches(d, query):
                    return dict(d)
        return None

    def insert_one(self, document: Dict[str, Any]) -> Any:
        with self.parent_db.lock:
            doc = dict(document)
            if "id" not in doc:
                doc["id"] = str(uuid.uuid4())
            if "_id" not in doc:
                doc["_id"] = doc["id"]
            self._get_data().append(doc)
            self.parent_db.save()
        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertResult(doc["id"])

    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> Any:
        with self.parent_db.lock:
            matched = False
            for d in self._get_data():
                if self._matches(d, query):
                    if "$set" in update:
                        d.update(update["$set"])
                    else:
                        d.update(update)
                    matched = True
                    break
            if matched:
                self.parent_db.save()
        class UpdateResult:
            def __init__(self, matched_count):
                self.matched_count = 1 if matched else 0
        return UpdateResult(1 if matched else 0)

    def delete_one(self, query: Dict[str, Any]) -> Any:
        with self.parent_db.lock:
            data = self._get_data()
            initial_len = len(data)
            for i, d in enumerate(data):
                if self._matches(d, query):
                    del data[i]
                    self.parent_db.save()
                    break
            deleted = initial_len - len(data)
        class DeleteResult:
            def __init__(self, deleted_count):
                self.deleted_count = deleted
        return DeleteResult(deleted)

    def delete_many(self, query: Dict[str, Any]) -> Any:
        with self.parent_db.lock:
            data = self._get_data()
            initial_len = len(data)
            self.parent_db.data[self.name] = [d for d in data if not self._matches(d, query)]
            deleted = initial_len - len(self.parent_db.data[self.name])
            if deleted > 0:
                self.parent_db.save()
        class DeleteResult:
            def __init__(self, deleted_count):
                self.deleted_count = deleted
        return DeleteResult(deleted)

    def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        return len(self.find(query))


class JsonDocumentDB:
    """Embedded document database with persistence to data/db_store.json"""
    def __init__(self, file_path=FALLBACK_DB_FILE):
        self.file_path = file_path
        self.lock = threading.Lock()
        self.data: Dict[str, List[Dict[str, Any]]] = {}
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        else:
            self.data = {}

    def save(self):
        try:
            temp_path = f"{self.file_path}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, default=str)
            if os.path.exists(self.file_path):
                os.replace(temp_path, self.file_path)
            else:
                os.rename(temp_path, self.file_path)
        except Exception as e:
            print(f"[DB] Error saving embedded database: {e}")

    def get_collection(self, name: str) -> EmbeddedCollection:
        return EmbeddedCollection(name, self)


class DatabaseManager:
    """Unified Database Manager supporting real MongoDB with automatic fallback."""
    def __init__(self):
        self.client = None
        self.db = None
        self.mode = "embedded"  # 'mongodb' or 'embedded'
        self.status_message = "Initializing..."
        self.embedded_db = JsonDocumentDB()
        self.connect()

    def connect(self):
        try:
            mongo_client = pymongo.MongoClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=MONGO_TIMEOUT_MS,
                connectTimeoutMS=MONGO_TIMEOUT_MS
            )
            # Ping database to confirm live connectivity
            mongo_client.admin.command('ping')
            self.client = mongo_client
            self.db = self.client[DATABASE_NAME]
            self.mode = "mongodb"
            self.status_message = f"Connected to MongoDB at {MONGODB_URL} (Database: {DATABASE_NAME})"
            print(f"[DB] {self.status_message}")
        except Exception as e:
            self.client = None
            self.db = None
            self.mode = "embedded"
            self.status_message = f"MongoDB not reachable ({e.__class__.__name__}). Using Embedded JSON Document Store."
            print(f"[DB] {self.status_message}")

    def get_collection(self, name: str):
        if self.mode == "mongodb" and self.db is not None:
            return self.db[name]
        return self.embedded_db.get_collection(name)

    @property
    def jobs(self):
        return self.get_collection("jobs")

    @property
    def candidates(self):
        return self.get_collection("candidates")

    @property
    def users(self):
        return self.get_collection("users")

    @property
    def activity(self):
        return self.get_collection("activity")

    def log_activity(self, action: str, details: str, category: str = "general"):
        """Record system activity log."""
        try:
            self.activity.insert_one({
                "id": str(uuid.uuid4()),
                "action": action,
                "details": details,
                "category": category,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception:
            pass

    def get_status(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "connected": True,
            "engine": "MongoDB (Native)" if self.mode == "mongodb" else "Embedded Document Engine (Dual-Mode)",
            "database": DATABASE_NAME,
            "url": MONGODB_URL if self.mode == "mongodb" else str(FALLBACK_DB_FILE),
            "message": self.status_message
        }

db_manager = DatabaseManager()
