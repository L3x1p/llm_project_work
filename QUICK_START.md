# Quick Start Guide - LLaMA Chat API Service

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure you have GPU support for llama-cpp-python:
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

### 2. Start the API Service

```bash
python api_service.py
```

The service will start on **http://localhost:8002**

You should see:
```
Loading model: qwen2.5-3b-instruct-q4_k_m.gguf
Model loaded successfully!
API Service ready on http://localhost:8002
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8002
```

### 3. Test the Service

**Option A: Use the interactive docs**
Open your browser: http://localhost:8002/docs

**Option B: Use the example client**
```bash
python example_client.py
```

**Option C: Use curl**
```bash
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## 📝 Basic Usage

### Python Example

```python
import requests

# Send a message
response = requests.post(
    "http://localhost:8002/chat",
    json={"message": "What is Python?"}
)

data = response.json()
print(data["response"])
```

### JavaScript Example

```javascript
fetch('http://localhost:8002/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello!' })
})
.then(res => res.json())
.then(data => console.log(data.response));
```

## 🔗 Integration in Your Project

### Using the Example Client

```python
from example_client import LLMChatClient

client = LLMChatClient()

# Simple chat
response = client.chat("Your message here")
print(response)

# With conversation history
client.chat("My name is John")
response = client.chat("What's my name?")  # Remembers John
```

### Direct API Calls

```python
import requests

# Chat endpoint
response = requests.post(
    "http://localhost:8002/chat",
    json={
        "message": "Your message",
        "session_id": "optional-session-id",
        "temperature": 0.7
    }
)
```

## 📚 Full Documentation

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

## 🛠️ Troubleshooting

**Port already in use?**
- Change port in `api_service.py`: `uvicorn.run(app, host="0.0.0.0", port=8003)`

**Model not found?**
- Make sure the model file exists in the project directory
- Or specify path: `python api_service.py path/to/model.gguf`

**Service not responding?**
- Check if it's running: `curl http://localhost:8002/health`
- Check logs for errors

## 🎯 Next Steps

1. Read the full [API Documentation](API_DOCUMENTATION.md)
2. Try the [example client](example_client.py)
3. Integrate into your project using the provided examples


