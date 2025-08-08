# Three.js Web Engine

## Overview
Web-based 3D cosmic exploration using Three.js library for cross-platform browser compatibility.

## Features
- Cross-platform web access
- WebGL-based rendering
- No installation required
- Easy sharing via URL
- Mobile-friendly interface
- Real-time 3D graphics
- Shader support
- Physics integration (Cannon.js)

## Setup
1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm start
   ```

3. Open http://localhost:3000 in your browser

## Controls
- **WASD**: Move camera
- **Mouse**: Look around
- **Space**: Move up
- **Shift**: Move down
- **Speed Slider**: Adjust movement speed

## Files
- `src/App.js` - Main React application
- `src/components/UniverseViewer.jsx` - Three.js 3D renderer
- `src/components/cosmicData.json` - Cosmic object data
- `public/index.html` - HTML entry point

## System Requirements
- Modern browser with WebGL 2.0 support
- 4GB RAM recommended
- WebGL-compatible GPU
- Network connection (optional for local files)

## Technologies Used
- Three.js (3D graphics)
- React (UI framework)
- WebGL (rendering)
- JavaScript ES6+
- HTML5/CSS3
