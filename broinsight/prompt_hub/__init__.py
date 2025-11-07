from pathlib import Path

def _run(filename):
    return Path(__file__).parent.joinpath(filename).read_text()

class PromptHub:

    @property
    def generate_sql(self):
        return _run(filename="generate_sql.md")

    @property
    def guide_question(self):
        return _run(filename="guide_question.md")

    @property
    def chart_builder(self):
        return _run(filename="chart_builder.md")
    
    @property
    def chat(self):
        return _run(filename="chat.md")
    
    @property
    def chat_with_data(self):
        return _run(filename="chat_with_data.md")

    @property
    def quick_chat(self):
        return _run(filename="quick_chat.md")
    
    @property
    def router(self):
        return _run(filename="router.md")