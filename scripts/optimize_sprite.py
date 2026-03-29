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
TARGET_W = 640      # ancho por frame
TARGET_H = 360      # alto por frame
COLS = 10           # columnas en el grid
ROWS = 6            # filas en el grid
WEBP_QUALITY = 85
FPS = 48            # referencia (se usa en JS, no en imagen)

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

# ── PASO 2: Extraer y redimensionar cada frame ──
print("\n─── PASO 2: Extrayendo y redimensionando frames ───")
frames_list = []
errors = []

for i in range(FRAMES):
    top = i * orig_frame_h
    bottom = top + orig_frame_h
    frame = img.crop((0, top, orig_w, bottom))
    
    # Verificar que el frame no está vacío (todo transparente)
    bbox = frame.getbbox()
    if bbox is None:
        errors.append(f"  ⚠ Frame {i}: completamente transparente/vacío")
    
    # Redimensionar con LANCZOS (mejor calidad de downscale)
    frame_resized = frame.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    frames_list.append(frame_resized)

print(f"  Frames extraídos: {len(frames_list)}/{FRAMES}")
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

print(f"  Sheet: {sheet_w}x{sheet_h}")

# ── PASO 4: Verificar integridad del grid ──
print("\n─── PASO 4: Verificando integridad del grid ───")
# Leer de vuelta cada posición del grid y verificar que no está vacío
ok_count = 0
for i in range(FRAMES):
    col = i % COLS
    row = i // COLS
    x = col * TARGET_W
    y = row * TARGET_H
    cell = sheet.crop((x, y, x + TARGET_W, y + TARGET_H))
    if cell.getbbox() is not None:
        ok_count += 1
    else:
        print(f"  ⚠ Celda [{row},{col}] (frame {i}): vacía")

print(f"  Frames válidos en grid: {ok_count}/{FRAMES}")

# ── PASO 5: Exportar ──
print("\n─── PASO 5: Exportando ───")

webp_path = os.path.join(OUTPUT_DIR, f"{ANIM_NAME}.webp")
sheet.save(webp_path, "WEBP", quality=WEBP_QUALITY, method=4)
webp_kb = os.path.getsize(webp_path) / 1024

png_path = os.path.join(OUTPUT_DIR, f"{ANIM_NAME}.png")
sheet.save(png_path, "PNG", optimize=True)
png_kb = os.path.getsize(png_path) / 1024

orig_mb = os.path.getsize(SOURCE) / 1024 / 1024

print(f"  WebP: {webp_kb:.0f} KB  ({webp_path})")
print(f"  PNG:  {png_kb:.0f} KB  ({png_path})")
print(f"  Compresión: {orig_mb:.1f} MB → {webp_kb:.0f} KB WebP")

# ── PASO 6: Verificar archivos exportados ──
print("\n─── PASO 6: Verificando archivos exportados ───")
for path, fmt in [(webp_path, "WebP"), (png_path, "PNG")]:
    try:
        check = Image.open(path)
        cw, ch = check.size
        if cw == sheet_w and ch == sheet_h:
            print(f"  ✅ {fmt}: {cw}x{ch} — OK")
        else:
            print(f"  ❌ {fmt}: esperado {sheet_w}x{sheet_h}, obtenido {cw}x{ch}")
    except Exception as e:
        print(f"  ❌ {fmt}: error al abrir — {e}")

# ── RESUMEN ──
print(f"""
═══════════════════════════════════════
  RESUMEN
  Frames: {FRAMES} @ {FPS}fps ({FRAMES/FPS:.2f}s de duración)
  Frame: {TARGET_W}x{TARGET_H}
  Grid: {COLS}x{ROWS} = {sheet_w}x{sheet_h}
  WebP: {webp_kb:.0f} KB
  Animación: {ANIM_NAME}
  Estado: {"✅ TODO OK" if ok_count == FRAMES and not errors else "⚠ HAY ERRORES"}
═══════════════════════════════════════
""")
