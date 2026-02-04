# Bulbasaur - Estados de Mascota

Esta carpeta contiene todas las imágenes de estados de **Bulbasaur** (mascota tipo Planta).

## Estados Requeridos

### Básicos (Alta Prioridad)
- `idle.png` - Estado normal/respirando suavemente
- `happy.png` - Feliz (cuando se completa un hábito)
- `sad.png` - Triste (HP bajo < 30%)

### Avanzados (Prioridad Media)
- `excited.png` - Emocionado (racha nueva, nivel up)
- `sleeping.png` - Dormido (noche o sin actividad 2+ horas)

### Opcionales (Baja Prioridad)
- `eating.png` - Comiendo (para interacciones futuras)
- `playing.png` - Jugando (para interacciones futuras)

## Especificaciones

- **Formato**: PNG con transparencia
- **Dimensiones**: 512x512px (cuadrado)
- **Fondo**: Transparente
- **Estilo**: Pixel art o ilustración cartoon similar a Pokémon
- **Paleta**: Verdes (#4ade80, tonos orgánicos)

## Ejemplos de Estados

### Idle
- Bulbasaur parado, respirando suavemente
- Ojos abiertos, expresión neutral
- Bulbo en la espalda saludable

### Happy
- Saltando o con brazos arriba
- Sonrisa amplia
- Brillo en los ojos

### Sad
- Cabeza gacha
- Ojos semi-cerrados
- Colores más apagados/desaturados
- Bulbo marchito o seco

### Excited
- Salto alto
- Expresión muy alegre
- Posible brillo alrededor

### Sleeping
- Acostado o sentado
- Ojos cerrados
- Símbolo "Zzz" cerca (opcional, se puede agregar en código)

## Uso en Código

```typescript
const mascotaImage = `/assets/mascotas/${especie}/${estado}.png`
// Ejemplo: /assets/mascotas/bulbasaur/happy.png
```
