from typing import Any, Dict, Optional
from broprompt import Prompt
import os
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

class BroInsight:
    """
    LLM-agnostic data analysis agent that helps analyze data through natural language.
    
    Usage:
        broinsight = BroInsight(model)
        
        # Data quality assessment
        response = broinsight.assess_data_quality(profile_context, "Check my data quality")
        
        # Question suggestions  
        response = broinsight.suggest_questions(metadata_context, "I'm a restaurant manager")
        
        # SQL generation
        response = broinsight.generate_sql(metadata_context, "What's the average tip amount?")
        
        # Data insights
        response = broinsight.ask_data(query_results, "What does this data tell me?")
    """
    
    def __init__(self, model):
        """
        Initialize BroInsight with an LLM model.
        
        Args:
            model: LLM model instance with .run() method and .UserMessage()
        """
        self.model = model
    
    def _get_prompt_path(self, filename: str) -> str:
        """Get the full path to a prompt file, works for both dev and installed package"""
        try:
            # Try importlib.resources first (for installed package)
            prompt_files = files('broinsight.prompt_hub')
            return str(prompt_files / filename)
        except:
            # Fallback to relative path (for development)
            return os.path.join(os.path.dirname(__file__), "prompt_hub", filename)
    
    def assess_data_quality(self, context: str, message: str):
        """
        Assess data quality and provide recommendations.
        
        Args:
            context: Formatted profile data (from DataCatalog.to_dq_profile())
            message: User's question about data quality
            
        Returns:
            LLM response with data quality assessment and recommendations
        """
        prompt_path = self._get_prompt_path("dq_suggestion.md")
        prompt = Prompt.from_markdown(prompt_path)
        user_input = f"PROFILE:\n\n{context}\n\nUSER_INPUT:\n\n{message}\n\n"
        
        return self.model.run(
            system_prompt=prompt.str,
            messages=[self.model.UserMessage(text=user_input)]
        )
    
    def suggest_questions(self, context: str, message: str):
        """
        Suggest questions users can ask about their data.
        
        Args:
            context: Formatted metadata (from DataCatalog.to_guide_metadata())
            message: User context (role, goals, etc.)
            
        Returns:
            LLM response with suggested questions organized by business topics
        """
        prompt_path = self._get_prompt_path("guide_question.md")
        prompt = Prompt.from_markdown(prompt_path)
        user_input = f"METADATA:\n\n{context}\n\nUSER_INPUT:\n\n{message}\n\n"
        
        return self.model.run(
            system_prompt=prompt.str,
            messages=[self.model.UserMessage(text=user_input)]
        )
    
    def generate_sql(self, context: str, message: str):
        """
        Generate SQL query from natural language question.
        
        Args:
            context: Formatted metadata (from DataCatalog.to_sql_metadata())
            message: Natural language question about the data
            
        Returns:
            LLM response with SQL query
        """
        prompt_path = self._get_prompt_path("generate_sql.md")
        prompt = Prompt.from_markdown(prompt_path)
        user_input = f"METADATA:\n\n{context}\n\nUSER_INPUT:\n\n{message}\n\n"
        
        return self.model.run(
            system_prompt=prompt.str,
            messages=[self.model.UserMessage(text=user_input)]
        )

    def create_chart(self, query_result, message):
        """Generate Plotly visualization using LLM-generated code"""
        prompt_path = self._get_prompt_path("chart_builder.md")
        prompt = Prompt.from_markdown(prompt_path)
        user_input = f"DATA:\n\n{query_result.to_string()}\n\nUSER_INPUT:\n\n{message}\n\n"
        response = self.model.run(
            system_prompt=prompt.str,
            messages=[self.model.UserMessage(text=user_input)]
        )
        try:
            # prompt = self._load_prompt("chart_builder")
            # data = f"DATA:\n\n{context.to_string()}"
            # user_input = f"USER_INPUT:\n\n{message}"
            
            # response = self.llm.run(
            #     system_prompt=prompt.str,
            #     messages=[self.llm.UserMessage(data + "\n\n" + user_input)]
            # )
            
            # Extract function code
            function_code = response['content'].split("```python")[-1].split("```")[0]
            
            # Execute to create function
            exec(function_code)
            
            # Call with actual data
            fig = locals()['create_chart'](query_result)
            response['chart'] = fig
            return response
            
        except Exception as e:
            print(f"Visualization generation failed: {e}")
            return None

    def ask_data(self, context: str, message: str):
        """
        Provide conversational insights about data results.
        
        Args:
            context: Query results or data to analyze
            message: User's question about the data
            
        Returns:
            LLM response with business insights and interpretations
        """
        prompt_path = self._get_prompt_path("chat.md")
        prompt = Prompt.from_markdown(prompt_path)
        user_input = f"CONTEXT:\n\n{context}\n\nUSER_INPUT:\n\n{message}\n\n"
        
        return self.model.run(
            system_prompt=prompt.str,
            messages=[self.model.UserMessage(text=user_input)]
        )