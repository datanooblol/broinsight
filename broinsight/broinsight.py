from .flow import get_flow
from .actions.interface import Shared

class BroInsight:
    @staticmethod
    def chat(shared: Shared) -> Shared:
        """Process a question using the provided shared state"""
        # Run the flow with model from shared
        flow = get_flow(shared.model)
        # flow.run(shared)
        try:
            flow.run(shared)
        except Exception as e:
            print(str(e))
        
        return shared