from Agent.LLM.llm import LLM
import json
import requests
from typing import List
import os


class GeminiLLM(LLM):
    
    GEMINI_API_KEY=os.environ["GEMINI_API_KEY"]
        
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    
    def __init__(self ,history:List[LLM.Message]=[]):
        self.history = []
        for item in history:
            self.history.append({"role":item["role"] ,"parts":[{"text":item["content"]}]})
        
    def generate_content(self,prompts):
        hist = []
        for prompt in prompts:
            hist.append({"role":"user","parts":[{"text":prompt}]})
            
        payload={
            "contents":hist
        }         
        response = requests.post(GeminiLLM.url, headers=GeminiLLM.headers, data=json.dumps(payload))
        obj = response.json()
        model_reply = obj["candidates"][0]["content"]["parts"][0]["text"]      
        return model_reply
    
        
    def prompt(self,prompt):
        self.history.append({"role":"user","parts":[{"text":prompt}]})
        payload={
            "contents":self.history
        }         
        response = requests.post(GeminiLLM.url, headers=GeminiLLM.headers, data=json.dumps(payload))
        obj = response.json()
        try :
            model_reply = obj["candidates"][0]["content"]["parts"][0]["text"]      
            self.history.append({"role":"model","parts":[{"text":model_reply}]})
            return model_reply
        except Exception as e:
            return obj
    
    def get_history(self):
        history = []
        for item in self.history:
            history.append(LLM.Message(role=item["role"] ,content=item["parts"][0]["text"] ))
            
        return history
    
    