"""
ComfyUI Tencent Hunyuan 3D Node Implementation
"""

from .nodes import (
    HunyuanTextTo3DNode,
    HunyuanImageTo3DNode,
    HunyuanConfigNode
)

# Node class mappings for ComfyUI registration
NODE_CLASS_MAPPINGS = {
    "HunyuanTextTo3D": HunyuanTextTo3DNode,
    "HunyuanImageTo3D": HunyuanImageTo3DNode,
    "HunyuanConfig": HunyuanConfigNode,
}

# Display names for the ComfyUI interface
NODE_DISPLAY_NAME_MAPPINGS = {
    "HunyuanTextTo3D": "Hunyuan Text to 3D",
    "HunyuanImageTo3D": "Hunyuan Image to 3D",
    "HunyuanConfig": "Hunyuan Config",
}