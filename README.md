# Local LLaMA 3.1B Chat

A simple command-line chat interface for running LLaMA 3.1B-3.2B models locally on your RTX 4070 Super GPU.

## Setup

### 1. Install Dependencies

For GPU support (CUDA 12.1):
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

For CPU only (slower):
```bash
pip install llama-cpp-python
```

### 2. Download a Model

Download a 3.1B-3.2B model in GGUF format. Here are **working** options:

**Option 1: Qwen 2.5 3B Instruct (Recommended - Fast & Good Quality)**
```bash
pip install huggingface-hub
hf download Qwen/Qwen2.5-3B-Instruct-GGUF qwen2.5-3b-instruct-q4_k_m.gguf --local-dir .
```
Then update the default model name in `main.py` or run: `python main.py qwen2.5-3b-instruct-q4_k_m.gguf`

**Option 2: Phi-3 Mini 3.8B (Very Fast)**
```bash
hf download microsoft/Phi-3-mini-4k-instruct-gguf Phi-3-mini-4k-instruct-q4.gguf --local-dir .
```
Then run: `python main.py Phi-3-mini-4k-instruct-q4.gguf`

**Option 3: Browse HuggingFace**
- Visit: https://huggingface.co/models?search=gguf+3b
- Look for models with `q4_k_m` or `q4` quantization
- Download the `.gguf` file manually
- Run: `python main.py path/to/downloaded/model.gguf`

**Quantization Guide:**
- `Q4_K_M` - Recommended: Good quality/speed balance (~2-3GB)
- `Q4` - Faster, slightly lower quality (~2GB)
- `Q5_K_M` - Better quality, slightly slower (~3-4GB)
- `Q8` - Best quality, slower (~6GB)

### 3. Run the Chat

```bash
python main.py
```

Or specify a custom model path:
```bash
python main.py path/to/your/model.gguf
```

## Usage

- Type your message and press Enter
- Type `quit`, `exit`, or `bye` to exit
- Type `clear` to clear conversation history
- Press Ctrl+C to interrupt

## System Requirements

- NVIDIA GPU with CUDA support (RTX 4070 Super recommended)
- CUDA toolkit installed
- ~4-6GB VRAM for 3B models (Q4 quantization)
- Python 3.8+

## Troubleshooting

**Model not found error:**
- Make sure you've downloaded a GGUF model file
- Place it in the same directory as `main.py` or provide the full path

**GPU not being used:**
- Verify CUDA is installed: `nvidia-smi`
- Reinstall with GPU support: `pip uninstall llama-cpp-python && pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121`

**Out of memory:**
- Try a smaller quantization (Q4_K_S instead of Q4_K_M)
- Reduce `n_ctx` in the code (currently 4096)

