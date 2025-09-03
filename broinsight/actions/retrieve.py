from . import Action, Shared

class Retrieve(Action):
    def run(self, shared:Shared):
        if shared.db:
            result = shared.db.execute(shared.sql_query).fetch_df()
            shared.query_result = result
        return shared
        