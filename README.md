# Brawl Bunny 🐰

A fast-paced 4-player multiplayer action game built with Python and Pygame, featuring four unique bunny characters with custom abilities and team-based combat.

---

## 🎮 Game Overview

In **Multiplayer Bunny Brawl**, players join teams (Red or Blue), select their characters, and compete to achieve the highest number of kills before time runs out. The game includes rich procedural animations, shaders, and real-time multiplayer features.

---
## 🧰 Technologies Used

- **Programming Language**: Python 3.8+
- **Game Engine**: Pygame
- **Networking**: UDP (sockets)
- **Graphics**:
  - Procedural VFX animation (eg., orbs, vines, light beams)
  - Shaders (Fresnel effects, glow, laser)
- **Data Structures & Math**:
  - Bézier curves (for vines)
  - Roots of unity, 3D Matrix Transformation and Projection (for orbs)
  - Minimum Spanning Tree, Graph Algorithms (VFX for explosion)
- **Map & Camera**:
  - `.xml`-based map loading
  - Chunked rendering for performance
  - Dynamic layering via bottom-y sorting
- **UI**:
  - Interactive menus and buttons
  - Character selection UI
  - Real-time multiplayer UI updates
- **Others**:
  - Game state management
  - Optimized client-server performance
---

## 🧩 Game States

### 1. Menu
### 2. Instruction
### 3. Matchmaking
### 4. Character Selection
### 5. Gameplay
- Team-based combat: Red vs Blue.
- First team to reach **X kills** wins.
- Respawning, kill scoring, and match timer.
### 6. Endscreen
---

## 🧙‍♂️ Characters

### 🟣 Orb Bunny
- **Base**: 5 rotating orbs with a Fresnel shader effect
- **Attack**: Fires an orb towards mouse position
- **Super**: Fires all 5 orbs in a star pattern using roots of unity

### 🌿 Nature Bunny
- **Base**: Procedural vines follow the mouse using Bézier curves
- **Attack**: Short-range vine punch with easing animation
- **Super**: Grappling vine hook that pulls the player

### ✨ Angel Bunny
- **Attack**: Chargeable light orb that glows and cracks on impact
- **Crack Animation**: Procedural crack using MST and chordless cycles
- **Super**: Laser beam that pierces obstacles using shader effects

### 🗡️ Shadow Bunny
- **Attack**: Melee sword strike 
- **Super**: Enters shadow realm (become invisible) with particle effects
---

## 🌐 Multiplayer System

A custom-built **client-server architecture** using **UDP**:
- Clients encode keyboard input → server.
- Server decodes inputs, updates game state, then sends updated state to all clients.
- Efficient broadcasting ensures all players see consistent gameplay.

---

