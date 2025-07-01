import logging
from typing import Dict
from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State
from core.stub import Stub

from Agent.Agent import Agent
from Agent.Generator import Generator
import base64


  
    
    
# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()

############################################################
# Config callback function
############################################################
def config(configuration: Dict[str, ConfigClass], state: State) -> None:
    """
    Stores user-specific configuration data.

    Args:
        configuration (Dict[str, ConfigClass]): A mapping of user IDs to configuration objects.
        state (State): The current state of the application (not used in this implementation).
    """
    for uid, conf in configuration.items():
        logging.info(f"Saving new config for user with id:'{uid}'")
        configurations[uid] = conf
        


class OpenfabricGenerator(Generator):
    
    #Singleton Generator
    _generator = None
    
    @classmethod
    def get_generator(cls,app_ids): 
        if cls._generator is None:
            cls._generator = OpenfabricGenerator(app_ids=app_ids)
        return cls._generator
            
    def __init__(self,app_ids):
        self.app_ids = app_ids
        self.stub = Stub(self.app_ids)
        pass
    
    def generate_image(self,prompt ):
        
        try:
            result = self.stub.call(self.app_ids[0], {'prompt':prompt}, 'super-user')
            image = result.get('result')
            base64image  = base64.b64encode(image).decode("utf-8")
            return base64image
        except Exception as e:
            logging.info(f"Excetion {e} occcured")
            return e
        
        
    def generate_3drender(self,base64image):
        
        try:
            result = self.stub.call(self.app_ids[1], {'input_image':base64image}, 'super-user')
            object = result.get('generated_object') 
            base64object  = base64.b64encode(object).decode("utf-8")
            return base64object
        except Exception as e:
            return e           
        
############################################################
# Execution callback function
############################################################

def execute(model: AppModel) -> None:

    """
    Main execution entry point for handling a model pass.

    Args:
        model (AppModel): The model object containing request and response structures.
    """
    request: InputClass = model.request
    user_prompt = request.prompt
    attachments = request.attachments
    session_id = request.session_id
    
    user_config: ConfigClass = configurations.get('super-user', None)
    app_ids = user_config.app_ids if user_config else []
    
    generator = OpenfabricGenerator.get_generator(app_ids=app_ids)
    if generator is None:
        return
    
    # agent = Agent('llama3.2:1b',"TEST_USER",session_id ,generator)
    
    agent = Agent('gemini',"TEST_USER",session_id ,generator)
    
    
    msg , img , obj , sessid  = agent.Exec(user_prompt)
    
    
    response: OutputClass = model.response
    
    response.message = msg
    response.image  = img
    response.object = obj          
    response.session_id = sessid
    
    
    
    
