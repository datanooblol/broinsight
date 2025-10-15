import requests

class LocalOpenAI:
    def __init__(self):
        self.model_name = "gpt-oss:latest"
        self.base_url = "http://localhost:11434"
        self.temperature = 0.8        
    
    def UserMessage(self, text):
        return {"role": "user", "content": text}

    def AIMessage(self, text):
        return {"role": "assistant", "content": text}

    def SystemMessage(self, text):
        return {"role": "system", "content": text}

    def OutputMessage(self, response):
        return dict(
            content=response["message"]["content"],
            model_name=self.model_name,
            input_token=0,
            output_token=0
        )
        # return response

    def run(self, system_prompt, messages):
        all_messages = [self.SystemMessage(system_prompt)] + messages
        response = requests.post(
            "{base_url}/api/chat".format(base_url=self.base_url), 
            json={
                "model": self.model_name,
                "messages": all_messages,
                "stream": False,
                "options": {"temperature": self.temperature}
            }
        )
        response = response.json()
        return self.OutputMessage(response)