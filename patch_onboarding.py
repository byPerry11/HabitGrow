import os

def patch_file(path, old_text, new_text, label):
    if not os.path.exists(path):
        print(f"Error: {path} not found")
        return False
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Normalize line endings for searching
    content_norm = content.replace('\r\n', '\n')
    old_text_norm = old_text.replace('\r\n', '\n')
    
    if old_text_norm in content_norm:
        content = content_norm.replace(old_text_norm, new_text)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"SUCCESS: {label}")
        return True
    else:
        print(f"FAILURE: {label} (Not found)")
        # Show a bit of the first line to debug
        print(f"Searching for start: {old_text_norm[:50]}...")
        return False

# --- PATCH DASHBOARD.HTML ---
html_path = r"c:\Users\tagit\LABS\TestMascota\frontend\dashboard.html"

# Step 2 HTML
old_ob_step2 = """        <!-- Step 2: Primer Hábito -->
        <div id="obStep2" class="hidden flex-col bg-white text-slate-800 rounded-[3.5rem] shadow-2xl w-full max-w-4xl p-6 md:p-10 transition-all duration-500 transform scale-95 opacity-0 pb-16 md:pb-10 max-h-[95vh] min-h-[500px] overflow-y-auto custom-scrollbar">
            <div class="text-center mb-8 shrink-0">
                <h2 class="text-4xl font-black text-slate-900 tracking-tighter">Tu Primer Objetivo</h2>
                <p class="text-slate-500 font-medium mt-2">Planta la semilla de tu éxito. ¡Puedes cambiarlo después!</p>
            </div>
            
            <!-- Clon simplificado del formulario de hábitos -->
            <form id="obHabitForm" onsubmit="handleObHabitSubmit(event)" class="space-y-6 flex-1 flex flex-col justify-between">
                <div>
                    <input type="text" id="obHabitInput" placeholder="Ej: Beber 2L de agua" required
                        class="w-full px-6 py-5 rounded-[2rem] bg-slate-50 border-2 border-slate-100 focus:border-brand-500 focus:bg-white outline-none transition-all text-slate-800 placeholder-slate-400 font-black text-2xl text-center">
                </div>
                
                <div>
                    <!-- Reutilizamos las mismas categorias pero sin labels para ahorrar espacio -->
                    <div class="grid grid-cols-3 lg:grid-cols-6 gap-3">
                        <label class="cursor-pointer group"><input type="radio" name="obCategory" value="salud" class="peer hidden" checked><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-green-500 peer-checked:bg-green-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-heart-beat text-2xl text-slate-400 peer-checked:text-green-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-green-700">Salud</span></div></label>
                        <label class="cursor-pointer group"><input type="radio" name="obCategory" value="ejercicio" class="peer hidden"><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-orange-500 peer-checked:bg-orange-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-barbell text-2xl text-slate-400 peer-checked:text-orange-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-orange-700">Gym</span></div></label>
                        <label class="cursor-pointer group"><input type="radio" name="obCategory" value="estudio" class="peer hidden"><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-blue-500 peer-checked:bg-blue-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-book-open text-2xl text-slate-400 peer-checked:text-blue-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-blue-700">Estudio</span></div></label>
                        <label class="cursor-pointer group"><input type="radio" name="obCategory" value="trabajo" class="peer hidden"><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-purple-500 peer-checked:bg-purple-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-briefcase text-2xl text-slate-400 peer-checked:text-purple-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-purple-700">Trabajo</span></div></label>
                        <label class="cursor-pointer group"><input type="radio" name="obCategory" value="tarea" class="peer hidden"><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-teal-500 peer-checked:bg-teal-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-check-square text-2xl text-slate-400 peer-checked:text-teal-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-teal-700">Tarea</span></div></label>
                        <label class="cursor-pointer group"><input type="radio" name="obCategory" value="arte" class="peer hidden"><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-pink-500 peer-checked:bg-pink-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-paint-brush text-2xl text-slate-400 peer-checked:text-pink-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-pink-700">Arte</span></div></label>
                    </div>
                </div>

                <div class="mt-auto pt-8 flex flex-col sm:flex-row gap-4">
                    <button type="button" onclick="nextObStep(3)" class="w-full sm:w-1/3 py-5 bg-slate-100 text-slate-500 font-bold rounded-[2rem] hover:bg-slate-200 transition-all text-lg active:scale-95">Dejar para después</button>
                    <button type="submit" id="btnCreateObHabit" class="w-full sm:w-2/3 py-5 bg-brand-500 text-white font-black rounded-[2rem] shadow-[0_10px_20px_rgba(16,185,129,0.3)] hover:bg-brand-400 hover:-translate-y-1 transition-all text-lg active:scale-95 flex justify-center items-center gap-2">
                        <span>Definir Destino</span> <i class="ph-bold ph-arrow-right"></i>
                    </button>
                </div>
            </form>
        </div>"""

new_ob_step2 = """        <!-- Step 2: Primer Hábito -->
        <div id="obStep2" class="hidden flex-col bg-white text-slate-800 rounded-[3.5rem] shadow-2xl w-full max-w-4xl p-6 md:p-10 transition-all duration-500 transform scale-95 opacity-0 pb-16 md:pb-10 max-h-[95vh] min-h-[600px] overflow-y-auto custom-scrollbar">
            <div class="text-center mb-8 shrink-0">
                <div class="flex justify-center mb-4">
                    <span class="px-4 py-1.5 bg-brand-100 text-brand-600 rounded-full text-xs font-black uppercase tracking-widest">Paso 2 de 3</span>
                </div>
                <h2 class="text-4xl font-black text-slate-900 tracking-tighter">Tu Primer Objetivo</h2>
                <p class="text-slate-500 font-medium mt-2">Planta la semilla de tu éxito. Podrás ajustar los detalles después.</p>
            </div>
            
            <form id="obHabitForm" onsubmit="handleObHabitSubmit(event)" class="space-y-8 flex-1 flex flex-col">
                <!-- Nombre y Categoría -->
                <div class="space-y-6">
                    <div>
                        <label class="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3 ml-2">¿Qué hábito quieres iniciar?</label>
                        <input type="text" id="obHabitInput" placeholder="Ej: Beber 2L de agua" required
                            class="w-full px-6 py-5 rounded-[2rem] bg-slate-50 border-2 border-slate-100 focus:border-brand-500 focus:bg-white outline-none transition-all text-slate-800 placeholder-slate-400 font-black text-2xl text-center shadow-inner">
                    </div>

                    <div>
                        <label class="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3 ml-2">Categoría</label>
                        <div class="grid grid-cols-3 lg:grid-cols-6 gap-3">
                            <label class="cursor-pointer group"><input type="radio" name="obCategory" value="salud" class="peer hidden" checked><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-green-500 peer-checked:bg-green-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-heart-beat text-2xl text-slate-400 peer-checked:text-green-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-green-700">Salud</span></div></label>
                            <label class="cursor-pointer group"><input type="radio" name="obCategory" value="ejercicio" class="peer hidden"><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-orange-500 peer-checked:bg-orange-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-barbell text-2xl text-slate-400 peer-checked:text-orange-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-orange-700">Gym</span></div></label>
                            <label class="cursor-pointer group"><input type="radio" name="obCategory" value="estudio" class="peer hidden"><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-blue-500 peer-checked:bg-blue-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-book-open text-2xl text-slate-400 peer-checked:text-blue-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-blue-700">Estudio</span></div></label>
                            <label class="cursor-pointer group"><input type="radio" name="obCategory" value="trabajo" class="peer hidden"><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-purple-500 peer-checked:bg-purple-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-briefcase text-2xl text-slate-400 peer-checked:text-purple-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-purple-700">Trabajo</span></div></label>
                            <label class="cursor-pointer group"><input type="radio" name="obCategory" value="tarea" class="peer hidden"><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-teal-500 peer-checked:bg-teal-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-check-square text-2xl text-slate-400 peer-checked:text-teal-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-teal-700">Tarea</span></div></label>
                            <label class="cursor-pointer group"><input type="radio" name="obCategory" value="arte" class="peer hidden"><div class="h-20 rounded-3xl bg-slate-50 border-2 border-transparent peer-checked:border-pink-500 peer-checked:bg-pink-50 flex flex-col items-center justify-center gap-1 transition-all hover:bg-slate-100"><i class="ph-fill ph-paint-brush text-2xl text-slate-400 peer-checked:text-pink-500"></i><span class="text-[10px] font-bold text-slate-500 peer-checked:text-pink-700">Arte</span></div></label>
                        </div>
                    </div>
                </div>

                <!-- Frecuencia y Pasos (Detalles Adicionales) -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 border-t border-slate-100 pt-8">
                    <div>
                        <label class="block text-xs font-black text-slate-400 uppercase tracking-widest mb-4 ml-2">¿Qué días repetirás?</label>
                        <div class="flex justify-between gap-1" id="obDaysSelector">
                            <label class="cursor-pointer"><input type="checkbox" name="obDays" value="0" class="peer hidden" checked><span class="w-10 h-10 rounded-xl bg-slate-50 border-2 border-transparent flex items-center justify-center text-xs font-black text-slate-400 peer-checked:bg-brand-500 peer-checked:text-white transition-all">L</span></label>
                            <label class="cursor-pointer"><input type="checkbox" name="obDays" value="1" class="peer hidden" checked><span class="w-10 h-10 rounded-xl bg-slate-50 border-2 border-transparent flex items-center justify-center text-xs font-black text-slate-400 peer-checked:bg-brand-500 peer-checked:text-white transition-all">M</span></label>
                            <label class="cursor-pointer"><input type="checkbox" name="obDays" value="2" class="peer hidden" checked><span class="w-10 h-10 rounded-xl bg-slate-50 border-2 border-transparent flex items-center justify-center text-xs font-black text-slate-400 peer-checked:bg-brand-500 peer-checked:text-white transition-all">M</span></label>
                            <label class="cursor-pointer"><input type="checkbox" name="obDays" value="3" class="peer hidden" checked><span class="w-10 h-10 rounded-xl bg-slate-50 border-2 border-transparent flex items-center justify-center text-xs font-black text-slate-400 peer-checked:bg-brand-500 peer-checked:text-white transition-all">J</span></label>
                            <label class="cursor-pointer"><input type="checkbox" name="obDays" value="4" class="peer hidden" checked><span class="w-10 h-10 rounded-xl bg-slate-50 border-2 border-transparent flex items-center justify-center text-xs font-black text-slate-400 peer-checked:bg-brand-500 peer-checked:text-white transition-all">V</span></label>
                            <label class="cursor-pointer"><input type="checkbox" name="obDays" value="5" class="peer hidden" checked><span class="w-10 h-10 rounded-xl bg-slate-50 border-2 border-transparent flex items-center justify-center text-xs font-black text-slate-400 peer-checked:bg-brand-500 peer-checked:text-white transition-all">S</span></label>
                            <label class="cursor-pointer"><input type="checkbox" name="obDays" value="6" class="peer hidden" checked><span class="w-10 h-10 rounded-xl bg-slate-50 border-2 border-transparent flex items-center justify-center text-xs font-black text-slate-400 peer-checked:bg-brand-500 peer-checked:text-white transition-all">D</span></label>
                        </div>
                    </div>

                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <label class="block text-xs font-black text-slate-400 uppercase tracking-widest ml-2">¿Cuántas veces al día?</label>
                            <span class="text-xs font-black text-brand-600 bg-brand-50 px-2 py-1 rounded-full" id="obStepsValueDisplay">1 vez</span>
                        </div>
                        <input type="range" id="obStepsInput" min="1" max="10" value="1"
                            oninput="document.getElementById('obStepsValueDisplay').textContent = this.value + (this.value == 1 ? ' vez' : ' veces')"
                            class="w-full accent-brand-500 h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer">
                        <p class="text-[10px] text-slate-400 mt-2 italic font-medium">Divide tu hábito en pequeñas victorias.</p>
                    </div>
                </div>

                <!-- Botones de Acción -->
                <div class="mt-auto pt-10 flex flex-col sm:flex-row gap-4">
                    <button type="button" onclick="showObStep(1)" class="w-full sm:w-1/4 py-5 bg-slate-100 text-slate-500 font-bold rounded-[2rem] hover:bg-slate-200 transition-all text-sm active:scale-95 flex items-center justify-center gap-2">
                        <i class="ph-bold ph-arrow-left"></i> Volver
                    </button>
                    <button type="button" onclick="showObStep(3)" class="w-full sm:w-1/4 py-5 bg-slate-50 text-slate-400 font-bold rounded-[2rem] hover:bg-slate-100 transition-all text-sm">Omitir</button>
                    <button type="submit" id="btnCreateObHabit" class="w-full sm:w-2/3 py-5 bg-slate-900 text-white font-black rounded-[2rem] shadow-[0_10px_20px_rgba(15,23,42,0.2)] hover:bg-slate-800 hover:-translate-y-1 transition-all text-lg active:scale-95 flex justify-center items-center gap-2">
                        <span>Definir Destino</span> <i class="ph-bold ph-arrow-right"></i>
                    </button>
                </div>
            </form>
        </div>"""

# Step 3 HTML
old_ob_step3_btn = """                <div class="relative z-10 w-full mt-auto">
                    <button onclick="finishOnboarding()" id="btnSelectPet" class="w-full py-6 md:py-8 bg-white text-slate-900 font-black rounded-[2.5rem] shadow-[0_20px_50px_rgba(255,255,255,0.3)] hover:scale-105 transition-all text-2xl uppercase tracking-widest active:scale-95 flex items-center justify-center gap-3">
                        ¡Elegir! <i class="ph-bold ph-sparkle text-brand-500"></i>
                    </button>
                </div>"""

new_ob_step3_btn = """                <div class="relative z-10 w-full mt-auto flex flex-col gap-4">
                    <!-- Campo para el nombre de la mascota -->
                    <div class="bg-black/20 backdrop-blur-md p-4 rounded-3xl border border-white/10">
                        <label class="block text-[10px] font-black text-brand-200 uppercase tracking-[0.2em] mb-2 ml-2">¿Cómo se llamará?</label>
                        <input type="text" id="obPetNameInput" placeholder="Ej: Sparky" class="w-full bg-white/10 border-2 border-white/10 rounded-2xl py-3 px-4 text-white font-bold placeholder-white/30 outline-none focus:border-white/40 transition-all text-center">
                    </div>

                    <div class="flex gap-4">
                        <button onclick="showObStep(2)" class="flex-1 py-5 bg-slate-900/60 text-white font-bold rounded-[2rem] border border-white/10 hover:bg-slate-800/80 transition-all active:scale-95 flex items-center justify-center gap-2">
                            <i class="ph-bold ph-arrow-left"></i> Volver
                        </button>
                        <button onclick="finishOnboarding()" id="btnSelectPet" class="flex-[2] py-6 bg-white text-slate-900 font-black rounded-[2rem] shadow-[0_20px_40px_rgba(255,255,255,0.2)] hover:scale-105 transition-all text-xl uppercase tracking-widest active:scale-95 flex items-center justify-center gap-2">
                            Confirmar <i class="ph-bold ph-check-circle text-brand-500"></i>
                        </button>
                    </div>
                </div>"""

# --- PATCH DASHBOARD.JS ---
js_path = r"c:\Users\tagit\LABS\TestMascota\frontend\js\dashboard.js"

# handleObHabitSubmit update
old_ob_submit = """async function handleObHabitSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById('btnCreateObHabit');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="ph-bold ph-spinner animate-spin"></i> Guardando...';
    btn.disabled = true;

    const nombre = document.getElementById('obHabitInput').value.trim();
    const categoria = document.querySelector('input[name="obCategory"]:checked').value;
    
    try {
        await authenticatedFetch(`${API_BASE_URL}/habits/`, {
            method: 'POST',
            body: JSON.stringify({
                nombre: nombre,
                categoria: categoria,
                dias_semana: "0,1,2,3,4,5,6", // Todos los días por defecto
                total_pasos: 1,
                activo: true
            })
        });
        showToast('¡Primer hábito plantado!', 'success');
        nextObStep(3);
    } catch (error) {
        showToast('Error al crear el hábito', 'error');
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}"""

new_ob_submit = """async function handleObHabitSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById('btnCreateObHabit');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="ph-bold ph-spinner animate-spin"></i> Guardando...';
    btn.disabled = true;

    const nombre = document.getElementById('obHabitInput').value.trim();
    const categoria = document.querySelector('input[name="obCategory"]:checked').value;
    
    // Capturar días de la semana
    const selectedDays = Array.from(document.querySelectorAll('input[name="obDays"]:checked'))
                             .map(cb => cb.value)
                             .join(',');
    
    const totalPasos = parseInt(document.getElementById('obStepsInput').value) || 1;

    try {
        await authenticatedFetch(`${API_BASE_URL}/habits/`, {
            method: 'POST',
            body: JSON.stringify({
                nombre: nombre,
                categoria: categoria,
                dias_semana: selectedDays || "0,1,2,3,4,5,6",
                total_pasos: totalPasos,
                activo: true
            })
        });
        showToast('¡Primer hábito plantado!', 'success');
        nextObStep(3);
    } catch (error) {
        showToast('Error al crear el hábito', 'error');
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}"""

# finishOnboarding update
old_finish = """        // 1. Adoptar Mascota (Gizzmo)
        try {
            await authenticatedFetch(`${API_BASE_URL}/mascota/adoptar/`, {
                method: 'POST',
                body: JSON.stringify({ nombre: 'Gizzmo', especie: 'gizzmo' })
            });
        } catch(e) { /* Si ya había adoptado por error, ignorar */ }"""

new_finish = """        // 1. Adoptar Mascota (Gizzmo)
        const petName = document.getElementById('obPetNameInput').value.trim() || 'Gizzmo';
        try {
            await authenticatedFetch(`${API_BASE_URL}/mascota/adoptar/`, {
                method: 'POST',
                body: JSON.stringify({ nombre: petName, especie: 'gizzmo' })
            });
        } catch(e) { /* Si ya había adoptado por error, ignorar */ }"""

patch_file(html_path, old_ob_step2, new_ob_step2, "Step 2 HTML")
patch_file(html_path, old_ob_step3_btn, new_ob_step3_btn, "Step 3 Buttons HTML")
patch_file(js_path, old_ob_submit, new_ob_submit, "Submit Ob Habit JS")
patch_file(js_path, old_finish, new_finish, "Finish Onboarding JS")
