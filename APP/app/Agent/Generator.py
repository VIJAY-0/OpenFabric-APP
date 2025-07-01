from abc import ABC , abstractmethod

class Generator(ABC):
    
    @abstractmethod
    def generate_image(prompt):
        pass
    @abstractmethod
    def generate_3drender(promot):
        pass