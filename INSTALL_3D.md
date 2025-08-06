# 🌌 Installation Guide for 3D Cosmic Worlds

## Prerequisites

- **Python 3.8+** (required for all components)
- **Node.js 16+** and **npm** (required for web portal)
- **Git** (for cloning and updates)

## 🚀 Quick Installation

### 1. Install Python Dependencies

For the **desktop app** and **world generator**:
```bash
pip install ursina pandas numpy
```

For **data processing** (if you want to regenerate data):
```bash
pip install astropy astroquery requests beautifulsoup4 h5py
```

### 2. Install Web Portal Dependencies

```bash
cd web_portal
npm install
```

## 🎯 Verify Installation

### Test the Launcher
```bash
python launch_3d_world.py stats
```

You should see cosmic data statistics displayed.

### Test Desktop App (if Ursina installed)
```bash
python launch_3d_world.py desktop
```

### Test Web Portal (if Node.js installed)
```bash
python launch_3d_world.py web
```

## 📦 Individual Component Installation

### Desktop App Only
```bash
pip install ursina
python desktop_app/cosmic_explorer.py
```

### Web Portal Only
```bash
cd web_portal
npm install
npm start
```

### World Generator Only
```bash
pip install pandas numpy
python scripts/generate_3d_world.py --format all
```

## 🔧 Troubleshooting

### Common Issues

#### "No module named 'ursina'"
```bash
pip install ursina
```

#### "npm: command not found"
Install Node.js from https://nodejs.org/

#### "Cannot find module 'three'"
```bash
cd web_portal
npm install
```

#### Desktop app opens then closes immediately
This is normal - Ursina creates a window that stays open until you close it.

### Performance Issues

#### Desktop app is slow
- Reduce the number of stars rendered by editing `stars[:200]` in `cosmic_explorer.py`
- Lower the background star count by reducing `range(1000)` in `create_starfield()`

#### Web portal is laggy
- The web version is limited to 500 main stars and 10,000 background stars for performance
- Try closing other browser tabs
- Use a modern browser with WebGL support

## 🌟 Recommended Setup

For the **best experience**:

1. **Install both versions**:
   ```bash
   pip install ursina pandas numpy
   cd web_portal && npm install
   ```

2. **Use the launcher**:
   ```bash
   python launch_3d_world.py
   ```

3. **Desktop app** for high-performance exploration
4. **Web portal** for sharing and cross-platform access

## 📊 System Requirements

### Minimum Requirements
- **CPU**: Any modern processor
- **RAM**: 4GB minimum, 8GB recommended
- **GPU**: Integrated graphics sufficient
- **Storage**: 500MB for full installation

### Recommended Requirements
- **CPU**: Multi-core processor
- **RAM**: 8GB or more
- **GPU**: Dedicated graphics card for best performance
- **Storage**: 1GB free space

## 🔄 Updating

To update the 3D worlds with fresh data:
```bash
python launch_3d_world.py generate
```

This will regenerate all visualization files with the latest processed cosmic data.

---

**Ready to explore the cosmos! 🚀✨**
