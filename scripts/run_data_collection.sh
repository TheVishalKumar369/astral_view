#!/bin/bash
# Wrapper script to run data collection, processing, and integration with virtual display

# Start virtual framebuffer
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
XVFB_PID=$!

# Wait a moment for Xvfb to start
sleep 2

# Run the data collection script
python3 -u scripts/collect_data.py

# # Run the data processing script
python3 -u scripts/process_data.py

# # Run the data integration script
python3 -u scripts/integrate_cosmic_data.py

# Clean up virtual framebuffer
kill $XVFB_PID 2>/dev/null || true