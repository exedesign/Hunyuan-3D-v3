"""
Batch Processing Nodes for Hunyuan3D v3
"""

import os
import glob
from pathlib import Path
from typing import Dict, Any, Tuple, List
import asyncio
import base64
import io
from PIL import Image

from .api_client import TencentCloudAPIClient
from .file_manager import FileManager


class HunyuanBatchImageTo3DNode:
    """
    Batch Image to 3D generation - processes entire folder automatically
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # Get available folders from input directory
        try:
            import folder_paths
            input_dir = folder_paths.get_input_directory()
            # List all subdirectories
            folders = ["input"]  # Default
            if os.path.exists(input_dir):
                subdirs = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
                if subdirs:
                    folders.extend(subdirs)
        except:
            folders = ["input"]
        
        return {
            "required": {
                "config": ("HUNYUAN_CONFIG",),
                "file_pattern": ("STRING", {"default": "*.png", "multiline": False}),
                "output_folder": ("STRING", {"default": "batch_output", "multiline": False}),
                "enable_pbr": ("BOOLEAN", {"default": False, "label_on": "PBR ON", "label_off": "PBR OFF"}),
                "face_count": ("INT", {"default": 500000, "min": 40000, "max": 1500000, "step": 10000}),
                "generate_type": (["Normal", "LowPoly", "Geometry", "Sketch"], {"default": "Normal"}),
                "polygon_type": (["triangle", "quadrilateral"], {"default": "triangle"}),
                "max_wait_time": ("INT", {"default": 600, "min": 60, "max": 3600, "step": 60}),
                "max_images": ("INT", {"default": 10, "min": 1, "max": 100, "step": 1})
            },
            "optional": {
                "input_folder": ("STRING", {"default": "input", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("batch_summary", "model_paths")
    FUNCTION = "batch_generate"
    OUTPUT_NODE = True
    CATEGORY = "Hunyuan3D/v3"
    
    def __init__(self):
        self.file_manager = FileManager()
    
    def _get_image_files(self, input_folder: str, pattern: str, max_images: int) -> List[Path]:
        """Get list of image files from folder"""
        try:
            import folder_paths
            input_dir = folder_paths.get_input_directory()
            
            if input_folder == "input":
                search_path = input_dir
            else:
                search_path = os.path.join(input_dir, input_folder)
            
            # Search for files matching pattern
            pattern_path = os.path.join(search_path, pattern)
            files = glob.glob(pattern_path)
            
            # Sort and limit
            files = sorted(files)[:max_images]
            return [Path(f) for f in files]
        except Exception as e:
            print(f"❌ Error getting image files: {e}")
            return []
    
    def _get_output_path(self, output_folder: str, filename: str) -> str:
        """Get full output path for GLB file"""
        try:
            import folder_paths
            output_dir = folder_paths.get_output_directory()
            
            # Create subfolder
            full_output_dir = os.path.join(output_dir, output_folder)
            os.makedirs(full_output_dir, exist_ok=True)
            
            return os.path.join(full_output_dir, filename)
        except Exception as e:
            print(f"❌ Error creating output path: {e}")
            # Fallback to models/3d_models
            return self.file_manager.get_output_path(filename)
    
    def _image_to_base64(self, image_path: Path) -> str:
        """Convert image file to base64"""
        image = Image.open(image_path)
        
        # Resize if too large
        max_size = 2048
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    async def _process_single_image(self, client: TencentCloudAPIClient, image_path: Path,
                                    output_folder: str, enable_pbr: bool, face_count: int, 
                                    generate_type: str, polygon_type: str, max_wait_time: int) -> Tuple[str, bool, str]:
        """Process single image and return (path, success, message)"""
        try:
            print(f"\n{'='*60}")
            print(f"📷 Processing: {image_path.name}")
            print(f"{'='*60}")
            
            # Convert to base64
            image_data = self._image_to_base64(image_path)
            
            # Submit task
            print("📤 Submitting to API...")
            job_id = await client.image_to_3d(
                image_data, enable_pbr, face_count, generate_type, polygon_type
            )
            
            if not job_id:
                return (str(image_path), False, "Failed to get JobId")
            
            print(f"✅ Job ID: {job_id}")
            
            # Wait for completion
            def progress_callback(percent, message):
                print(f"\r⏳ {message} ({percent:.1f}%)", end='', flush=True)
            
            result = await client.wait_for_task_completion(
                job_id, max_wait_time, progress_callback=progress_callback
            )
            print()
            
            # Get GLB URL
            result_files = result.get("result_urls", [])
            glb_url = None
            for file_info in result_files:
                if file_info.get("type") == "GLB":
                    glb_url = file_info.get("url")
                    break
            
            if not glb_url:
                return (str(image_path), False, "No GLB file in results")
            
            # Download to custom output folder
            output_filename = f"{image_path.stem}_3d.glb"
            output_path = self._get_output_path(output_folder, output_filename)
            
            print(f"⬇️  Downloading...")
            await client.download_model(glb_url, output_path)
            
            print(f"✅ Saved: {output_path}")
            return (output_path, True, "Success")
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error: {error_msg}")
            return (str(image_path), False, error_msg)
    
    def batch_generate(self, config: Dict[str, str], file_pattern: str,
                      output_folder: str, enable_pbr: bool, face_count: int, 
                      generate_type: str, polygon_type: str, max_wait_time: int, 
                      max_images: int, input_folder: str = "input") -> Tuple[str]:
        """Batch process images from folder"""
        
        print("\n" + "="*60)
        print("🚀 HUNYUAN3D BATCH PROCESSING")
        print("="*60)
        
        # Get image files
        image_files = self._get_image_files(input_folder, file_pattern, max_images)
        
        if not image_files:
            error_msg = f"❌ No images found in '{input_folder}' matching '{file_pattern}'"
            print(error_msg)
            return (error_msg,)
        
        print(f"📁 Found {len(image_files)} images")
        print(f"📂 Output folder: {output_folder}")
        print(f"⚙️  Settings: {generate_type}, {face_count} faces, PBR: {enable_pbr}")
        print()
        
        # Initialize client
        client = TencentCloudAPIClient(
            secret_id=config["secret_id"],
            secret_key=config["secret_key"],
            region=config["region"]
        )
        
        # Process images
        results = []
        successful = 0
        failed = 0
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                
            for idx, image_path in enumerate(image_files, 1):
                print(f"\n[{idx}/{len(image_files)}]")
                
                result = loop.run_until_complete(
                    self._process_single_image(
                        client, image_path, output_folder, enable_pbr, face_count,
                        generate_type, polygon_type, max_wait_time
                    )
                )
                
                results.append(result)
                if result[1]:  # Success
                    successful += 1
                else:
                    failed += 1
                    
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            for idx, image_path in enumerate(image_files, 1):
                print(f"\n[{idx}/{len(image_files)}]")
                
                result = loop.run_until_complete(
                    self._process_single_image(
                        client, image_path, output_folder, enable_pbr, face_count,
                        generate_type, polygon_type, max_wait_time
                    )
                )
                
                results.append(result)
                if result[1]:
                    successful += 1
                else:
                    failed += 1
            
            loop.close()
        
        # Generate summary
        import folder_paths
        output_dir = folder_paths.get_output_directory()
        full_output_path = os.path.join(output_dir, output_folder)
        
        summary = f"""
╔══════════════════════════════════════════════════════════╗
║           BATCH PROCESSING COMPLETE                      ║
╚══════════════════════════════════════════════════════════╝

✅ Successful: {successful}
❌ Failed: {failed}
📊 Total: {len(image_files)}
📂 Output: {full_output_path}

RESULTS:
"""
        
        # Collect successful model paths
        model_paths = []
        for path, success, message in results:
            status = "✅" if success else "❌"
            filename = Path(path).name
            summary += f"\n{status} {filename}: {message}"
            if success:
                model_paths.append(path)
        
        print("\n" + summary)
        
        # Return paths as newline-separated string for compatibility
        paths_string = "\n".join(model_paths) if model_paths else ""
        
        return {"ui": {"text": [summary]}, "result": (summary, paths_string)}
