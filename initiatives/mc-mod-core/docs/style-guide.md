# Mana Core - Visual Style Guide

## Design Philosophy

Mana Core uses a clean, technical aesthetic that conveys energy flow and resource management without overwhelming the player. Visual elements are subtle but informative, allowing players to understand mana mechanics at a glance.

## Color Palette

| Name | Hex | Usage | Accessibility |
|------|-----|-------|---------------|
| Mana Blue Primary | `#00A2FF` | Primary mana color, high-density indicators | AA contrast 4.5:1 on white |
| Mana Blue Secondary | `#66C9FF` | Medium-density indicators, particles | AA contrast 3.5:1 on white |
| Mana Blue Light | `#B3E0FF` | Low-density indicators, subtle overlays | AA contrast 2.5:1 on white |
| Mana Glow | `#00F0FF` | Particle glow, emissive effects | No text use |
| Warning Yellow | `#FFD700` | Storage full, errors | AA contrast 4.5:1 on dark |
| Neutral Gray | `#808080` | Inactive elements, borders | AA compliant |
| Background Dark | `#1A1A2E` | Particle backgrounds (transparent) | N/A |

### Accessibility Notes
- All color-coded information has redundant shape/motion indicators
- Mana density is indicated by both color intensity AND particle count
- Flow direction is indicated by particle motion, not just color gradient
- Text information is always available via debug commands

## Particle System

### Mana Flow Particles
- **Shape:** Small sphere (0.125 blocks diameter)
- **Base Color:** Mana Blue Primary (`#00A2FF`)
- **Glow:** Soft additive glow with Mana Glow (`#00F0FF`) at 50% opacity
- **Motion:** Smooth linear movement following flow direction
- **Lifetime:** 1.5 seconds with fade-out
- **Size Variation:** Random 0.8x-1.2x scale for natural appearance
- **Spawn Rate:** 1-5 particles per tick per mana unit flowing (configurable)
- **Collision:** None - particles pass through blocks

### Particle Density Scale
| Mana Flow Rate | Particles/sec | Color | Size |
|----------------|---------------|-------|------|
| 0 | 0 | N/A | N/A |
| 0-10 | 1-5 | Mana Blue Light | 0.8x |
| 10-50 | 5-20 | Mana Blue Secondary | 1.0x |
| 50-100 | 20-40 | Mana Blue Primary | 1.1x |
| 100+ | 40-60 | Mana Blue Primary + glow | 1.2x |

### Particle Spawning Rules
1. Particles spawn at mana source positions
2. Particles travel toward mana sink positions
3. Particle velocity proportional to flow rate
4. Maximum 100 particles visible per chunk (culling)
5. Particles respect client graphics settings
6. Particles disabled when graphics set to "Fancy: OFF"

## Block Overlays

### Mana Density Overlay
- **Render Type:** Block outline overlay (not full block tint)
- **Color:** Semi-transparent mana blue based on density
- **Opacity:** 20-60% based on mana value
- **Edge Width:** 2 pixels
- **Render Distance:** 32 blocks (configurable)
- **Culling:** Only render for blocks player is looking at

### Overlay Color Mapping
| Mana Value | Opacity | Edge Color |
|------------|---------|------------|
| 0 | 0% | N/A (no overlay) |
| 1-10 | 20% | Mana Blue Light |
| 10-50 | 40% | Mana Blue Secondary |
| 50-100 | 60% | Mana Blue Primary |
| 100+ | 60% | Mana Blue Primary + white highlight |

## Block Models

### Mana Generator
- **Base Model:** Cube with subtle glow
- **Texture:** `mana-core:block/mana_generator`
- **Particle Emitter:** Center of top face
- **Emitter Radius:** 0.5 blocks
- **Emitter Rate:** 10 particles/tick (when active)
- **Light Level:** 10 (subtle blue-tinted light)

### Mana Collector
- **Base Model:** Cube with recessed center
- **Texture:** `mana-core:block/mana_collector`
- **Storage Indicator:** Top face fills with mana blue based on % full
- **Particle Sink:** Center of top face (particles disappear here)
- **Light Level:** Varies with stored mana (0-8)

### Mana Crystal (Entity)
- **Model:** Floating crystal geometry (octahedron)
- **Texture:** `mana-core:entity/mana_crystal`
- **Size:** 0.75 blocks tall
- **Glow:** Pulsing glow effect (0.5-1.0 intensity)
- **Rotation:** Slow rotation (5 degrees/tick)
- **Particle Trail:** Leaves faint mana particles as it moves

## Texture Specifications

### Texture Format
- **Resolution:** 16x16, 32x32, or 64x64 pixels
- **Format:** PNG with transparency
- **Color Space:** sRGB
- **Naming:** `snake_case.png`

### Texture Files
| Path | Size | Description |
|------|------|-------------|
| `textures/block/mana_generator.png` | 32x32 | Generator block texture |
| `textures/block/mana_collector.png` | 32x32 | Collector block texture |
| `textures/block/mana_generator_front.png` | 32x32 | Generator front face (optional) |
| `textures/block/mana_collector_front.png` | 32x32 | Collector front face with storage indicator |
| `textures/particle/mana_particle.png` | 16x16 | Particle sprite sheet (4 frames) |
| `entity/mana_crystal.png` | 64x64 | Crystal entity texture |

### Particle Sprite Sheet
- **Layout:** 2x2 grid (4 frames)
- **Frame Size:** 8x8 pixels
- **Animation:** 4-frame cycle at 10 FPS
- **Frames:** Fade in/out glow effect

## Animation Guidelines

### Block Animations
- **Generator:** Subtle pulse (0.5-1.0 scale) at 1 Hz
- **Collector:** Fill animation on storage (0-100% height)
- **Easing:** Linear for particles, ease-in-out for block animations

### Particle Animations
- **Spawn:** Fade in over 0.2 seconds
- **Death:** Fade out over 0.3 seconds
- **Scale:** Random 0.8-1.2x at spawn, constant
- **Color:** Constant (based on density)

## Accessibility Requirements

### Visual Alternatives
1. All color information has shape/motion equivalent
2. Particle flow direction indicated by motion trail
3. Mana density indicated by both color AND particle count
4. Storage level indicated by both fill AND numeric overlay

### Text Information
1. All visual information available via `/mana debug` command
2. Numeric values always displayed in chat
3. Screen reader compatible (no visual-only information)

### Configurable Options
1. Particle count slider (0-100%)
2. Overlay opacity slider (0-100%)
3. Particle size slider (50-150%)
4. Enable/disable individual visualization types

## File Organization

```
src/main/resources/assets/mana-core/
├── lang/
│   └── en_us.json              # Translations
├── textures/
│   ├── block/
│   │   ├── mana_generator.png
│   │   └── mana_collector.png
│   └── particle/
│       └── mana_particle.png    # Particle sprite sheet
└── particles/
    └── mana_flow.json          # Particle definition

src/client/resources/assets/mana-core/
└── textures/
    └── entity/
        └── mana_crystal.png     # Entity texture (client-only)
```

## Quality Standards

1. **Texture Resolution:** Minimum 16x16, preferred 32x32 for blocks
2. **Compression:** PNG optimization without visual loss
3. **Naming:** Consistent snake_case naming
4. **Transparency:** Alpha channel used appropriately
5. **Performance:** Textures use mipmapping where applicable
6. **Originality:** All assets are procedural or clearly marked placeholders

## Placeholder Assets

All v1 assets are procedural placeholders:
- Particle texture: Programmatically generated gradient
- Block textures: Solid colors with procedural details
- Entity texture: Procedural geometric pattern

Provenance for all placeholders: `"procedural:mana-core-v1"`
