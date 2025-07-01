
from typing import Literal
import logging
import json
from  enum import Enum

# from Agent.Agent import Agent
from Agent.Storage.DB import DB
from Agent.LLM.Gemini import GeminiLLM
from Agent.LLM.Ollama import OllamaLLM
from Agent.PromptManager import PromptManager



class Processor:
    
    class States(Enum):
             
        EXIT=0
        MEM_RECALL = 1
        IMAGE= 2
        MODEL= 3
        QUERY= 4
    
    
    def __init__(self,session_data,generator , session_manager ,db ,baseLLM):
        
        self.session_data = session_data
        self.session_manager = session_manager
        self.db:DB = db
        self.generator = generator
        self.prompt_mngr = PromptManager()
        self.llm = self.init_baseLLM(baseLLM)
        
    def init_baseLLM(self,baseLLM):    
        if baseLLM=='gemini':
            return GeminiLLM([])
        if 'llama' in self.baseLLM:
            return OllamaLLM([], MODEL=baseLLM)
        
        
    def process(self ,llm_response)-> str:
        try:
            self.State = preprocess(llm_response)
        except Exception as e:
            logging.info(f"Processor:ExceptionOccured:{e}")
            return "WRONG RESPONSE"
        state = self.States((int)(self.State['state']))
                
        if state == self.States.EXIT:
            return self.exit()
        
        elif state == self.States.MEM_RECALL:                
            return self.recall_from_memory()
        
        elif state == self.States.IMAGE:
            return self.generate_image()   
        
        elif state == self.States.MODEL:
            return self.generate_model()
        
        elif state == self.States.QUERY:
            return self.process_query()
    

    def exit(self):
        logging.info("Processor:Exiting")
        self.session_data.set(summary= self.State["summary"])
        return "EXIT"
        
    def recall_from_memory(self):
        logging.info("Processor:RecallingMemory")
        
        intent = self.State["data"]["intent"]
        refered_image_description=self.db.get_image_description(intent=intent)
        self.session_data.set(image_description=refered_image_description)
        return refered_image_description
    
    def process_query(self):
        logging.info("Processor:OricesingQuery")
        self.session_data.set(message = self.State["query"])
        return "EXIT"
    
    def generate_image(self):
        logging.info("Processor:GeneratingImage")
        try :
            image_intent = self.State['image']
            image_description = self.llm.generate_content([self.prompt_mngr.get('ImagePrompt') , image_intent])
            
            self.session_data.set(image_description=image_description)
            self.session_data.set(IMAGE = self.generator.generate_image(image_description))
            
            logging.info("Processor:ImageGenerated")
            return "IMAGE GENERATED"
        except Exception as e:
            logging.info(f"Error in model generation {e}")          
            return "FAILED"
    
    def generate_model(self):
        logging.info("Processor:GeneratingModel")
        try :
            self.session_data.set(OBJECT= self.generator.generate_3drender(self.session_data.IMAGE))
            logging.info("Processor:ModelGenerated")
            return "MODEL GENERATED"
        except Exception as e:
            logging.info(f"Eror in model generation {e}")
            return "FAILED"
    
    
    


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
    
    return json.loads(resp)
