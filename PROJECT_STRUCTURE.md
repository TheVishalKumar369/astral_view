# Exo Planet Cosmos Traveller - Project Structure

## Overview
This project provides multiple 3D engine implementations for exploring cosmic data, organized into engine-specific directories for scalability and maintainability.

## Directory Structure

```
exo_planet_cosmos_traveller/
├── desktop_app/                    # Desktop 3D Engine Implementations
│   ├── engines/
│   │   ├── ursina/                # Python Ursina Engine
│   │   │   ├── cosmic_explorer_simple.py
│   │   │   ├── cosmic_explorer_fixed.py
│   │   │   ├── enhanced_cosmic_explorer.py  # Generated implementation
│   │   │   ├── engine_info.json
│   │   │   └── README.md
│   │   ├── panda3d/              # Advanced Panda3D Engine
│   │   │   ├── main.py
│   │   │   ├── materials.py
│   │   │   ├── physics.py
│   │   │   ├── engine_info.json
│   │   │   └── requirements.txt
│   │   ├── godot/                # Godot Engine (Planned)
│   │   │   ├── engine_info.json
│   │   │   └── README.md
│   │   ├── unity/                # Unity Engine (Planned)
│   │   │   ├── cosmic_world_unity.json     # Generated Unity data
│   │   │   ├── engine_info.json
│   │   │   └── README.md
│   │   ├── bevy/                 # Bevy Rust Engine (Research)
│   │   │   ├── engine_info.json
│   │   │   └── README.md
│   │   └── future/               # Future Engine Plans
│   │       └── planned_engines.json
│   ├── cosmic_engine_launcher.py  # Universal Engine Launcher
│   ├── engine_manager.py         # Engine Management System
│   └── README.md
│
├── web_portal/                    # Web-Based 3D Engine Implementations
│   ├── engines/
│   │   ├── threejs/              # Three.js Web Engine (Ready)
│   │   │   ├── src/
│   │   │   │   ├── App.js
│   │   │   │   └── components/
│   │   │   │       ├── UniverseViewer.jsx
│   │   │   │       ├── EnhancedUniverseViewer.jsx  # Generated
│   │   │   │       └── cosmicData.json
│   │   │   ├── public/index.html
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   ├── babylonjs/            # Babylon.js Engine (Planned)
│   │   │   └── README.md
│   │   ├── webgpu/               # WebGPU Engine (Research)
│   │   │   └── README.md
│   │   ├── webxr/                # WebXR VR/AR (Research)
│   │   │   └── README.md
│   │   └── progressive_web_app/  # PWA Implementation (Planned)
│   │       └── README.md
│   ├── engines/
│   │   └── web_engines.json      # Web Engine Configuration
│   └── README.md
│
├── shared/                       # Shared Resources
│   └── generated_content/        # Processed Astronomical Data
│       ├── cosmicData.json      # Three.js compatible data (214 KB)
│       └── README.md            # Data documentation
│
├── data/                        # Raw and Processed Data
│   ├── raw/                     # Original astronomical data
│   └── processed/               # Cleaned and formatted data
│
├── scripts/                     # Utility and Processing Scripts
├── notebooks/                   # Jupyter notebooks for analysis
├── generated_worlds/           # LEGACY - moved to shared/generated_content
└── README.md                   # Main project documentation
```

## Engine Categories

### Desktop Engines
- **Ursina** (✅ Ready) - Lightweight Python 3D engine
- **Panda3D** (✅ Ready) - Professional Python 3D engine  
- **Godot** (🚧 Planned) - Open-source game engine
- **Unity** (🚧 Planned) - Industry-standard game engine
- **Bevy** (🔬 Research) - Modern Rust ECS engine

### Web Engines
- **Three.js** (✅ Ready) - Popular JavaScript 3D library
- **Babylon.js** (🚧 Planned) - Advanced web 3D engine
- **WebGPU** (🔬 Research) - Next-gen web graphics API
- **WebXR** (🔬 Research) - VR/AR web experiences
- **PWA** (🚧 Planned) - Progressive web app

## Key Features

### Multi-Engine Support
- **Universal Launcher**: Single interface to launch any engine
- **Engine Manager**: Handles dependencies and isolation
- **Shared Data**: Common astronomical data format
- **Cross-Platform**: Desktop and web implementations

### Real Astronomical Data
- **GAIA Catalog**: European Space Agency star data
- **SIMBAD Integration**: Astronomical database access
- **Exoplanet Catalogs**: Real exoplanet systems
- **Real-time Positioning**: Accurate 3D coordinates

### Generated Content Pipeline
- **Data Processing**: Raw → Processed → Engine-ready
- **Multi-Format Export**: JSON, Unity, Binary formats
- **Performance Optimized**: LOD and streaming support
- **Engine-Specific**: Tailored for each engine's needs

## Status Legend
- ✅ **Ready**: Fully implemented and functional
- 🚧 **Planned**: In development roadmap
- 🔬 **Research**: Experimental/investigation phase
- ❌ **Future**: Long-term goals

## Getting Started

1. **Choose Engine**: Use cosmic_engine_launcher.py
2. **Install Dependencies**: Follow engine-specific README
3. **Launch Explorer**: Select preferred 3D engine
4. **Navigate Cosmos**: Explore real astronomical data

## Data Sources
- **GAIA DR3**: 1+ billion stars
- **SIMBAD**: 11+ million astronomical objects  
- **NASA Exoplanet Archive**: 5000+ confirmed exoplanets
- **Messier Catalog**: Deep space objects

## Contributing
Each engine directory contains specific contribution guidelines and setup instructions. The modular structure allows independent development of each engine while sharing common data sources.
