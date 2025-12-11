"""
ComfyUI Custom Nodes for Hunyuan 3D v3
"""

import os
import asyncio
import base64
import io
import json
import time
from typing import Dict, Any, Tuple, Optional
import numpy as np
from PIL import Image
import logging

from .api_client import TencentCloudAPIClient
from .file_manager import FileManager

logger = logging.getLogger(__name__)


class HunyuanConfigNode:
    """
    Configuration node for Hunyuan 3D API credentials and settings
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "secret_id": ("STRING", {
                    "multiline": False,
                    "placeholder": "Tencent Cloud Secret ID"
                }),
                "secret_key": ("STRING", {
                    "multiline": False,
                    "placeholder": "Tencent Cloud Secret Key"
                }),
                "region": (["ap-singapore"], {
                    "default": "ap-singapore"
                })
            }
        }
    
    RETURN_TYPES = ("HUNYUAN_CONFIG",)
    RETURN_NAMES = ("config",)
    FUNCTION = "create_config"
    CATEGORY = "Hunyuan3D/v3"
    
    def create_config(self, secret_id: str, secret_key: str, region: str):
        """Create configuration object"""
        if not secret_id.strip():
            raise ValueError("Secret ID cannot be empty")
        if not secret_key.strip():
            raise ValueError("Secret Key cannot be empty")
            
        config = {
            "secret_id": secret_id.strip(),
            "secret_key": secret_key.strip(),
            "region": region
        }
        
        return (config,)


class HunyuanTextTo3DNode:
    """
    Text to 3D generation node using Hunyuan 3D API
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config": ("HUNYUAN_CONFIG",),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A cute robot toy",
                    "placeholder": "Describe the 3D object you want to generate..."
                }),
                "enable_pbr": ("BOOLEAN", {
                    "default": False,
                    "label_on": "PBR Enabled",
                    "label_off": "PBR Disabled"
                }),
                "face_count": ("INT", {
                    "default": 500000,
                    "min": 40000,
                    "max": 1500000,
                    "step": 10000
                }),
                "generate_type": (["Normal", "LowPoly", "Geometry", "Sketch"], {
                    "default": "Normal"
                }),
                "polygon_type": (["triangle", "quadrilateral"], {
                    "default": "triangle"
                }),
                "max_wait_time": ("INT", {
                    "default": 600,
                    "min": 60,
                    "max": 3600,
                    "step": 60
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model_path",)
    FUNCTION = "generate_3d"
    OUTPUT_NODE = True
    CATEGORY = "Hunyuan3D/v3"
    OUTPUT_IS_LIST = (False,)
    
    def __init__(self):
        self.file_manager = FileManager()
    
    def generate_3d(self, config: Dict[str, str], prompt: str, enable_pbr: bool, 
                   face_count: int, generate_type: str, polygon_type: str, max_wait_time: int) -> Tuple[str]:
        """
        Generate 3D model from text prompt
        
        Args:
            config: API configuration
            prompt: Text description
            enable_pbr: Enable PBR materials
            face_count: Number of faces (40k-1.5M)
            generate_type: Normal/LowPoly/Geometry/Sketch
            polygon_type: triangle/quadrilateral (LowPoly only)
            max_wait_time: Maximum wait time in seconds
        Returns:
            Tuple of (model_path,)
        """
        try:
            # Validate inputs
            if not prompt.strip():
                raise ValueError("Prompt cannot be empty")
            
            # Initialize API client
            client = TencentCloudAPIClient(
                secret_id=config["secret_id"],
                secret_key=config["secret_key"],
                region=config["region"]
            )
            
            # Run async generation
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import nest_asyncio
                    nest_asyncio.apply()
                    result = loop.run_until_complete(
                        self._async_generate(client, prompt, enable_pbr, face_count, 
                                           generate_type, polygon_type, max_wait_time)
                    )
                else:
                    result = loop.run_until_complete(
                        self._async_generate(client, prompt, enable_pbr, face_count,
                                           generate_type, polygon_type, max_wait_time)
                    )
                return result
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self._async_generate(client, prompt, enable_pbr, face_count,
                                           generate_type, polygon_type, max_wait_time)
                    )
                    return result
                finally:
                    loop.close()
                
        except Exception as e:
            logger.error(f"Text-to-3D generation failed: {e}")
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return (error_msg,)
    
    async def _async_generate(self, client: TencentCloudAPIClient, prompt: str,
                             enable_pbr: bool, face_count: int, generate_type: str,
                             polygon_type: str, max_wait_time: int) -> Tuple[str]:
        """Async 3D model generation from text"""
        try:
            # Submit task
            logger.info(f"Submitting text-to-3D task: {prompt}")
            job_id = await client.text_to_3d(prompt, enable_pbr, face_count, generate_type, polygon_type)
            
            if not job_id:
                raise Exception("Failed to get JobId from API response")
            
            logger.info(f"Task submitted with ID: {job_id}")
            print(f"🚀 Job ID: {job_id}")
            
            # Wait for completion with progress tracking
            def update_progress(percent, message):
                print(f"\r[Text-to-3D] {message} ({percent:.1f}%)", end='', flush=True)
            
            final_result = await client.wait_for_task_completion(
                job_id, 
                max_wait_time,
                progress_callback=update_progress
            )
            print()  # New line after progress
            
            # Get download URLs from result
            result_files = final_result.get("result_urls", [])
            if not result_files:
                raise Exception("No result files in task result")
            
            # Get GLB file URL
            download_url = None
            for file_info in result_files:
                if file_info.get("type") == "GLB":
                    download_url = file_info.get("url")
                    break
            
            if not download_url:
                raise Exception("No GLB file found in results")
            
            # Save to output folder
            model_path = await client.download_model(
                download_url,
                self.file_manager.get_output_path(prompt)
            )
            
            print(f"✅ Model saved: {model_path}")
            
            # Return with UI display info
            return {"ui": {"text": [model_path]}, "result": (model_path,)}
            
        except Exception as e:
            logger.error(f"Async generation failed: {e}")
            raise


class HunyuanImageTo3DNode:
    """
    Image to 3D generation node using Hunyuan 3D API
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config": ("HUNYUAN_CONFIG",),
                "image": ("IMAGE",),
                "enable_pbr": ("BOOLEAN", {
                    "default": False,
                    "label_on": "PBR Enabled",
                    "label_off": "PBR Disabled"
                }),
                "face_count": ("INT", {
                    "default": 500000,
                    "min": 40000,
                    "max": 1500000,
                    "step": 10000
                }),
                "generate_type": (["Normal", "LowPoly", "Geometry", "Sketch"], {
                    "default": "Normal"
                }),
                "polygon_type": (["triangle", "quadrilateral"], {
                    "default": "triangle"
                }),
                "max_wait_time": ("INT", {
                    "default": 600,
                    "min": 60,
                    "max": 3600,
                    "step": 60
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model_path",)
    FUNCTION = "generate_3d"
    OUTPUT_NODE = True
    CATEGORY = "Hunyuan3D/v3"
    OUTPUT_IS_LIST = (False,)
    
    def __init__(self):
        self.file_manager = FileManager()
    
    def _tensor_to_base64(self, tensor) -> str:
        """Convert ComfyUI image tensor to base64"""
        # ComfyUI image format: [batch, height, width, channels] with values [0, 1]
        # Convert torch.Tensor to numpy if needed
        if hasattr(tensor, 'cpu'):
            tensor = tensor.cpu().numpy()
        
        if len(tensor.shape) == 4:
            tensor = tensor[0]
        
        # Convert to PIL Image
        image_np = (tensor * 255).astype(np.uint8)
        image = Image.fromarray(image_np)
        
        # Convert to RGB if needed
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to reasonable size
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to base64 with JPEG compression
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85, optimize=True)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Check size
        size_mb = len(image_base64) / (1024 * 1024)
        if size_mb > 4:
            print(f"⚠️  Warning: Base64 size {size_mb:.2f}MB - may exceed API limit")
        
        return image_base64
    
    def generate_3d(self, config: Dict[str, str], image, enable_pbr: bool,
                   face_count: int, generate_type: str, polygon_type: str, max_wait_time: int) -> Tuple[str]:
        """
        Generate 3D model from image
        
        Args:
            config: API configuration
            image: Input image tensor
            enable_pbr: Enable PBR materials
            face_count: Number of faces (40k-1.5M)
            generate_type: Normal/LowPoly/Geometry/Sketch
            polygon_type: triangle/quadrilateral (LowPoly only)
        Returns:
            Tuple of (model_path,)
        """
        try:
            # Convert image tensor to base64
            image_data = self._tensor_to_base64(image)
            
            # Initialize API client
            client = TencentCloudAPIClient(
                secret_id=config["secret_id"],
                secret_key=config["secret_key"],
                region=config["region"]
            )
            
            # Run async generation
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import nest_asyncio
                    nest_asyncio.apply()
                    result = loop.run_until_complete(
                        self._async_generate(client, image_data, enable_pbr, face_count,
                                           generate_type, polygon_type, max_wait_time)
                    )
                else:
                    result = loop.run_until_complete(
                        self._async_generate(client, image_data, enable_pbr, face_count,
                                           generate_type, polygon_type, max_wait_time)
                    )
                return result
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self._async_generate(client, image_data, enable_pbr, face_count,
                                           generate_type, polygon_type, max_wait_time)
                    )
                    return result
                finally:
                    loop.close()
                
        except Exception as e:
            logger.error(f"Image-to-3D generation failed: {e}")
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return (error_msg,)
    
    async def _async_generate(self, client: TencentCloudAPIClient, image_data: str,
                             enable_pbr: bool, face_count: int, generate_type: str,
                             polygon_type: str, max_wait_time: int) -> Tuple[str]:
        """Async 3D model generation from image"""
        try:
            # Submit task
            logger.info("Submitting image-to-3D task")
            job_id = await client.image_to_3d(image_data, enable_pbr, face_count, generate_type, polygon_type)
            
            if not job_id:
                raise Exception("Failed to get JobId from API response")
            
            logger.info(f"Task submitted with ID: {job_id}")
            print(f"🚀 Job ID: {job_id}")
            
            # Wait for completion with progress tracking
            def update_progress(percent, message):
                print(f"\r[Image-to-3D] {message} ({percent:.1f}%)", end='', flush=True)
            
            final_result = await client.wait_for_task_completion(
                job_id,
                max_wait_time,
                progress_callback=update_progress
            )
            print()  # New line after progress
            
            # Get download URLs from result
            result_files = final_result.get("result_urls", [])
            if not result_files:
                raise Exception("No result files in task result")
            
            # Get GLB file URL
            download_url = None
            for file_info in result_files:
                if file_info.get("type") == "GLB":
                    download_url = file_info.get("url")
                    break
            
            if not download_url:
                raise Exception("No GLB file found in results")
            
            # Save to output folder
            model_path = await client.download_model(
                download_url,
                self.file_manager.get_output_path("image_to_3d")
            )
            
            print(f"✅ Model saved: {model_path}")
            
            # Return with UI display info
            return {"ui": {"text": [model_path]}, "result": (model_path,)}
            
        except Exception as e:
            logger.error(f"Async generation failed: {e}")
            raise
