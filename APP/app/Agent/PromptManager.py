import os

class PromptManager:
    _prompts = None

    def __init__(self):
        if PromptManager._prompts is None:
            PromptManager.load_prompts()
        
    
    @classmethod
    def get_base_prompt(cls):
        return cls._prompts["BasePrompt"]
    @classmethod
    def get(cls,key):
        return cls._prompts[key]
    
    @classmethod
    def load_prompts(cls):
        cls._prompts={}
        base_dir = os.path.dirname(os.path.abspath(__file__))
        Baseprompt_path = os.path.join(base_dir, "Prompts", "BasePrompt.txt")
        Imageprompt_path = os.path.join(base_dir, "Prompts", "ImagePrompt.txt")
        
        with open(Baseprompt_path,"r") as f:
            content = f.read()
            cls._prompts["BasePrompt"] = content
                        
        with open(Imageprompt_path,"r") as f:
            content = f.read()
            cls._prompts["ImagePrompt"] = content

