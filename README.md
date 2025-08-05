# Cosmic Explorer: Exoplanet 3D Visualization System

## Overview
Cosmic Explorer is a cross-platform, GPU-accelerated system for collecting, processing, and visualizing exoplanet and stellar data in an immersive 3D environment. It features:
- Automated data collection from NASA, Gaia, SIMBAD, and more
- Efficient data processing and storage (Parquet, HDF5)
- Desktop 3D visualization (Python + Ursina + OpenGL)
- Web-based 3D portal (React + Three.js)
- Modular, Podman-based architecture with GPU support

---

## Directory Structure
```
cosmic_explorer/
  data/                # All data files (mounted as Podman volume)
    raw/               # Raw downloaded data
    processed/         # Cleaned/processed data
  scripts/             # Data collection and processing scripts
    collect_data.py    # Collects data from APIs
    process_data.py    # Cleans/transforms/saves data
    tess_processing_template.py # (Future) TESS raw data processing
  desktop_app/         # Ursina/OpenGL 3D desktop app
  web_portal/          # React + Three.js web app
  requirements.txt     # Python dependencies
  Containerfile.data   # Data processing container
  Containerfile.desktop # Desktop app container
  Containerfile.web    # Web portal container
  podman-compose.yml   # Orchestrates all containers
  podman_commands.txt  # Podman command reference
  rebuild-podman.ps1   # PowerShell rebuild script
  README.md            # This file
```

---

## Prerequisites
- **NVIDIA GPU** with drivers installed (for data processing and desktop app)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) (for GPU support)
- [Podman](https://podman.io/getting-started/installation) and [podman-compose](https://github.com/containers/podman-compose)
- (For desktop app GUI) X11 server (Linux) or WSL2 GUI (Windows)

---

## Quick Start

### 1. Build All Containers
```sh
podman-compose build
```

### 2. Collect Data (Run Data Service)
```sh
podman-compose run --rm data_service
```

### 3. Process Data
```sh
podman-compose run --rm data_service python3 scripts/process_data.py
```

### 4. Run Desktop 3D App (with GPU and GUI)
```sh
# Linux (with X11)
xhost +local:podman
podman-compose run --rm \
  -e DISPLAY=$DISPLAY \
  desktop_app
```

### 5. Run Web Portal
```sh
podman-compose up web_portal
# Visit http://localhost:3000
```

### Alternative: Use PowerShell Script (Windows)
```powershell
# Build all services
.\rebuild-podman.ps1

# Or build specific service
.\rebuild-podman.ps1 data_service
```

### 6. Test GPU Access
```sh
# Test GPU access in containers
podman-compose run --rm data_service python3 test_gpu.py

# Quick GPU check
podman-compose run --rm data_service nvidia-smi
```

---

## GPU Support
- All containers that require GPU (data_service, desktop_app) are configured for NVIDIA GPUs.
- Podman automatically handles GPU device access through device mapping and cgroup rules.
- For desktop GUI, ensure X11 or WSL2 GUI is set up.
- GPU access is lighter on system resources compared to Docker's approach.

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
- If you encounter issues with GPU access, check your NVIDIA driver and ensure Podman can access GPU devices.
- For desktop GUI issues, verify X11/WSL2 GUI configuration.
- Podman runs rootless by default, which reduces system load but may require additional setup for GPU access.
- Check `podman_commands.txt` for additional Podman-specific commands and troubleshooting tips.

---

## License
MIT License 