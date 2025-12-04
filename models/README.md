# Models Directory

This directory stores the generated 3D model files.

## File Format
Generated models are saved in GLB format, which is widely supported by 3D software and viewers.

## File Naming
Files are automatically named based on:
- Text prompt (for Text-to-3D)
- Timestamp
- Content hash for uniqueness

Example: `cute_robot_toy_a1b2c3d4_1735776000.glb`

## Automatic Cleanup
Files in this directory are automatically cleaned up:
- Files older than 24 hours are removed
- Maximum of 50 files are kept
- Cleanup runs automatically during extension operation

## Manual Management
You can:
- Browse and open model files with any 3D viewer
- Copy important models to a permanent location
- Delete old files manually if needed

## Supported Viewers
GLB files can be opened with:
- Blender
- Windows 3D Viewer
- Online viewers (like gltf-viewer.donmccurdy.com)
- Most modern browsers with WebGL support