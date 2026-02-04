import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Paleta Zen-Productivo
        'zen-green': '#4ade80',
        'zen-earth': '#3d3635',
        'zen-cream': '#fdfaf6',
        
        // Colores de Mascota según estado de salud
        'mascota-optimo': '#4ade80',    // Verde brillante
        'mascota-regular': '#fbbf24',   // Amarillo warning
        'mascota-mal': '#f97316',       // Naranja alerta
        'mascota-marchito': '#ef4444',  // Rojo crítico
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      transitionDuration: {
        '400': '400ms',
        '700': '700ms',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
} satisfies Config
