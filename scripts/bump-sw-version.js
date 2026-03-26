/**
 * bump-sw-version.js
 * 
 * Inyecta el hash del commit actual (COMMIT_REF) como versión del Service Worker.
 * Se ejecuta automáticamente en cada deploy de Netlify antes de publicar.
 * 
 * Variables de entorno de Netlify usadas:
 *   $COMMIT_REF  — hash completo del commit (ej: "a3f9c12...")
 *   $BUILD_ID    — ID único del build de Netlify (fallback)
 */

const fs = require('fs');
const path = require('path');

const SW_PATH = path.join(__dirname, '..', 'frontend', 'sw.js');

// Usar los primeros 8 caracteres del commit hash, o timestamp como fallback
const commitRef = process.env.COMMIT_REF
  ? process.env.COMMIT_REF.slice(0, 8)
  : Date.now().toString(36); // base36 timestamp si no hay env var (dev local)

const buildId = process.env.BUILD_ID || commitRef;

console.log(`[SW] Inyectando versión de cache: ${commitRef} (build: ${buildId})`);

// Leer sw.js actual
let swContent = fs.readFileSync(SW_PATH, 'utf8');

// Reemplazar la línea de versión con el nuevo hash
swContent = swContent.replace(
  /const CACHE_VERSION = '[^']*';/,
  `const CACHE_VERSION = '${commitRef}';`
);

// Escribir el archivo modificado
fs.writeFileSync(SW_PATH, swContent, 'utf8');

console.log(`[SW] ✅ Cache version actualizado a: habitgrow-cache-${commitRef}`);
