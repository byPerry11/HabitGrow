const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_URL = isLocalhost ? 'http://localhost:8000/users/api' : 'https://api.habitgrowtracking.com/users/api';

// Handle Login
async function handleLogin(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const emailInput = e.target.querySelector('input[type="text"]'); // Verify selector matches HTML
    const passwordInput = document.getElementById('loginPass');

    // Loading State
    const originalContent = btn.innerHTML;
    btn.innerHTML = '<i class="ph-bold ph-spinner animate-spin text-xl"></i>';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: emailInput.value, // Using username as per DRF default
                password: passwordInput.value
            })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            showToast(`¡Bienvenido de vuelta, ${data.user.username}!`, 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            showToast(data.non_field_errors ? data.non_field_errors[0] : 'Error al iniciar sesión', 'error');
            resetBtn(btn, originalContent);
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error de conexión con el servidor', 'error');
        resetBtn(btn, originalContent);
    }
}

// Handle Register
async function handleRegister(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const usernameInput = e.target.querySelector('input[placeholder="Tu nombre público"]');
    const emailInput = e.target.querySelector('input[type="email"]');
    const passwordInput = document.getElementById('regPass');
    const confirmInput = document.getElementById('regPassConfirm');

    // Validation
    if (passwordInput.value !== confirmInput.value) {
        showToast('Las contraseñas no coinciden', 'error');
        confirmInput.parentElement.classList.add('border-red-400', 'shake');
        setTimeout(() => confirmInput.parentElement.classList.remove('shake'), 500);
        return;
    }

    // Loading State
    const originalContent = btn.innerHTML;
    btn.innerHTML = '<i class="ph-bold ph-spinner animate-spin text-xl"></i>';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: usernameInput.value,
                email: emailInput.value,
                password: passwordInput.value
            })
        });

        const data = await response.json();

        if (response.ok) {
            showToast('¡Cuenta creada con éxito! Iniciando sesión...', 'success');

            // Auto Login / or Token provided?
            if (data.token) {
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
            } else {
                // Fallback to login tab
                switchTab('login');
                resetBtn(btn, originalContent);
            }
        } else {
            // Handle errors
            let msg = 'Error al registrarse';
            if (data.username) msg = `Usuario: ${data.username[0]}`;
            if (data.email) msg = `Email: ${data.email[0]}`;
            showToast(msg, 'error');
            resetBtn(btn, originalContent);
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error de conexión', 'error');
        resetBtn(btn, originalContent);
    }
}

function resetBtn(btn, content) {
    btn.innerHTML = content;
    btn.disabled = false;
}

// ───────────────────────────────────────────────
// Google Sign-In / One Tap
// ───────────────────────────────────────────────

/**
 * Callback que invoca Google cuando el usuario completa el Sign-In.
 * Se llama desde el botón de Google (data-callback="handleGoogleLogin")
 * y también desde One Tap.
 *
 * @param {Object} response - Objeto de respuesta de Google con { credential }
 */
async function handleGoogleLogin(response) {
    const googleBtn = document.getElementById('googleSignInBtn');
    const originalContent = googleBtn ? googleBtn.innerHTML : null;

    // Mostrar estado de carga en el botón
    if (googleBtn) {
        googleBtn.innerHTML = '<i class="ph-bold ph-spinner animate-spin text-xl mr-2"></i>Conectando...';
        googleBtn.disabled = true;
    }

    try {
        const res = await fetch(`${API_URL}/google-auth/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_token: response.credential })
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));

            const msg = data.created
                ? `¡Bienvenido a HabitGrow, ${data.user.username}! 🐾`
                : `¡Hola de nuevo, ${data.user.username}!`;

            showToast(msg, 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1200);
        } else {
            // Log completo para diagnóstico
            console.error('❌ Google Auth Error Detail:', data.detail || data.error);
            console.error('❌ Google Auth Trace:', data.trace);
            showToast(data.detail || data.error || 'Error al iniciar sesión con Google', 'error');
            if (googleBtn && originalContent) resetBtn(googleBtn, originalContent);
        }
    } catch (error) {
        console.error('Google Auth Error:', error);
        showToast('Error de conexión con el servidor', 'error');
        if (googleBtn && originalContent) resetBtn(googleBtn, originalContent);
    }
}

// Initial check — redirige al dashboard si ya tiene sesión activa
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = 'dashboard.html';
    }
});
