class AgentRegistry:
    _agents = {}

    @classmethod
    def register(cls, name:str, agent_class):
        cls._agents[name] = agent_class
        return agent_class
    
    @classmethod
    def list(cls):
        return cls._agents
    
def agent(name):
    def decorator(cls):
        AgentRegistry.register(name, cls)
        return cls
    return decorator