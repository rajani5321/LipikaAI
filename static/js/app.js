// TalentAI • AI-Based Resume Screening & Candidate Matching System
// Enhanced Modular Application Logic with SVG Visualizations & AI Interview Copilot

const appState = {
  currentView: 'dashboard',
  jobs: [],
  selectedJobId: '',
  candidates: [],
  selectedCandidateIds: new Set(),
  matchingData: null,
  activeCandidateIdForModal: null,
  minMatchScore: 0,
  systemStatus: null,

  navigateTo(viewId) {
    this.currentView = viewId;
    document.querySelectorAll('.page-view').forEach(view => view.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));

    const targetView = document.getElementById(`view-${viewId}`);
    const targetNav = document.getElementById(`nav-${viewId}`);
    if (targetView) targetView.classList.add('active');
    if (targetNav) targetNav.classList.add('active');

    const titleEl = document.getElementById('page-title');
    const titles = {
      dashboard: 'Dashboard Overview',
      jobs: 'Job Openings & Requirements',
      upload: 'Resume Upload & OCR Extraction',
      candidates: 'Candidate Pool & Profiles',
      matching: 'Candidate Matcher & Ranking Engine',
      compare: 'Side-by-Side Candidate Comparison',
      system: 'System Architecture & MongoDB Diagnostics'
    };
    if (titleEl) titleEl.textContent = titles[viewId] || 'TalentAI ATS';

    // Refresh view specific data
    if (viewId === 'dashboard') loadDashboard();
    if (viewId === 'jobs') loadJobs();
    if (viewId === 'candidates') loadCandidates();
    if (viewId === 'matching') loadMatching();
    if (viewId === 'compare') loadCompare();
    if (viewId === 'system') loadSystemDiagnostics();
  }
};

// ---------------- Toast Notifications ----------------
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  if (type === 'success') toast.style.borderColor = 'var(--success)';
  if (type === 'error') toast.style.borderColor = 'var(--danger)';
  if (type === 'warning') toast.style.borderColor = 'var(--warning)';

  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
  toast.innerHTML = `<span style="font-weight:800; font-size:1.1rem; color:${type === 'success' ? 'var(--success)' : type === 'error' ? 'var(--danger)' : '#818cf8'};">${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}

// ---------------- Modals & Tabs ----------------
function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add('active');
}

function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove('active');
}

function switchProfileModalTab(tabId) {
  document.querySelectorAll('.modal-tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.profile-tab-content').forEach(content => content.style.display = 'none');

  const targetTab = document.getElementById(tabId);
  if (targetTab) targetTab.style.display = 'block';

  // Highlight button
  const activeBtn = Array.from(document.querySelectorAll('.modal-tab-btn')).find(b => 
    b.getAttribute('onclick')?.includes(tabId)
  );
  if (activeBtn) activeBtn.classList.add('active');
}

// ---------------- Data Synchronization ----------------
async function loadSystemStatus() {
  try {
    const res = await fetch('/api/analytics/system-status');
    const data = await res.json();
    appState.systemStatus = data;

    const dbBadgeText = document.getElementById('db-status-text');
    const dbDot = document.getElementById('db-status-dot');
    if (data.database && dbBadgeText && dbDot) {
      if (data.database.mode === 'mongodb') {
        dbBadgeText.textContent = 'MongoDB: Connected (Native)';
        dbDot.style.background = 'var(--success)';
        dbDot.style.boxShadow = '0 0 8px var(--success)';
      } else {
        dbBadgeText.textContent = 'DB: Embedded Engine (Dual-Mode)';
        dbDot.style.background = '#8b5cf6';
        dbDot.style.boxShadow = '0 0 8px #8b5cf6';
      }
    }
  } catch (err) {
    console.error('Failed to load system status:', err);
  }
}

async function loadJobs() {
  try {
    const res = await fetch('/api/jobs/');
    const data = await res.json();
    appState.jobs = data;

    const sel = document.getElementById('global-job-selector');
    if (sel) {
      const prevVal = sel.value;
      sel.innerHTML = '';
      data.forEach(job => {
        const opt = document.createElement('option');
        opt.value = job.id;
        opt.textContent = `${job.title} (${job.department})`;
        sel.appendChild(opt);
      });
      if (prevVal && data.some(j => j.id === prevVal)) {
        sel.value = prevVal;
      } else if (data.length > 0) {
        sel.value = data[0].id;
        appState.selectedJobId = data[0].id;
      }
    }

    renderJobsGrid(data);
  } catch (err) {
    console.error('Failed to load jobs:', err);
    showToast('Failed to load jobs', 'error');
  }
}

async function loadDashboard() {
  try {
    const res = await fetch('/api/analytics/dashboard');
    const data = await res.json();

    document.getElementById('dash-active-jobs').textContent = data.active_jobs;
    document.getElementById('dash-total-cvs').textContent = data.total_cvs_uploaded;
    document.getElementById('dash-avg-score').textContent = `${data.average_match_score}%`;
    document.getElementById('dash-high-match').textContent = data.high_match_candidates;

    // Render SVG Donut Chart & Distribution bars
    renderDistributionVisuals(data.score_distribution, data.average_match_score);

    // Top skills cloud
    const skillsCloud = document.getElementById('top-skills-cloud');
    skillsCloud.innerHTML = '';
    for (const [skill, count] of Object.entries(data.top_skills_in_demand)) {
      const chip = document.createElement('div');
      chip.className = 'skill-tag';
      chip.innerHTML = `<span>${skill}</span> <span class="badge">${count}</span>`;
      skillsCloud.appendChild(chip);
    }

    // Load recent candidate screenings
    loadCandidatesForDashboard();
  } catch (err) {
    console.error('Failed to load dashboard:', err);
  }
}

function renderDistributionVisuals(distribution, avgScore) {
  const distContainer = document.getElementById('score-distribution-list');
  const donutContainer = document.getElementById('dist-donut-container');
  if (!distContainer || !donutContainer) return;

  distContainer.innerHTML = '';
  const total = Object.values(distribution).reduce((a, b) => a + b, 0) || 1;

  const colors = {
    'Strong (80-100%)': '#10b981',
    'Good (65-79%)': '#6366f1',
    'Moderate (50-64%)': '#f59e0b',
    'Low (<50%)': '#f43f5e'
  };

  // Render bars
  for (const [bucket, count] of Object.entries(distribution)) {
    const pct = Math.round((count / total) * 100);
    const color = colors[bucket] || '#6366f1';
    const item = document.createElement('div');
    item.className = 'dist-item';
    item.innerHTML = `
      <div class="dist-meta">
        <span>${bucket}</span>
        <span style="color: ${color}; font-weight:700;">${count} (${pct}%)</span>
      </div>
      <div class="dist-bar-track">
        <div class="dist-bar-fill" style="width: ${pct}%; background: ${color};"></div>
      </div>
    `;
    distContainer.appendChild(item);
  }

  // Render SVG Donut Chart
  const strongCount = distribution['Strong (80-100%)'] || 0;
  const goodCount = distribution['Good (65-79%)'] || 0;
  const modCount = distribution['Moderate (50-64%)'] || 0;
  const lowCount = distribution['Low (<50%)'] || 0;

  const c = 2 * Math.PI * 45; // Circumference for r=45
  const sOffset = (strongCount / total) * c;
  const gOffset = (goodCount / total) * c;
  const mOffset = (modCount / total) * c;
  const lOffset = (lowCount / total) * c;

  donutContainer.innerHTML = `
    <svg width="130" height="130" viewBox="0 0 120 120" style="transform: rotate(-90deg);">
      <circle cx="60" cy="60" r="45" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="12" />
      <circle cx="60" cy="60" r="45" fill="none" stroke="#10b981" stroke-width="12"
              stroke-dasharray="${sOffset} ${c}" stroke-dashoffset="0" stroke-linecap="round" />
      <circle cx="60" cy="60" r="45" fill="none" stroke="#6366f1" stroke-width="12"
              stroke-dasharray="${gOffset} ${c}" stroke-dashoffset="-${sOffset}" />
      <circle cx="60" cy="60" r="45" fill="none" stroke="#f59e0b" stroke-width="12"
              stroke-dasharray="${mOffset} ${c}" stroke-dashoffset="-${sOffset + gOffset}" />
      <circle cx="60" cy="60" r="45" fill="none" stroke="#f43f5e" stroke-width="12"
              stroke-dasharray="${lOffset} ${c}" stroke-dashoffset="-${sOffset + gOffset + mOffset}" />
    </svg>
    <div class="donut-chart-center">
      <div class="donut-val">${avgScore}%</div>
      <div class="donut-lbl">Avg Match</div>
    </div>
  `;
}

async function loadCandidatesForDashboard() {
  try {
    const res = await fetch('/api/candidates/');
    const candidates = await res.json();
    const tbody = document.getElementById('dash-recent-candidates-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    candidates.slice(0, 5).forEach(c => {
      const tr = document.createElement('tr');
      const skillsHtml = c.skills.slice(0, 4).map(s => `<span class="job-skill-chip">${s}</span>`).join(' ') + 
        (c.skills.length > 4 ? ` <span style="font-size:0.75rem; color:var(--text-muted); font-weight:700;">+${c.skills.length - 4}</span>` : '');

      tr.innerHTML = `
        <td>
          <div style="font-weight:700; color:#fff;">${c.name}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">${c.email || 'No email provided'}</div>
        </td>
        <td>${skillsHtml}</td>
        <td><strong>${c.experience_years}</strong> Years</td>
        <td>${c.education}</td>
        <td><span class="badge-pill badge-${c.status === 'Shortlisted' ? 'strong' : 'good'}">${c.status}</span></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="viewCandidateProfile('${c.id}')">Inspect Profile</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
  }
}

function renderJobsGrid(jobs) {
  const container = document.getElementById('jobs-cards-grid');
  if (!container) return;
  container.innerHTML = '';

  jobs.forEach(job => {
    const card = document.createElement('div');
    card.className = 'job-card';

    const reqSkillsHtml = job.required_skills.map(s => `<span class="job-skill-chip">${s}</span>`).join(' ');
    const prefSkillsHtml = (job.preferred_skills || []).map(s => 
      `<span class="job-skill-chip" style="background: rgba(6, 182, 212, 0.12); color: #67e8f9; border-color: rgba(6, 182, 212, 0.25);">⭐ ${s}</span>`
    ).join(' ');

    card.innerHTML = `
      <div>
        <div class="job-card-header">
          <div>
            <h4 class="job-card-title">${job.title}</h4>
            <div class="job-card-dept">${job.department} • Posted ${job.created_at || 'Recently'}</div>
          </div>
          <span class="badge-pill badge-strong">${job.status}</span>
        </div>
        <div class="job-card-meta" style="margin: 14px 0;">
          <span class="job-meta-pill">⏱️ ${job.min_experience}+ Yrs Exp</span>
          <span class="job-meta-pill">🎓 ${job.education_level}</span>
          <span class="job-meta-pill">👥 ${job.candidate_count || 0} Candidates</span>
        </div>
        <p style="font-size: 0.84rem; color: var(--text-secondary); margin-bottom: 14px; line-height: 1.45;">
          ${job.description.length > 135 ? job.description.substring(0, 135) + '...' : job.description}
        </p>
        <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 800; margin-bottom: 6px; text-transform:uppercase;">CORE REQUIREMENTS:</div>
        <div class="job-card-skills" style="margin-bottom: 10px;">${reqSkillsHtml}</div>
        ${prefSkillsHtml ? `
          <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 800; margin-bottom: 5px; text-transform:uppercase;">PREFERRED:</div>
          <div class="job-card-skills">${prefSkillsHtml}</div>
        ` : ''}
      </div>
      <div class="job-card-actions">
        <button class="btn btn-primary btn-sm" onclick="matchCandidatesForJob('${job.id}')">
          🎯 Find Best Matches
        </button>
        <button class="btn btn-secondary btn-sm" onclick="deleteJob('${job.id}')" title="Delete vacancy">
          🗑️
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

// ---------------- Candidate Pool ----------------
async function loadCandidates() {
  try {
    const search = document.getElementById('cand-search-input')?.value || '';
    const minExp = document.getElementById('cand-min-exp')?.value || '0';
    const edu = document.getElementById('cand-edu-filter')?.value || '';

    let url = `/api/candidates/?min_exp=${minExp}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (edu) url += `&education=${encodeURIComponent(edu)}`;

    const res = await fetch(url);
    const candidates = await res.json();
    appState.candidates = candidates;

    renderCandidatesTable(candidates);
  } catch (err) {
    console.error('Failed to load candidates:', err);
  }
}

function renderCandidatesTable(candidates) {
  const tbody = document.getElementById('candidates-table-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  candidates.forEach(c => {
    const tr = document.createElement('tr');
    const isChecked = appState.selectedCandidateIds.has(c.id);
    const skillsHtml = c.skills.map(s => `<span class="job-skill-chip">${s}</span>`).join(' ');

    tr.innerHTML = `
      <td>
        <input type="checkbox" class="cand-checkbox" value="${c.id}" ${isChecked ? 'checked' : ''} onchange="toggleCandidateSelection('${c.id}')">
      </td>
      <td>
        <div style="font-weight:700; color:#fff; font-size:0.92rem;">${c.name}</div>
        <div style="font-size:0.75rem; color:var(--text-muted);">${c.resume_filename || 'Uploaded CV'}</div>
      </td>
      <td>
        <div style="font-size:0.84rem;">${c.email || '—'}</div>
        <div style="font-size:0.75rem; color:var(--text-muted);">${c.phone || '—'}</div>
      </td>
      <td style="max-width: 290px;">${skillsHtml}</td>
      <td><strong>${c.experience_years}</strong> Yrs</td>
      <td>${c.education}</td>
      <td>
        <select class="form-control" style="padding: 5px 8px; font-size: 0.78rem; width: 125px; font-weight:600;" onchange="updateCandidateStatus('${c.id}', this.value)">
          <option value="Active" ${c.status === 'Active' ? 'selected' : ''}>Active</option>
          <option value="Shortlisted" ${c.status === 'Shortlisted' ? 'selected' : ''}>Shortlisted</option>
          <option value="Interviewed" ${c.status === 'Interviewed' ? 'selected' : ''}>Interviewed</option>
          <option value="Rejected" ${c.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
        </select>
      </td>
      <td>
        <div style="display:flex; gap:6px;">
          <button class="btn btn-secondary btn-sm" onclick="viewCandidateProfile('${c.id}')">Inspect</button>
          <button class="btn btn-primary btn-sm" onclick="openQuestionsForCandidate('${c.id}')" title="Generate AI Interview Questions">🤖 Prep</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function toggleCandidateSelection(candId) {
  if (appState.selectedCandidateIds.has(candId)) {
    appState.selectedCandidateIds.delete(candId);
  } else {
    if (appState.selectedCandidateIds.size >= 3) {
      showToast('You can compare a maximum of 3 candidates simultaneously.', 'warning');
      loadCandidates();
      return;
    }
    appState.selectedCandidateIds.add(candId);
  }
  document.getElementById('compare-count').textContent = appState.selectedCandidateIds.size;
}

async function updateCandidateStatus(candId, newStatus) {
  try {
    const res = await fetch(`/api/candidates/${candId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
      showToast(`Status updated to ${newStatus}`, 'success');
    }
  } catch (err) {
    showToast('Failed to update candidate status', 'error');
  }
}

// ---------------- Candidate Matcher (Machine Learning Ranking) ----------------
async function loadMatching() {
  const jobId = appState.selectedJobId || (appState.jobs.length > 0 ? appState.jobs[0].id : null);
  if (!jobId) {
    showToast('Please create or select a job vacancy first.', 'warning');
    return;
  }

  const slider = document.getElementById('match-threshold-slider');
  const minScore = slider ? slider.value : 0;

  try {
    const res = await fetch(`/api/matching/job/${jobId}?min_score=${minScore}`);
    const data = await res.json();
    appState.matchingData = data;

    const titleEl = document.getElementById('matching-target-title');
    if (titleEl) {
      titleEl.textContent = `${data.job.title} (${data.job.department})`;
    }

    renderMatchingResults(data.ranked_candidates);
  } catch (err) {
    console.error('Failed to load matching:', err);
    showToast('Failed to compute match rankings', 'error');
  }
}

function renderMatchingResults(ranked) {
  const container = document.getElementById('matching-cards-container');
  if (!container) return;
  container.innerHTML = '';

  if (ranked.length === 0) {
    container.innerHTML = `
      <div class="card" style="text-align: center; padding: 56px 20px; color: var(--text-muted);">
        <p style="font-size: 1.15rem; margin-bottom: 8px;">No candidates meet the minimum ${appState.minMatchScore}% threshold.</p>
        <p style="font-size: 0.85rem;">Adjust the Min Score slider or upload additional CVs to screen.</p>
      </div>
    `;
    return;
  }

  const medals = ['🥇 #1', '🥈 #2', '🥉 #3'];

  ranked.forEach((item, index) => {
    const c = item.candidate;
    const m = item.match;

    const card = document.createElement('div');
    card.className = 'match-card';

    let scoreColor = '#f43f5e';
    let badgeClass = 'badge-low';
    if (m.overall_score >= 80) {
      scoreColor = '#10b981';
      badgeClass = 'badge-strong';
    } else if (m.overall_score >= 65) {
      scoreColor = '#6366f1';
      badgeClass = 'badge-good';
    } else if (m.overall_score >= 50) {
      scoreColor = '#f59e0b';
      badgeClass = 'badge-moderate';
    }

    const rankLabel = index < 3 ? medals[index] : `#${index + 1}`;
    const matchedTags = m.matched_required_skills.map(s => `<span class="tag-matched">✓ ${s}</span>`).join(' ');
    const missingTags = m.missing_required_skills.map(s => `<span class="tag-missing">✗ ${s}</span>`).join(' ');
    const prefTags = (m.matched_preferred_skills || []).map(s => 
      `<span class="tag-matched" style="background: rgba(6,182,212,0.15); color: #67e8f9; border-color: rgba(6,182,212,0.35);">⭐ ${s}</span>`
    ).join(' ');

    card.innerHTML = `
      <div class="match-card-main">
        <div class="score-radial" style="border-color: ${scoreColor}; box-shadow: 0 0 16px ${scoreColor}40;">
          <div class="score-val" style="color: ${scoreColor};">${Math.round(m.overall_score)}%</div>
          <div class="score-lbl">MATCH</div>
        </div>
        <div class="match-info-center">
          <h4>
            <span>${rankLabel} ${c.name}</span>
            <span class="badge-pill ${badgeClass}">${m.recommendation}</span>
          </h4>
          <div class="match-candidate-meta">
            <span>⏱️ ${c.experience_years} Years Exp</span>
            <span>🎓 ${c.education}</span>
            <span>📧 ${c.email || 'No email provided'}</span>
            <span>📄 ${c.resume_filename}</span>
          </div>
          <div class="match-skills-tags">
            ${matchedTags}
            ${missingTags}
            ${prefTags}
          </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          <button class="btn btn-primary btn-sm" onclick="openQuestionsForCandidate('${c.id}')">
            📋 AI Interview Prep
          </button>
          <button class="btn btn-secondary btn-sm" onclick="viewCandidateProfile('${c.id}')">
            Inspect Full CV
          </button>
          <button class="btn btn-secondary btn-sm" onclick="quickShortlist('${c.id}')">
            ${c.status === 'Shortlisted' ? '✓ Shortlisted' : 'Shortlist Candidate'}
          </button>
        </div>
      </div>

      <!-- Multi-factor Subscores Breakdown -->
      <div class="match-subscores">
        <div class="subscore-item">
          <div class="subscore-header">
            <span>Core Skills (45%)</span>
            <strong>${m.skill_score}%</strong>
          </div>
          <div class="subscore-bar">
            <div class="subscore-fill" style="width: ${m.skill_score}%; background: #6366f1;"></div>
          </div>
        </div>
        <div class="subscore-item">
          <div class="subscore-header">
            <span>Semantic TF-IDF (30%)</span>
            <strong>${m.semantic_score}%</strong>
          </div>
          <div class="subscore-bar">
            <div class="subscore-fill" style="width: ${m.semantic_score}%; background: #06b6d4;"></div>
          </div>
        </div>
        <div class="subscore-item">
          <div class="subscore-header">
            <span>Experience (15%)</span>
            <strong>${m.experience_score}%</strong>
          </div>
          <div class="subscore-bar">
            <div class="subscore-fill" style="width: ${m.experience_score}%; background: #10b981;"></div>
          </div>
        </div>
        <div class="subscore-item">
          <div class="subscore-header">
            <span>Education (10%)</span>
            <strong>${m.education_score}%</strong>
          </div>
          <div class="subscore-bar">
            <div class="subscore-fill" style="width: ${m.education_score}%; background: #f59e0b;"></div>
          </div>
        </div>
      </div>

      <!-- Human-Readable AI Screening Verdict -->
      <div class="match-verdict-box">
        <strong>💡 Automated Screening Insight:</strong> ${m.verdict}
      </div>
    `;
    container.appendChild(card);
  });
}

function matchCandidatesForJob(jobId) {
  appState.selectedJobId = jobId;
  const sel = document.getElementById('global-job-selector');
  if (sel) sel.value = jobId;
  appState.navigateTo('matching');
}

async function quickShortlist(candId) {
  await updateCandidateStatus(candId, 'Shortlisted');
  loadMatching();
}

// ---------------- Side-by-Side Compare ----------------
async function loadCompare() {
  const container = document.getElementById('compare-content-container');
  if (appState.selectedCandidateIds.size < 2) {
    container.innerHTML = `
      <div class="card" style="text-align: center; padding: 64px 20px; color: var(--text-muted);">
        <div style="font-size: 3rem; margin-bottom: 14px;">⚖️</div>
        <p style="font-size: 1.2rem; font-weight:700; color:#fff; margin-bottom: 8px;">Select 2 or 3 Candidates to Compare</p>
        <p style="font-size: 0.88rem; margin-bottom: 20px;">Check candidate boxes in the Candidate Pool to run side-by-side competency & fit analysis.</p>
        <button class="btn btn-primary" onclick="appState.navigateTo('candidates')">Go to Candidate Pool →</button>
      </div>
    `;
    return;
  }

  const jobId = appState.selectedJobId || (appState.jobs.length > 0 ? appState.jobs[0].id : null);
  if (!jobId) {
    showToast('Select a job vacancy first.', 'warning');
    return;
  }

  try {
    const res = await fetch('/api/compare/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_id: jobId,
        candidate_ids: Array.from(appState.selectedCandidateIds)
      })
    });
    const data = await res.json();
    renderComparison(data);
  } catch (err) {
    console.error('Failed to compare:', err);
    showToast('Comparison failed', 'error');
  }
}

function renderComparison(data) {
  const container = document.getElementById('compare-content-container');
  if (!container) return;

  const job = data.job;
  const candidates = data.candidates;

  let colsHtml = '';
  candidates.forEach(item => {
    const c = item.candidate;
    const m = item.match;
    const isWinner = c.id === data.top_candidate_id;

    const strengthsHtml = item.strengths.map(s => `<li style="color:var(--success); margin-bottom:5px; font-weight:600;">✓ ${s}</li>`).join('');
    const gapsHtml = item.gaps.map(g => `<li style="color:var(--danger); margin-bottom:5px; font-weight:600;">✗ ${g}</li>`).join('');

    // Skills checkmark matrix
    const skillsMatrixRows = job.required_skills.map(sk => {
      const has = m.matched_required_skills.includes(sk);
      return `
        <div style="display:flex; justify-content:space-between; font-size:0.82rem; padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.04);">
          <span>${sk}</span>
          <span style="font-weight:800; font-size:0.95rem; color:${has ? 'var(--success)' : 'var(--danger)'};">${has ? '✓' : '✗'}</span>
        </div>
      `;
    }).join('');

    colsHtml += `
      <div class="compare-card ${isWinner ? 'winner' : ''}">
        ${isWinner ? '<div class="compare-winner-banner">🏆 TOP RECOMMENDED APPLICANT</div>' : ''}
        <h4 style="font-size:1.25rem; font-weight:800; color:#fff;">${c.name}</h4>
        <div style="font-size:0.82rem; color:var(--text-muted); margin-bottom:16px;">${c.education} • ${c.experience_years} Yrs Exp</div>

        <div style="background:rgba(255,255,255,0.035); padding:16px; border-radius:var(--radius-md); text-align:center; margin-bottom:18px; border:1px solid var(--border-color);">
          <div style="font-size:2.4rem; font-weight:800; color:${isWinner ? 'var(--success)' : '#818cf8'};">${Math.round(m.overall_score)}%</div>
          <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em;">${m.recommendation}</div>
        </div>

        <div style="margin-bottom:18px;">
          <div style="font-size:0.74rem; font-weight:800; color:var(--text-muted); margin-bottom:8px; text-transform:uppercase;">REQUIRED SKILLS COVERAGE:</div>
          ${skillsMatrixRows}
        </div>

        <div style="margin-bottom:18px;">
          <div style="font-size:0.74rem; font-weight:800; color:var(--text-muted); margin-bottom:6px; text-transform:uppercase;">KEY STRENGTHS:</div>
          <ul style="list-style:none; font-size:0.82rem;">${strengthsHtml || '<li>Meets standard requirements</li>'}</ul>
        </div>

        <div style="margin-bottom:20px;">
          <div style="font-size:0.74rem; font-weight:800; color:var(--text-muted); margin-bottom:6px; text-transform:uppercase;">AREAS TO PROBE:</div>
          <ul style="list-style:none; font-size:0.82rem;">${gapsHtml || '<li style="color:var(--success); font-weight:600;">✓ Fully satisfies core criteria</li>'}</ul>
        </div>

        <div style="display:flex; flex-direction:column; gap:8px;">
          <button class="btn btn-primary btn-sm" onclick="openQuestionsForCandidate('${c.id}')">🤖 AI Interview Prep</button>
          <button class="btn btn-secondary btn-sm" onclick="viewCandidateProfile('${c.id}')">Inspect Profile</button>
        </div>
      </div>
    `;
  });

  container.innerHTML = `
    <div class="card" style="margin-bottom: 22px; border-left: 4px solid var(--success);">
      <div style="font-size: 0.92rem; color: var(--text-primary); line-height: 1.6;">
        <strong>🎯 AI Decision Recommendation:</strong> ${data.hr_recommendation_summary}
      </div>
    </div>
    <div style="display: grid; grid-template-columns: repeat(${candidates.length}, 1fr); gap: 20px;">
      ${colsHtml}
    </div>
  `;
}

// ---------------- Candidate Profile & Interview Questions Modal ----------------
async function viewCandidateProfile(candId) {
  appState.activeCandidateIdForModal = candId;
  try {
    const res = await fetch(`/api/candidates/${candId}`);
    const c = await res.json();

    const titleEl = document.getElementById('modal-profile-name');
    titleEl.textContent = `${c.name} • Candidate Dossier`;

    const bodyEl = document.getElementById('modal-profile-body');
    const skillsHtml = c.skills.map(s => `<span class="job-skill-chip">${s}</span>`).join(' ');

    bodyEl.innerHTML = `
      <!-- Tab 1: Overview -->
      <div class="profile-tab-content" id="tab-overview" style="display: block;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 20px;">
          <div style="background: rgba(255,255,255,0.025); padding:16px; border-radius:var(--radius-md); border:1px solid var(--border-color);">
            <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 800; text-transform:uppercase;">CONTACT INFORMATION</div>
            <div style="font-size: 0.95rem; font-weight:700; color: #fff; margin-top:4px;">${c.email || '—'}</div>
            <div style="font-size: 0.86rem; color: var(--text-secondary); margin-top:2px;">${c.phone || '—'}</div>
          </div>
          <div style="background: rgba(255,255,255,0.025); padding:16px; border-radius:var(--radius-md); border:1px solid var(--border-color);">
            <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 800; text-transform:uppercase;">QUALIFICATION & TENURE</div>
            <div style="font-size: 0.95rem; font-weight:700; color: #fff; margin-top:4px;">${c.education}</div>
            <div style="font-size: 0.86rem; color: var(--text-secondary); margin-top:2px;">${c.experience_years} Years Professional Experience</div>
          </div>
        </div>

        <div style="margin-bottom: 20px;">
          <div style="font-size: 0.74rem; color: var(--text-muted); font-weight: 800; text-transform:uppercase; margin-bottom: 6px;">EXTRACTED PROFILE SUMMARY</div>
          <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; background: rgba(255,255,255,0.02); padding: 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
            ${c.summary || 'Summary unavailable.'}
          </p>
        </div>

        <div style="margin-bottom: 20px;">
          <div style="font-size: 0.74rem; color: var(--text-muted); font-weight: 800; text-transform:uppercase; margin-bottom: 8px;">VERIFIED SKILLS ONTOLOGY (${c.skills.length})</div>
          <div style="display: flex; flex-wrap: wrap; gap: 7px;">${skillsHtml}</div>
        </div>
      </div>

      <!-- Tab 2: AI Interview Questions -->
      <div class="profile-tab-content" id="tab-questions" style="display: none;">
        <div id="modal-questions-loading" style="text-align:center; padding:30px; color:var(--text-muted);">
          Generating customized AI interview questions for ${c.name}...
        </div>
        <div id="modal-questions-container" style="display:none;"></div>
      </div>

      <!-- Tab 3: Raw Text -->
      <div class="profile-tab-content" id="tab-raw" style="display: none;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <span style="font-size: 0.74rem; color: var(--text-muted); font-weight: 800; text-transform:uppercase;">EXTRACTED DOCUMENT TEXT</span>
          <button class="btn btn-secondary btn-sm" onclick="copyRawText()">Copy All Text</button>
        </div>
        <pre id="raw-cv-text-box" style="background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 16px; font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-secondary); max-height: 320px; overflow-y: auto; white-space: pre-wrap;">${escapeHtml(c.raw_text)}</pre>
      </div>
    `;

    openModal('modal-candidate-profile');
    switchProfileModalTab('tab-overview');

    // Pre-load interview questions for tab 2
    loadInterviewQuestionsForModal(candId);
  } catch (err) {
    showToast('Failed to load candidate profile', 'error');
  }
}

async function openQuestionsForCandidate(candId) {
  await viewCandidateProfile(candId);
  switchProfileModalTab('tab-questions');
}

async function loadInterviewQuestionsForModal(candId) {
  const jobId = appState.selectedJobId || (appState.jobs.length > 0 ? appState.jobs[0].id : null);
  if (!jobId) return;

  const loadingEl = document.getElementById('modal-questions-loading');
  const containerEl = document.getElementById('modal-questions-container');

  try {
    const res = await fetch(`/api/matching/job/${jobId}/candidate/${candId}/questions`);
    const data = await res.json();

    if (loadingEl) loadingEl.style.display = 'none';
    if (containerEl) {
      containerEl.style.display = 'block';
      let qHtml = `
        <div style="font-size:0.86rem; color:var(--text-secondary); margin-bottom:16px;">
          AI-generated technical and behavioral questions tailored specifically to <strong>${data.candidate_name}</strong> and the <strong>${data.job_title}</strong> opening:
        </div>
      `;

      data.questions.forEach((q, idx) => {
        qHtml += `
          <div class="interview-q-card">
            <div class="interview-q-meta">
              <span class="interview-q-cat">${idx + 1}. ${q.category}</span>
              <span class="job-skill-chip" style="font-size:0.7rem;">${q.tag}</span>
            </div>
            <div class="interview-q-text">"${q.question}"</div>
            <div class="interview-q-guide">💡 <strong>Interviewer Evaluation:</strong> ${q.eval_guide}</div>
          </div>
        `;
      });

      containerEl.innerHTML = qHtml;
    }
  } catch (err) {
    if (loadingEl) loadingEl.textContent = 'Could not load interview questions.';
  }
}

function copyRawText() {
  const el = document.getElementById('raw-cv-text-box');
  if (el) {
    navigator.clipboard.writeText(el.textContent);
    showToast('Resume text copied to clipboard!', 'success');
  }
}

function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ---------------- Document Uploads ----------------
async function handleFilesUpload(files) {
  if (!files || files.length === 0) return;

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }
  if (appState.selectedJobId) {
    formData.append('job_id', appState.selectedJobId);
  }

  showToast(`Uploading and extracting ${files.length} document(s)...`, 'info');

  try {
    const res = await fetch('/api/resumes/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();

    showToast(`Successfully processed ${data.successful} of ${data.total_files} resume(s)!`, 'success');
    renderUploadResults(data.results);
    loadDashboard();
    loadJobs();
  } catch (err) {
    console.error('Upload failed:', err);
    showToast('Document upload and extraction failed', 'error');
  }
}

async function uploadSampleFile(sampleFilename) {
  showToast(`Parsing demo CV '${sampleFilename}'...`, 'info');
  try {
    let url = `/api/resumes/upload-sample/${sampleFilename}`;
    if (appState.selectedJobId) {
      url += `?job_id=${appState.selectedJobId}`;
    }
    const res = await fetch(url, { method: 'POST' });
    const data = await res.json();

    showToast(`Parsed ${data.name} from ${sampleFilename}!`, 'success');
    renderUploadResults([data]);
    loadDashboard();
    loadJobs();
  } catch (err) {
    console.error(err);
    showToast(`Failed to parse sample file`, 'error');
  }
}

function renderUploadResults(results) {
  const container = document.getElementById('upload-results-container');
  const tbody = document.getElementById('upload-results-tbody');
  if (!container || !tbody) return;

  container.style.display = 'block';
  tbody.innerHTML = '';

  results.forEach(r => {
    const tr = document.createElement('tr');
    if (r.status === 'success') {
      const skillsHtml = (r.skills || []).map(s => `<span class="job-skill-chip">${s}</span>`).join(' ');
      tr.innerHTML = `
        <td><strong>${r.filename}</strong></td>
        <td style="color:#fff; font-weight:700;">${r.name}</td>
        <td>${skillsHtml}</td>
        <td>${r.experience_years} Yrs</td>
        <td>${r.education}</td>
        <td><span class="badge-pill badge-strong">Parsed & Indexed ✓</span></td>
      `;
    } else {
      tr.innerHTML = `
        <td>${r.filename}</td>
        <td colspan="4" style="color:var(--danger);">${r.message}</td>
        <td><span class="badge-pill badge-low">Failed</span></td>
      `;
    }
    tbody.appendChild(tr);
  });
}

// ---------------- Job Actions ----------------
async function createJob(e) {
  e.preventDefault();
  const title = document.getElementById('job-title-input').value.trim();
  const department = document.getElementById('job-dept-input').value.trim();
  const minExp = parseFloat(document.getElementById('job-exp-input').value || 0);
  const reqSkillsStr = document.getElementById('job-req-skills-input').value;
  const prefSkillsStr = document.getElementById('job-pref-skills-input').value;
  const eduLevel = document.getElementById('job-edu-input').value;
  const desc = document.getElementById('job-desc-input').value.trim();

  const reqSkills = reqSkillsStr.split(',').map(s => s.trim()).filter(s => s);
  const prefSkills = prefSkillsStr.split(',').map(s => s.trim()).filter(s => s);

  try {
    const res = await fetch('/api/jobs/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        department,
        min_experience: minExp,
        required_skills: reqSkills,
        preferred_skills: prefSkills,
        education_level: eduLevel,
        description: desc
      })
    });

    if (res.ok) {
      showToast(`Vacancy '${title}' published!`, 'success');
      closeModal('modal-create-job');
      document.getElementById('form-create-job').reset();
      loadJobs();
      loadDashboard();
    } else {
      showToast('Error publishing vacancy', 'error');
    }
  } catch (err) {
    showToast('Failed to create vacancy', 'error');
  }
}

async function deleteJob(jobId) {
  if (!confirm('Are you sure you want to delete this job vacancy?')) return;
  try {
    const res = await fetch(`/api/jobs/${jobId}`, { method: 'DELETE' });
    if (res.ok) {
      showToast('Job vacancy deleted', 'success');
      loadJobs();
      loadDashboard();
    }
  } catch (err) {
    showToast('Failed to delete job', 'error');
  }
}

// ---------------- System Diagnostics & Reseed ----------------
async function loadSystemDiagnostics() {
  const container = document.getElementById('system-diagnostics-content');
  try {
    const res = await fetch('/api/analytics/system-status');
    const data = await res.json();
    container.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
  } catch (err) {
    container.innerHTML = 'Error loading diagnostics.';
  }
}

async function reseedData() {
  if (!confirm('Reseed database with original demo jobs and sample candidates?')) return;
  try {
    const res = await fetch('/api/system/reseed', { method: 'POST' });
    const data = await res.json();
    showToast(data.message, 'success');
    loadDashboard();
    loadJobs();
    loadCandidates();
  } catch (err) {
    showToast('Reseed failed', 'error');
  }
}

// ---------------- Mobile Navigation Drawer ----------------
function openMobileNav() {
  var sidebar  = document.querySelector('.sidebar');
  var backdrop = document.getElementById('sidebar-backdrop');
  if (sidebar)  sidebar.classList.add('mobile-open');
  if (backdrop) backdrop.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeMobileNav() {
  var sidebar  = document.querySelector('.sidebar');
  var backdrop = document.getElementById('sidebar-backdrop');
  if (sidebar)  sidebar.classList.remove('mobile-open');
  if (backdrop) backdrop.classList.remove('active');
  document.body.style.overflow = '';
}

// ---------------- Session & Auth Guard ----------------
function logoutUser() {
  sessionStorage.removeItem('ats_user');
  window.location.href = '/login';
}

// ---------------- Event Listeners Initialization ----------------
document.addEventListener('DOMContentLoaded', () => {
  // Auth Guard: redirect to login if no session
  const sessionUser = sessionStorage.getItem('ats_user');
  if (!sessionUser) {
    window.location.href = '/login';
    return;
  }

  // Populate sidebar user badge from session
  try {
    const user = JSON.parse(sessionUser);
    const nameEl = document.getElementById('user-name-display');
    const roleEl = document.getElementById('user-role-display');
    const avatarEl = document.getElementById('user-avatar-initials');
    if (nameEl && user.name) nameEl.textContent = user.name;
    if (roleEl && user.role) roleEl.textContent = user.role;
    if (avatarEl && user.name) {
      const parts = user.name.trim().split(' ');
      avatarEl.textContent = parts.length >= 2
        ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
        : user.name.substring(0, 2).toUpperCase();
    }
  } catch (e) {}
  // Navigation
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
      const view = item.getAttribute('data-view');
      if (view) appState.navigateTo(view);
      // Auto-close drawer on mobile when a nav item is tapped
      closeMobileNav();
    });
  });

  // Hide non-essential table columns on small mobile screens
  if (window.innerWidth <= 480) {
    document.querySelectorAll('thead th:nth-child(n+5), td:nth-child(n+5)').forEach(el => {
      el.classList.add('mobile-hidden');
    });
  }


  // Global Job Selector change
  const jobSel = document.getElementById('global-job-selector');
  if (jobSel) {
    jobSel.addEventListener('change', (e) => {
      appState.selectedJobId = e.target.value;
      if (appState.currentView === 'matching') loadMatching();
      if (appState.currentView === 'compare') loadCompare();
    });
  }

  // Header quick buttons
  document.getElementById('btn-reseed-data')?.addEventListener('click', reseedData);
  document.getElementById('btn-quick-new-job')?.addEventListener('click', () => openModal('modal-create-job'));
  document.getElementById('btn-open-create-job-modal')?.addEventListener('click', () => openModal('modal-create-job'));
  document.getElementById('btn-view-all-candidates')?.addEventListener('click', () => appState.navigateTo('candidates'));

  // Job creation form
  document.getElementById('form-create-job')?.addEventListener('submit', createJob);

  // File Upload Drag and Drop
  const dropzone = document.getElementById('resume-dropzone');
  const fileInput = document.getElementById('resume-file-input');
  const browseBtn = document.getElementById('btn-browse-files');

  if (browseBtn && fileInput) {
    browseBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      fileInput.click();
    });
  }

  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => handleFilesUpload(e.target.files));

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      handleFilesUpload(e.dataTransfer.files);
    });
  }

  // Candidates filtering
  const candSearch = document.getElementById('cand-search-input');
  if (candSearch) {
    candSearch.addEventListener('input', () => loadCandidates());
  }

  const candExpSlider = document.getElementById('cand-min-exp');
  if (candExpSlider) {
    candExpSlider.addEventListener('input', (e) => {
      document.getElementById('filter-exp-val').textContent = e.target.value;
      loadCandidates();
    });
  }

  const candEduFilter = document.getElementById('cand-edu-filter');
  if (candEduFilter) {
    candEduFilter.addEventListener('change', () => loadCandidates());
  }

  document.getElementById('btn-compare-selected')?.addEventListener('click', () => {
    if (appState.selectedCandidateIds.size < 2) {
      showToast('Please select at least 2 candidates using the checkboxes.', 'warning');
      return;
    }
    appState.navigateTo('compare');
  });

  // Matching threshold slider
  const matchSlider = document.getElementById('match-threshold-slider');
  if (matchSlider) {
    matchSlider.addEventListener('input', (e) => {
      appState.minMatchScore = e.target.value;
      document.getElementById('match-threshold-val').textContent = `${e.target.value}%`;
      loadMatching();
    });
  }

  // Export CSV button
  document.getElementById('btn-export-csv')?.addEventListener('click', () => {
    const jobId = appState.selectedJobId;
    if (!jobId) {
      showToast('Select a job opening first', 'warning');
      return;
    }
    window.open(`/api/reports/job/${jobId}/csv`, '_blank');
  });

  // Initial load
  loadSystemStatus();
  loadJobs();
  loadDashboard();
});
