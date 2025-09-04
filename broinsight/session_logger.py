from datetime import datetime

class SessionLogger:
    def __init__(self, ):
        self.logs = []  # In-memory fallback
    
    def log(self, action: str, input_data: str = None, output_data: str = None, 
            status: str = "success", error_message: str = None):
        """Log an action in the session (memory only)"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "input_data": input_data,
            "output_data": output_data,
            "status": status,
            "error_message": error_message
        }
        
        # Store in memory only during execution
        self.logs.append(log_entry)
    
    def get_session_logs(self):
        """Get all logs for this session"""
        return self.logs
    
    def get_summary(self):
        """Get a summary of the session"""
        return {
            "total_actions": len(self.logs),
            "actions": [log["action"] for log in self.logs],
            "errors": [log for log in self.logs if log["status"] == "error"]
        }