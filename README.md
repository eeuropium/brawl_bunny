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
  - Procedural VFX animation (eg: orbs, vines, light beams)
  - Shaders (fresnel effects, glow, laser)
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

![orb_bunny_splash_signed](https://github.com/user-attachments/assets/256d3c30-55f8-4aaf-863a-60d88b49b8a6)

https://github.com/user-attachments/assets/fcedc8f3-1cea-4fc1-a3a0-a0396833c4d1


### 🌿 Nature Bunny
- **Base**: Procedural vines follow the mouse using Bézier curves
- **Attack**: Short-range vine punch with easing animation
- **Super**: Grappling vine hook that pulls the player

![nature_bunny_splash_signed](https://github.com/user-attachments/assets/90c68f5d-1615-4403-b6d4-eeb1c3caede0)

https://github.com/user-attachments/assets/3270c65a-3f26-41d6-a1f5-0564c6502b60


### ✨ Angel Bunny
- **Attack**: Chargeable light orb that glows and cracks on impact
- **Crack Animation**: Procedural crack using MST and chordless cycles
- **Super**: Laser beam that pierces obstacles using shader effects

![angel_bunny_splash_signed](https://github.com/user-attachments/assets/a0b02121-f784-40a1-af70-ea49d3a892ec)

https://github.com/user-attachments/assets/9927e284-4828-4c4c-9909-743b1b1c7a43

### 🗡️ Shadow Bunny
- **Attack**: Melee sword strike 
- **Super**: Enters shadow realm (become invisible) with particle effects

![shadow_bunny_splash_signed](https://github.com/user-attachments/assets/bc2e9038-0152-4c86-8fc3-a6409819cebe)

https://github.com/user-attachments/assets/81b9e0bc-b2df-4ae4-9034-be8cf3d3d8be

---


## 🌐 Multiplayer System

A custom-built **client-server architecture** using **UDP**:
- Clients encode keyboard input → server.
- Server decodes inputs, updates game state, then sends updated state to all clients.
- Efficient broadcasting ensures all players see consistent gameplay.

---

