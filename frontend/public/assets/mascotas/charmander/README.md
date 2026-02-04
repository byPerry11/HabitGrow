# Charmander - Estados de Mascota

Esta carpeta contiene todas las imágenes de estados de **Charmander** (mascota tipo Fuego).

## Estados Requeridos

### Básicos (Alta Prioridad)
- `idle.png` - Estado normal/parado con cola encendida
- `happy.png` - Feliz (cuando se completa un hábito)
- `sad.png` - Triste (HP bajo < 30%)

### Avanzados (Prioridad Media)
- `excited.png` - Emocionado (racha nueva, nivel up)
- `sleeping.png` - Dormido (noche o sin actividad 2+ horas)

### Especiales para Charmander
- `fire_on.png` - Cola con fuego muy intenso (muy feliz/energético)
- `fire_dim.png` - Cola con fuego débil (triste/cansado)

## Especificaciones

- **Formato**: PNG con transparencia
- **Dimensiones**: 512x512px (cuadrado)
- **Fondo**: Transparente
- **Estilo**: Pixel art o ilustración cartoon similar a Pokémon
- **Paleta**: Naranjas (#f97316, #ea580c), rojos, amarillos para fuego

## Ejemplos de Estados

### Idle
- Charmander parado en posición neutral
- Cola con fuego normal/estable
- Ojos abiertos, expresión tranquila
- Postura estable

### Happy
- Saltando o brazos arriba
- Sonrisa amplia
- Cola con fuego más grande/brillante
- Energía visible

### Sad
- Cabeza gacha
- Ojos tristes o cerrados
- Cola con fuego pequeño/débil
- Colores más apagados
- Postura encorvada

### Excited
- Salto alto
- Fuego en la cola muy intenso
- Expresión muy alegre
- Posible chispas alrededor

### Sleeping
- Acostado o sentado
- Ojos cerrados
- Fuego en la cola bajo pero estable
- Respiración suave visible
- Símbolo "Zzz" opcional

### Fire_on (Especial)
- Similar a happy pero con énfasis en el fuego
- Llama muy grande y brillante
- Para momentos de alta energía
- Posibles chispas voladoras

### Fire_dim (Especial)
- Similar a sad pero con énfasis en la llama débil
- Fuego casi apagándose
- Para HP crítico
- Estado de advertencia visual

## Elemento Clave: La Cola

La cola de Charmander es su característica definitoria:
- **Fuego fuerte** = Feliz, saludable, energético
- **Fuego débil** = Triste, enfermo, cansado
- **Fuego apagado** = NUNCA (en el lore, si se apaga muere)

El estado de la llama debe ser consistente con el estado emocional.

## Uso en Código

```typescript
const mascotaImage = `/assets/mascotas/charmander/${estado}.png`
// Ejemplo: /assets/mascotas/charmander/fire_on.png

// Lógica especial para Charmander
if (hp_percentage < 20) {
  estado = 'fire_dim'
} else if (hp_percentage > 90) {
  estado = 'fire_on'
}
```
