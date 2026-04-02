const API_URL = '/api';

// ===== AUTENTICACIÓN =====
function getToken() {
    return localStorage.getItem('token');
}

function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            return JSON.parse(userStr);
        } catch (e) {
            return null;
        }
    }
    return null;
}

function isAuthenticated() {
    return !!getToken() && !!getCurrentUser();
}

function isAdmin() {
    const user = getCurrentUser();
    return user && user.rol === 'admin';
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

// Utilities
async function apiCall(endpoint, method = 'GET', body = null) {
    const token = getToken();
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const data = await response.json();
        
        // Si el token es inválido, cerrar sesión
        if ((response.status === 401 || response.status === 422) && data.error && data.error.toLowerCase().includes('token')) {
            logout();
            throw new Error('Sesión expirada, por favor inicie sesión nuevamente');
        }
        
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
    if (!dateStr) return '';
    // Fix for YYYY-MM-DD strings being treated as UTC by some browsers
    const d = new Date(dateStr.replace(/-/g, '/'));
    return d.toLocaleDateString('es-ES', { 
        weekday: 'short', 
        day: '2-digit', 
        month: 'short' 
    }).replace('.', '');
}

// UI Helpers
function showToast(message, type = 'success') {
    // Basic alert for now, could be improved to a real toast
    alert(message);
}

// ===== ACTUALIZAR NAVBAR SEGÚN ESTADO DE SESIÓN =====
function updateNavbarAuth() {
    const navLinks = document.querySelector('.nav-links');
    if (!navLinks) return;
    
    const user = getCurrentUser();
    
    if (isAuthenticated()) {
        // User is logged in - show personalized menu
        let adminLinks = '';
        if (user.rol === 'admin') {
            adminLinks = `
                <a href="admin.html">Admin</a>
                <a href="validacion.html">Validar Tiquete</a>
            `;
        }
        
        navLinks.innerHTML = `
            <a href="index.html">Cartelera</a>
            ${adminLinks}
            <span style="color: var(--text-muted); margin: 0 0.5rem;">|</span>
            <a href="#" onclick="showProfileModal(); return false;" style="color: var(--primary);">${user.nombre}</a>
            <a href="#" onclick="logout(); return false;" style="color: var(--danger);">Cerrar Sesión</a>
        `;
    } else {
        // User is not logged in - show login/register links
        navLinks.innerHTML = `
            <a href="index.html">Cartelera</a>
            <a href="login.html" style="color: var(--primary);">Iniciar Sesión</a>
            <a href="registro.html" style="color: var(--success);">Registrarse</a>
        `;
    }
}

// Show user profile modal
function showProfileModal() {
    const user = getCurrentUser();
    if (!user) return;
    
    const modalHtml = `
        <div id="profileModal" style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;display:flex;align-items:center;justify-content:center;">
            <div style="background:#1a1a2e;padding:2rem;border-radius:12px;max-width:450px;width:90%;">
                <h2 style="margin-bottom:1.5rem;">Mi Perfil</h2>
                
                <div style="margin-bottom:1rem;">
                    <label style="display:block;margin-bottom:0.5rem;color:#94a3b8;">Nombre</label>
                    <input type="text" id="profileName" value="${user.nombre}" style="width:100%;padding:0.75rem;background:#0f0f23;border:1px solid #333;border-radius:8px;color:white;">
                </div>
                
                <div style="margin-bottom:1rem;">
                    <label style="display:block;margin-bottom:0.5rem;color:#94a3b8;">Email</label>
                    <input type="email" value="${user.email || 'No disponible'}" disabled style="width:100%;padding:0.75rem;background:#333;border:1px solid #333;border-radius:8px;color:#666;">
                </div>
                
                <div style="margin-bottom:1.5rem;">
                    <label style="display:block;margin-bottom:0.5rem;color:#94a3b8;">Rol</label>
                    <span style="background:${user.rol === 'admin' ? '#22c55e' : '#6366f1'};padding:0.25rem 0.75rem;border-radius:4px;">${user.rol === 'admin' ? 'Administrador' : 'Cliente'}</span>
                </div>
                
                <hr style="border-color:#333;margin:1.5rem 0;">
                
                <h3 style="margin-bottom:1rem;">Cambiar Contraseña</h3>
                <div style="margin-bottom:1rem;">
                    <label style="display:block;margin-bottom:0.5rem;color:#94a3b8;">Contraseña Actual</label>
                    <input type="password" id="currentPassword" style="width:100%;padding:0.75rem;background:#0f0f23;border:1px solid #333;border-radius:8px;color:white;">
                </div>
                <div style="margin-bottom:1rem;">
                    <label style="display:block;margin-bottom:0.5rem;color:#94a3b8;">Nueva Contraseña</label>
                    <input type="password" id="newPassword" style="width:100%;padding:0.75rem;background:#0f0f23;border:1px solid #333;border-radius:8px;color:white;">
                </div>
                <div style="margin-bottom:1.5rem;">
                    <label style="display:block;margin-bottom:0.5rem;color:#94a3b8;">Confirmar Nueva Contraseña</label>
                    <input type="password" id="confirmPassword" style="width:100%;padding:0.75rem;background:#0f0f23;border:1px solid #333;border-radius:8px;color:white;">
                </div>
                
                <div style="display:flex;gap:1rem;">
                    <button onclick="updateProfile()" style="flex:1;padding:0.75rem;background:#6366f1;border:none;border-radius:8px;color:white;cursor:pointer;">Guardar</button>
                    <button onclick="document.getElementById('profileModal').remove()" style="padding:0.75rem;background:transparent;border:1px solid #666;border-radius:8px;color:#94a3b8;cursor:pointer;">Cerrar</button>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existing = document.getElementById('profileModal');
    if (existing) existing.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// Update user profile
async function updateProfile() {
    const nombre = document.getElementById('profileName').value;
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    try {
        // Update name
        await apiCall('/auth/update-profile', 'PUT', { nombre });
        
        // Update local storage
        const user = getCurrentUser();
        user.nombre = nombre;
        localStorage.setItem('user', JSON.stringify(user));
        
        // Change password if provided
        if (currentPassword && newPassword) {
            if (newPassword !== confirmPassword) {
                alert('Las contraseñas no coinciden');
                return;
            }
            if (newPassword.length < 6) {
                alert('La contraseña debe tener al menos 6 caracteres');
                return;
            }
            
            await apiCall('/auth/change-password', 'POST', {
                current_password: currentPassword,
                new_password: newPassword
            });
        }
        
        alert('Perfil actualizado correctamente');
        document.getElementById('profileModal').remove();
        updateNavbarAuth();
    } catch (error) {
        alert('Error al actualizar: ' + error.message);
    }
}
