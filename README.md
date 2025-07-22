# Brawl Bunny

A fast-paced 4-player multiplayer action game built with Python and Pygame, featuring four unique bunny characters with custom abilities and team-based combat.

---

## 🎮 Game Overview

In Brawl Bunny, players join teams (Red or Blue), select their characters, and compete to achieve a set number of kills before time runs out. The game includes rich procedural animations, shaders, and real-time multiplayer features.

---
## 🧰 Technologies Used

- **Programming Language**: Python 3.8+
- **Game Engine**: Pygame
- **Networking**: UDP (sockets)
- **Graphics**:
  - Procedural VFX animation (eg: orbs, vines, explosions)
  - Shaders (fresnel effects, glowing orbs, laser)
- **Data Structures & Math**:
  - Bézier curves (for vines)
  - Roots of unity, 3D Matrix Transformation and Projection (for orbs)
  - Minimum Spanning Tree, Graph Algorithms (explosion VFX)
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

**1. Menu**

**2. Instruction**

**3. Matchmaking**

**4. Character Selection**

**5. Gameplay**

**6. Endscreen**
---

## 🧙‍♂️ Characters

### 🧿 Orb Bunny
- **Base**: 5 rotating orbs
- **Attack**: Fires an orb
- **Super**: Fires all 5 orbs in a star pattern

![orb_bunny_splash_signed](https://github.com/user-attachments/assets/256d3c30-55f8-4aaf-863a-60d88b49b8a6)

https://github.com/user-attachments/assets/fcedc8f3-1cea-4fc1-a3a0-a0396833c4d1


### 🌿 Nature Bunny
- **Base**: Procedural vine
- **Attack**: Short-range vine punch
- **Super**: Grappling vine hook that pulls the player

![nature_bunny_splash_signed](https://github.com/user-attachments/assets/90c68f5d-1615-4403-b6d4-eeb1c3caede0)

https://github.com/user-attachments/assets/3270c65a-3f26-41d6-a1f5-0564c6502b60


### ✨ Angel Bunny
- **Attack**: Chargeable light orb that grows and explodes on impact
- **Super**: Laser beam that pierces obstacles

![angel_bunny_splash_signed](https://github.com/user-attachments/assets/a0b02121-f784-40a1-af70-ea49d3a892ec)

https://github.com/user-attachments/assets/9927e284-4828-4c4c-9909-743b1b1c7a43

### 🗡️ Shadow Bunny
- **Attack**: Melee sword strike 
- **Super**: Enters shadow realm (become invisible)

![shadow_bunny_splash_signed](https://github.com/user-attachments/assets/bc2e9038-0152-4c86-8fc3-a6409819cebe)

https://github.com/user-attachments/assets/81b9e0bc-b2df-4ae4-9034-be8cf3d3d8be

---


## 🌐 Multiplayer System

A custom-built **client-server architecture** using **UDP**:
- Clients encode keyboard input in a string which is sent to the server.
- Server decodes inputs, updates game state, then sends updated state (in a string) to all clients.
- Efficient broadcasting ensures all players see consistent gameplay.

---

