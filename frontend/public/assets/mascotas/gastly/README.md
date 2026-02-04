# Gastly - Estados de Mascota

Esta carpeta contiene todas las imágenes de estados de **Gastly** (mascota tipo Fantasma).

## Estados Requeridos

### Básicos (Alta Prioridad)
- `idle.png` - Estado normal/flotando
- `happy.png` - Feliz (cuando se completa un hábito)
- `sad.png` - Triste (HP bajo < 30%)

### Avanzados (Prioridad Media)
- `excited.png` - Emocionado (racha nueva, nivel up)
- `sleeping.png` - Dormido (noche o sin actividad 2+ horas)

### Especiales para Gastly
- `floating.png` - Flotando con movimiento más pronunciado
- `glowing.png` - Brillando con aura púrpura intensa

## Especificaciones

- **Formato**: PNG con transparencia
- **Dimensiones**: 512x512px (cuadrado)
- **Fondo**: Transparente
- **Estilo**: Pixel art o ilustración cartoon similar a Pokémon
- **Paleta**: Púrpuras (#8b5cf6, #6d28d9), negros, blancos para ojos

## Ejemplos de Estados

### Idle
- Gastly flotando en el aire
- Gas/niebla alrededor moviéndose sutilmente
- Ojos blancos brillantes abiertos
- Sonrisa característica

### Happy
- Cuerpo de gas expandido (más grande)
- Ojos muy brillantes
- Sonrisa amplia
- Posible aura púrpura brillante

### Sad
- Cuerpo contraído (más pequeño)
- Ojos apagados o semi-cerrados
- Gas menos denso (más transparente)
- Colores desaturados

### Excited
- Gas muy expandido y brillante
- Aura intensa
- Expresión muy alegre
- Posiblemente girando

### Sleeping
- Flotando bajo
- Ojos cerrados
- Gas más denso/estable
- Movimiento mínimo

### Floating (Especial)
- Movimiento ondulante exagerado
- Para cuando está muy activo
- Gas con patrones de movimiento

### Glowing (Especial)
- Aura púrpura muy intensa
- Posible uso nocturno
- Estados especiales de poder

## Diferencias con otras mascotas

Gastly es único porque:
- No tiene extremidades (solo cuerpo gaseoso)
- Siempre está flotando
- El "movimiento" se logra con variaciones en el gas
- Los estados se expresan más con brillo y tamaño

## Uso en Código

```typescript
const mascotaImage = `/assets/mascotas/gastly/${estado}.png`
// Ejemplo: /assets/mascotas/gastly/glowing.png
```
