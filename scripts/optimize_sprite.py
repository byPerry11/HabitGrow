"""
Optimiza el sprite sheet de Gizzmo:
1. Lee el sprite sheet original (vertical, 60 frames, 1280x720 cada frame)
2. Redimensiona cada frame a un tamaño apto para web
3. Exporta como WebP con buena compresión
"""
from PIL import Image
import os

# Config
SOURCE = r"C:\Users\tagit\Pictures\Gizmo\Secuencia\frames 60\sprite sheets\spritesheet_bby.png"
OUTPUT_DIR = r"C:\Users\tagit\LABS\TestMascota\frontend\assets\mascotas\Gizzmo\animations"
ANIM_NAME = "tap"  # nombre de la animación
FRAME_COUNT = 60
TARGET_FRAME_W = 320  # ancho objetivo por frame (web-friendly)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Abrir imagen original
img = Image.open(SOURCE)
orig_w, orig_h = img.size
frame_h_orig = orig_h // FRAME_COUNT

print(f"Original: {orig_w}x{orig_h}")
print(f"Frame original: {orig_w}x{frame_h_orig}")

# Calcular escala
scale = TARGET_FRAME_W / orig_w
target_frame_h = int(frame_h_orig * scale)
target_total_h = target_frame_h * FRAME_COUNT

print(f"Frame redimensionado: {TARGET_FRAME_W}x{target_frame_h}")
print(f"Sprite sheet final: {TARGET_FRAME_W}x{target_total_h}")

# Redimensionar todo el sprite sheet
resized = img.resize((TARGET_FRAME_W, target_total_h), Image.LANCZOS)

# Guardar como WebP (buena calidad, excelente compresión)
webp_path = os.path.join(OUTPUT_DIR, f"{ANIM_NAME}.webp")
resized.save(webp_path, "WEBP", quality=80)

# También guardar como PNG por compatibilidad
png_path = os.path.join(OUTPUT_DIR, f"{ANIM_NAME}.png")
resized.save(png_path, "PNG", optimize=True)

webp_size = os.path.getsize(webp_path) / 1024
png_size = os.path.getsize(png_path) / 1024

print(f"\n✅ Exportado:")
print(f"   WebP: {webp_path} ({webp_size:.0f} KB)")
print(f"   PNG:  {png_path} ({png_size:.0f} KB)")
print(f"\n📊 Compresión: {os.path.getsize(SOURCE)/1024/1024:.1f} MB → {webp_size:.0f} KB (WebP)")
