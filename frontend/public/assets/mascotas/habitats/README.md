# Directorio de Habitats

Este directorio contiene las imágenes de fondo para los hábitats de las mascotas.

## Estructura

Cada hábitat corresponde a una categoría de mascota:

```
habitats/
├── jardin.png       # Para mascotas tipo Planta (Bulbasaur)
├── cueva.png        # Para mascotas tipo Fantasma (Gastly)
└── volcan.png       # Para mascotas tipo Fuego (Charmander)
```

## Especificaciones de Imágenes

- **Formato**: PNG con transparencia (si aplica)
- **Dimensiones**: 1080x1920px (móvil vertical) o adaptable
- **Estilo**: Fondos inmersivos que complementen la mascota
- **Paleta**: Colores orgánicos del Método HabitGrow

### Jardin (Planta)
- Escena: Jardín soleado con flores, pasto verde
- Atmósfera: Cálida, alegre, natural
- Colores: Verdes (#4ade80), amarillos, cielos azules

### Cueva (Fantasma/Oscuridad)
- Escena: Cueva misteriosa con niebla púrpura, rocas
- Atmósfera: Mística, tranquila, nocturna
- Colores: Púrpuras, azules oscuros, grises

### Volcan (Fuego)
- Escena: Zona volcánica con lava, rocas calientes
- Atmósfera: Energética, cálida, intensa
- Colores: Rojos, naranjas, amarillos, grises oscuros

## Uso en el Código

```typescript
// En HomePage.tsx
const habitatMap = {
  'Planta': 'jardin.png',
  'Animal': 'cueva.png',    // Default para animales
  'Fuego': 'volcan.png',
  'Fantasma': 'cueva.png'
}

<div 
  style={{ 
    backgroundImage: `url(/assets/mascotas/habitats/${habitatMap[mascota.categoria]})`,
    backgroundSize: 'cover'
  }}
>
```

## Notas de Implementación

- Las imágenes deben ser optimizadas (< 500KB cada una)
- Se pueden generar con herramientas de IA o contratar diseñador
- El diseño debe permitir que la mascota se vea claramente en el centro
- Evitar distracciones visuales en el área donde aparece la mascota
