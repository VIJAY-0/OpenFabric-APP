from abc import ABC , abstractmethod


class DB(ABC):
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def save_session(self,username,session_id,image_desc,history,summary):
        pass
    
    
    @abstractmethod
    def get_image_description(self,intent,session_id):
        pass
    
    @abstractmethod
    def get_conversation_history(self,intent,session_id):
        pass

