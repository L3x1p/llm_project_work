#!/usr/bin/env python3
"""
Helper script to download a 3B model for the chat interface
"""

import subprocess
import sys
import os

def download_model():
    """Download a recommended 3B model"""
    print("Available models to download:")
    print("\n1. Qwen 2.5 3B Instruct (Recommended - Best balance)")
    print("2. Phi-3 Mini 3.8B (Very fast)")
    print("3. Custom model URL")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        repo = "Qwen/Qwen2.5-3B-Instruct-GGUF"
        filename = "qwen2.5-3b-instruct-q4_k_m.gguf"
    elif choice == "2":
        repo = "microsoft/Phi-3-mini-4k-instruct-gguf"
        filename = "Phi-3-mini-4k-instruct-q4.gguf"
    elif choice == "3":
        repo = input("Enter HuggingFace repo (e.g., username/model-name): ").strip()
        filename = input("Enter filename to download: ").strip()
    else:
        print("Invalid choice")
        return
    
    print(f"\nDownloading {filename} from {repo}...")
    print("This may take a few minutes depending on your internet speed.\n")
    
    try:
        # Use hf download (new command)
        result = subprocess.run(
            ["hf", "download", repo, filename, "--local-dir", "."],
            check=True
        )
        print(f"\n✓ Successfully downloaded {filename}")
        print(f"\nYou can now run: python main.py {filename}")
    except subprocess.CalledProcessError:
        # Fallback to huggingface-cli
        print("\nTrying with huggingface-cli (deprecated but may work)...")
        try:
            result = subprocess.run(
                ["huggingface-cli", "download", repo, filename, "--local-dir", "."],
                check=True
            )
            print(f"\n✓ Successfully downloaded {filename}")
            print(f"\nYou can now run: python main.py {filename}")
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Download failed: {e}")
            print("\nTry downloading manually from:")
            print(f"  https://huggingface.co/{repo}")
            sys.exit(1)
    except FileNotFoundError:
        print("\n✗ 'hf' command not found. Please install huggingface-hub:")
        print("  pip install huggingface-hub")
        print("\nThen try again, or download manually from:")
        print(f"  https://huggingface.co/{repo}")
        sys.exit(1)

if __name__ == "__main__":
    download_model()


