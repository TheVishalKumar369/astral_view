# Cosmic Explorer: Exoplanet 3D Visualization System

## Overview
Cosmic Explorer is a cross-platform, GPU-accelerated system for collecting, processing, and visualizing exoplanet and stellar data in an immersive 3D environment. It features:
- Automated data collection from NASA, Gaia, SIMBAD, and more
- Efficient data processing and storage (Parquet, HDF5)
- Desktop 3D visualization (Python + Ursina + OpenGL)
- Web-based 3D portal (React + Three.js)
- Modular, Dockerized architecture with GPU support

---

## Directory Structure
```
cosmic_explorer/
  data/                # All data files (mounted as Docker volume)
    raw/               # Raw downloaded data
    processed/         # Cleaned/processed data
  scripts/             # Data collection and processing scripts
    collect_data.py    # Collects data from APIs
    process_data.py    # Cleans/transforms/saves data
    tess_processing_template.py # (Future) TESS raw data processing
  desktop_app/         # Ursina/OpenGL 3D desktop app
  web_portal/          # React + Three.js web app
  requirements.txt     # Python dependencies
  Dockerfile.data      # Data processing container
  Dockerfile.desktop   # Desktop app container
  Dockerfile.web       # Web portal container
  docker-compose.yml   # Orchestrates all containers
  README.md            # This file
```

---

## Prerequisites
- **NVIDIA GPU** with drivers installed (for data processing and desktop app)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) (`nvidia-docker`)
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- (For desktop app GUI) X11 server (Linux) or WSL2 GUI (Windows)

---

## Quick Start

### 1. Build All Containers
```sh
docker-compose build
```

### 2. Collect Data (Run Data Service)
```sh
docker-compose run --rm data_service
```

### 3. Process Data
```sh
docker-compose run --rm data_service python3 scripts/process_data.py
```

### 4. Run Desktop 3D App (with GPU and GUI)
```sh
# Linux (with X11)
xhost +local:docker
docker-compose run --rm \
  -e DISPLAY=$DISPLAY \
  desktop_app
```

### 5. Run Web Portal
```sh
docker-compose up web_portal
# Visit http://localhost:3000
```

---

## GPU Support
- All containers that require GPU (data_service, desktop_app) are configured for NVIDIA GPUs.
- Make sure to use `--gpus all` or Docker Compose with the NVIDIA runtime.
- For desktop GUI, ensure X11 or WSL2 GUI is set up.

---

## Data Sources
- NASA Exoplanet Archive
- Gaia DR3
- SIMBAD
- (Future) TESS raw data

---

## Future Development
- TESS raw data processing (see `scripts/tess_processing_template.py`)
- Advanced 3D features, VR/AR, multiplayer, and more

---

## Troubleshooting
- If you encounter issues with GPU access, check your NVIDIA driver and Docker runtime setup.
- For desktop GUI issues, verify X11/WSL2 GUI configuration.

---

## License
MIT License 