#!/usr/bin/env python3
"""
Example client for the LLM Chat API
Demonstrates how to connect to the API service from other parts of your project
"""

import requests
import json

API_BASE_URL = "http://localhost:8002"


class LLMChatClient:
    """Simple client for interacting with the LLM Chat API"""
    
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        self.session_id = None
    
    def chat(self, message, temperature=0.7, max_tokens=512):
        """
        Send a chat message and get response
        
        Args:
            message: Your message to the AI
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
        
        Returns:
            str: The AI's response
        """
        payload = {
            "message": message,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Include session_id if we have one (for conversation history)
        if self.session_id:
            payload["session_id"] = self.session_id
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=120  # 2 minute timeout for long responses
            )
            response.raise_for_status()
            data = response.json()
            
            # Save session_id for future requests
            self.session_id = data["session_id"]
            return data["response"]
        
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"
    
    def chat_stream(self, message, temperature=0.7, max_tokens=512):
        """
        Send a chat message and get streaming response
        
        Yields tokens as they are generated
        """
        payload = {
            "message": message,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if self.session_id:
            payload["session_id"] = self.session_id
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/stream",
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = json.loads(line[6:])
                        if 'token' in data:
                            token = data['token']
                            full_response += token
                            yield token
                        elif 'done' in data:
                            self.session_id = data.get('session_id', self.session_id)
                            break
                        elif 'error' in data:
                            raise Exception(data['error'])
        
        except requests.exceptions.RequestException as e:
            yield f"Error: {e}"
    
    def clear_history(self):
        """Clear conversation history for current session"""
        if self.session_id:
            try:
                requests.post(
                    f"{self.base_url}/chat/clear",
                    json={"session_id": self.session_id}
                )
                self.session_id = None
                return True
            except:
                return False
        return True
    
    def health_check(self):
        """Check if the API service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except:
            return {"status": "unhealthy", "model_loaded": False}


def example_usage():
    """Example usage of the client"""
    print("Connecting to LLM Chat API...")
    
    # Create client
    client = LLMChatClient()
    
    # Check health
    health = client.health_check()
    if not health.get("model_loaded"):
        print("⚠️  Warning: Model may not be loaded")
    else:
        print("✓ API is healthy\n")
    
    # Simple chat
    print("=== Simple Chat ===")
    response = client.chat("Hello! Can you introduce yourself?")
    print(f"AI: {response}\n")
    
    # Conversation with history
    print("=== Conversation with History ===")
    client.chat("My name is Alice and I love Python programming.")
    response = client.chat("What's my name and what do I love?")
    print(f"AI: {response}\n")
    
    # Streaming response
    print("=== Streaming Response ===")
    print("AI: ", end="", flush=True)
    for token in client.chat_stream("Tell me a fun fact about space"):
        print(token, end="", flush=True)
    print("\n")
    
    # Clear history
    print("=== Clearing History ===")
    client.clear_history()
    print("History cleared. Starting new conversation.\n")
    
    # New conversation
    response = client.chat("What did we talk about before?")
    print(f"AI: {response}\n")


if __name__ == "__main__":
    example_usage()


