#!/usr/bin/env python3
"""
Local LLM 3B Chat Interface
Optimized for RTX 4070 Super GPU
"""

import os
from llama_cpp import Llama
import sys
from langdetect import detect, LangDetectException

SYSTEM_PROMPT_BASE = (
    "You are a helpful assistant. "
    "Answer ONLY the user's latest question. "
    "Do NOT add extra sections like 'Actionable advice', 'User question', or multiple Q&A. "
    "If you need missing info, ask ONE short clarification question."
)

def detect_language(text: str) -> str:
    """Detect the language of the input text"""
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return "en"  # Default to English if detection fails

def get_language_instruction(lang: str) -> str:
    """Get instruction to respond in the detected language"""
    language_names = {
        "de": "German",
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "nl": "Dutch",
        "pl": "Polish",
        "tr": "Turkish",
        "sv": "Swedish",
        "da": "Danish",
        "no": "Norwegian",
        "fi": "Finnish",
        "cs": "Czech",
        "hu": "Hungarian",
        "ro": "Romanian",
        "el": "Greek",
        "he": "Hebrew",
        "th": "Thai",
        "vi": "Vietnamese",
        "id": "Indonesian",
        "hi": "Hindi",
    }
    language_name = language_names.get(lang, "the same language")
    if lang == "en":
        return ""  # No extra instruction needed for English
    return f" IMPORTANT: Respond in {language_name}. Use {language_name} for your entire response."

def load_model(model_path: str = None):
    """Load the LLM model with GPU acceleration"""
    if model_path is None:
        # Default model path - user can specify their own
        model_path = "qwen2.5-3b-instruct-q4_k_m.gguf"
    
    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        print("\nPlease download a 3.1B-3.2B model in GGUF format.")
        print("\n=== WORKING DOWNLOAD OPTIONS ===")
        print("\nOption 1: LLM 3B Instruct (Recommended)")
        print("  hf download Qwen/Qwen2.5-3B-Instruct-GGUF qwen2.5-3b-instruct-q4_k_m.gguf --local-dir .")
        print("  OR")
        print("  hf download Qwen/Qwen2.5-3B-Instruct-GGUF qwen2.5-3b-instruct-q4_k_m.gguf")
        print("\nOption 2: Phi-3 Mini (3.8B, very fast)")
        print("  hf download microsoft/Phi-3-mini-4k-instruct-gguf Phi-3-mini-4k-instruct-q4.gguf")
        print("\nOption 3: Browse and download manually")
        print("  Visit: https://huggingface.co/models?search=gguf+3b")
        print("  Look for models with 'q4_k_m' or 'q4' quantization")
        print("\nNote: Use 'hf download' (new) instead of 'huggingface-cli download' (deprecated)")
        sys.exit(1)
    
    print(f"Loading model: {model_path}")
    print("This may take a moment...")
    
    try:
        # Initialize with GPU support (n_gpu_layers=-1 uses all GPU layers)
        llm = Llama(
            model_path=model_path,
            n_ctx=4096,  # Context window
            n_threads=4,  # CPU threads
            n_gpu_layers=-1,  # Use all GPU layers (-1 = all)
            verbose=False,
        )
        print("Model loaded successfully!")
        return llm
    except Exception as e:
        print(f"Error loading model: {e}")
        print("\nMake sure you have:")
        print("  1. Installed llama-cpp-python with GPU support:")
        print("     pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121")
        print("  2. CUDA toolkit installed")
        sys.exit(1)

def chat_loop(llm):
    """Main chat loop"""
    print("\n" + "="*60)
    print("LLM 3B Chat Interface")
    print("Type 'quit', 'exit', or 'bye' to end the conversation")
    print("Type 'clear' to clear the conversation history")
    print("="*60 + "\n")
    
    conversation_history = []
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nGoodbye!")
                break
            
            if user_input.lower() == 'clear':
                conversation_history = []
                print("Conversation history cleared.\n")
                continue
            
            # Detect language and build language-aware prompt
            detected_lang = detect_language(user_input)
            lang_instruction = get_language_instruction(detected_lang)
            system_prompt = SYSTEM_PROMPT_BASE + lang_instruction
            
            # Build prompt with conversation history
            prompt = f"System: {system_prompt}\n\n"
            for msg in conversation_history:
                prompt += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"
            prompt += f"User: {user_input}\nAssistant:"
            
            # Generate response
            print("Assistant: ", end="", flush=True)
            
            response = llm(
                prompt,
                max_tokens=512,
                temperature=0.7,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["User:", "System:", "Actionable advice:", "User question:", "\n\n\n"],
                stream=True,
            )
            
            # Stream the response
            full_response = ""
            for chunk in response:
                text = chunk['choices'][0]['text']
                print(text, end="", flush=True)
                full_response += text
            
            print("\n")
            
            # Save to history
            conversation_history.append({
                'user': user_input,
                'assistant': full_response.strip()
            })
            
            # Limit history to last 5 exchanges to manage context
            if len(conversation_history) > 5:
                conversation_history = conversation_history[-5:]
                
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            continue

def main():
    """Main entry point"""
    # Check if model path is provided as command line argument
    model_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Load model
    llm = load_model(model_path)
    
    # Start chat loop
    chat_loop(llm)

if __name__ == "__main__":
    main()

