import logging

from Agent.LLM.llm import LLM
from Agent.Storage.VectorDB import VectorDB
from Agent.Storage.DB import DB
from Agent.PromptManager import PromptManager
import uuid

class SessionManager:
    _sessions ={}
    _db:DB = VectorDB()
    _prompt_manager=PromptManager()
    
    def __init__(self):
        pass
    
    @classmethod
    def add_session(cls,session_id):
        if session_id: #LOADING EXISTING SESSION (assumed that the session_id is a valid previous session's id)
            cls.load_session_history(session_id)
        else :        # NEW SESSION CREATED
            session_id = cls.generate_session_id()
            logging.info(f"NEW Session initiated : {session_id}")
            cls._sessions[session_id] = [LLM.Message(role='user',content=cls._prompt_manager.get_base_prompt())]
        return session_id
                    
    @classmethod
    def generate_session_id(cls):
        return str(uuid.uuid4())
    
    @classmethod
    def load_session_history(cls,session_id):
        if session_id not in cls._sessions:
            logging.info("loading session form DATABASE")
            cls._sessions[session_id] = cls.get_session_history(session_id=session_id)
            
    @classmethod
    def get_session_history(cls,session_id):
        if session_id in cls._sessions:
            if len(cls._sessions[session_id])==1:
                logging.info("Initiating new session history")
            else:
                logging.info("Loading session history from memory")
            return cls._sessions[session_id]
        
        logging.info("Loading session history from DATABASE")
        return cls._db.get_conversation_history(session_id=session_id)
    
    @classmethod
    def set_session_history(cls,session_id , history):
        logging.info(f"session history modified: {session_id}")
        cls._sessions[session_id] =history         
    
    @classmethod
    def save_session(cls,username,session_id , image_desc , summary):
        logging.info(f"SessionManager:SaveSession {session_id}")
        cls._db.save_session(username=username, session_id=session_id,image_desc=image_desc,history=cls._sessions[session_id],summary=summary)

class SessionData:
    def __init__(self,session_id,username):
        logging.info(f"SessionData:NewSessionData")
        self.session_id=session_id
        self.username= username
        self.message:str = ""
        self.IMAGE:str = ""
        self.OBJECT:str = ""
        self.image_description:str = ""
        self.summary:str = ""
        self.current_prompt=""
        
    def set(self,message="",IMAGE ="" , OBJECT="", image_description="",summary="" , current_prompt="",history=[]):
        if message:
           self.message = message 
        if IMAGE:
           self.IMAGE = IMAGE 
        if OBJECT:
            self.OBJECT = OBJECT
        if image_description:
            self.image_description = image_description
        if summary:
            self.sumary = summary
        if current_prompt:
            self.current_prompt= current_prompt
        if len(history):
            self.history= history
    