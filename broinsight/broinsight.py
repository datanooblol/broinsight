from typing import List, Optional
from broprompt import Prompt
from .utils.data_catalog import DataCatalog


class BroInsight:
    """Main interface for data analysis and quality assessment"""
    
    def __init__(self, llm, catalog: DataCatalog):
        self.llm = llm
        self.catalog = catalog
    
    def _load_prompt(self, module: str) -> Prompt:
        """Load prompt template at runtime"""
        return Prompt.from_markdown(f"broinsight/prompt_hub/{module}.md")
    
    def _construct_user_input(self, profile: str, question: str) -> str:
        """Construct user input in expected format"""
        return f"PROFILE:\n\n{profile}\n\nUSER_INPUT:\n\n{question}\n\n"
    
    def _build_table_metadata(self, table_name: str) -> dict:
        """Build rich metadata dictionary for a single table"""
        field_profile = self.catalog.get_field_profile(table_name)
        table_metadata = self.catalog.get_metadata(table_name)
        
        # Start with table info
        metadata_dict = {
            'table_name': table_name,
            'table_description': table_metadata.get('table_description', '') if table_metadata else ''
        }
        
        # Add field profiles with descriptions
        for field, profile in field_profile.items():
            metadata_dict[field] = profile.copy()
            # Add description if available
            if table_metadata and 'description' in table_metadata:
                metadata_dict[field]['description'] = table_metadata['description'].get(field, '')
        
        return metadata_dict
    
    def generate_sql(self, question: str, tables: Optional[List[str]] = None, messages: Optional[List] = None) -> str:
        """Generate SQL query from natural language question"""
        # Use all tables if none specified
        if tables is None:
            tables = self.catalog.list_tables()
        
        # Validate tables exist
        for table in tables:
            if table not in self.catalog.list_tables():
                raise ValueError(f"Table '{table}' not found")
        
        # Build metadata for all tables
        all_metadata = {}
        for table in tables:
            all_metadata[table] = self._build_table_metadata(table)
        
        # Format metadata as string (like your example)
        metadata_lines = []
        for table_name, table_meta in all_metadata.items():
            for field, detail in table_meta.items():
                metadata_lines.append(f"{field}: {detail}")
        
        metadata_str = "\n".join(metadata_lines)
        
        # Load prompt and construct input
        prompt = self._load_prompt("generate_sql")
        metadata_input = f"METADATA:\n\n{metadata_str}\n\n"
        user_input = f"USER_INPUT:\n\n{question}"
        
        # Prepare messages
        llm_messages = messages.copy() if messages else []
        llm_messages.append(self.llm.UserMessage(metadata_input + user_input))
        
        # Call LLM
        response = self.llm.run(system_prompt=prompt.str, messages=llm_messages)
        
        return response
    
    def assess_data_quality(self, table_name: str, question: str, messages: Optional[List] = None) -> str:
        """Assess data quality for a specific table"""
        # Validate table exists
        if table_name not in self.catalog.list_tables():
            raise ValueError(f"Table '{table_name}' not found")
        
        # Get formatted profile
        profile_str = self.catalog.get_formatted_profile(table_name)
        
        # Load prompt and construct input
        prompt = self._load_prompt("dq_suggestion")
        user_input = self._construct_user_input(profile_str, question)
        
        # Prepare messages
        llm_messages = messages.copy() if messages else []
        llm_messages.append(self.llm.UserMessage(user_input))
        
        # Call LLM
        response = self.llm.run(system_prompt=prompt.str, messages=llm_messages)
        
        return response
    
    def suggest_questions(self, message: str, tables: Optional[List[str]] = None, messages: Optional[List] = None) -> str:
        """Generate suggested questions based on available tables"""
        # Use all tables if none specified
        if tables is None:
            tables = self.catalog.list_tables()
        
        # Validate tables exist
        for table in tables:
            if table not in self.catalog.list_tables():
                raise ValueError(f"Table '{table}' not found")
        
        # Build metadata for all specified tables
        metadata_lines = []
        for table in tables:
            field_profile = self.catalog.get_field_profile(table)
            table_metadata = self.catalog.get_metadata(table)
            
            for field, profile in field_profile.items():
                # Get description from metadata if available
                description = ""
                if table_metadata and 'descriptions' in table_metadata:
                    description = table_metadata['descriptions'].get(field, "")
                
                # Format: table.field: type - description - key_stats
                data_type = profile['data_types']
                stats_summary = ""
                
                if data_type in ['integer', 'float'] and 'statistics' in profile:
                    stats = profile['statistics']
                    stats_summary = f"(min: {stats.get('min', 'N/A')}, max: {stats.get('max', 'N/A')}, avg: {stats.get('mean', 'N/A')})"
                elif data_type == 'string' and 'most_frequent' in profile:
                    top_values = list(profile['most_frequent'].keys())[:3]
                    stats_summary = f"(top values: {', '.join(map(str, top_values))})"
                
                field_name = f"{table}.{field}" if len(tables) > 1 else field
                line = f"{field_name}: {data_type}"
                if description:
                    line += f" - {description}"
                if stats_summary:
                    line += f" {stats_summary}"
                
                metadata_lines.append(line)
        
        # Construct input
        metadata_str = "\n".join(metadata_lines)
        user_input = f"METADATA:\n{metadata_str}\n\nUSER_CONTEXT:\n{message}\n\n"
        
        # Load prompt
        prompt = self._load_prompt("guide_question")
        
        # Prepare messages
        llm_messages = messages.copy() if messages else []
        llm_messages.append(self.llm.UserMessage(user_input))
        
        # Call LLM
        response = self.llm.run(system_prompt=prompt.str, messages=llm_messages)
        
        return response
    
    def create_visualization(self, question: str, query_result):
        """Generate Plotly visualization using LLM-generated code"""
        try:
            prompt = self._load_prompt("chart_builder")
            data = f"DATA:\n\n{query_result.to_string()}"
            user_input = f"USER_INPUT:\n\n{question}"
            
            response = self.llm.run(
                system_prompt=prompt.str,
                messages=[self.llm.UserMessage(data + "\n\n" + user_input)]
            )
            
            # Extract function code
            function_code = response['content'].split("```python")[-1].split("```")[0]
            
            # Execute to create function
            exec(function_code)
            
            # Call with actual data
            fig = locals()['create_chart'](query_result)
            return fig
            
        except Exception as e:
            print(f"Visualization generation failed: {e}")
            return None
    
    def ask_data(self, message: str, tables: Optional[List[str]] = None, visualize: bool = False, messages: Optional[List] = None):
        """Ask questions about data across one or more tables"""
        # Step 1: Generate SQL query
        sql_query = self.generate_sql(message, tables, messages)
        sql_query = sql_query['content'].split("```sql")[-1].split("```")[0]
        
        # Step 2: Execute SQL on catalog
        try:
            query_result = self.catalog.query(sql_query)
            
            # Step 3: Generate final answer using results + original question
            answer_prompt = self._load_prompt("chat")  # Assuming you have a chat prompt
            answer_input = f"QUESTION: {message}\n\nQUERY_RESULTS:\n{query_result.to_string()}\n\nPlease provide a clear answer based on the query results."
            
            answer_messages = [self.llm.UserMessage(answer_input)]
            final_response = self.llm.run(system_prompt=answer_prompt.str, messages=answer_messages)
            
            if visualize:
                chart = self.create_visualization(message, query_result)
                if chart:
                    final_response["chart"] = chart
            
            return final_response
            
        except Exception as e:
            return {"content": f"Error executing query: {str(e)}\n\nGenerated SQL: {sql_query}"}