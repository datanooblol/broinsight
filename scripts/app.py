from broinsight.flows import combined_app, FlowState, FlowContext
from broinsight.utils.data_catalog import DataCatalog
import seaborn as sns

def main():
    catalog = DataCatalog()
    catalog.register("tips", sns.load_dataset('tips'))
    machine = combined_app.create_machine(FlowState.ROUTER, FlowState.COMPLETE)
    chat_history = []
    while True:
        context = FlowContext(user_input="", catalog=catalog)
        context.chat.chat_history = chat_history
        user_input = input("You: ")
        if user_input.lower().startswith("/exit"):
            break
        context.user_input = user_input
        machine.run(context=context)
        if context.chat.response is not None:
            print("Bro:", context.chat.response.content)
    print(context)
if __name__=='__main__':
    main()