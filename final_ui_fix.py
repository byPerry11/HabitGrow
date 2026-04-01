import os
import re

html_path = r"c:\Users\tagit\LABS\TestMascota\frontend\dashboard.html"

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# --- STEP 3 BUTTON ADDITION (Right Panel) ---
# We want to insert the button after the grid ends but before the last div of id="obStep3" right column ends.
# The grid ends at </div> <!-- end of grid -->
# Let's find the specific block for slot 3 and then the closing </div> of the grid.

# Searching for the end of the grid inside obStep3
grid_end_marker = r'<!-- Locked slot 3 -->.*?</div>\s*</div>\s*</div>'
# This matches the slot div, its inner div, and the parent grid div.

new_confirm_btn = """
                <div class="mt-6 pt-4 border-t border-white/5 space-y-4">
                    <button onclick="finishOnboarding()" class="w-full py-5 bg-brand-500 text-white font-black rounded-2xl shadow-[0_10px_20px_rgba(16,185,129,0.3)] hover:bg-brand-400 hover:scale-[1.02] transition-all text-sm uppercase tracking-[0.2em]">
                        Confirmar Mi Compañero
                    </button>
                    <p class="text-[9px] text-center text-slate-500 font-bold uppercase tracking-widest opacity-60">¡Crezcamos juntos!</p>
                </div>
"""

# Find the end of the grid and insert the button before the closing div of the right panel
pattern_right_column = re.compile(r'(<div\s+class="flex-1 grid grid-cols-2 gap-4 auto-rows-fr">.*?</div>)\s*(</div>\s*</div>\s*</div>)', re.DOTALL)

if pattern_right_column.search(content):
    content = pattern_right_column.sub(r'\1' + new_confirm_btn + r'\2', content)
    print("SUCCESS: Companion panel button added via improved regex")
else:
    # Backup attempt: search for "Compañeros" and go down
    print("FAILURE: Could not find right column grid precisely")

# --- FINAL COMPACTNESS CHECK for Step 2 ---
# Ensure obStep2 has no internal scroll if possible.
# Most of it was done, but let's ensure the min-height is gone or smaller.
content = content.replace('min-h-[600px]', 'min-h-0')

with open(html_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

print("SUCCESS: HTML update completed")
