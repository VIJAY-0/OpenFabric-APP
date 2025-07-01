
from typing import Literal
import logging
import json
from  enum import Enum

# from Agent.Agent import Agent
from Agent.Storage.DB import DB
from Agent.LLM.Gemini import GeminiLLM
from Agent.PromptManager import PromptManager


class Processor:
    
    class States(Enum):
        def _generate_next_value_(name, start, count, last_values):
            return count     
        EXIT=0
        MEM_RECALL = 1
        IMAGE= 2
        MODEL= 3
        QUERY= 4
        SHOW_HISTORY=5
        LOAD_HISTORY=6
    
    
    def __init__(self,session_data,generator , session_manager ,db):
        
        self.session_data = session_data
        self.session_manager = session_manager
        self.db:DB = db
        self.llm = GeminiLLM([])
        self.generator = generator
        self.prompt_mngr = PromptManager()
        
    def process(self ,llm_response)-> str:
        resp = preprocess(llm_response)
        parsed = json.loads(resp)
        state = self.States((int)(parsed['state']))
                
        if state == self.States.EXIT:
            return self.exit(parsed)
        elif state == self.States.MEM_RECALL:                
            return self.recall_from_memory(parsed)
        elif state == self.States.IMAGE:
            return self.generate_image(parsed)   
        elif state == self.States.QUERY:
            return self.process_query(parsed)
        elif state == self.States.MODEL:
            return self.generate_model(parsed)
        # elif state == self.States.SHOW_HISTORY:
        #     self.show_history(parsed)
        return "OK"  
    

    def exit(self,resp:dict):
        self.session_data.set(summary= resp["summary"])
        return "EXIT"
        
    def recall_from_memory(self,resp:dict):
        
        intent = resp["data"]["intent"]
        logging.info(f"intent: {intent}")
        refered_image_description=self.db.get_image_description(intent=intent)
        self.session_data.set(image_description=refered_image_description)
        logging.info(f"image desc: {refered_image_description}")
        return refered_image_description
    
    # def reload_conversation_history(self,resp:dict):
    #     intent = resp["data"]["intent"]
    #     re_prompt = resp["data"]["re_prompt"]
    #     self.session_data.set(current_prompt=re_prompt)
    #     hist= self.db.get_conversation_history(intent = intent)
    #     ### wnated to avoid but is necessary
    #     Agent._sessionsManager.set_session_history(self.session_data.session_id , hist)
    #     return "REFRESH"
    
    
    def process_query(self,resp:dict):
        self.session_data.set(message = resp["query"])
        return "EXIT"
    
    def generate_image(self,prompt:dict):
        image_intent = prompt['image']
        logging.info(f"image intent :{image_intent}")
        image_description = self.llm.generate_content([self.prompt_mngr.get('ImagePrompt') , image_intent])
        self.session_data.set(image_description=image_description)
        logging.info(f"image desc :{image_description}")
        self.session_data.set(IMAGE = self.generator.generate_image(image_description))
        return "IMAGE GENERATED"
    
    def generate_model(self,prompt:dict):
        return "MODEL GENERATED"
        self.session_data.set(OBJECT= self.generator.generate_3drender(self.session_data.IMAGE))
    
    # def show_history(self,prompt:dict):
    #     hist = self.llm.get_history()
    #     for message in hist:
    #         logging.info(message)
    #         logging.info(" ")
    #     self.message = str(Agent.sessions[self.session_id])
    #     return "HISTORY"


# utility functions
def remove_prefix(s, prefix=""):
    if prefix and s.startswith(prefix):
        s = s[len(prefix):]
    return s

def remove_suffix(s,suffix=""):
    if suffix and s.endswith(suffix):
        s = s[:-len(suffix)]
    return s

def preprocess(resp):
    resp = remove_prefix(resp , "```json\n")
    resp = remove_prefix(resp , "```json")
    resp = remove_suffix(resp , "```\n")
    resp = remove_suffix(resp , "```")    
    return resp
