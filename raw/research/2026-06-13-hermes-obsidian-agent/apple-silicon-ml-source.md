# Apple Silicon ML — Primary Source Dump
Fetched: 2026-06-13
Source: developer.apple.com/machine-learning/ (direct fetch — medium confidence, page was sparse)

## Key Frameworks (as of 2026-06-13)

### Core AI
- Apple's primary framework for on-device AI
- Purpose-built for Apple Silicon
- Zero server dependencies, zero token costs (fully local inference)
- Scales across devices

### Foundation Models Framework
- Native Swift API
- Accesses Apple Foundation Models (on-device AND Private Cloud Compute)
- Multimodal prompts: text + Vision framework
- Dynamic Profiles: swap models/tools in real-time sessions
- Note: This is Apple's own proprietary on-device model — not open-weight

### MLX Framework
- Open-source ML framework for Apple Silicon (from Apple's ML Research team)
- Supports Metal 4 and GPU Neural Accelerators
- Scales training across multiple Macs with RDMA over Thunderbolt
- Used for training AND fine-tuning on Mac
- Community has ported Llama, Mistral, and other open-weight models to MLX

### Core ML
- For traditional ML models (tree ensembles, regression, classification)
- Fast on-device inference

### Metal 4
- GPU acceleration
- MetalFX capabilities
- Direct inference in shaders
- Neural rendering
