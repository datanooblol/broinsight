from .register import tool
from datetime import datetime

@tool()
def add(a:float, b:float)->float:
    """Perform mathematical addition of two numbers
    
    Use this tool when users need to calculate the sum of two numbers,
    perform basic arithmetic operations, or solve mathematical problems.
    
    Keywords: add, plus, sum, total, calculate, math, arithmetic, 
    computation, numbers, addition, combine
    Category: mathematics
    
    Examples:
    - "What is 5 plus 3?"
    - "Add 10.5 and 7.2"
    - "Calculate the sum of 25 and 30"
    - "What's twenty two plus one?"
    
    Args:
        a (float) : first number to add
        b (float) : second number to add
    Returns:
        float : the sum of the two input numbers
    """
    return a + b

@tool()
def add_calendar(event_name:str, datetime:datetime)->str:
    """Add an event, appointment, or reminder to the calendar
    
    Use this tool when users want to schedule something, create reminders, 
    plan visits, book appointments, or add any time-based activities.
    
    Keywords: calendar, schedule, appointment, meeting, event, reminder, visit, 
    plan, book, add, create, time, date, when, at, on, see, meet
    Category: scheduling
    
    Examples:
    - "I want to see my grandma at 2025-10-01"
    - "Schedule a meeting tomorrow"
    - "Add doctor appointment next week"
    - "Remind me to call mom on Friday"
    
    Args:
        event_name (str) : name or description of the event/activity
        datetime (datetime) : when the event should occur
    Returns:
        str : confirmation message that event was added
    """
    return f"Successfully added '{event_name}' to calendar at {datetime}"

@tool()
def check_stock_index(index:str)->str:
    """Get current stock price and information by ticker symbol
    
    Use this tool when users want to check stock prices, get market data,
    track investments, or analyze financial performance of companies.
    
    Keywords: stock, price, ticker, market, investment, finance, shares,
    equity, trading, portfolio, company, NASDAQ, NYSE, check, lookup
    Category: finance
    
    Examples:
    - "How is Apple stock doing?"
    - "Check the price of TSLA"
    - "What's the current value of Microsoft shares?"
    - "Look up GOOGL stock price"
    
    Args:
        index (str) : stock ticker symbol (e.g., AAPL, TSLA, MSFT)
    Returns:
        str : current stock information and price data
    """
    return index