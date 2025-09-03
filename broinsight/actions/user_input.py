from . import Action, Shared

class UserInput(Action):
    def logic(self, user_input:str):
        if user_input.lower().startswith("/exit"):
            self.next_action = "exit"

    def run(self, shared:Shared):
        user_input = input("YOU: ")
        self.logic(user_input)
        shared.user_input = user_input
        return shared