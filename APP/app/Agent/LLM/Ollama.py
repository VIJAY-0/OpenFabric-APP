from Agent.LLM.llm import LLM
import requests
from typing import List

class OllamaLLM(LLM):
    OLLAMA_URL = "http://host.docker.internal:11434/api/chat"

    MODEL_NAME = "llama3.2:1b"  # change this to any available ollama model

    def __init__(self, history: List[LLM.Message] = [] , MODEL = ""):
        self.history = []
        if MODEL:
            OllamaLLM.MODEL_NAME = MODEL
        
        for item in history:
            self.history.append({
                "role": item["role"],
                "content": item["content"]
            })

    def generate_content(self, prompts):
        hist = [{"role": "user", "content": prompt} for prompt in prompts]

        payload = {
            "model": self.MODEL_NAME,
            "stream": False,  # ← disables streaming
            "messages": hist
        }

        response = requests.post(self.OLLAMA_URL, json=payload)
        obj = response.json()

        try:
            return obj["message"]["content"]
        except KeyError:
            return obj

    def prompt(self, prompt):
        self.history.append({
            "role": "user",
            "content": prompt
        })

        payload = {
            "model": self.MODEL_NAME,
            "stream": False,  # ← disables streaming
            "messages": self.history
        }

        response = requests.post(self.OLLAMA_URL, json=payload)
        obj = response.json()

        try:
            reply = obj["message"]["content"]
            self.history.append({
                "role": "assistant",
                "content": reply
            })
            return reply
        except KeyError:
            return obj

    def get_history(self):
        return [LLM.Message(role=item["role"], content=item["content"]) for item in self.history]
