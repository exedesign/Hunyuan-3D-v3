# ComfyUI-Hunyuan3D-v3

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

## Troubleshooting

**ResourceInsufficient Error:**
- Check account balance
- Add credits ($10+ recommended)
- Verify service activated

## License

MIT - See [LICENSE](LICENSE)

---

 **Requires Tencent Cloud account with billing enabled**
