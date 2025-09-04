from . import Action, Shared

class UserInput(Action):
    def logic(self, user_input:str):
        if user_input.lower().startswith("/exit"):
            self.next_action = "exit"

    def run(self, shared:Shared):
        # Check if user_input is already set (one-shot mode)
        if shared.method == "chat":
            user_input = input("YOU: ")
            shared.user_input = user_input
        
        self.logic(shared.user_input)
        return shared