from abc import ABC , abstractmethod
from typing import TypedDict , Literal ,List




class LLM(ABC):

    class Message(TypedDict):            
        role:Literal["model","user"]
        content:str
    
    def __init__(self,history):
        pass
    
    @abstractmethod
    def generate_content(self,prompt):
        pass
    
    @abstractmethod
    def prompt(self , history):
        pass
    
    @abstractmethod
    def get_history(self)->List["LLM.Message"]:
        pass
    
    
    