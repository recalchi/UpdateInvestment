// API Base URLs
const API_BASE = '/api/portfolio';

// DOM Elements
const elements = {
    statusIndicator: document.getElementById('status-indicator'),
    totalPositions: document.getElementById('total-positions'),
    lastUpdate: document.getElementById('last-update'),
    nordStatus: document.getElementById('nord-status'),
    levanteStatus: document.getElementById('levante-status'),
    portfolioTableBody: document.getElementById('portfolio-table-body'),
    configModal: document.getElementById('config-modal'),
    toast: document.getElementById('toast'),
    toastIcon: document.getElementById('toast-icon'),
    toastMessage: document.getElementById('toast-message'),
    
    // Buttons
    updatePortfolioBtn: document.getElementById('update-portfolio-btn'),
    testConnectionsBtn: document.getElementById('test-connections-btn'),
    viewConfigBtn: document.getElementById('view-config-btn'),
    closeModalBtn: document.getElementById('close-modal'),
    cancelConfigBtn: document.getElementById('cancel-config'),
    saveConfigBtn: document.getElementById('save-config'),
    testNordBtn: document.getElementById('test-nord-btn'),
    testLevanteBtn: document.getElementById("test-levante-btn"),
    testExcelBtn: document.getElementById("test-excel-btn"),
    
    // Loading indicators
    updateLoading: document.getElementById('update-loading'),
    testLoading: document.getElementById('test-loading'),
    
    // Form inputs
    nordEmail: document.getElementById('nord-email'),
    nordPassword: document.getElementById('nord-password'),
    levanteEmail: document.getElementById('levante-email'),
    levantePassword: document.getElementById("levante-password"),
    logPanel: document.getElementById("log-panel")
};

// Utility Functions
function showToast(message, type = 'success') {
    const toast = elements.toast;
    const icon = elements.toastIcon;
    const messageEl = elements.toastMessage;
    
    // Set message
    messageEl.textContent = message;
    
    // Set style based on type
    if (type === 'success') {
        toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300';
        icon.className = 'fas fa-check-circle mr-2';
    } else if (type === 'error') {
        toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300';
        icon.className = 'fas fa-exclamation-circle mr-2';
    } else if (type === 'warning') {
        toast.className = 'fixed top-4 right-4 bg-yellow-500 text-white px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300';
        icon.className = 'fas fa-exclamation-triangle mr-2';
    }
    
    // Show toast
    toast.style.transform = 'translateX(0)';
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
    }, 3000);
}

function showLoading(element) {
    element.classList.add("show");
}

function hideLoading(element) {
    element.classList.remove("show");
}

function appendLog(message, type = "info") {
    const logEntry = document.createElement("div");
    logEntry.classList.add("mb-1");
    let icon = "";
    let textColor = "text-gray-300";

    if (type === "success") {
        icon = "<i class=\"fas fa-check-circle mr-2\"></i>";
        textColor = "text-green-400";
    } else if (type === "error") {
        icon = "<i class=\"fas fa-times-circle mr-2\"></i>";
        textColor = "text-red-400";
    } else if (type === "warning") {
        icon = "<i class=\"fas fa-exclamation-triangle mr-2\"></i>";
        textColor = "text-yellow-400";
    } else if (type === "info") {
        icon = "<i class=\"fas fa-info-circle mr-2\"></i>";
        textColor = "text-blue-400";
    }

    logEntry.innerHTML = `<span class="${textColor}">${icon}${message}</span>`;
    elements.logPanel.appendChild(logEntry);
    elements.logPanel.scrollTop = elements.logPanel.scrollHeight;
}

function formatCurrency(value) {
    if (value === null || value === undefined || value === '') return '-';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatNumber(value) {
    if (value === null || value === undefined || value === '') return '-';
    return new Intl.NumberFormat('pt-BR').format(value);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR');
    } catch (e) {
        return dateString;
    }
}

// API Functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `HTTP error! status: ${response.status}`);
        }
        
        appendLog(`API call to ${endpoint} successful.`, "success");
        return data;
    } catch (error) {
        console.error("API call failed:", error);
        appendLog(`API call to ${endpoint} failed: ${error.message}`, "error");
        throw error;
    }
}

async function checkSystemStatus() {
    try {
        const response = await apiCall('/status');
        elements.statusIndicator.innerHTML = '<i class="fas fa-circle mr-1"></i>Online';
        elements.statusIndicator.className = 'px-3 py-1 rounded-full text-sm bg-green-500';
        appendLog("Sistema online.", "success");
    } catch (error) {
        elements.statusIndicator.innerHTML = '<i class="fas fa-circle mr-1"></i>Offline';
        elements.statusIndicator.className = 'px-3 py-1 rounded-full text-sm bg-red-500';
        appendLog("Sistema offline ou erro ao verificar status.", "error");
    }
}

async function loadPortfolioData() {
    try {
        const response = await apiCall('/portfolio');
        const portfolioData = response.data || [];
        
        // Update dashboard cards
        elements.totalPositions.textContent = portfolioData.length;
        
        // Fetch last update time from backend
        const lastUpdateTimeResponse = await apiCall("/last-update-time");
        if (lastUpdateTimeResponse.status === "success") {
            elements.lastUpdate.textContent = formatDate(lastUpdateTimeResponse.last_update_time);
        } else {
            elements.lastUpdate.textContent = "N/A";
        }
        
        // Update table
        updatePortfolioTable(portfolioData);
        
    } catch (error) {
        console.error('Failed to load portfolio data:', error);
        appendLog(`Erro ao carregar dados do portfólio: ${error.message}`, "error");
        elements.portfolioTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-4 text-center text-red-500">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    Erro ao carregar dados do portfólio: ${error.message}
                </td>
            </tr>
        `;
    }
}

function updatePortfolioTable(data) {
    if (!data || data.length === 0) {
        elements.portfolioTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                    <i class="fas fa-info-circle mr-2"></i>
                    Nenhuma posição encontrada
                </td>
            </tr>
        `;
        return;
    }
    
    elements.portfolioTableBody.innerHTML = data.map(item => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                ${item.Ativo || '-'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatNumber(item.Quantidade)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatCurrency(item.PrecoMedio)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatCurrency(item.PrecoAtual)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatCurrency(item.ValorAtual)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatDate(item['DATA ATT'])}
            </td>
        </tr>
    `).join('');
}

async function updatePortfolio() {
    showLoading(elements.updateLoading);
    elements.updatePortfolioBtn.disabled = true;
    
    try {
        const response = await apiCall('/update', { method: 'POST' });
        showToast('Portfólio atualizado com sucesso!', 'success');
        
        // Reload portfolio data
        await loadPortfolioData();
        
    } catch (error) {
        console.error('Failed to update portfolio:', error);
        showToast(`Erro ao atualizar portfólio: ${error.message}`, 'error');
    } finally {
        hideLoading(elements.updateLoading);
        elements.updatePortfolioBtn.disabled = false;
    }
}

async function testConnections() {
    showLoading(elements.testLoading);
    elements.testConnectionsBtn.disabled = true;
    
    try {
        // Test Nord Research connection
        const nordResponse = await apiCall('/test-nord', {
            method: 'POST',
            body: JSON.stringify({
                email: 'renan.recalchi.adm@gmail.com',
                password: 'Gordinez123@'
            })
        });
        
        elements.nordStatus.textContent = nordResponse.status === 'success' ? 'OK' : 'Erro';
        
        // Test Levante Ideias connection
        const levanteResponse = await apiCall('/test-levante', {
            method: 'POST',
            body: JSON.stringify({
                email: 'recalchi.consultoria@gmail.com',
                password: 'Gordinez123@'
            })
        });
        
        elements.levanteStatus.textContent = levanteResponse.status === 'success' ? 'OK' : 'Erro';
        
        showToast('Teste de conexões concluído!', 'success');
        
    } catch (error) {
        console.error('Failed to test connections:', error);
        showToast(`Erro ao testar conexões: ${error.message}`, 'error');
        elements.nordStatus.textContent = 'Erro';
        elements.levanteStatus.textContent = 'Erro';
    } finally {
        hideLoading(elements.testLoading);
        elements.testConnectionsBtn.disabled = false;
    }
}

async function testNordConnection() {
    const email = elements.nordEmail.value;
    const password = elements.nordPassword.value;
    
    if (!email || !password) {
        showToast('Por favor, preencha email e senha da Nord Research', 'warning');
        return;
    }
    
    elements.testNordBtn.disabled = true;
    elements.testNordBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Testando...';
    
    try {
        const response = await apiCall('/test-nord', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (response.status === 'success') {
            showToast('Conexão com Nord Research bem-sucedida!', 'success');
        } else {
            showToast('Falha na conexão com Nord Research', 'error');
        }
        
    } catch (error) {
        console.error('Failed to test Nord connection:', error);
        showToast(`Erro ao testar Nord Research: ${error.message}`, 'error');
    } finally {
        elements.testNordBtn.disabled = false;
        elements.testNordBtn.innerHTML = '<i class="fas fa-plug mr-1"></i>Testar Conexão';
    }
}

async function testLevanteConnection() {
    const email = elements.levanteEmail.value;
    const password = elements.levantePassword.value;
    
    if (!email || !password) {
        showToast('Por favor, preencha email e senha da Levante Ideias', 'warning');
        return;
    }
    
    elements.testLevanteBtn.disabled = true;
    elements.testLevanteBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Testando...';
    
    try {
        const response = await apiCall('/test-levante', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (response.status === 'success') {
            showToast('Conexão com Levante Ideias bem-sucedida!', 'success');
        } else {
            showToast('Falha na conexão com Levante Ideias', 'error');
        }
        
    } catch (error) {
        console.error('Failed to test Levante connection:', error);
        showToast(`Erro ao testar Levante Ideias: ${error.message}`, 'error');
    } finally {
        elements.testLevanteBtn.disabled = false;
        elements.testLevanteBtn.innerHTML = '<i class="fas fa-plug mr-1"></i>Testar Conexão';
    }
}

function showConfigModal() {
    elements.configModal.classList.remove('hidden');
    
    // Load current credentials (placeholder - in production, don't show passwords)
    elements.nordEmail.value = 'renan.recalchi.adm@gmail.com';
    elements.levanteEmail.value = 'recalchi.consultoria@gmail.com';
}

function hideConfigModal() {
    elements.configModal.classList.add('hidden');
}

async function testExcelConnection() {
    elements.testExcelBtn.disabled = true;
    elements.testExcelBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Testando...';

    try {
        const response = await apiCall('/test-excel');
        if (response.status === 'success') {
            showToast(`Planilha lida com sucesso! Colunas: ${response.columns.join(', ')}`, 'success');
            console.log("Prévia da planilha:", response.preview);
        } else {
            showToast(`Erro ao ler planilha: ${response.message}`, 'error');
        }
    } catch (error) {
        console.error('Failed to test Excel connection:', error);
        showToast(`Erro ao testar planilha: ${error.message}`, 'error');
    } finally {
        elements.testExcelBtn.disabled = false;
        elements.testExcelBtn.innerHTML = '<i class="fas fa-file-excel mr-1"></i>Testar Planilha';
    }
}

function saveConfig() {
    // In a real implementation, you would save the configuration
    showToast("Configurações salvas com sucesso!", "success");
    hideConfigModal();
}

// Event Listeners
elements.updatePortfolioBtn.addEventListener("click", updatePortfolio);
elements.testConnectionsBtn.addEventListener("click", testConnections);
elements.viewConfigBtn.addEventListener("click", showConfigModal);
elements.closeModalBtn.addEventListener("click", hideConfigModal);
elements.cancelConfigBtn.addEventListener("click", hideConfigModal);
elements.saveConfigBtn.addEventListener("click", saveConfig);
elements.testNordBtn.addEventListener("click", testNordConnection);
elements.testLevanteBtn.addEventListener("click", testLevanteConnection);
elements.testExcelBtn.addEventListener("click", testExcelConnection);

// Close modal when clicking outside
elements.configModal.addEventListener('click', (e) => {
    if (e.target === elements.configModal) {
        hideConfigModal();
    }
});

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Portfolio Management System initialized');
    
    // Check system status
    await checkSystemStatus();
    
    // Load initial data
    await loadPortfolioData();
    
    // Set up periodic status checks
    setInterval(checkSystemStatus, 30000); // Check every 30 seconds
});

// Handle keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Escape key closes modal
    if (e.key === 'Escape' && !elements.configModal.classList.contains('hidden')) {
        hideConfigModal();
    }
    
    // Ctrl+U for update portfolio
    if (e.ctrlKey && e.key === 'u') {
        e.preventDefault();
        updatePortfolio();
    }
    
    // Ctrl+T for test connections
    if (e.ctrlKey && e.key === 't') {
        e.preventDefault();
        testConnections();
    }
});

