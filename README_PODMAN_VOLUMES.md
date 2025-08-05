# Podman Volume Setup for Cosmic Explorer

This setup allows you to modify **Python files**, configuration files, and code without rebuilding Podman containers.

## 🚀 Quick Start

### Running Services (No Rebuild Required)
```bash
# Run data collection
podman-compose run --rm data_service

# Run desktop app
podman-compose run --rm desktop_app

# Run web portal
podman-compose up web_portal
```

### Rebuilding When Needed
```bash
# Rebuild all services
.\rebuild-podman.ps1

# Rebuild specific service
.\rebuild-podman.ps1 data_service
.\rebuild-podman.ps1 desktop_app
.\rebuild-podman.ps1 web_portal
```

## 📁 Volume Mounts

The following files/directories are mounted as volumes:

### Data Service (`data_service`)
- `./scripts/` → `/workspace/scripts/` (read-only) **← Python files here**
- `./desktop_app/` → `/workspace/desktop_app/` (read-only) **← Python files here**
- `./requirements.txt` → `/workspace/requirements.txt/` (read-only)
- `./podman-compose.yml` → `/workspace/podman-compose.yml/` (read-only)
- `./Containerfile.data` → `/workspace/Containerfile.data/` (read-only)

### Desktop App (`desktop_app`)
- `./desktop_app/` → `/workspace/desktop_app/` (read-only) **← Python files here**
- `./scripts/` → `/workspace/scripts/` (read-only) **← Python files here**
- `./requirements.txt` → `/workspace/requirements.txt/` (read-only)
- `./podman-compose.yml` → `/workspace/podman-compose.yml/` (read-only)
- `./Containerfile.desktop` → `/workspace/Containerfile.desktop/` (read-only)

### Web Portal (`web_portal`)
- `./web_portal/` → `/app/web_portal/` (read-only)
- `./package.json` → `/app/package.json/` (read-only)
- `./podman-compose.yml` → `/app/podman-compose.yml/` (read-only)
- `./Containerfile.web` → `/app/Containerfile.web/` (read-only)

## 🔧 What You Can Modify Without Rebuilding

### ✅ **NO REBUILD REQUIRED** (Most Changes)
- **Python Scripts**: `scripts/collect_data.py`, `scripts/process_data.py`, etc.
- **Python App Code**: `desktop_app/cosmic_explorer.py`, `desktop_app/data_loader.py`
- **Python Requirements**: `requirements.txt` (automatically reinstalled)
- **Web Portal**: `web_portal/src/`, `web_portal/public/`
- **Package.json**: `web_portal/package.json` (automatically reinstalled)
- **Podman Compose**: `podman-compose.yml`

### 🔄 Rebuild Required
- **Containerfiles**: `Containerfile.data`, `Containerfile.desktop`, `Containerfile.web`
- **Base Images**: Changes to FROM statements
- **System Dependencies**: apt-get install commands
- **Build Process**: Changes to RUN commands

## 🐍 Python File Changes (NO REBUILD NEEDED!)

### **Key Point**: Python files are mounted as volumes and changes take effect immediately!

```bash
# Edit any Python file
code scripts/collect_data.py
code desktop_app/cosmic_explorer.py
code scripts/process_data.py

# Run immediately - changes are live!
podman-compose run --rm data_service
podman-compose run --rm desktop_app
```

### Test Python Changes
```bash
# Test the volume mount functionality
podman-compose run --rm data_service python3 test_python_changes.py
```

## 🛠️ Development Workflow

### 1. Modify Python Code
```bash
# Edit Python files
code scripts/collect_data.py
code desktop_app/cosmic_explorer.py
code scripts/process_data.py
```

### 2. Run Without Rebuild
```bash
# Test Python changes immediately
podman-compose run --rm data_service
podman-compose run --rm desktop_app
```

### 3. Rebuild Only When Necessary
```bash
# Only rebuild if you changed Containerfiles or system dependencies
.\rebuild-podman.ps1 data_service
```

## 🔍 Troubleshooting

### Python Changes Not Reflected
If your Python changes aren't reflected:
1. **Check volume mounts**: Ensure the file is in the correct mounted directory
2. **Restart container**: `podman-compose run --rm [service_name]`
3. **Check Python path**: The container automatically sets `PYTHONPATH` to include mounted directories
4. **Verify file permissions**: Ensure the file is readable
5. **SELinux context**: On SELinux systems, use `:Z` flag for volume mounts

### Dependencies Not Updated
For Python dependencies:
- The container automatically reinstalls `requirements.txt` on startup
- Check the logs for any installation errors
- Dependencies are cached - only reinstalled when `requirements.txt` changes

### Permission Issues
On Windows, ensure Podman has access to your project directory:
1. Use Windows-style paths with Podman Desktop
2. Ensure your user has access to the project directory
3. Consider using `podman unshare` for rootless containers

### SELinux Issues (Linux)
If you encounter SELinux permission issues:
```bash
# Use :Z flag for proper SELinux labeling
podman run -v ./data:/workspace/data:Z your_image
```

## 📝 Examples

### Modifying Python Data Collection Script
```bash
# Edit the Python script
code scripts/collect_data.py

# Run immediately (no rebuild needed)
podman-compose run --rm data_service
```

### Modifying Python Desktop App
```bash
# Edit the Python app
code desktop_app/cosmic_explorer.py

# Run immediately (no rebuild needed)
podman-compose run --rm desktop_app
```

### Adding New Python Dependencies
```bash
# Edit requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Run immediately (dependencies auto-installed)
podman-compose run --rm data_service
```

### Testing Python Changes
```bash
# Create a test Python file
echo 'print("Hello from mounted Python file!")' > test.py

# Run it in the container
podman-compose run --rm data_service python3 test.py
```

## 🎯 Benefits

1. **Instant Python Updates**: Python file changes take effect immediately
2. **No Rebuild Time**: Most changes don't require rebuilding
3. **Live Development**: See Python changes in real-time
4. **Automatic Dependencies**: Python requirements auto-install on changes
5. **Selective Rebuilding**: Only rebuild when absolutely necessary
6. **Full Python Support**: All Python files, modules, and packages work seamlessly
7. **Lower Resource Usage**: Podman's rootless approach uses fewer system resources
8. **Better Security**: Rootless containers provide better isolation and security
