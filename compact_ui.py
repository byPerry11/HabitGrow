import os
import re

html_path = r"c:\Users\tagit\LABS\TestMascota\frontend\dashboard.html"

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# --- COMPACTING STEP 2 (obStep2) ---
# Replace the container classes for Step 2
pattern_step2_div = re.compile(r'(<div id="obStep2"\s+class="[^"]*?)(md:p-10)([^"]*?)(space-y-8)([^"]*?)"', re.DOTALL)
content = pattern_step2_div.sub(r'\1md:p-8\3space-y-4\5"', content)

# Reduce font of H2
content = content.replace('<h2 class="text-4xl font-black text-slate-900 tracking-tighter">', '<h2 class="text-3xl font-black text-slate-900 tracking-tighter">')

# Reduce height of category icons (h-20 -> h-16)
content = content.replace('h-20 rounded-3xl bg-slate-50 border-2 border-transparent', 'h-16 rounded-2xl bg-slate-50 border-2 border-transparent')

# Reduce padding of main input (py-5 -> py-3)
content = content.replace('w-full px-6 py-5 rounded-[2rem] bg-slate-50 border-2 border-slate-100', 'w-full px-6 py-3 rounded-2xl bg-slate-50 border-2 border-slate-100')
content = content.replace('placeholder-slate-400 font-black text-2xl text-center shadow-inner', 'placeholder-slate-400 font-black text-xl text-center shadow-inner')

# Reduce main buttons padding (py-5 -> py-4)
content = content.replace('py-5 bg-slate-900 text-white font-black rounded-[2rem]', 'py-4 bg-slate-900 text-white font-black rounded-2xl')
content = content.replace('py-5 bg-slate-100 text-slate-500 font-bold rounded-[2rem]', 'py-4 bg-slate-100 text-slate-500 font-bold rounded-2xl')
content = content.replace('py-5 bg-slate-50 text-slate-400 font-bold rounded-[2rem]', 'py-4 bg-slate-50 text-slate-400 font-bold rounded-2xl')

# Reduce gaps
content = content.replace('class="space-y-8 flex-1 flex flex-col"', 'class="space-y-3 flex-1 flex flex-col"')
content = content.replace('class="space-y-6"', 'class="space-y-3"')
content = content.replace('class="grid grid-cols-1 md:grid-cols-2 gap-8 border-t border-slate-100 pt-8"', 'class="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-slate-100 pt-4"')
content = content.replace('class="mt-auto pt-10 flex flex-col sm:flex-row gap-4"', 'class="mt-auto pt-4 flex flex-col sm:flex-row gap-2"')

# Eliminate redundant Passo text? No, user just said compact.

# --- STEP 3 BUTTON ADDITION ---
# Insert "Confirmar Adopción" button inside the right panel (flex-[2])
# We find the end of the grid (div class="flex-1 grid grid-cols-2 gap-4 auto-rows-fr")
# And insert after it.

pattern_right_panel = re.compile(r'(<div\s+class="flex-1 grid grid-cols-2 gap-4 auto-rows-fr">.*?</div>\s*)(</div>\s*</div>)', re.DOTALL)
new_confirm_btn = """
                <div class="mt-6 pt-4 border-t border-white/5 space-y-4">
                    <button onclick="finishOnboarding()" class="w-full py-5 bg-brand-500 text-white font-black rounded-2xl shadow-[0_10px_20px_rgba(16,185,129,0.3)] hover:bg-brand-400 hover:scale-[1.02] transition-all text-sm uppercase tracking-[0.2em] animate-pulse">
                        Confirmar Mi Compañero
                    </button>
                    <p class="text-[9px] text-center text-slate-500 font-bold uppercase tracking-widest opacity-60">¡Prepárate para crecer juntos!</p>
                </div>
"""

# Re-match more precisely for Step 3 right panel content
grid_end = '<!-- Locked slot 3 (Coming Soon) -->\s*<div.*?</div>\s*</div>'
# Instead, let's just use the end of the flex-1 grid section
# Match until the closing </div> of the companion grid container.

pattern_companion_panel = re.compile(r'(<!-- Locked slot 3 \(Coming Soon\) -->.*?</div>\s*</div>)(\s*</div>\s*</div>)', re.DOTALL)
if pattern_companion_panel.search(content):
    content = pattern_companion_panel.sub(r'\1' + new_confirm_btn + r'\2', content)
    print("SUCCESS: Companion panel button added")
else:
    print("FAILURE: Companion panel not found precisely")

with open(html_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

print("SUCCESS: UI Compacted")
