/**
 * =============================================================================
 * Collaborative AI Research Platform - Frontend Logic (script.js)
 * =============================================================================
 * 
 * Hey there! This script powers all client-side interactions for our multi-agent
 * research dashboard. Here is a quick breakdown of what this file takes care of:
 * 
 *  1. Base API routing (auto-detects local vs production backend URL)
 *  2. JWT Auth & Session management (localStorage token handling & route guards)
 *  3. Toast notifications (sleek feedback messages for success / error alerts)
 *  4. Centralized API fetch wrapper (attaches Bearer tokens & handles expired sessions)
 *  5. Page-specific lifecycle event listeners (Login, Signup, Dashboard, Results)
 *  6. Simulated agent stage progress animations (gives visual feedback during multi-agent run)
 *  7. Markdown parsing with Marked.js & clipboard copying for research reports
 * =============================================================================
 */

// Auto-detect the backend API root URL.
// When running locally, point directly to FastAPI running on port 8000.
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000'
  : '';

/* =============================================================================
   1. Authentication & Session Helpers
   ============================================================================= */

// Grab the current user's JWT access token from browser storage
function getToken() {
  return localStorage.getItem('access_token');
}

// Retrieve the logged-in researcher's email address
function getUserEmail() {
  return localStorage.getItem('user_email');
}

// Save authentication credentials when user successfully logs in or signs up
function setSession(token, email) {
  localStorage.setItem('access_token', token);
  localStorage.setItem('user_email', email);
}

// Clear stored credentials on logout or expired token
function clearSession() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_email');
}

// Helper to check whether we currently have a saved session token
function isAuthenticated() {
  return !!getToken();
}

// Route guard: boot unauthenticated users back to the login page
function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = 'login.html';
  }
}

// Log out the current user by wiping storage and heading to login screen
function logout() {
  clearSession();
  window.location.href = 'login.html';
}

/* =============================================================================
   2. Toast Notification System
   ============================================================================= */

/**
 * Displays a non-intrusive floating toast notification on the bottom-right.
 * @param {string} message - The message string to show the user.
 * @param {'error'|'success'|'info'} type - Styling category for the toast.
 */
function showToast(message, type = 'error') {
  let toast = document.getElementById('toast');
  
  // Lazily create the toast element if it doesn't already exist in the DOM
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }

  // Update content and trigger visibility
  toast.textContent = message;
  toast.className = `toast toast-${type}`;
  toast.style.display = 'block';

  // Automatically dismiss the toast after 4 seconds
  setTimeout(() => {
    toast.style.display = 'none';
  }, 4000);
}

/* =============================================================================
   3. Unified API Request Wrapper
   ============================================================================= */

/**
 * Standard wrapper around fetch() that handles JSON serialization,
 * Bearer token injection, and automatic 401 handling for expired sessions.
 * 
 * @param {string} endpoint - Relative API route (e.g. '/research' or '/my-reports')
 * @param {RequestInit} options - Standard fetch options (method, body, headers, etc.)
 */
async function apiRequest(endpoint, options = {}) {
  const token = getToken();
  
  // Attach standard headers and include Bearer token if researcher is logged in
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle token expiry or unauthorized access gracefully
    if (response.status === 401) {
      clearSession();
      // Only redirect if not already on the auth pages to avoid redirect loops
      if (!window.location.pathname.endsWith('login.html') && !window.location.pathname.endsWith('signup.html')) {
        window.location.href = 'login.html';
      }
      throw new Error('Session expired. Please log in again.');
    }

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      // Return FastAPI's detail error message if available, otherwise fallback
      throw new Error(data.detail || 'Request failed. Please try again.');
    }

    return data;
  } catch (err) {
    // Re-throw so caller can catch and display specific toast notifications
    throw err;
  }
}

/* =============================================================================
   4. DOM Ready & Event Handlers
   ============================================================================= */
document.addEventListener('DOMContentLoaded', () => {
  // Populate user badge in navbar if session exists
  const userEmailDisplay = document.getElementById('nav-user-email');
  const navAuthBtn = document.getElementById('nav-auth-btn');

  if (userEmailDisplay && isAuthenticated()) {
    userEmailDisplay.textContent = getUserEmail() || 'Researcher';
  }

  // Toggle between Sign In / Sign Out button in navbar
  if (navAuthBtn) {
    if (isAuthenticated()) {
      navAuthBtn.textContent = 'Sign Out';
      navAuthBtn.onclick = logout;
    } else {
      navAuthBtn.textContent = 'Sign In';
      navAuthBtn.onclick = () => window.location.href = 'login.html';
    }
  }

  // ---------------------------------------------------------------------------
  // 4.1. Signup Form Handling
  // ---------------------------------------------------------------------------
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const confirmPassword = document.getElementById('confirm_password').value;

      // Basic client-side validation
      if (password !== confirmPassword) {
        showToast('Passwords do not match. Please verify.');
        return;
      }

      const submitBtn = signupForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner"></span> Creating account...';

      try {
        await apiRequest('/signup', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        });
        showToast('Account created successfully! Redirecting...', 'success');
        setTimeout(() => window.location.href = 'login.html', 1200);
      } catch (err) {
        showToast(err.message);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
      }
    });
  }

  // ---------------------------------------------------------------------------
  // 4.2. Login Form Handling
  // ---------------------------------------------------------------------------
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;

      const submitBtn = loginForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner"></span> Authenticating...';

      try {
        const data = await apiRequest('/login', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        });
        
        // Save the JWT token and user email in session storage
        setSession(data.access_token, email);
        showToast('Login successful! Welcome back.', 'success');
        setTimeout(() => window.location.href = 'index.html', 800);
      } catch (err) {
        showToast(err.message);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign In';
      }
    });
  }

  // ---------------------------------------------------------------------------
  // 4.3. Research Dashboard Form & Pipeline Execution
  // ---------------------------------------------------------------------------
  const researchForm = document.getElementById('research-form');
  if (researchForm) {
    // Ensure researcher is logged in before accessing dashboard
    requireAuth();
    // Load historical requests from PostgreSQL database
    loadPastReports();

    researchForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const topicInput = document.getElementById('topic-input');
      const topic = topicInput.value.trim();

      if (!topic) {
        showToast('Please enter a research topic to investigate.');
        return;
      }

      const submitBtn = document.getElementById('submit-btn');
      const progressCard = document.getElementById('progress-card');

      // Lock UI while agents are busy synthesizing
      submitBtn.disabled = true;
      topicInput.disabled = true;
      progressCard.style.display = 'block';
      progressCard.scrollIntoView({ behavior: 'smooth' });

      // Grab stage DOM cards for live progression animations
      const step1 = document.getElementById('step-search');
      const step2 = document.getElementById('step-reader');
      const step3 = document.getElementById('step-writer');
      const step4 = document.getElementById('step-critic');

      // Reset all steps to initial state
      step1.className = 'agent-step active';
      step2.className = 'agent-step';
      step3.className = 'agent-step';
      step4.className = 'agent-step';
      
      // Simulate progressive agent stage transitions while waiting for backend LangGraph
      const stageTimer1 = setTimeout(() => {
        step1.className = 'agent-step done';
        step2.className = 'agent-step active';
      }, 3500);

      const stageTimer2 = setTimeout(() => {
        step2.className = 'agent-step done';
        step3.className = 'agent-step active';
      }, 7500);

      const stageTimer3 = setTimeout(() => {
        step3.className = 'agent-step done';
        step4.className = 'agent-step active';
      }, 12000);

      try {
        // Send request to FastAPI LangGraph pipeline
        const report = await apiRequest('/research', {
          method: 'POST',
          body: JSON.stringify({ topic }),
        });

        // Clear timeouts and mark all agent stages as complete
        clearTimeout(stageTimer1);
        clearTimeout(stageTimer2);
        clearTimeout(stageTimer3);

        step1.className = 'agent-step done';
        step2.className = 'agent-step done';
        step3.className = 'agent-step done';
        step4.className = 'agent-step done';

        showToast('Research synthesis complete! Loading report...', 'success');
        setTimeout(() => {
          window.location.href = `results.html?id=${report.id}`;
        }, 1000);
      } catch (err) {
        // Clear stage animation timers on error
        clearTimeout(stageTimer1);
        clearTimeout(stageTimer2);
        clearTimeout(stageTimer3);
        
        showToast(err.message || 'Research pipeline failed. Please check server logs.');
        submitBtn.disabled = false;
        topicInput.disabled = false;
        progressCard.style.display = 'none';
      }
    });
  }

  // ---------------------------------------------------------------------------
  // 4.4. Results Page Initialization
  // ---------------------------------------------------------------------------
  const resultsContainer = document.getElementById('results-view');
  if (resultsContainer) {
    requireAuth();
    
    // Parse the ?id= parameter from the query string
    const urlParams = new URLSearchParams(window.location.search);
    const reportId = urlParams.get('id');

    if (!reportId) {
      // Redirect back if no ID was provided
      window.location.href = 'index.html';
      return;
    }

    // Fetch and render the markdown report + critic evaluation
    loadReportDetails(reportId);
  }
});

/* =============================================================================
   5. Research History Loader (PostgreSQL via FastAPI)
   ============================================================================= */

/**
 * Fetches previous research queries submitted by the logged-in user and renders
 * clickable history cards with status badges.
 */
async function loadPastReports() {
  const listContainer = document.getElementById('history-list');
  if (!listContainer) return;

  try {
    const requests = await apiRequest('/my-reports');
    if (!requests || requests.length === 0) {
      listContainer.innerHTML = '<p style="color: var(--text-faint); font-size: 0.9rem;">No past research reports found. Run your first research query above!</p>';
      return;
    }

    // Map each report request into a clean clickable item
    listContainer.innerHTML = requests.map(req => {
      const isDone = req.status === 'done' && req.report;
      const href = isDone ? `results.html?id=${req.report.id}` : '#';
      const statusClass = `status-${req.status}`;
      const dateStr = req.created_at ? new Date(req.created_at).toLocaleDateString() : '';

      return `
        <a href="${href}" class="history-item" ${!isDone ? 'style="cursor: default;"' : ''}>
          <div>
            <div style="font-weight: 600; margin-bottom: 0.2rem;">${escapeHtml(req.topic)}</div>
            <div style="font-size: 0.75rem; color: var(--text-faint);">${dateStr}</div>
          </div>
          <span class="status-tag ${statusClass}">${req.status}</span>
        </a>
      `;
    }).join('');
  } catch (err) {
    listContainer.innerHTML = '<p style="color: var(--text-faint);">Could not load history. Is the backend server running?</p>';
  }
}

/* =============================================================================
   6. Report & Critique Details Loader
   ============================================================================= */

/**
 * Fetches a single synthesized research report by ID and renders:
 *  - Formatted Markdown report via Marked.js
 *  - Numeric score badge from Critic agent
 *  - Qualitative feedback & improvement suggestions
 *  - One-click copy to clipboard action
 * 
 * @param {string|number} reportId - The unique ID of the research report
 */
async function loadReportDetails(reportId) {
  const reportContentEl = document.getElementById('report-content');
  const criticScoreEl = document.getElementById('critic-score');
  const criticFeedbackEl = document.getElementById('critic-feedback');
  const copyBtn = document.getElementById('copy-btn');

  try {
    const report = await apiRequest(`/reports/${reportId}`);

    // Render Markdown into styled HTML using marked.js
    if (window.marked && report.content) {
      reportContentEl.innerHTML = marked.parse(report.content);
    } else {
      reportContentEl.textContent = report.content || 'No synthesized content found.';
    }

    // Display numeric Critic Score badge
    if (criticScoreEl) {
      criticScoreEl.textContent = report.critique_score ? `${report.critique_score}/10` : 'Evaluated';
    }

    // Display Critic Feedback text
    if (criticFeedbackEl) {
      criticFeedbackEl.textContent = report.critique_feedback || 'No critique feedback recorded.';
    }

    // Bind clipboard copy functionality with user feedback
    if (copyBtn) {
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(report.content);
        showToast('Report copied to clipboard!', 'success');
      };
    }
  } catch (err) {
    reportContentEl.innerHTML = `<div style="color: #f43f5e;">Error loading report: ${escapeHtml(err.message)}</div>`;
  }
}

/**
 * Basic HTML sanitizer to prevent XSS when interpolating user-supplied strings.
 * @param {string} text - Raw input string
 * @returns {string} Escaped HTML string
 */
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

