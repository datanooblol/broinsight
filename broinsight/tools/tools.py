from .register import tool
from datetime import datetime

@tool()
def add(a:float, b:float)->float:
    """Add two numbers together
    Keywords: math, calculation, arithmetic, sum
    Args:
        a (float) : a number
        b (float) : a number
    Returns:
        float : a scalar number
    """
    return a + b

@tool()
def add_calendar(event_name:str, datetime:datetime)->str:
    """Add event into calendar
    Keywords: calendar, schedule, appointment, meeting, event
    Category: scheduling
    Args:
        event_name (str) : name of the event
        datetime (datetime) : a datetime of the event
    Returns:
        str : successfully added message
    """
    return f"{event_name} at {datetime}"

@tool()
def check_stock_index(index:str)->str:
    """Check a stock by index from Yahoo API
    Keywords: stock, investment, finance
    Args:
        index (str) : a stock index
    Returns:
        str : a response from Yahoo API
    """
    return index