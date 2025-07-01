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

from enum import Enum


class Agent:
    
    _sessionsManager = None
    _db:DB = None     
    _generator:Generator =None
    
    def __init__(self,baseLLM,username,session_id, generator:Generator):
        
        if Agent._generator is None:
            logging.info("Agent:Initializing Generator")
            Agent._generator = generator
            
        if Agent._sessionsManager is None:
            logging.info("Agent:Initializing Sessions Manager")
            Agent._sessionsManager = SessionManager()
            
        if Agent._db is None:
            logging.info("Agent:Initializing DataBase")
            Agent._db = VectorDB()
                
        self.llm=None 
        self.session_id = self.add_session(session_id=session_id) #generate a session_id if new session is initiated
        self.session_data = SessionData(session_id=self.session_id , username=username)     
        
        self.init_baseLLM(baseLLM)
    
    def add_session(self,session_id):
        logging.info("Agent:AddSession")
        return Agent._sessionsManager.add_session(session_id=session_id)
        
    def get_session_history(self):
        logging.info("Agent:GetSessionHistory")
        if hasattr(self,"llm"):
            if self.llm is not None:
                return Agent.llm.get_history()
        return Agent._sessionsManager.get_session_history(self.session_data.session_id) 
    
    def set_session_history(self , history):
        logging.info("Agent:SestSessionHistory")
        Agent._sessionsManager.set_session_history(self.session_id ,history)
    
    def init_baseLLM(self , baseLLM):
        logging.info("Agent:InitBaseLLM")
        self.baseLLM=baseLLM
        new_history = self.get_session_history() ## for new sessions it returns history with only base_prompt in it 
        if self.baseLLM=='gemini':
            self.llm:LLM = GeminiLLM(new_history)
        if 'llama' in self.baseLLM:
            self.llm:LLM = OllamaLLM(new_history , MODEL=self.baseLLM)
    
    
        
    def Exec(self,user_prompt:str):
        logging.info("Agent:Execution")
        prompt = user_prompt
        while True:
            
            llm_response = self.llm.prompt(prompt)
        
            logging.info(f"llm response :{llm_response}")
            
            PROCESSOR = Processor(  
                session_data=self.session_data,
                generator=Agent._generator,
                session_manager=Agent._sessionsManager,
                db=Agent._db,
                baseLLM = self.baseLLM 
            )
            
            agent_response = PROCESSOR.process(llm_response=llm_response)
            
            logging.info(f"Agent:AgentResponse{agent_response}")
            prompt = agent_response
            
            if agent_response =="EXIT":
                break
    
        return self.EXIT()
    
    
    def EXIT(self):
        sd = self.session_data
        self.save_session()
        logging.info("Agent:Exiting")
        return self.return_data()
        
    def return_data(self):
        sd = self.session_data
        return sd.message ,sd.IMAGE , sd.OBJECT ,sd.session_id
    
    
    def save_session(self):
        logging.info("Agent:SaveSession")
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
        
        