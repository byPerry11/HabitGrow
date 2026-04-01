import os
import re

html_path = r"c:\Users\tagit\LABS\TestMascota\frontend\dashboard.html"

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# --- REDUCE INTERNAL SCALING IN obStep3 ---
# Izquierda: Personaje Destacado
# Padding p-8 md:p-12 -> p-6 md:p-8
content = content.replace('flex-[3] bg-gradient-to-br from-brand-600 to-slate-900 rounded-[3.5rem] p-8 md:p-12 shadow-2xl', 
                        'flex-[3] bg-gradient-to-br from-brand-600 to-slate-900 rounded-[3.5rem] p-6 md:p-8 shadow-2xl')

# Title size text-6xl md:text-8xl -> text-4xl md:text-6xl
content = content.replace('text-6xl md:text-8xl font-black italic tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-brand-200 drop-shadow-lg leading-none',
                        'text-4xl md:text-6xl font-black italic tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-brand-200 drop-shadow-lg leading-none')

# Subtitle size text-base md:text-xl -> text-xs md:text-sm
content = content.replace('text-brand-100 mt-4 text-base md:text-xl font-medium max-w-md mx-auto md:mx-0',
                        'text-brand-100 mt-3 text-sm md:text-base font-medium max-w-md mx-auto md:mx-0')

# Image size w-64 h-64 md:w-96 md:h-96 -> w-48 h-48 md:w-64 md:h-64
content = content.replace('w-64 h-64 md:w-96 md:h-96 object-contain drop-shadow-[0_0_50px_rgba(16,185,129,0.5)] scale-110',
                        'w-48 h-48 md:w-64 md:h-64 object-contain drop-shadow-[0_0_30px_rgba(16,185,129,0.5)] scale-105')

# Derecha: Selector de Rejilla
# Padding p-6 -> p-4
content = content.replace('flex-[2] bg-slate-900/60 backdrop-blur-2xl rounded-[3.5rem] p-6 shadow-2xl ring-1 ring-white/10 flex flex-col overflow-hidden shrink-0',
                        'flex-[2] bg-slate-900/60 backdrop-blur-2xl rounded-[3.5rem] p-4 shadow-2xl ring-1 ring-white/10 flex flex-col overflow-hidden shrink-0')

# Grid gaps and margins
content = content.replace('grid-cols-2 gap-4 auto-rows-fr', 'grid-cols-2 gap-2 auto-rows-fr')
content = content.replace('mb-6 mt-4', 'mb-4 mt-2')

# Buttons and input in left panel
content = content.replace('py-5 bg-slate-900/60 text-white font-bold rounded-[2rem]', 'py-3 bg-slate-900/60 text-white font-bold rounded-2xl')
content = content.replace('py-6 bg-white text-slate-900 font-black rounded-[2rem]', 'py-4 bg-white text-slate-900 font-black rounded-2xl')

# Petitioner name input
content = content.replace('id="obPetNameInput" placeholder="Ej: Sparky" class="w-full bg-white/10 border-2 border-white/10 rounded-2xl py-3 px-4 text-white font-bold placeholder-white/30 outline-none focus:border-white/40 transition-all text-center"',
                        'id="obPetNameInput" placeholder="Ej: Sparky" class="w-full bg-white/10 border-2 border-white/10 rounded-xl py-2 px-4 text-white font-bold placeholder-white/20 outline-none focus:border-white/40 transition-all text-center text-sm"')

with open(html_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

print("SUCCESS: Internal Step 3 elements scaled down")
