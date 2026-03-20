const API_URL = 'http://localhost:5000/api';

// Utilities
async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'API Error');
        }
        return data;
    } catch (error) {
        console.error('API Call Error:', error);
        throw error;
    }
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
}

// UI Helpers
function showToast(message, type = 'success') {
    // Basic alert for now, could be improved to a real toast
    alert(message);
}
