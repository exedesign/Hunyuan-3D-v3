"""
ComfyUI Tencent Hunyuan 3D v3 Extension
A custom node extension for ComfyUI that provides Text-to-3D and Image-to-3D capabilities
using Tencent Cloud Hunyuan 3D Global API.
"""

from .hunyuan_3d import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# Version information
__version__ = "3.1.0"
__author__ = "exedesign"
__license__ = "MIT"