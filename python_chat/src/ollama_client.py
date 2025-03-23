class OllamaClient:
    def __init__(self, host="http://localhost:11434"):
        self.host = host
        self.available_models = []
        self.current_model = None
        
    async def connect(self):
        return True
        
    async def list_models(self):
        return [{"name": "mistral"}, {"name": "llama2"}]
        
    async def generate(self, model, prompt, system="", parameters=None):
        return f"Response to: {prompt}"
