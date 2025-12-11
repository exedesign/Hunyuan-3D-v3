# ComfyUI-Hunyuan3D-v3

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/v/release/exedesign/Hunyuan-3D-v3)](https://github.com/exedesign/Hunyuan-3D-v3/releases)

ComfyUI custom node for **Text-to-3D** and **Image-to-3D** generation using **Tencent Cloud Hunyuan 3D Global API v3**.

## Features

-  **Text-to-3D**: Create 3D models from text prompts
-  **Image-to-3D**: Convert images to 3D models
-  **Advanced Options**: PBR materials, face count control (40K-1.5M), generation types
-  **GLB Output**: Industry-standard format
-  **Global API**: ap-singapore region

## Installation

### Via ComfyUI Manager

1. Open ComfyUI Manager
2. Search "Hunyuan 3D"
3. Install & Restart

### Manual

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/exedesign/Hunyuan-3D-v3.git
cd Hunyuan-3D-v3
pip install -r requirements.txt
```

## Setup

1. Get API keys: https://console.intl.cloud.tencent.com/  Access Management  API Keys
2. Activate Hunyuan 3D service (Console  AI Services)
3. Add billing info ( **Paid API**: ~$0.10-0.60 per request)

## Quick Start

```
HunyuanConfig (SecretId, SecretKey)  HunyuanTextTo3D  Preview3D
```

## Parameters

- **enable_pbr**: PBR materials (default: False)
- **face_count**: 40000-1500000 (default: 500000)
- **generate_type**: Normal/LowPoly/Geometry/Sketch
- **polygon_type**: triangle/quadrilateral

## Output

- Format: GLB
- Location: `ComfyUI/models/3d_models/`

## Batch Processing

### Method 1: Python Script (Recommended for Many Images)

```bash
# 1. Copy batch_hunyuan3d.py to ComfyUI root folder
# 2. Edit API credentials in the script
# 3. Place images in 'input_images' folder
# 4. Run:
python batch_hunyuan3d.py
```

Models will be saved to `output_models/` folder.

### Method 2: ComfyUI Workflow

Use `examples/batch_image_to_3d_workflow.json`:
1. Load workflow in ComfyUI
2. Use "Load Images" node (or similar batch loader)
3. Queue prompt multiple times
4. Check `models/3d_models/` for outputs

## Troubleshooting

**ResourceInsufficient Error:**
- Check account balance
- Add credits ($10+ recommended)
- Verify service activated

**Batch Processing Tips:**
- Process 5-10 images at a time
- Each image takes ~2-5 minutes
- Monitor API credits

## License

MIT - See [LICENSE](LICENSE)

---

 **Requires Tencent Cloud account with billing enabled**
