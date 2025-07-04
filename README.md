# Multiplayer Bunny Brawl

**Creator**: Eugene Hwang  
**Centre**: The Alice Smith School (Centre Number: 74008)  
**Candidate Number**: 2146  

A fast-paced multiplayer action game built with Python and Pygame, featuring four unique bunny characters with custom abilities, team-based combat, and a fully functional client-server architecture using UDP.

---

## 🎮 Game Overview

In **Multiplayer Bunny Brawl**, players join teams (Red or Blue), select their characters, and compete to achieve the highest number of kills before time runs out. The game includes rich procedural animations, shaders, and real-time multiplayer features.

---

## 🧩 Game States

### 1. Menu
- **Buttons**: `Start`, `How to Play`
- **Features**: Animated flags, hover-responsive buttons
- **Transitions**:  
  - `Start` → Team Selection  
  - `How to Play` → Instruction Screen

### 2. Instruction
- Displays character attacks and abilities.
- `Back` button to return to menu.

### 3. Team Selection
- Supports 2–6 players.
- Choose Red or Blue team.
- Player numbers and team compositions displayed to all.
- Proceeds only if ≥2 players are ready.

### 4. Character Selection
- Players select characters from a scrollable UI.
- Shows selections of other players in real-time.
- Readiness triggers countdown to start the match.

### 5. Gameplay
- Team-based combat: Red vs Blue.
- First team to reach **X kills** wins.
- Respawning, kill scoring, and match timer.
- Ends in win/lose/draw → Endscreen.

### 6. Endscreen
- Split screen results display.
- Shows win/lose/draw.
- Exit to menu.

---

## 🌐 Multiplayer System

A custom-built **client-server architecture** using **UDP**:
- Clients encode keyboard input → server.
- Server decodes inputs, updates game state, then sends updated state to all clients.
- Efficient broadcasting ensures all players see consistent gameplay.

---

## 🔧 Helper Classes

### Camera
- Controls draw order based on `y` position for correct layering.
- Dynamically adds visible sprites and sorts by bottom-y.

### Map
- Loads map from `.xml` file.
- Implements **chunking** to only render nearby sections, optimizing performance.

---

## 🧙‍♂️ Characters

### 🟣 Orb Bunny
- **Base**: 5 rotating orbs with a Fresnel shader effect.
- **Attack**: Fires an orb towards mouse; returns if blocked.
- **Super**: Fires all 5 orbs in a star pattern using roots of unity and shaders.

### 🌿 Nature Bunny
- **Base**: Procedural vines follow the mouse using Bézier curves.
- **Attack**: Short-range vine punch with easing animation.
- **Super**: Grappling vine hook that pulls the player across obstacles.

### ✨ Angel Bunny
- **Attack**: Chargeable light orb that glows and cracks on impact.
- **Crack Animation**: Procedural crack using MST and chordless cycles.
- **Super**: Laser beam that pierces obstacles using shader effects.

### 🗡️ Shadow Bunny
- **Attack**: Melee sword strike.
- **Super**: *(WIP)* Teleportation dash or stealth state (assumed based on concept).

---

## 💡 Features & Technologies

- ✅ Python + Pygame
- ✅ Real-time UDP networking
- ✅ Procedural animation & movement
- ✅ Shader-based effects (Fresnel, glow, crack, laser)
- ✅ Chunked map rendering
- ✅ Dynamic camera + layering
- ✅ Bézier curves, roots of unity, MSTs for logic
- ✅ Smooth game state transitions
- ✅ Multiplayer up to 6 players

---

## 🚀 Getting Started

> Requires: Python 3.8+, Pygame

### 1. Clone the repository
```bash
git clone https://github.com/your-username/bunny-brawl.git
cd bunny-brawl
