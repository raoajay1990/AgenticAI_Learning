import datetime
from langchain.agents import tool

@tool
def check_system_time(format : str = "%Y-%m-%d %H:%M:%S"):
    """Retuns the current date and time"""

    current_time  = datetime.datetime.now()

    return current_time