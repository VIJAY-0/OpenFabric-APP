from typing import Literal
import logging

from Agent.LLM.llm import LLM
from Agent.Storage.VectorDB import VectorDB
from Agent.Storage.DB import DB
from Agent.LLM.Gemini import GeminiLLM
from Agent.LLM.Ollama import OllamaLLM
from Agent.Generator import Generator

from Agent.Processor import Processor
from Agent.SessionsManager import SessionManager , SessionData 


class Agent:
    
    _sessionsManager = None
    _db:DB = None     
    _generator:Generator =None
    
    def __init__(self,baseLLM:Literal['gemini'],username,session_id:str , generator:Generator):
        
        if Agent._generator is None:
            Agent._generator = generator
            
        if Agent._sessionsManager is None:
            Agent._sessionsManager = SessionManager()
            
        if Agent._db is None:
            Agent._db = VectorDB()
                
        self.llm=None 
        self.session_id = self.add_session(session_id=session_id) #generate a session_id if new session is initiated
        self.session_data = SessionData(session_id=self.session_id , username=username)     
        
        self.init_baseLLM(baseLLM)
    
    def add_session(self,session_id):
        return Agent._sessionsManager.add_session(session_id=session_id)
        
    def get_session_history(self):
        if hasattr(self,"llm"):
            if self.llm is not None:
                return Agent.llm.get_history()
        return Agent._sessionsManager.get_session_history(self.session_data.session_id) 
    
    def set_session_history(self , history):
        Agent._sessionsManager.set_session_history(self.session_id ,history)
    
    def init_baseLLM(self , baseLLM):
        self.baseLLM=baseLLM
        new_history = self.get_session_history() ## for new sessions it returns history with only base_prompt in it 
        if self.baseLLM=='gemini':
            self.llm:LLM = GeminiLLM(new_history)
        if 'llama' in self.baseLLM:
            self.llm:LLM = OllamaLLM(new_history , MODEL=self.baseLLM)
        
        
    def Exec(self , user_prompt:str):
        prompt = user_prompt
        while True:
            agent_response = self.exec(prompt)
            if agent_response =="EXIT":
                break
            if agent_response == "REFRESH":
                self.refresh()
                prompt = self.session_data.current_prompt
        return self.EXIT()
    
    def refresh(self):
        self.llm=None
        self.init_baseLLM(self.baseLLM)           
    
    
    def exec(self,user_prompt):        
        llm_response = self.llm.prompt(user_prompt)
        while True:
            logging.warning(f" llm_response : {llm_response}")
            PROCESSOR = Processor(  
                                    session_data=self.session_data,
                                    generator=Agent._generator,
                                    session_manager=Agent._sessionsManager,
                                    db=Agent._db
                                  )
            
            processor_response = PROCESSOR.process(llm_response=llm_response)
            
            logging.info(f" SD after PROCESSING : {self.session_data}")
            if processor_response in ("EXIT", "REFRESH"):
                return processor_response
            llm_response = self.llm.prompt(processor_response)    
            
    def EXIT(self):
        sd = self.session_data
        self.save_session()
        return self.return_data()
        
    def return_data(self):
        sd = self.session_data
        return sd.message ,sd.IMAGE , sd.OBJECT ,sd.session_id
    
    
    def save_session(self):
        sd = self.session_data
        
        session_history =self.llm.get_history()
        self.set_session_history(session_history)
        
        #saving to db at every exit ## because currently
        ## TODO store last image rescription in memory
        if sd.image_description:
            ## TODO use cache for SessionManager and save to db only when session is evicted form cache
            Agent._sessionsManager.save_session(
                                                session_id=sd.session_id,
                                                username=  sd.username,
                                                image_desc=sd.image_description,
                                                summary=   sd.image_description,     # TODO make it work with summary of convo
                                                )
        
        logging.info("Sucessfully exiting")
        