from . import Action, Shared

class Retrieve(Action):
    def run(self, shared:Shared):
        if shared.db:
            try:
                result = shared.db.execute_query(shared.sql_query)
                shared.query_result = result
                shared.error_log = []
                shared.retries = 0
            except Exception as e:
                if shared.retries < shared.max_retries:
                    self.next_action = "generate_sql"
                    shared.error_log.append(str(e))
                    shared.retries += 1
                else:
                    self.next_action = "default"
                    shared.fallback_message = "I couldn't generate a working SQL query after {max_retries} attempts. The error was: \n{error_history}".format(max_retries=shared.max_retries, error_history="\n".join(["\t -{err}".format(err=err) for err in shared.error_log]))
                    shared.error_log = []
                    shared.retries = 0
        return shared
        