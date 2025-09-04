from . import Action
from .interface import Shared

class Retrieve(Action):
    def run(self, shared:Shared):
        if shared.db:
            try:
                result = shared.db.execute_query(shared.sql_query)
                shared.query_result = result
                shared.error_log = []
                shared.retries = 0
                
                if len(result) == 0:
                    shared.fallback_message = "The query executed successfully but returned no results. This might mean the data doesn't exist or the filters are too restrictive."
                    shared.session_logger.log(
                        action=self.__class__.__name__, input_data=shared.sql_query, status='success', error_message='Empty result set'
                    )
                else:
                    shared.session_logger.log(
                        action=self.__class__.__name__, input_data=shared.sql_query, status='success',
                    )                
                self.next_action = "default"
            except Exception as e:
                shared.error_log.append(str(e))
                shared.retries += 1
                if shared.retries <= shared.max_retries:
                    self.next_action = "generate_sql"
                    shared.session_logger.log(
                        action=self.__class__.__name__, input_data=shared.sql_query, status='failed', error_message=str(e)
                    )                         
                else:
                    self.next_action = "default"
                    fallback_message = "I couldn't generate a working SQL query after {max_retries} attempts. The error was: \n{error_history}".format(max_retries=shared.max_retries, error_history="\n".join(["\t -{err}".format(err=err) for err in shared.error_log]))
                    shared.fallback_message = fallback_message
                    shared.error_log = []
                    shared.retries = 0
                    shared.session_logger.log(
                        action=self.__class__.__name__, input_data=shared.sql_query, status='failed', error_message=fallback_message
                    )
                    return shared                 
        return shared
        