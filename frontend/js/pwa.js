// pwa.js
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js')
            .then(registration => {
                console.log('✅ ServiceWorker registrado con éxito en el alcance:', registration.scope);
            })
            .catch(error => {
                console.error('❌ Fallo al registrar ServiceWorker:', error);
            });
    });
}
