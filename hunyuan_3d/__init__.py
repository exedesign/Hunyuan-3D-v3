"""
ComfyUI Tencent Hunyuan 3D Node Implementation
"""

from .nodes import (
    HunyuanTextTo3DNode,
    HunyuanImageTo3DNode,
    HunyuanConfigNode
)

from .batch_nodes import (
    HunyuanBatchImageTo3DNode
)

from .preview_nodes import (
    Hunyuan3DPreviewNode,
    HunyuanBatchPreviewNode
)

# Node class mappings for ComfyUI registration
NODE_CLASS_MAPPINGS = {
    "HunyuanTextTo3D": HunyuanTextTo3DNode,
    "HunyuanImageTo3D": HunyuanImageTo3DNode,
    "HunyuanConfig": HunyuanConfigNode,
    "HunyuanBatchImageTo3D": HunyuanBatchImageTo3DNode,
    "Hunyuan3DPreview": Hunyuan3DPreviewNode,
    "HunyuanBatchPreview": HunyuanBatchPreviewNode,
}

# Display names for the ComfyUI interface
NODE_DISPLAY_NAME_MAPPINGS = {
    "HunyuanTextTo3D": "Hunyuan Text to 3D",
    "HunyuanImageTo3D": "Hunyuan Image to 3D",
    "HunyuanConfig": "Hunyuan Config",
    "HunyuanBatchImageTo3D": "Hunyuan Batch Image to 3D",
    "Hunyuan3DPreview": "Hunyuan 3D Model Preview",
    "HunyuanBatchPreview": "Hunyuan Batch Model Preview"
}