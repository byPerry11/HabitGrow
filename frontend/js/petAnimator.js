/**
 * PetAnimator — Motor de animaciones por sprite sheet para Gizzmo.
 * 
 * Uso:
 *   const animator = new PetAnimator(container, {
 *     basePath: 'assets/mascotas/Gizzmo/animations',
 *     animations: {
 *       tap: { frames: 60, frameW: 320, frameH: 180, fps: 24, loop: false }
 *     }
 *   });
 *   animator.play('tap');
 * 
 * Estructura de archivos esperada:
 *   assets/mascotas/Gizzmo/animations/
 *     tap.webp       ← sprite sheet vertical (320×10800 para 60 frames de 320×180)
 *     idle.webp      ← futuras animaciones
 */
class PetAnimator {
    constructor(container, config) {
        this.container = container;
        this.basePath = config.basePath || 'assets/mascotas/Gizzmo/animations';
        this.animations = config.animations || {};
        this._currentAnim = null;
        this._frameIndex = 0;
        this._rafId = null;
        this._lastFrameTime = 0;
        this._canvas = null;
        this._ctx = null;
        this._spriteImages = {};  // cache de imágenes cargadas
        this._isPlaying = false;
        this._onComplete = null;

        this._initCanvas();
    }

    _initCanvas() {
        this._canvas = document.createElement('canvas');
        this._canvas.classList.add('pet-anim-canvas');
        this._canvas.style.cssText = 'display:none; image-rendering:auto;';
        this.container.appendChild(this._canvas);
    }

    /**
     * Pre-carga un sprite sheet para que la animación arranque instantáneamente.
     */
    preload(animName) {
        return new Promise((resolve, reject) => {
            if (this._spriteImages[animName]) return resolve();

            const anim = this.animations[animName];
            if (!anim) return reject(new Error(`Animación "${animName}" no definida`));

            const img = new Image();
            img.onload = () => {
                this._spriteImages[animName] = img;
                resolve();
            };
            img.onerror = () => {
                // Fallback a PNG si WebP falla
                const fallback = new Image();
                fallback.onload = () => {
                    this._spriteImages[animName] = fallback;
                    resolve();
                };
                fallback.onerror = reject;
                fallback.src = `${this.basePath}/${animName}.png`;
            };
            img.src = `${this.basePath}/${animName}.webp`;
        });
    }

    /**
     * Reproduce una animación.
     * @param {string} animName - Nombre de la animación (ej: 'tap')
     * @param {Function} [onComplete] - Callback al terminar (si no es loop)
     */
    async play(animName, onComplete) {
        const anim = this.animations[animName];
        if (!anim) return console.warn(`Animación "${animName}" no encontrada`);

        // Pre-cargar si no está en cache
        if (!this._spriteImages[animName]) {
            await this.preload(animName);
        }

        // Detener animación anterior
        this.stop();

        this._currentAnim = animName;
        this._frameIndex = 0;
        this._isPlaying = true;
        this._onComplete = onComplete || null;
        this._lastFrameTime = 0;

        // Configurar canvas
        this._canvas.width = anim.frameW;
        this._canvas.height = anim.frameH;
        this._canvas.style.display = 'block';

        // Ocultar la imagen estática
        const staticImg = this.container.querySelector('img');
        if (staticImg) staticImg.style.display = 'none';

        this._ctx = this._canvas.getContext('2d');

        // Iniciar loop de renderizado
        this._rafId = requestAnimationFrame((t) => this._tick(t));
    }

    _tick(timestamp) {
        if (!this._isPlaying) return;

        const anim = this.animations[this._currentAnim];
        const frameDuration = 1000 / (anim.fps || 24);

        if (!this._lastFrameTime) this._lastFrameTime = timestamp;

        const elapsed = timestamp - this._lastFrameTime;

        if (elapsed >= frameDuration) {
            this._lastFrameTime = timestamp - (elapsed % frameDuration);
            this._renderFrame();
            this._frameIndex++;

            if (this._frameIndex >= anim.frames) {
                if (anim.loop) {
                    this._frameIndex = 0;
                } else {
                    this.stop();
                    if (this._onComplete) this._onComplete();
                    return;
                }
            }
        }

        this._rafId = requestAnimationFrame((t) => this._tick(t));
    }

    _renderFrame() {
        const anim = this.animations[this._currentAnim];
        const sprite = this._spriteImages[this._currentAnim];
        if (!sprite || !this._ctx) return;

        const cols = anim.cols || 1;  // columnas en el grid (1 = vertical)
        const col = this._frameIndex % cols;
        const row = Math.floor(this._frameIndex / cols);

        const sx = col * anim.frameW;
        const sy = row * anim.frameH;

        this._ctx.clearRect(0, 0, anim.frameW, anim.frameH);
        this._ctx.drawImage(
            sprite,
            sx, sy, anim.frameW, anim.frameH,  // fuente
            0, 0, anim.frameW, anim.frameH       // destino
        );
    }

    /**
     * Detiene la animación actual y restaura la imagen estática.
     */
    stop() {
        this._isPlaying = false;
        if (this._rafId) {
            cancelAnimationFrame(this._rafId);
            this._rafId = null;
        }
    }

    /**
     * Oculta el canvas y muestra la imagen estática de nuevo.
     */
    restore() {
        this.stop();
        if (this._canvas) this._canvas.style.display = 'none';

        const staticImg = this.container.querySelector('img');
        if (staticImg) staticImg.style.display = '';
    }

    /**
     * Destruye el animator y limpia recursos.
     */
    destroy() {
        this.stop();
        if (this._canvas && this._canvas.parentNode) {
            this._canvas.parentNode.removeChild(this._canvas);
        }
        this._spriteImages = {};
    }
}
