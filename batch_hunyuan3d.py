"""
Batch Image to 3D Processing Script for Hunyuan3D v3

This script processes multiple images from a folder and generates 3D models.
Place this in ComfyUI root directory and run:
    python batch_hunyuan3d.py

Requirements:
- ComfyUI-Hunyuan3D-v3 installed
- API credentials configured
"""

import os
import sys
import asyncio
from pathlib import Path

# Add ComfyUI to path
comfy_path = Path(__file__).parent
sys.path.insert(0, str(comfy_path))

# Import Hunyuan3D modules
from custom_nodes.Hunyuan_3D_v3.hunyuan_3d.api_client import TencentCloudAPIClient
from custom_nodes.Hunyuan_3D_v3.hunyuan_3d.file_manager import FileManager

# Configuration
SECRET_ID = "YOUR_SECRET_ID"
SECRET_KEY = "YOUR_SECRET_KEY"
REGION = "ap-singapore"

# Batch settings
INPUT_FOLDER = "input_images"  # Folder with images
OUTPUT_FOLDER = "output_models"  # Where to save 3D models
ENABLE_PBR = False
FACE_COUNT = 500000
GENERATE_TYPE = "Normal"
POLYGON_TYPE = "triangle"
MAX_WAIT_TIME = 600

# Supported image formats
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}


def get_image_files(folder_path):
    """Get all image files from folder"""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Folder not found: {folder_path}")
        return []
    
    images = []
    for file in folder.iterdir():
        if file.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(file)
    
    return sorted(images)


async def process_image(client, file_manager, image_path):
    """Process single image to 3D"""
    try:
        print(f"\n{'='*60}")
        print(f"Processing: {image_path.name}")
        print(f"{'='*60}")
        
        # Load image and convert to base64
        from PIL import Image
        import base64
        import io
        
        image = Image.open(image_path)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Submit task
        print("📤 Submitting to Hunyuan 3D API...")
        job_id = await client.image_to_3d(
            image_base64, 
            ENABLE_PBR, 
            FACE_COUNT, 
            GENERATE_TYPE, 
            POLYGON_TYPE
        )
        
        if not job_id:
            raise Exception("Failed to get JobId")
        
        print(f"✅ Job ID: {job_id}")
        
        # Wait for completion
        def progress_callback(percent, message):
            print(f"\r⏳ Progress: {message} ({percent:.1f}%)", end='', flush=True)
        
        result = await client.wait_for_task_completion(
            job_id,
            MAX_WAIT_TIME,
            progress_callback=progress_callback
        )
        print()  # New line
        
        # Get GLB URL
        result_files = result.get("result_urls", [])
        glb_url = None
        for file_info in result_files:
            if file_info.get("type") == "GLB":
                glb_url = file_info.get("url")
                break
        
        if not glb_url:
            raise Exception("No GLB file in results")
        
        # Download model
        output_filename = f"{image_path.stem}_3d.glb"
        output_path = Path(OUTPUT_FOLDER) / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"⬇️  Downloading model...")
        await client.download_model(glb_url, str(output_path))
        
        print(f"✅ Saved: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error processing {image_path.name}: {e}")
        return None


async def main():
    """Main batch processing function"""
    print("""
╔══════════════════════════════════════════════════════════╗
║      Hunyuan3D v3 - Batch Image to 3D Processor         ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # Check credentials
    if SECRET_ID == "YOUR_SECRET_ID" or SECRET_KEY == "YOUR_SECRET_KEY":
        print("❌ Please configure your API credentials in the script!")
        print("   Edit: SECRET_ID and SECRET_KEY")
        return
    
    # Get image files
    print(f"📁 Scanning folder: {INPUT_FOLDER}")
    images = get_image_files(INPUT_FOLDER)
    
    if not images:
        print(f"❌ No images found in {INPUT_FOLDER}")
        print(f"   Supported formats: {', '.join(IMAGE_EXTENSIONS)}")
        return
    
    print(f"✅ Found {len(images)} images")
    
    # Initialize API client
    print(f"\n🔧 Initializing API client...")
    print(f"   Region: {REGION}")
    print(f"   Settings: {GENERATE_TYPE}, {FACE_COUNT} faces, PBR: {ENABLE_PBR}")
    
    client = TencentCloudAPIClient(SECRET_ID, SECRET_KEY, REGION)
    file_manager = FileManager()
    
    # Process each image
    print(f"\n🚀 Starting batch processing...")
    successful = 0
    failed = 0
    
    for idx, image_path in enumerate(images, 1):
        print(f"\n[{idx}/{len(images)}]")
        result = await process_image(client, file_manager, image_path)
        
        if result:
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Output folder: {OUTPUT_FOLDER}")
    print()


if __name__ == "__main__":
    # Create input folder if not exists
    Path(INPUT_FOLDER).mkdir(exist_ok=True)
    
    # Run batch processing
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
