from datetime import datetime, timedelta
from logger import *

def get_past_date_symbols(symbol, num_months):
    result = []
    today = datetime.now()

    for i in range(num_months):
        # Calculate start and end dates for each month
        end_date = today.replace(day=1) - timedelta(days=1)
        start_date = end_date.replace(day=1)

        # Format the dates as per your requirement
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # Create the symbol using the last three characters of the month abbreviation and last two digits of the year
        symbol_date_str = end_date.strftime("%b%y").upper()
        symbol_str = f"{symbol}{symbol_date_str}FUT"

        # Add the result to the list
        result.append({
            "start_date": start_date_str,
            "end_date": end_date_str,
            "symbol": symbol_str,
            "month" : symbol_date_str
        })

        # Move to the previous month
        today = start_date
    return result

def get_past_dates(num_months):
    today = datetime.now()
    return get_past_date_symbols(today, num_months)

def get_past_dates(start_date, num_months):  
    today = start_date
    result = []
    result.append({
        "start_date": today.replace(day=1).strftime("%Y-%m-%d"),
        "end_date": today.strftime("%Y-%m-%d"),
        "month": today.strftime("%b%y").upper()
    })   
    if num_months <= 1:
        return result

    for i in range(num_months):  # Add 1 to include the current month
        # Calculate start and end dates for each month
        end_date = today.replace(day=1) - timedelta(days=1)
        start_date = end_date.replace(day=1)

        # Format the dates as per your requirement
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # Create the symbol using the last three characters of the month abbreviation and last two digits of the year
        symbol_date_str = end_date.strftime("%b%y").upper()

        # Add the result to the list
        result.append({
            "start_date": start_date_str,
            "end_date": end_date_str,
            "month" : symbol_date_str
        })

        # Move to the previous month
        today = start_date

    return result

# Define your process method
def do_process(entry):
    # Replace this with your actual processing logic
    print(f"Custom processing data for {entry['month']} - {entry['start_date']} to {entry['end_date']}")

def process_all(result, process_method):
    for entry in result:
        process_method(entry)

if __name__ == '__main__':
    # Example usage
    current_date = datetime.now()
    start_date = datetime(current_date.year, current_date.month, 1) - timedelta(days=1)
    dates = get_past_dates(start_date, 6)   
    process_all(dates, do_process)