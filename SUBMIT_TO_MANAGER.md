# How to Add to ComfyUI-Manager

Follow these steps to get your plugin listed in ComfyUI-Manager:

## Step 1: Fork ComfyUI-Manager Repository

1. Go to https://github.com/ltdrdata/ComfyUI-Manager
2. Click **Fork** button (top right)

## Step 2: Add Your Plugin Entry

1. In your forked repo, navigate to: `custom-node-list.json`
2. Click **Edit** (pencil icon)
3. Find a good position in the JSON array (alphabetically is best)
4. Add this entry:

```json
{
    "author": "exedesign",
    "title": "ComfyUI-Hunyuan3D-v3",
    "id": "hunyuan3d-v3",
    "reference": "https://github.com/exedesign/Hunyuan-3D-v3",
    "files": [
        "https://github.com/exedesign/Hunyuan-3D-v3"
    ],
    "install_type": "git-clone",
    "description": "Text-to-3D and Image-to-3D generation using Tencent Cloud Hunyuan 3D Global API. Supports PBR materials, face count control (40K-1.5M faces), and multiple generation types (Normal/LowPoly/Geometry/Sketch). Outputs industry-standard GLB format. Requires Tencent Cloud account with API access.",
    "nodename_pattern": "Hunyuan",
    "tags": ["3D", "generation", "text-to-3d", "image-to-3d", "hunyuan", "tencent"]
}
```

**Important:** Add a comma after the previous entry, and make sure JSON syntax is valid!

## Step 3: Commit Changes

1. Scroll down to **Commit changes**
2. Title: `Add ComfyUI-Hunyuan3D-v3 plugin`
3. Description: `Text-to-3D and Image-to-3D generation using Tencent Hunyuan 3D Global API v3`
4. Click **Commit changes**

## Step 4: Create Pull Request

1. Go to your forked repository main page
2. Click **Contribute** → **Open pull request**
3. Title: `Add ComfyUI-Hunyuan3D-v3 - Tencent Hunyuan 3D Global API`
4. Description:
   ```
   This PR adds support for ComfyUI-Hunyuan3D-v3, a plugin that provides:
   
   - Text-to-3D generation
   - Image-to-3D generation
   - PBR material support
   - Face count control (40K-1.5M)
   - Multiple generation types (Normal/LowPoly/Geometry/Sketch)
   - Global API support (ap-singapore region)
   
   Repository: https://github.com/exedesign/Hunyuan-3D-v3
   License: MIT
   ```
5. Click **Create pull request**

## Step 5: Wait for Review

- ComfyUI-Manager maintainers will review your PR
- Usually takes 1-7 days
- They may request changes or ask questions
- Once approved, your plugin will appear in ComfyUI-Manager!

## Alternative: Manual Installation (Users can use this now)

Users can install immediately without waiting for PR approval:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/exedesign/Hunyuan-3D-v3.git
cd Hunyuan-3D-v3
pip install -r requirements.txt
```

Then restart ComfyUI.
