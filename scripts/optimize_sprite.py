"""
Pipeline completo: Sprite Sheet → WebP optimizado para web.
Verifica cada paso para evitar errores de imagen.
"""
from PIL import Image
import os
import sys

# ── CONFIG ──
SOURCE = r"C:\Users\tagit\Pictures\Gizmo\Secuencia\frames 60\sprite sheets\spritesheet_bby.png"
OUTPUT_DIR = r"C:\Users\tagit\LABS\TestMascota\frontend\assets\mascotas\Gizzmo\animations"
ANIM_NAME = "tap"
FRAMES = 60
COLS = 10           # columnas en el grid
ROWS = 6            # filas en el grid
WEBP_QUALITY = 85
FPS = 48            # referencia (se usa en JS, no en imagen)

# El bounding box [left, top, right, bottom] se calculó para que la escala del bebe
# coincida EXACTAMENTE con la escala y padding de "frontend/assets/mascotas/Gizzmo/bby/Idle.png"
# Esto evita saltos de escala cuando la animación reemplaza a la imagen estática en el frontend.
CROP_BOX = (225, 78, 912, 648)
TARGET_W = CROP_BOX[2] - CROP_BOX[0]  # 687
TARGET_H = CROP_BOX[3] - CROP_BOX[1]  # 570

assert COLS * ROWS == FRAMES, f"Grid {COLS}x{ROWS} != {FRAMES} frames"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── PASO 1: Cargar y validar original ──
print("─── PASO 1: Cargando sprite sheet original ───")
img = Image.open(SOURCE)
orig_w, orig_h = img.size
orig_frame_h = orig_h // FRAMES

print(f"  Original: {orig_w}x{orig_h} ({img.mode})")
print(f"  Frame original: {orig_w}x{orig_frame_h}")

if orig_h % FRAMES != 0:
    print(f"  ⚠ ADVERTENCIA: {orig_h} no es divisible entre {FRAMES}, residuo: {orig_h % FRAMES}px")

# ── PASO 2: Extraer y recortar cada frame ──
print("\n─── PASO 2: Extrayendo y recortando proporciones (matching Idle.png) ───")
frames_list = []
errors = []

for i in range(FRAMES):
    top = i * orig_frame_h
    bottom = top + orig_frame_h
    frame = img.crop((0, top, orig_w, bottom))
    
    # Recorte personalizado para alinear el tamaño del personaje al estático
    frame_cropped = frame.crop(CROP_BOX)
    
    bbox = frame_cropped.getbbox()
    if bbox is None:
        errors.append(f"  ⚠ Frame {i}: completamente transparente/vacío tras recorte")
    
    frames_list.append(frame_cropped)

print(f"  Frames extraídos y recortados a {TARGET_W}x{TARGET_H}: {len(frames_list)}/{FRAMES}")
if errors:
    for e in errors:
        print(e)
else:
    print("  ✅ Todos los frames tienen contenido visible")

# ── PASO 3: Ensamblar grid ──
print(f"\n─── PASO 3: Ensamblando grid {COLS}x{ROWS} ───")
sheet_w = TARGET_W * COLS
sheet_h = TARGET_H * ROWS
sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

for i, frame in enumerate(frames_list):
    col = i % COLS
    row = i // COLS
    x = col * TARGET_W
    y = row * TARGET_H
    sheet.paste(frame, (x, y))

print(f"  Sheet final: {sheet_w}x{sheet_h}")

# ── PASO 4: Exportar ──
print("\n─── PASO 4: Exportando ───")

webp_path = os.path.join(OUTPUT_DIR, f"{ANIM_NAME}.webp")
sheet.save(webp_path, "WEBP", quality=WEBP_QUALITY, method=4)
webp_kb = os.path.getsize(webp_path) / 1024

png_path = os.path.join(OUTPUT_DIR, f"{ANIM_NAME}.png")
sheet.save(png_path, "PNG", optimize=True)
png_kb = os.path.getsize(png_path) / 1024

try:
    orig_mb = os.path.getsize(SOURCE) / 1024 / 1024 if os.path.exists(SOURCE) else 0
except Exception:
    orig_mb = 0

print(f"  WebP: {webp_kb:.0f} KB  ({webp_path})")
print(f"  PNG:  {png_kb:.0f} KB  ({png_path})")
if orig_mb > 0:
    print(f"  Compresión: {orig_mb:.1f} MB → {webp_kb:.0f} KB WebP")

# ── RESUMEN ──
print(f"""
═══════════════════════════════════════
  RESUMEN DE ANIMACIÓN
  Animación: {ANIM_NAME}
  Frames: {FRAMES} @ {FPS}fps ({FRAMES/FPS:.2f}s de duración)
  Frame JS conf: {{ frameW: {TARGET_W}, frameH: {TARGET_H}, cols: {COLS} }}
  Tamaño final de imagen css: w-64 h-64 (16rem) - Debe empatar al 100%
  Sprite: {sheet_w}x{sheet_h} WebP ({webp_kb:.0f} KB)
  Estado: {"✅ TODO OK" if len(errors)==0 else "⚠ HAY ERRORES"}
═══════════════════════════════════════
""")
