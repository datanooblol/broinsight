def parse_blockcode(code_str:str, language:str)->str:
    code_str = code_str.split(f"```{language}")[-1]
    code_str = code_str.split("```")[0]
    return code_str.strip()

def parse_sql(sql_str:str)->str:
    return parse_blockcode(sql_str, "sql")