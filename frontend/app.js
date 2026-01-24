// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
const GOOGLE_CLIENT_ID = '539440677347-7dadrilnks0kn51a9q1f8c3v7str0h93.apps.googleusercontent.com';
const MICROSOFT_CLIENT_ID = '365ff30a-6fd2-4ad1-9d34-91845ccb618e';
const MICROSOFT_TENANT_ID = 'aea9dfde-d6c4-4b08-be03-a56388eddc74';

// State
let currentToken = localStorage.getItem('token') || null;
let currentUserType = localStorage.getItem('userType') || null; // 'client' or 'service_provider'
let msalInstance = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeAuth();
    initializeClientAPIs();
    initializeServiceProviderAPIs();
    initializeProjectAPIs();
    initializeBiddingAPIs();
    initializeContractAPIs();
    initializeTokenDisplay();
    initializeMSAL();
    updateUIBasedOnAuth();
});

// Token Management
function initializeTokenDisplay() {
    if (currentToken) {
        displayToken(currentToken);
    }

    document.getElementById('copyToken')?.addEventListener('click', () => {
        navigator.clipboard.writeText(currentToken);
        showToast('Token copied to clipboard!', 'success');
    });

    document.getElementById('clearToken')?.addEventListener('click', () => {
        currentToken = null;
        currentUserType = null;
        localStorage.removeItem('token');
        localStorage.removeItem('userType');
        document.getElementById('tokenDisplay').classList.add('hidden');
        updateUIBasedOnAuth();
        showToast('Token cleared - Please login again', 'success');
    });
}

function displayToken(token, userType = null) {
    currentToken = token;
    localStorage.setItem('token', token);

    if (userType) {
        currentUserType = userType;
        localStorage.setItem('userType', userType);
    }

    document.getElementById('tokenValue').textContent = token;
    document.getElementById('tokenDisplay').classList.remove('hidden');
    updateUIBasedOnAuth();
}

// UI Update Based on Auth
function updateUIBasedOnAuth() {
    const clientTab = document.querySelector('[data-tab="client"]');
    const spTab = document.querySelector('[data-tab="service-provider"]');
    const authTab = document.querySelector('[data-tab="auth"]');

    if (!currentToken || !currentUserType) {
        // Not authenticated - hide profile tabs
        clientTab.style.display = 'none';
        spTab.style.display = 'none';

        // Show auth tab
        authTab.click();
    } else if (currentUserType === 'client') {
        // Client authenticated - show only client tab
        clientTab.style.display = 'block';
        spTab.style.display = 'none';

        // Auto-switch to client tab
        clientTab.click();
    } else if (currentUserType === 'service_provider') {
        // Service Provider authenticated - show only SP tab
        clientTab.style.display = 'none';
        spTab.style.display = 'block';

        // Auto-switch to SP tab
        spTab.click();
    }
}

// Tab Navigation
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;

            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            button.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// API Helper
async function apiRequest(endpoint, method = 'GET', body = null, requiresAuth = false) {
    const headers = {
        'Content-Type': 'application/json',
    };

    if (requiresAuth && currentToken) {
        headers['Authorization'] = `Bearer ${currentToken}`;
    }

    const options = {
        method,
        headers,
    };

    if (body && method !== 'GET') {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }

        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function apiMultipartRequest(endpoint, method = 'POST', formData = null, requiresAuth = false) {
    const headers = {};

    if (requiresAuth && currentToken) {
        headers['Authorization'] = `Bearer ${currentToken}`;
    }

    const options = {
        method,
        headers,
        body: formData,
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }

        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Display Response
function displayResponse(response, isError = false) {
    const display = document.getElementById('responseDisplay');
    display.innerHTML = `<pre>${JSON.stringify(response, null, 2)}</pre>`;
    display.classList.remove('success', 'error');
    display.classList.add(isError ? 'error' : 'success');
}

// Toast Notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Form Helper
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        if (value) {
            data[key] = value;
        }
    }

    return data;
}

// Form Helper for Service Provider (uses 'pass' instead of 'password')
function getSPFormData(form) {
    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        if (value) {
            // Backend Service Provider schema expects 'pass' instead of 'password'
            if (key === 'password') {
                data['pass'] = value;
            } else {
                data[key] = value;
            }
        }
    }

    return data;
}

function setLoading(element, loading) {
    if (loading) {
        element.classList.add('loading');
        element.disabled = true;
    } else {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

// ==================== AUTHENTICATION ====================

function initializeAuth() {
    // Client Signup
    document.getElementById('clientSignupForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/auth/signup/client', 'POST', data);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Client signup successful!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Client Login
    document.getElementById('clientLoginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/auth/login/client', 'POST', data);

        setLoading(btn, false);

        if (result.success) {
            displayToken(result.data.access_token, 'client');
            displayResponse(result.data);
            showToast('Client login successful!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Service Provider Signup
    document.getElementById('spSignupForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getSPFormData(e.target);
        const result = await apiRequest('/auth/signup/service-provider', 'POST', data);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Service Provider signup successful!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Service Provider Login
    document.getElementById('spLoginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getSPFormData(e.target);
        const result = await apiRequest('/auth/login/service-provider', 'POST', data);

        setLoading(btn, false);

        if (result.success) {
            displayToken(result.data.access_token, 'service_provider');
            displayResponse(result.data);
            showToast('Service Provider login successful!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Google OAuth
    initializeGoogleAuth();

    // Microsoft OAuth
    document.getElementById('microsoftLoginClient')?.addEventListener('click', () => {
        loginWithMicrosoft('client');
    });

    document.getElementById('microsoftLoginSP')?.addEventListener('click', () => {
        loginWithMicrosoft('service_provider');
    });
}

// Google OAuth Integration
function initializeGoogleAuth() {
    if (typeof google !== 'undefined') {
        google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleCallback
        });

        google.accounts.id.renderButton(
            document.getElementById('googleButtonClient'),
            { theme: 'filled_blue', size: 'large', text: 'signin_with', width: '100%' }
        );

        google.accounts.id.renderButton(
            document.getElementById('googleButtonSP'),
            { theme: 'filled_blue', size: 'large', text: 'signin_with', width: '100%' }
        );

        // Store user type for callback
        document.getElementById('googleButtonClient').addEventListener('click', () => {
            sessionStorage.setItem('googleUserType', 'client');
        });

        document.getElementById('googleButtonSP').addEventListener('click', () => {
            sessionStorage.setItem('googleUserType', 'service_provider');
        });
    }
}

async function handleGoogleCallback(response) {
    const userType = sessionStorage.getItem('googleUserType') || 'client';

    const result = await apiRequest(`/auth/login/google/${userType}`, 'POST', {
        token: response.credential
    });

    if (result.success) {
        displayToken(result.data.access_token, userType);
        displayResponse(result.data);
        showToast(`Google login successful as ${userType}!`, 'success');
    } else {
        displayResponse({ error: result.error }, true);
        showToast(result.error, 'error');
    }
}

// Microsoft OAuth Integration
function initializeMSAL() {
    const msalConfig = {
        auth: {
            clientId: MICROSOFT_CLIENT_ID,
            authority: `https://login.microsoftonline.com/${MICROSOFT_TENANT_ID}`,
            redirectUri: window.location.origin + window.location.pathname,
        },
        cache: {
            cacheLocation: 'sessionStorage',
            storeAuthStateInCookie: false,
        }
    };

    if (typeof msal !== 'undefined') {
        msalInstance = new msal.PublicClientApplication(msalConfig);
    }
}

async function loginWithMicrosoft(userType) {
    if (!msalInstance) {
        showToast('Microsoft authentication not initialized', 'error');
        return;
    }

    const loginRequest = {
        scopes: ['openid', 'profile', 'email']
    };

    try {
        const loginResponse = await msalInstance.loginPopup(loginRequest);

        const result = await apiRequest(`/auth/login/microsoft/${userType}`, 'POST', {
            token: loginResponse.idToken
        });

        if (result.success) {
            displayToken(result.data.access_token, userType);
            displayResponse(result.data);
            showToast(`Microsoft login successful as ${userType}!`, 'success');
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    } catch (error) {
        displayResponse({ error: error.message }, true);
        showToast('Microsoft login failed: ' + error.message, 'error');
    }
}

// ==================== CLIENT APIs ====================

function initializeClientAPIs() {
    // Get Profile
    document.getElementById('getClientProfile')?.addEventListener('click', async (e) => {
        setLoading(e.target, true);

        const result = await apiRequest('/client/profile', 'GET', null, true);

        setLoading(e.target, false);

        if (result.success) {
            displayResponse(result.data);
            displayClientProfile(result.data);
            showToast('Profile fetched successfully!', 'success');
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Update Personal Details
    document.getElementById('clientPersonalForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/client/personal-details', 'PUT', data, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Personal details updated!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Update Company Info
    document.getElementById('clientCompanyForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/client/company-info', 'PUT', data, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Company info updated!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Update Contact Preferences
    document.getElementById('clientContactForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/client/contact-preferences', 'PUT', data, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Contact preferences updated!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Update Billing Info
    document.getElementById('clientBillingForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/client/billing-info', 'PUT', data, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Billing info updated!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });
}

function displayClientProfile(data) {
    const display = document.getElementById('clientProfileDisplay');
    const completion = data.completion_percentage || 0;

    display.innerHTML = `
        <pre>${JSON.stringify(data, null, 2)}</pre>
        <div class="completion-bar">
            <div class="completion-fill" style="width: ${completion}%"></div>
        </div>
        <div class="completion-text">Profile Completion: ${completion}%</div>
    `;
}

// ==================== SERVICE PROVIDER APIs ====================

function initializeServiceProviderAPIs() {
    // Get Profile
    document.getElementById('getSPProfile')?.addEventListener('click', async (e) => {
        setLoading(e.target, true);

        const result = await apiRequest('/service-provider/profile', 'GET', null, true);

        setLoading(e.target, false);

        if (result.success) {
            displayResponse(result.data);
            displaySPProfile(result.data);
            showToast('Profile fetched successfully!', 'success');
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Update Professional Info
    document.getElementById('spProfessionalForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/service-provider/professional-info', 'PUT', data, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Professional info updated!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Add Portfolio Project
    document.getElementById('spPortfolioForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/service-provider/portfolio', 'POST', data, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Portfolio project added!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Add Work Experience
    document.getElementById('spExperienceForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/service-provider/experience', 'POST', data, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Work experience added!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Add Education
    document.getElementById('spEducationForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/service-provider/education', 'POST', data, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Education added!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Add Certification
    document.getElementById('spCertificationForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/service-provider/certification', 'POST', data, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Certification added!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Upload KYC
    document.getElementById('spKYCForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/service-provider/kyc', 'POST', data, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('KYC document uploaded!', 'success');
            e.target.reset();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });
}

function displaySPProfile(data) {
    const display = document.getElementById('spProfileDisplay');
    const completion = data.completion_percentage || 0;

    display.innerHTML = `
        <pre>${JSON.stringify(data, null, 2)}</pre>
        <div class="completion-bar">
            <div class="completion-fill" style="width: ${completion}%"></div>
        </div>
        <div class="completion-text">Profile Completion: ${completion}%</div>
    `;
}

// ==================== PROJECT APIs ====================

function initializeProjectAPIs() {
    // Create Project
    document.getElementById('createProjectForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        setLoading(btn, true);

        const data = getFormData(e.target);
        const result = await apiRequest('/client/projects/', 'POST', data, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Project created successfully!', 'success');
            e.target.reset();
            refreshMyProjects();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Refresh My Projects
    document.getElementById('refreshMyProjects')?.addEventListener('click', refreshMyProjects);
}

async function refreshMyProjects() {
    const btn = document.getElementById('refreshMyProjects');
    const list = document.getElementById('myProjectsList');

    setLoading(btn, true);
    const result = await apiRequest('/client/projects/', 'GET', null, true);
    setLoading(btn, false);

    if (result.success) {
        renderProjects(result.data, list, true);
        showToast('Projects list updated', 'success');
    } else {
        showToast(result.error, 'error');
    }
}

function renderProjects(projects, container, isOwner = false) {
    if (!projects || projects.length === 0) {
        container.innerHTML = '<p class="placeholder">No projects found.</p>';
        return;
    }

    container.innerHTML = projects.map(p => `
        <div class="item-card">
            <h4>${p.title}</h4>
            <div class="meta">${p.budget_range || 'No budget'} | ${p.currency || ''} | ${p.project_duration || 'No duration'}</div>
            <div class="description">${p.description}</div>
            <div class="tags">
                ${(p.skills_required || '').split(',').map(s => s.trim() ? `<span class="item-tag">${s.trim()}</span>` : '').join('')}
            </div>
            ${isOwner ? `
                <div class="item-actions">
                    <button class="btn btn-primary btn-sm" onclick="viewProjectBids(${p.id}, '${p.title.replace(/'/g, "\\'")}')">View Bids</button>
                    <div id="bids-container-${p.id}" class="bids-list hidden"></div>
                </div>
            ` : `
                <div class="item-actions">
                    <button class="btn btn-primary btn-sm" onclick="showBidForm(${p.id}, '${p.title.replace(/'/g, "\\'")}')">Submit Bid</button>
                </div>
            `}
        </div>
    `).join('');
}

// ==================== BIDDING APIs ====================

function initializeBiddingAPIs() {
    // Refresh Available Projects
    document.getElementById('refreshAvailableProjects')?.addEventListener('click', async (e) => {
        setLoading(e.target, true);
        // Note: For now we use the same endpoint but SP should ideally have a browse projects endpoint
        // For testing, we'll allow SP to see all projects or we should implement a public listing
        // Let's try to get projects from client projects endpoint (might fail if auth check is strict)
        // Actually, let's just use the same /client/projects/ for testing if SP has access or create a new one.
        // For this task, I'll assume SP can list projects they can bid on.
        const result = await apiRequest('/client/projects/', 'GET', null, true);
        setLoading(e.target, false);

        if (result.success) {
            renderProjects(result.data, document.getElementById('availableProjectsList'), false);
        } else {
            showToast(result.error, 'error');
        }
    });

    // Refresh My Bids
    document.getElementById('refreshMyBids')?.addEventListener('click', refreshMyBids);
}

async function refreshMyBids() {
    const btn = document.getElementById('refreshMyBids');
    const list = document.getElementById('myBidsList');

    setLoading(btn, true);
    const result = await apiRequest('/service-provider/my-bids', 'GET', null, true);
    setLoading(btn, false);

    if (result.success) {
        if (!result.data || result.data.length === 0) {
            list.innerHTML = '<p class="placeholder">No bids submitted yet.</p>';
            return;
        }

        list.innerHTML = result.data.map(b => `
            <div class="item-card">
                <h4>Project #${b.project_id}</h4>
                <div class="meta">Amount: ${b.bid_amount} ${b.currency}</div>
                <div class="description">${b.cover_letter}</div>
                <div class="status-badge ${b.status}">${b.status.toUpperCase()}</div>
            </div>
        `).join('');
        showToast('Bids list updated', 'success');
    } else {
        showToast(result.error, 'error');
    }
}

window.viewProjectBids = async function (projectId, projectTitle) {
    const container = document.getElementById(`bids-container-${projectId}`);

    if (!container.classList.contains('hidden')) {
        container.classList.add('hidden');
        return;
    }

    container.innerHTML = '<p class="loading">Loading bids...</p>';
    container.classList.remove('hidden');

    const result = await apiRequest(`/client/projects/${projectId}/bids`, 'GET', null, true);

    if (result.success) {
        if (!result.data || result.data.length === 0) {
            container.innerHTML = '<p class="placeholder">No bids yet.</p>';
            return;
        }

        container.innerHTML = result.data.map(b => `
            <div class="bid-item">
                <div class="bid-meta">Amount: ${b.bid_amount} ${b.currency} | Status: ${b.status}</div>
                <div class="bid-letter">${b.cover_letter}</div>
                 ${b.status === 'pending' ? `
                     <button class="btn btn-primary btn-sm" onclick="acceptBid(${projectId}, ${b.id})">Accept Bid</button>
                 ` : ''}
                 ${b.status === 'accepted' ? `
                     <button class="btn btn-success btn-sm" onclick="showContractForm(${projectId}, ${b.id}, '${projectTitle.replace(/'/g, "\\'")}')">Sign Contract</button>
                 ` : ''}
             </div>
        `).join('');
    } else {
        container.innerHTML = `<p class="error">${result.error}</p>`;
    }
};

window.acceptBid = async function (projectId, bidId) {
    if (!confirm('Are you sure you want to accept this bid? This will reject all other bids.')) return;

    const result = await apiRequest(`/client/projects/${projectId}/bids/${bidId}/accept`, 'PUT', null, true);

    if (result.success) {
        showToast('Bid accepted successfully!', 'success');
        refreshMyProjects();
    } else {
        showToast(result.error, 'error');
    }
}

window.showBidForm = function (projectId, projectTitle) {
    const bidAmount = prompt(`Enter Bid Amount for "${projectTitle}":`);
    if (bidAmount === null) return;

    const currency = prompt(`Enter Currency (e.g. USD):`, 'USD');
    if (currency === null) return;

    const coverLetter = prompt(`Enter Cover Letter:`);
    if (coverLetter === null) return;

    submitBid(projectId, {
        bid_amount: parseInt(bidAmount),
        currency: currency,
        cover_letter: coverLetter
    });
};


// ==================== CONTRACT APIs ====================

function initializeContractAPIs() {
    // Refresh My Contracts
    document.getElementById('refreshMyContracts')?.addEventListener('click', refreshMyContracts);
    document.getElementById('refreshMyContractsSP')?.addEventListener('click', refreshMyContractsSP);

    // Create Contract Form (Client)
    document.getElementById('createContractForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button[type="submit"]');
        setLoading(btn, true);

        const formData = new FormData(e.target);
        const result = await apiMultipartRequest('/client/contracts/', 'POST', formData, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Contract signed and saved successfully!', 'success');
            hideContractForm();
            refreshMyContracts();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });

    // Sign Contract Form (SP)
    document.getElementById('spSignContractForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button[type="submit"]');
        const contractId = document.getElementById('spContractId').value;
        setLoading(btn, true);

        const formData = new FormData(e.target);
        const result = await apiMultipartRequest(`/client/contracts/${contractId}/sign/service-provider`, 'POST', formData, true);

        setLoading(btn, false);

        if (result.success) {
            displayResponse(result.data);
            showToast('Contract signed by you!', 'success');
            hideSPContractForm();
            refreshMyContractsSP();
        } else {
            displayResponse({ error: result.error }, true);
            showToast(result.error, 'error');
        }
    });
}

window.showContractForm = function (projectId, bidId, projectTitle) {
    document.getElementById('contractProjectId').value = projectId;
    document.getElementById('contractBidId').value = bidId;
    document.getElementById('contractProjectTitle').textContent = projectTitle;
    document.getElementById('contractFormSection').classList.remove('hidden');
    document.getElementById('contractFormSection').scrollIntoView({ behavior: 'smooth' });
};

window.hideContractForm = function () {
    document.getElementById('contractFormSection').classList.add('hidden');
    document.getElementById('createContractForm').reset();
};

window.showSPContractForm = function (contractId, projectId) {
    document.getElementById('spContractId').value = contractId;
    document.getElementById('spContractProjectIdDisplay').textContent = projectId;
    document.getElementById('spContractFormSection').classList.remove('hidden');
    document.getElementById('spContractFormSection').scrollIntoView({ behavior: 'smooth' });
};

window.hideSPContractForm = function () {
    document.getElementById('spContractFormSection').classList.add('hidden');
    document.getElementById('spSignContractForm').reset();
};

async function refreshMyContracts() {
    const btn = document.getElementById('refreshMyContracts');
    const list = document.getElementById('myContractsList');

    setLoading(btn, true);
    const result = await apiRequest('/client/contracts/', 'GET', null, true);
    setLoading(btn, false);

    if (result.success) {
        renderContracts(result.data, list, 'client');
        showToast('Contracts list updated', 'success');
    } else {
        showToast(result.error, 'error');
    }
}

async function refreshMyContractsSP() {
    const btn = document.getElementById('refreshMyContractsSP');
    const list = document.getElementById('myContractsListSP');

    setLoading(btn, true);
    const result = await apiRequest('/client/contracts/service-provider', 'GET', null, true);
    setLoading(btn, false);

    if (result.success) {
        renderContracts(result.data, list, 'service_provider');
        showToast('Contracts list updated', 'success');
    } else {
        showToast(result.error, 'error');
    }
}

function renderContracts(contracts, container, role) {
    if (!contracts || contracts.length === 0) {
        container.innerHTML = '<p class="placeholder">No contracts yet.</p>';
        return;
    }

    container.innerHTML = contracts.map(c => `
        <div class="item-card">
            <h4>Contract #${c.id} for Project #${c.project_id}</h4>
            <div class="meta">Status: <span class="status-badge ${c.status}">${c.status.toUpperCase()}</span> | Created: ${new Date(c.created_at).toLocaleDateString()}</div>
            <div class="description">
                <strong>Terms:</strong><br>
                ${c.terms_and_conditions.replace(/\n/g, '<br>')}
            </div>
            
            <div class="signatures-grid">
                ${c.client_signature_path ? `
                    <div class="signature-display">
                        <strong>Client Signature:</strong><br>
                        <img src="http://localhost:8000/static/${c.client_signature_path}" alt="Client Signature" style="max-width: 150px; border: 1px solid #ddd; margin-top: 5px; background: white;">
                    </div>
                ` : ''}
                
                ${c.service_provider_signature_path ? `
                    <div class="signature-display">
                        <strong>Provider Signature:</strong><br>
                        <img src="http://localhost:8000/static/${c.service_provider_signature_path}" alt="Provider Signature" style="max-width: 150px; border: 1px solid #ddd; margin-top: 5px; background: white;">
                    </div>
                ` : (role === 'service_provider' && c.status === 'client_signed' ? `
                    <div class="signature-placeholder">
                        <button class="btn btn-success btn-sm" onclick="showSPContractForm(${c.id}, ${c.project_id})">Sign This Contract</button>
                    </div>
                ` : '<strong>Provider Signature:</strong><br><i>Waiting for provider signature...</i>')}
            </div>
        </div>
    `).join('');
}
