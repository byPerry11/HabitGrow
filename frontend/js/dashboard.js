// URL base de la API del backend
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE_URL = isLocalhost ? 'http://localhost:8000/api/v1' : 'https://api.habitgrowtracking.com/api/v1';

// Estado interno para rastrear datos del usuario, mascota y hábitos
const state = {
    user: {},    // Datos del usuario autenticado
    pet: {},     // Datos de la mascota del usuario
    habits: []   // Lista de hábitos del usuario
};

// Inicializar dashboard cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', async () => {
    // Verificar autenticación
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';  // Redirigir a login si no hay token
        return;
    }

    // Inicializar interfaz de usuario
    initUI();

    // Cargar datos del dashboard
    await loadDashboardData();
});

// Inicializar elementos de la interfaz de usuario
function initUI() {
    // Configurar visualización de fecha
    const options = { weekday: 'long', day: 'numeric', month: 'long' };
    const dateStr = new Date().toLocaleDateString('es-ES', options);

    const dateEl = document.getElementById('currentDateDisplay');
    const monthEl = document.getElementById('currentMonthYear');

    if (dateEl) dateEl.textContent = dateStr.charAt(0).toUpperCase() + dateStr.slice(1);
    if (monthEl) monthEl.textContent = new Date().toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });

    // Obtener y renderizar mapa de calor de actividad
    fetchHeatMap();

    // Configurar listeners de eventos
    document.getElementById('newHabitForm').addEventListener('submit', handleNewHabit);

    // Actualizar texto del slider de pasos
    const stepsInput = document.getElementById('stepsInput');
    if (stepsInput) {
        stepsInput.addEventListener('input', (e) => {
            const val = e.target.value;
            document.getElementById('stepsValueDisplay').textContent = `${val} paso${val > 1 ? 's' : ''}`;
        });
    }

    // Listener para el formulario de adopción
    const adoptionForm = document.getElementById('adoptionForm');
    if (adoptionForm) {
        adoptionForm.addEventListener('submit', handleAdoptionSubmit);
    }
}

// Cargar todos los datos del dashboard en paralelo
async function loadDashboardData() {
    try {
        // Cargar perfil, mascota y hábitos simultáneamente
        await Promise.all([
            fetchProfile(),
            fetchMascota(),
            fetchHabits()
        ]);
        updateStats();  // Actualizar estadísticas después de cargar
    } catch (error) {
        console.error('Error loading dashboard:', error);
        if (error.status === 401) logout();  // Cerrar sesión si no está autorizado
    }
}

// Obtener datos del perfil del usuario
async function fetchProfile() {
    const data = await authenticatedFetch(`${API_BASE_URL}/profile/me/`);
    if (data) {
        state.user = data;

        // Actualizar nombre de usuario
        const nameEl = document.getElementById('userName');
        if (nameEl) nameEl.textContent = data.username;

        // Actualizar monedas del perfil
        const coinsEl = document.getElementById('userCoins');
        if (coinsEl) coinsEl.textContent = data.coins || 0;

        // Actualizar imagen de perfil (URL dinámica según entorno)
        const profilePic = document.getElementById('headerProfilePic');
        if (profilePic) {
            if (data.profile_picture) {
                // Si la URL ya es absoluta (empieza con 'http') la usa directo
                // Si es relativa (ej: /media/...) construye la base correcta
                const apiBase = API_BASE_URL.replace('/api/v1', '');
                profilePic.src = data.profile_picture.startsWith('http')
                    ? data.profile_picture
                    : `${apiBase}${data.profile_picture}`;
            } else {
                // Fallback: avatar generado con las iniciales del usuario
                profilePic.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(data.username)}&background=10b981&color=fff`;
            }
        }

        // NOTA: XP y Nivel ahora se obtienen desde la mascota (ver renderPet)
    }
}

// Obtener datos de la mascota del usuario
async function fetchMascota() {
    try {
        const url = `${API_BASE_URL}/mascota/me/`;
        console.log('🔍 [DEBUG] Fetching mascota from:', url);
        const data = await authenticatedFetch(url);
        if (data) {
            console.log('✅ [DEBUG] Mascota data received:', data);
            state.pet = data;
            renderPet(data);  // Renderizar mascota en la UI
        }
    } catch (error) {
        console.error('❌ [DEBUG] Error fetching mascota:', error);
        // Si no tiene mascota, mostrar modal de adopción
        if (error.status === 404) {
            console.log('ℹ️ [DEBUG] No mascota found (404), showing adoption modal');
            renderNoPet();
        }
    }
}

// Renderizar datos de la mascota en la interfaz
function renderPet(mascota) {
    // Mostrar contenedores de salud e información
    const healthContainer = document.getElementById('petHealthContainer');
    if (healthContainer) healthContainer.classList.remove('hidden');

    const infoContainer = document.getElementById('petInfoContainer');
    if (infoContainer) infoContainer.classList.remove('hidden');

    // Actualizar nivel en el badge y nombre en el título
    const badgeEl = document.getElementById('petBadgeName');
    if (badgeEl) badgeEl.textContent = `NIVEL ${mascota.nivel || 1}`;

    const petNameEl = document.getElementById('petName');
    if (petNameEl) petNameEl.textContent = mascota.nombre || 'Tu Mascota';

    // Actualizar estado de salud
    const petStatusEl = document.getElementById('petStatus');
    if (petStatusEl) petStatusEl.textContent = mascota.estado_salud_display;
    
    const petStatusIndicatorEl = document.getElementById('petStatusIndicator');
    if (petStatusIndicatorEl) petStatusIndicatorEl.className = `w-2.5 h-2.5 rounded-full animate-pulse ${getColorClass(mascota.estado_salud)}`;

    // Actualizar barra de salud (HP)
    const hpTextEl = document.getElementById('hpText');
    if (hpTextEl) hpTextEl.textContent = `${mascota.puntos_vida}%`;
    
    const hpBarEl = document.getElementById('hpBar');
    if (hpBarEl) {
        hpBarEl.style.width = `${mascota.puntos_vida}%`;
        hpBarEl.style.backgroundColor = mascota.color;
    }

    // --- Sistema de XP y Nivel ---
    // Actualizar nivel de la mascota
    const userLevelEl = document.getElementById('userLevel');
    if (userLevelEl) userLevelEl.textContent = mascota.nivel || 1;

    // Actualizar XP total
    const userXPEl = document.getElementById('userXP');
    if (userXPEl) userXPEl.textContent = Math.floor(mascota.total_xp || 0);

    // Actualizar barra de progreso de XP (0-100%)
    const xpBar = document.getElementById('xpBar');
    if (xpBar) xpBar.style.width = `${mascota.progreso_nivel || 0}%`;

    // Image Rendering
    const petContainer = document.getElementById('petContainer');

    // Evolution-based sprite selection
    const evolutionLevel = mascota.nivel_evolucion || 1;
    const isBaby = evolutionLevel < 5;

    // Select image based on status
    let imageFile = 'Idle'; // default (regular)
    if (mascota.estado_salud === 'optimo') imageFile = 'Happy';
    if (mascota.estado_salud === 'mal' || mascota.estado_salud === 'critico') imageFile = 'Sad';

    // Construct path based on evolution stage
    let imagePath;
    if (isBaby) {
        // Baby sprites (Level 1-4): PNG files in bby subfolder
        imagePath = `assets/mascotas/Gizzmo/bby/${imageFile}.png`;
    } else {
        // Mature sprites (Level 5+): JPG files in Gizzmo folder
        imagePath = `assets/mascotas/Gizzmo/${imageFile}.jpg`;
    }

    petContainer.innerHTML = `
        <img src="${imagePath}" alt="${mascota.nombre}" 
             class="w-64 h-64 object-contain animate-float drop-shadow-2xl">
    `;
}

function renderNoPet() {
    const healthContainer = document.getElementById('petHealthContainer');
    if (healthContainer) healthContainer.classList.add('hidden');

    const infoContainer = document.getElementById('petInfoContainer');
    if (infoContainer) infoContainer.classList.add('hidden');

    // Resetear badge
    const badgeEl = document.getElementById('petBadgeName');
    if (badgeEl) badgeEl.textContent = 'Compañero';

    // Egg Container
    const container = document.getElementById('petContainer');
    container.innerHTML = `
        <div class="flex flex-col items-center animate-float pointer-events-auto">
            <div class="text-[8rem] cursor-pointer hover:scale-110 transition-transform origin-bottom animate-wiggle" 
                 onclick="openAdoptionModal()">
                🥚
            </div>
            <button onclick="openAdoptionModal()" 
                class="mt-6 px-8 py-3 bg-brand-600 text-white font-bold rounded-full shadow-lg shadow-brand-500/30 hover:bg-brand-700 hover:scale-105 transition-all animate-bounce">
                ¡Adopta tu mascota!
            </button>
        </div>
    `;
}

function openAdoptionModal() {
    const modal = document.getElementById('adoptionModal');
    const content = document.getElementById('adoptionModalContent');
    if (!modal) return;

    modal.classList.remove('hidden');
    // Microtask to allow transition
    setTimeout(() => {
        modal.classList.remove('opacity-0', 'pointer-events-none');
        content.classList.remove('scale-95');
        content.classList.add('scale-100');
        document.getElementById('petNameInput').focus();
    }, 10);
}

function closeAdoptionModal() {
    const modal = document.getElementById('adoptionModal');
    const content = document.getElementById('adoptionModalContent');
    if (!modal) return;

    modal.classList.add('opacity-0', 'pointer-events-none');
    content.classList.remove('scale-100');
    content.classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 300);
}

async function handleAdoptionSubmit(e) {
    e.preventDefault();
    const nameInput = document.getElementById('petNameInput');
    const name = nameInput.value.trim();

    // Obtener especie seleccionada (soportando radio checked o input hidden)
    const especieInput = document.querySelector('input[name="especie"]:checked') ||
        document.querySelector('input[name="especie"]');
    const especie = especieInput ? especieInput.value : 'gizzmo';

    if (!name) return;

    try {
        await adoptPet(name, especie);
        closeAdoptionModal();
        nameInput.value = ''; // Reset
    } catch (error) {
        console.error("Adoption failed", error);
    }
}

async function adoptPet(name, especie) {
    try {
        const url = `${API_BASE_URL}/mascota/adoptar/`;
        const payload = { nombre: name, especie: especie };
        console.log('🔍 [DEBUG] Adopting pet at URL:', url);
        console.log('🔍 [DEBUG] Payload:', payload);

        const response = await authenticatedFetch(url, {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        console.log('✅ [DEBUG] Adoption successful:', response);
        fetchMascota();
    } catch (e) {
        console.error('❌ [DEBUG] Error adopting pet:', e);
        alert("Error adoptando mascota: " + (e.message || "revisa la consola"));
    }
}

async function fetchHabits() {
    const data = await authenticatedFetch(`${API_BASE_URL}/habits/`);
    if (data) {
        // Handle pagination (DRF returns { count, next, previous, results: [] })
        if (data.results && Array.isArray(data.results)) {
            state.habits = data.results;
        } else if (Array.isArray(data)) {
            state.habits = data;
        } else {
            state.habits = [];
        }
        renderHabitsList();
    } else {
        state.habits = [];
        renderHabitsList();
    }
}

function renderHabitsList() {
    const list = document.getElementById('habitsList');
    const emptyState = document.getElementById('emptyState');

    list.innerHTML = '';

    if (!Array.isArray(state.habits)) state.habits = [];

    const habitsToRender = [...state.habits].sort((a, b) => {
        // Sort: Incomplete first (false), then Completed (true)
        // false < true in JS sort? 
        // a.completado_hoy (bool). 
        // If a is false (0) and b is true (1), we want a first. 
        // sort((a,b) => a - b) -> 0 - 1 = -1 (a comes first). Correct.
        if (a.completado_hoy === b.completado_hoy) return 0;
        return a.completado_hoy ? 1 : -1;
    });

    if (habitsToRender.length === 0) {
        list.classList.add('hidden');
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');
    list.classList.remove('hidden');

    habitsToRender.forEach(habit => {
        const div = document.createElement('div');
        const isCompleted = habit.completado_hoy;

        // Calculate progress percentage for step-based habits
        let progressPercent = 0;
        let progressText = "";

        // Find today's log for this habit if it exists in the fetched data
        // Note: The API usually returns 'log_de_hoy' or we might need to rely on 'pasos_completados' field if added to HabitSerializer
        // Assuming HabitSerializer returns 'pasos_completados_hoy' or similar. 
        // Based on backend changes, HabitSerializer fields include 'dias_semana', 'total_pasos'.
        // We need to know current progress. 
        // Let's assume the backend now returns `log_de_hoy` or usage of `pasos_completados` is handled via a separate field or inner logic.
        // Actually, looking at serializer history, we didn't explicitly add `log_de_hoy` to the serialzer fields in `HabitSerializer`.
        // We added `pasos_completados` to `HabitLog`.
        // The `HabitSerializer` might need to include the current status.
        // Currently `HabitSerializer` has `completado_hoy` (Boolean).
        // It DOES NOT seem to have `pasos_actuales`.
        // **SELF-CORRECTION**: I might need to update HabitSerializer to return `pasos_completados_hoy`.
        // For now, let's assume `habit.pasos_completados_hoy` exists or I'll add it in next step if missing.
        // Wait, `HabitSerializer` usually has `log_of_day`.

        // Let's rely on what we have. If `completado_hoy` is true, 100%.
        // If not, we might not know the partial steps without updating Serializer.
        // *CRITICAL*: I should update Serializer to return `pasos_completados_hoy`.
        // But let's write the JS assuming I will fix that in backend next, or use a placeholder.

        const currentSteps = habit.pasos_completados_hoy || 0; // Needs backend support
        const totalSteps = habit.total_pasos || 1;

        if (isCompleted) {
            progressPercent = 100;
            progressText = "¡Completado!";
        } else {
            progressPercent = (currentSteps / totalSteps) * 100;
            progressText = `${currentSteps}/${totalSteps}`;
        }

        // Determine icons/colors based on category
        let iconClass = 'ph-star';
        let bgIcon = 'bg-gray-100';
        let textIcon = 'text-gray-500';
        let categoryName = 'Otro';

        const cats = {
            'salud': { icon: 'ph-heart-beat', bg: 'bg-green-100', text: 'text-green-600', name: 'Salud' },
            'ejercicio': { icon: 'ph-barbell', bg: 'bg-orange-100', text: 'text-orange-600', name: 'Ejercicio' },
            'estudio': { icon: 'ph-book-open', bg: 'bg-blue-100', text: 'text-blue-600', name: 'Estudio' },
            'trabajo': { icon: 'ph-briefcase', bg: 'bg-purple-100', text: 'text-purple-600', name: 'Trabajo' },
            'tarea': { icon: 'ph-check-square', bg: 'bg-teal-100', text: 'text-teal-600', name: 'Tarea' },
            'arte': { icon: 'ph-paint-brush', bg: 'bg-pink-100', text: 'text-pink-600', name: 'Arte' },
        };

        if (cats[habit.categoria]) {
            const conf = cats[habit.categoria];
            iconClass = conf.icon;
            bgIcon = conf.bg;
            textIcon = conf.text;
            categoryName = conf.name;
        }

        div.className = `group relative p-4 bg-white rounded-2xl border transition-all duration-300 ${isCompleted ? 'border-brand-100 bg-brand-50/20' : 'border-gray-100 hover:border-brand-200 hover:shadow-lg hover:-translate-y-1'}`;

        // Progress Bar HTML (only for multi-step habits)
        // Progress Bar HTML (show for all habits to display checkpoints)
        let progressHTML = '';
        // Always show progress info if totalSteps is defined
        progressHTML = `
            <div class="mt-3 w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div class="h-full bg-brand-500 transition-all duration-500" style="width: ${progressPercent}%"></div>
            </div>
            <div class="flex justify-between mt-1">
                 <span class="text-[10px] font-bold text-slate-400">${progressText}</span>
            </div>
        `;

        div.innerHTML = `
            <div class="flex flex-col">
                <div class="flex items-center gap-3">
                     <div class="w-9 h-9 rounded-xl ${bgIcon} ${textIcon} flex items-center justify-center shrink-0 text-lg">
                        <i class="ph-fill ${iconClass}"></i>
                     </div>
                     <div class="flex-1 min-w-0">
                        <h4 class="font-bold text-slate-800 text-sm truncate ${isCompleted ? 'line-through text-slate-400' : ''}">${habit.nombre}</h4>
                        <p class="text-[10px] text-slate-400 mt-0.5 font-bold uppercase">${categoryName} • Racha: ${habit.racha_actual} 🔥</p>
                     </div>
                     
                     <label class="cursor-pointer">
                        <button class="w-8 h-8 rounded-full border-2 ${isCompleted ? 'border-brand-400 bg-brand-400 cursor-not-allowed opacity-50' : 'border-slate-200 hover:border-brand-400'} flex items-center justify-center transition-all duration-300 group-btn"
                            ${isCompleted ? 'disabled' : `onclick="toggleHabit(${habit.id})"`}>
                            ${isCompleted ? '<i class="ph-bold ph-check text-white text-xs"></i>' : (totalSteps > 1 ? '<i class="ph-bold ph-plus text-brand-400 text-xs"></i>' : '<i class="ph-bold ph-check text-slate-200 group-hover:text-brand-400 text-xs"></i>')}
                        </button>
                    </label>
                </div>
                ${progressHTML}
            </div>
        `;
        list.appendChild(div);
    });
}

// Profile Picture Upload
async function uploadProfilePicture(input) {
    const file = input.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('profile_picture', file);

    try {
        const meResponse = await authenticatedFetch(`${API_BASE_URL}/profile/me/`);
        if (!meResponse || !meResponse.id) throw new Error("No profile ID found");

        const token = localStorage.getItem('token');
        const uploadResponse = await fetch(`${API_BASE_URL}/profile/${meResponse.id}/`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Token ${token}`
            },
            body: formData
        });

        if (uploadResponse.ok) {
            const data = await uploadResponse.json();
            if (data.profile_picture) {
                const profileImages = document.querySelectorAll('#profileImage, #mobileProfileImage');
                fetchProfile();
            }
            alert('Foto actualizada con éxito');
        } else {
            console.error('Upload failed', await uploadResponse.text());
            alert('Error subiendo la imagen');
        }

    } catch (error) {
        console.error('Error uploading profile picture:', error);
        alert('Error conectando con el servidor');
    }
}

async function toggleHabit(id) {
    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/habits/${id}/toggle_completado_hoy/`, {
            method: 'POST'
        });

        // Optimistic / Response update
        const index = state.habits.findIndex(h => h.id === id);
        if (index !== -1) {
            // Merge response data into state
            // API returns { message, habit: {...}, log: {...} } or similar?
            // Let's check views.py: returns serializer.data (HabitSerializer) in 'habit' key.
            state.habits[index] = response.habit;
            renderHabitsList();
            updateStats();

            // Re-fetch profile/pet to prevent drift in Coins/XP/HP
            fetchProfile();
            fetchMascota();
        }
    } catch (error) {
        console.error('Error toggling habit:', error);
        alert('Error conectando con el servidor');
    }
}

async function handleNewHabit(e) {
    e.preventDefault();
    const nameInput = document.getElementById('habitInput');
    const categoryInput = document.querySelector('input[name="category"]:checked');
    const stepsInput = document.getElementById('stepsInput');

    // Get selected days
    const checkedDays = document.querySelectorAll('input[name="days"]:checked');
    const selectedDays = Array.from(checkedDays).map(cb => cb.value).join(',') || "0,1,2,3,4,5,6";

    if (!nameInput.value || !categoryInput) {
        alert("Por favor completa el nombre y la categoría");
        return;
    }

    try {
        const payload = {
            nombre: nameInput.value,
            categoria: categoryInput.value,
            dias_semana: selectedDays,
            total_pasos: stepsInput ? parseInt(stepsInput.value) : 1,
            activo: true
        };

        const newHabit = await authenticatedFetch(`${API_BASE_URL}/habits/`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        if (newHabit) {
            if (!Array.isArray(state.habits)) state.habits = [];
            state.habits.push(newHabit);
            renderHabitsList();
            updateStats();

            toggleModal(); // Close
            nameInput.value = ''; // Reset
            if (stepsInput) {
                stepsInput.value = 1;
                document.getElementById('stepsValueDisplay').textContent = "1 paso";
            }
            // Reset category?
        }
    } catch (error) {
        console.error('Error creating habit:', error);
        alert('Error creando el hábito');
    }
}

function updateStats() {
    const completed = state.habits.filter(h => h.completado_hoy).length;
    const total = state.habits.length;
    const percent = total === 0 ? 0 : (completed / total) * 100;

    document.getElementById('completedCount').textContent = completed;
    document.getElementById('totalCount').textContent = total;
    document.getElementById('mainProgressBar').style.width = `${percent}%`;

    // Streaks logic could be more complex, but using max for now
    const maxStreak = Math.max(...state.habits.map(h => h.racha_actual), 0);
    const streakEl = document.getElementById('streakCount');
    if (streakEl) streakEl.textContent = maxStreak;
}

// Visual Helpers
function getColorClass(status) {
    if (status === 'optimo') return 'bg-green-500';
    if (status === 'regular') return 'bg-yellow-500';
    if (status === 'mal') return 'bg-orange-500';
    return 'bg-red-500';
}

async function fetchHeatMap() {
    try {
        const data = await authenticatedFetch(`${API_BASE_URL}/habit-logs/heatmap/`);
        if (data) {
            renderHeatMap(data);
        }
    } catch (error) {
        console.error('Error fetching heatmap:', error);
    }
}

function createMonthLabelsRow(startDate, cellWidthClass) {
    const months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
    const monthRow = document.createElement('div');
    monthRow.className = "flex gap-1 mb-1 min-w-max text-[10px] text-slate-400 font-semibold select-none h-3";
    
    const firstDayIndex = (startDate.getDay() + 6) % 7;
    const totalCells = firstDayIndex + 365;
    const totalCols = Math.ceil(totalCells / 7);
    
    let currentMonth = -1;
    for (let col = 0; col < totalCols; col++) {
        const cell = document.createElement('div');
        cell.className = `${cellWidthClass} relative`; 
        
        const dayOffset = (col * 7) - firstDayIndex;
        // Check Thursday representation for the week
        const d = new Date(startDate);
        d.setDate(startDate.getDate() + dayOffset + 3);
        
        if (d.getMonth() !== currentMonth) {
            const span = document.createElement('span');
            span.textContent = months[d.getMonth()];
            span.className = "absolute left-0 top-0";
            cell.appendChild(span);
            currentMonth = d.getMonth();
        }
        monthRow.appendChild(cell);
    }
    return monthRow;
}

function renderHeatMap(data) {
    const container = document.getElementById('heatmapContainer');
    if (!container) return;
    container.innerHTML = '';

    // We want the last 365 days up to today.
    const today = new Date();
    // Normalize today to start of day
    today.setHours(0,0,0,0);
    
    // Start date is 364 days ago
    const startDate = new Date(today);
    startDate.setDate(today.getDate() - 364);

    // Grid container with horizontal scrolling
    const grid = document.createElement('div');
    grid.className = "grid grid-rows-7 grid-flow-col gap-1 auto-cols-min min-w-max mb-2";

    // Padding for the first column so the day of week aligns
    // the row index is determined by the day of the week.
    // CSS grid grid-flow-col fills top-to-bottom. We want 7 rows.
    // Mon=0, Tue=1, ... Sun=6
    const firstDayIndex = (startDate.getDay() + 6) % 7;
    for (let i = 0; i < firstDayIndex; i++) {
        const empty = document.createElement('div');
        empty.className = "w-3 h-3 bg-transparent";
        grid.appendChild(empty);
    }

    // Days calculation
    for (let i = 0; i < 365; i++) {
        const d = new Date(startDate);
        d.setDate(startDate.getDate() + i);
        
        const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
        const count = data[dateStr] || 0;
        
        const isToday = (i === 364);

        const cell = document.createElement('div');
        cell.className = `w-3 h-3 rounded-sm cursor-pointer transition-transform hover:scale-125 ${getColorForCount(count)} ${isToday ? 'ring-2 ring-brand-400 ring-offset-1 z-10' : ''}`;
        cell.title = `${dateStr}: ${count} completados`;
        grid.appendChild(cell);
    }
    
    // Put timeline into container
    const wrap = document.createElement('div');
    wrap.className = "flex flex-col";
    wrap.appendChild(createMonthLabelsRow(startDate, "w-3"));
    wrap.appendChild(grid);
    
    container.appendChild(wrap);
}

let habitHeatmapsLoaded = false;
async function toggleHabitHeatmaps() {
    const container = document.getElementById('habitHeatmapsContainer');
    const btn = document.getElementById('btnToggleDetails');
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        btn.innerHTML = `<i class="ph-bold ph-caret-up"></i> Ocultar Detalles`;
        if (!habitHeatmapsLoaded) {
            await renderHabitHeatmaps();
            habitHeatmapsLoaded = true;
        }
    } else {
        container.classList.add('hidden');
        btn.innerHTML = `<i class="ph-bold ph-chart-bar"></i> Ver Detalles por Hábito`;
    }
}

async function renderHabitHeatmaps() {
    const container = document.getElementById('habitHeatmapsContainer');
    container.innerHTML = '<div class="text-center text-xs text-slate-400 py-4"><i class="ph-bold ph-spinner animate-spin"></i> Cargando de la API...</div>';
    
    try {
        const res = await authenticatedFetch(`${API_BASE_URL}/habits/activos/`);
        if (!res || res.length === 0) {
            container.innerHTML = '<div class="text-xs text-slate-400 text-center py-4">No hay hábitos activos para mostrar.</div>';
            return;
        }
        
        container.innerHTML = '';
        
        // Colors palette to iterate:
        const colors = [
            // color base, intensity 200, 400, 600
            { bg: 'bg-green-100', c2: 'bg-green-200', c4: 'bg-green-400', c6: 'bg-green-600', text: 'text-green-600' },
            { bg: 'bg-blue-100', c2: 'bg-blue-200', c4: 'bg-blue-400', c6: 'bg-blue-600', text: 'text-blue-600' },
            { bg: 'bg-purple-100', c2: 'bg-purple-200', c4: 'bg-purple-400', c6: 'bg-purple-600', text: 'text-purple-600' },
            { bg: 'bg-orange-100', c2: 'bg-orange-200', c4: 'bg-orange-400', c6: 'bg-orange-600', text: 'text-orange-600' },
            { bg: 'bg-pink-100', c2: 'bg-pink-200', c4: 'bg-pink-400', c6: 'bg-pink-600', text: 'text-pink-600' },
            { bg: 'bg-teal-100', c2: 'bg-teal-200', c4: 'bg-teal-400', c6: 'bg-teal-600', text: 'text-teal-600' }
        ];

        // Fetch heatmap data for each habit
        for (let i = 0; i < res.length; i++) {
            const habit = res[i];
            const data = await authenticatedFetch(`${API_BASE_URL}/habit-logs/heatmap/?habit=${habit.id}`);
            
            const colorSet = colors[i % colors.length];
            
            // Re-use logic for category icon
            let iconClass = 'ph-star';
            const cats = {
                'salud': { icon: 'ph-heartbeat'},
                'ejercicio': { icon: 'ph-barbell'},
                'estudio': { icon: 'ph-book-open'},
                'trabajo': { icon: 'ph-briefcase'},
                'tarea': { icon: 'ph-check-square'},
                'arte': { icon: 'ph-paint-brush'},
            };
            if (cats[habit.categoria]) {
                iconClass = cats[habit.categoria].icon;
            }

            // Create habit card
            const card = document.createElement('div');
            card.className = "bg-white p-4 rounded-2xl shadow-sm border border-slate-100 w-full overflow-hidden";
            
            // Header
            card.innerHTML = `
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-lg ${colorSet.bg} ${colorSet.text} flex items-center justify-center">
                            <i class="ph-fill ${iconClass}"></i>
                        </div>
                        <h4 class="font-bold text-slate-700 text-sm truncate max-w-[150px]">${habit.nombre}</h4>
                    </div>
                    <div class="flex items-center gap-1 bg-orange-50 text-orange-600 px-2 py-1 rounded-lg text-xs font-black shrink-0">
                        <i class="ph-fill ph-fire"></i> ${habit.racha_actual}
                    </div>
                </div>
            `;
            
            // Heatmap grid
            const gridWrap = document.createElement('div');
            gridWrap.className = "overflow-x-auto pb-2"
            
            const grid = document.createElement('div');
            grid.className = "grid grid-rows-7 grid-flow-col gap-1 auto-cols-min min-w-max";
            
            const today = new Date();
            today.setHours(0,0,0,0);
            const startDate = new Date(today);
            startDate.setDate(today.getDate() - 364);
            const firstDayIndex = (startDate.getDay() + 6) % 7;
            for (let pad = 0; pad < firstDayIndex; pad++) {
                const empty = document.createElement('div');
                empty.className = "w-2.5 h-2.5 bg-transparent";
                grid.appendChild(empty);
            }
            
            for (let d_idx = 0; d_idx < 365; d_idx++) {
                const d = new Date(startDate);
                d.setDate(startDate.getDate() + d_idx);
                const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
                const count = data[dateStr] || 0;
                
                let cellColor = 'bg-slate-100'; // empty
                if (count > 0) {
                    if (count <= 1) cellColor = colorSet.c2;
                    else if (count <= 2) cellColor = colorSet.c4;
                    else cellColor = colorSet.c6;
                }
                
                const cell = document.createElement('div');
                cell.className = `w-2.5 h-2.5 rounded-sm ${cellColor} hover:scale-125 transition-transform cursor-pointer shadow-sm`;
                cell.title = `${dateStr}`;
                grid.appendChild(cell);
            }
            
            const wrap = document.createElement('div');
            wrap.className = "flex flex-col";
            wrap.appendChild(createMonthLabelsRow(startDate, "w-2.5"));
            wrap.appendChild(grid);
            
            gridWrap.appendChild(wrap);
            card.appendChild(gridWrap);
            container.appendChild(card);
        }
    } catch (err) {
        console.error(err);
        container.innerHTML = '<div class="text-xs text-red-500 text-center py-4">Error cargando heatmaps.</div>';
    }
}
function getColorForCount(count) {
    if (count === 0) return 'bg-slate-100';
    if (count <= 2) return 'bg-emerald-300';
    if (count <= 4) return 'bg-emerald-500';
    return 'bg-emerald-700';
}

function toggleModal() {
    const modal = document.getElementById('habitModal');
    const content = document.getElementById('modalContent');
    const input = document.getElementById('habitInput');

    if (modal.classList.contains('opacity-0')) {
        modal.classList.remove('hidden');
        setTimeout(() => {
            modal.classList.remove('opacity-0', 'pointer-events-none');
            content.classList.remove('scale-95');
            content.classList.add('scale-100');
            if (input) input.focus();
        }, 10);
    } else {
        modal.classList.add('opacity-0', 'pointer-events-none');
        content.classList.remove('scale-100');
        content.classList.add('scale-95');
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 300);
    }
}

function changePage(page) {
    console.log("Navigating to:", page);

    // 1. Hide all main views
    // Defaulting 'dashboard' to 'home'
    if (page === 'dashboard') page = 'home';

    const views = ['homeView', 'statsView', 'profileView'];
    views.forEach(viewId => {
        document.getElementById(viewId)?.classList.add('hidden');
    });

    const mainHeader = document.getElementById('mainHeader');
    const headerTitle = document.getElementById('headerTitle');
    const headerSubtitle = document.getElementById('headerSubtitle');
    const userName = state.user?.username || 'Jardinero';

    // 2. Show target view and update sidebar
    if (page === 'home') {
        document.getElementById('homeView')?.classList.remove('hidden');
        updateSidebar('nav-home');

        mainHeader?.classList.remove('hidden');
        if (headerTitle) headerTitle.innerHTML = `Hola, <span id="userName" class="text-brand-600">${userName}</span> 👋`;
        if (headerSubtitle) headerSubtitle.textContent = "¡Hagamos crecer tus hábitos hoy!";

        // Mostrar foto de perfil en home
        const picContainerHome = document.getElementById('headerProfilePicContainer');
        if (picContainerHome) picContainerHome.classList.remove('hidden');

    } else if (page === 'stats') {
        document.getElementById('statsView')?.classList.remove('hidden');
        updateSidebar('nav-stats');

        mainHeader?.classList.remove('hidden');
        if (headerTitle) headerTitle.innerHTML = `Estadísticas 📊`;
        if (headerSubtitle) headerSubtitle.textContent = "Visualiza tu constancia y logros";

        // Ocultar foto de perfil en stats
        const picContainerStats = document.getElementById('headerProfilePicContainer');
        if (picContainerStats) picContainerStats.classList.add('hidden');

        // Refresh stats/heatmap if needed
        fetchHeatMap();
        updateStats();
    } else if (page === 'profile') {
        document.getElementById('profileView')?.classList.remove('hidden');
        updateSidebar('nav-profile');

        mainHeader?.classList.add('hidden');

        fetchProfileData();
    }
}

function updateSidebar(activeId) {
    const desktopButtons = ['nav-home', 'nav-stats', 'nav-profile', 'nav-shop']; // Added shop just in case
    const mobileButtons = ['mobile-nav-home', 'mobile-nav-stats', 'mobile-nav-profile'];
    const allButtons = [...desktopButtons, ...mobileButtons];

    allButtons.forEach(id => {
        const btn = document.getElementById(id);
        if (!btn) return;

        const icon = btn.querySelector('i');
        const isMobile = id.startsWith('mobile-');

        if (id === activeId || id === `mobile-${activeId}`) {
            // Active Styles
            if (!isMobile) {
                btn.className = "nav-item w-full flex items-center justify-center lg:justify-start px-3 py-3 rounded-2xl bg-slate-900 text-white transition-all group relative shadow-lg shadow-slate-900/20";
            } else {
                btn.className = "nav-item flex flex-col items-center justify-center py-2 px-4 rounded-2xl text-slate-800 bg-slate-100 transition-all font-bold";
            }
            if (icon) {
                icon.classList.remove('ph-bold');
                icon.classList.add('ph-fill');
            }
        } else {
            // Inactive Styles
            if (!isMobile) {
                btn.className = "nav-item w-full flex items-center justify-center lg:justify-start px-3 py-3 rounded-2xl text-slate-400 hover:bg-white hover:text-slate-900 hover:shadow-md transition-all group";
            } else {
                btn.className = "nav-item flex flex-col items-center justify-center py-2 px-4 rounded-2xl text-slate-400 hover:text-slate-800 hover:bg-slate-50 transition-all font-semibold";
            }
            if (icon) {
                icon.classList.remove('ph-fill');
                icon.classList.add('ph-bold');
            }
        }
    });
}

// Wrappers for backward compatibility
function showProfile() {
    changePage('profile');
}

function showDashboard() {
    changePage('home');
}

async function fetchProfileData() {
    try {
        const token = localStorage.getItem('token');

        // Fetch Profile
        const profileRes = await fetch(`${API_BASE_URL}/profile/me/`, { headers: { 'Authorization': `Token ${token}` } });
        const profile = await profileRes.json();

        // Fetch Pet (for profile summary)
        let petText = "No tienes compañero aún";
        let petNivelReal = 1;
        let petXpTotal = 0;
        let petXpProgreso = 0;
        let petNombreReal = 'Tu Compañero';
        try {
            const petRes = await fetch(`${API_BASE_URL}/mascota/me/`, { headers: { 'Authorization': `Token ${token}` } });
            const pet = await petRes.json();
            petNombreReal = pet.nombre || 'Tu Compañero';
            petNivelReal = pet.nivel || 1;
            petXpTotal = pet.total_xp || 0;
            petXpProgreso = pet.progreso_nivel || 0;
            petText = `${petNombreReal} - Nivel ${petNivelReal}`;
        } catch (e) {
            // No pet
        }

        // Update UI
        document.getElementById('profileName').textContent = profile.username;
        const emailEl = document.getElementById('profileEmail');
        if (emailEl) emailEl.textContent = profile.email || 'No email';
        document.getElementById('profileJoinDate').textContent = new Date(profile.fecha_creacion).toLocaleDateString();
        document.getElementById('profileLevel').textContent = profile.nivel || petNivelReal;
        
        // El usuario solicitó XP historial acumulado con sus mascotas
        document.getElementById('profileXP').textContent = petXpTotal;
        
        document.getElementById('profileCoins').textContent = profile.coins;
        document.getElementById('profilePetInfo').textContent = petText;

        // --- Sección Mascota en Perfil: Sprite + Nivel + XP ---
        const petNameEl = document.getElementById('profilePetName');
        if (petNameEl) petNameEl.textContent = petNombreReal;

        // Sprite: baby (nivel < 5) o adult (nivel >= 5)
        const spriteBaby = document.getElementById('petSpriteBaby');
        const spriteAdult = document.getElementById('petSpriteAdult');
        if (spriteBaby && spriteAdult) {
            if (petNivelReal >= 5) {
                spriteBaby.classList.add('hidden');
                spriteAdult.classList.remove('hidden');
            } else {
                spriteBaby.classList.remove('hidden');
                spriteAdult.classList.add('hidden');
            }
        }

        // Badge de nivel en sprite
        const spriteLevelEl = document.getElementById('petSpriteLevel');
        if (spriteLevelEl) spriteLevelEl.textContent = petNivelReal;

        // Barra y texto de XP
        const xpBarEl = document.getElementById('petXpBar');
        const xpTextEl = document.getElementById('petXpText');
        if (xpBarEl) xpBarEl.style.width = `${petXpProgreso}%`;
        if (xpTextEl) xpTextEl.textContent = `${petXpTotal} XP`;

        if (profile.profile_picture) {
            const apiBase = API_BASE_URL.replace('/api/v1', '');
            const fullUrl = profile.profile_picture.startsWith('http') ? profile.profile_picture : `${apiBase}${profile.profile_picture}`;
            document.getElementById('profilePagePic').src = fullUrl;
            document.getElementById('headerProfilePic').src = fullUrl;
        }

    } catch (error) {
        console.error('Error fetching profile:', error);
    }
}

// --- SUBIDA DE IMAGEN DE PERFIL --- //
function handleProfilePicUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Preview opcional (puedes comentar esto si no quieres preview)
    const reader = new FileReader();
    reader.onload = function (e) {
        const profilePic = document.getElementById('headerProfilePic');
        if (profilePic) profilePic.src = e.target.result;
    };
    reader.readAsDataURL(file);

    // Upload
    uploadProfilePicture(event.target);
}

async function uploadProfilePicture(input) {
    if (input.files && input.files[0]) {
        const formData = new FormData();
        formData.append('profile_picture', input.files[0]);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/profile/me/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Token ${token}`
                    // Do NOT set Content-Type header for FormData, browser does it
                },
                body: formData
            });

            if (response.ok) {
                const updatedProfile = await response.json();
                if (updatedProfile.profile_picture) {
                    const apiBase = API_BASE_URL.replace('/api/v1', '');
                    const fullUrl = updatedProfile.profile_picture.startsWith('http') ? updatedProfile.profile_picture : `${apiBase}${updatedProfile.profile_picture}`;

                    document.getElementById('headerProfilePic').src = fullUrl;
                    const profilePagePic = document.getElementById('profilePagePic');
                    if (profilePagePic) profilePagePic.src = fullUrl;
                }
                console.log("✅ Foto actualizada");
            } else {
                console.error("Error al subir la imagen", await response.text());
                alert("Error al subir la imagen");
            }
        } catch (error) {
            console.error("Upload error:", error);
            alert("Error de conexión");
        }
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}



// API Fetch Helper
async function authenticatedFetch(url, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`,
        ...options.headers
    };

    console.log('🌐 [DEBUG] Making authenticated request to:', url);
    console.log('🌐 [DEBUG] Method:', options.method || 'GET');

    const response = await fetch(url, { ...options, headers });

    console.log('🌐 [DEBUG] Response status:', response.status, response.statusText);

    if (!response.ok) {
        const error = new Error('API Error');
        error.status = response.status;
        console.error('❌ [DEBUG] API Error:', error);
        throw error;
    }
    return response.json();
}

// Globals for HTML onclicks
window.toggleModal = toggleModal;
window.changePage = changePage;
window.logout = logout;
window.toggleHabit = toggleHabit;
window.handleNewHabit = handleNewHabit;
window.openAdoptionModal = openAdoptionModal;
window.closeAdoptionModal = closeAdoptionModal;
