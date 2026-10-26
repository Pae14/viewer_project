#!/usr/bin/env bash
set -e
source /opt/ros/humble/setup.bash
if [ -f /ros2_ws/install/setup.bash ]; then
    source /ros2_ws/install/setup.bash
fi
export QT_QPA_PLATFORM_PLUGIN_PATH="$(
    python3 -c 'from PyQt6.QtCore import QLibraryInfo; print(QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath))' 2>/dev/null || true
)"
exec "$@"

