import  ollama

class LLMService:
    def __init__(self, model_name: str = "tinyllama"):
        self.model_name = model_name

    async def generate_answer(self, question: str, context: str) -> str:
        prompt = f"""Tu es un assistant juridique expert français. Réponds à la question suivante en te basant uniquement sur le contexte fourni.\n\nSi l'information n'est pas dans le contexte, indique clairement \"Je ne trouve pas cette information dans les documents fournis.\"\n\nRègles importantes :\n- Réponds en français\n- Cite les documents utilisés\n- Sois précis et professionnel\n- Si tu n'es pas sûr, indique ton incertitude\n\nContexte des documents :\n{context}\n\nQuestion : {question}\n\nRéponse :"""
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            options={
                'temperature': 0.1,
                'top_p': 0.9,
                'max_tokens': 1000
            }
        )
        return response['message']['content']

    async def check_model_availability(self) -> bool:
        try:
            models = ollama.list()
            return any(self.model_name in model['name'] for model in models['models'])
        except:
            return False

    async def pull_model(self) -> bool:
        try:
            ollama.pull(self.model_name)
            return True
        except:
            return False 