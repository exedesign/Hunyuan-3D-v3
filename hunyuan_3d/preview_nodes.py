"""
Preview nodes for 3D models
"""
import os
from typing import Dict, Tuple


class Hunyuan3DPreviewNode:
    """
    Preview GLB 3D model in ComfyUI
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_path": ("STRING", {"forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model_path",)
    FUNCTION = "preview_model"
    OUTPUT_NODE = True
    CATEGORY = "Hunyuan3D/v3"
    
    def preview_model(self, model_path: str) -> Dict:
        """Preview 3D model"""
        
        if not model_path or not os.path.exists(model_path):
            return {
                "ui": {"text": [f"❌ Model file not found: {model_path}"]}, 
                "result": (model_path,)
            }
        
        # Get file info
        file_size = os.path.getsize(model_path)
        file_size_mb = file_size / (1024 * 1024)
        
        preview_text = f"""
╔══════════════════════════════════════════════════════════╗
║                  3D MODEL PREVIEW                        ║
╚══════════════════════════════════════════════════════════╝

📁 File: {os.path.basename(model_path)}
📂 Path: {model_path}
📊 Size: {file_size_mb:.2f} MB

💡 To view this model:
   • Use a GLB viewer extension in ComfyUI
   • Open with Blender
   • Use online viewer: https://gltf-viewer.donmccurdy.com/
"""
        
        return {
            "ui": {
                "text": [preview_text],
                "glb_path": [model_path]  # Some 3D preview nodes might use this
            }, 
            "result": (model_path,)
        }


class HunyuanBatchPreviewNode:
    """
    Preview multiple GLB models from batch processing
    Displays one model at a time with navigation
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_paths": ("STRING", {"forceInput": True}),
                "model_index": ("INT", {"default": 0, "min": 0, "max": 99, "step": 1}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model_path",)
    FUNCTION = "preview_batch_model"
    OUTPUT_NODE = True
    CATEGORY = "Hunyuan3D/v3"
    
    def preview_batch_model(self, model_paths: str, model_index: int) -> Dict:
        """Preview a specific model from batch results"""
        
        if not model_paths:
            return {
                "ui": {"text": ["❌ No model paths provided"]}, 
                "result": ("",)
            }
        
        # Split paths (newline-separated)
        paths = [p.strip() for p in model_paths.split('\n') if p.strip()]
        
        if not paths:
            return {
                "ui": {"text": ["❌ No valid model paths found"]}, 
                "result": ("",)
            }
        
        # Clamp index
        model_index = max(0, min(model_index, len(paths) - 1))
        selected_path = paths[model_index]
        
        # Check if file exists
        if not os.path.exists(selected_path):
            return {
                "ui": {"text": [f"❌ Model file not found: {selected_path}"]}, 
                "result": (selected_path,)
            }
        
        # Get file info
        file_size = os.path.getsize(selected_path)
        file_size_mb = file_size / (1024 * 1024)
        
        preview_text = f"""
╔══════════════════════════════════════════════════════════╗
║              BATCH MODEL PREVIEW ({model_index + 1}/{len(paths)})              ║
╚══════════════════════════════════════════════════════════╝

📁 File: {os.path.basename(selected_path)}
📂 Path: {selected_path}
📊 Size: {file_size_mb:.2f} MB

🔢 Model Index: {model_index} of {len(paths) - 1}
📋 Total Models: {len(paths)}

💡 Navigation:
   • Change 'model_index' parameter to view different models
   • Index 0 = first model, {len(paths) - 1} = last model

🌐 View Online:
   • https://gltf-viewer.donmccurdy.com/
"""
        
        return {
            "ui": {
                "text": [preview_text],
                "glb_path": [selected_path]
            }, 
            "result": (selected_path,)
        }
