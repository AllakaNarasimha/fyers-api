import pandas as pd
from datetime import  *
from fut_utils import *
from past_dates import *
from logger import *

def update_symbol_to_date(dates, symbols) :
    res = []
    #syms = pd.DataFrame(symbols, columns=None)
    for i, sym in symbols.iterrows():
        for dt in dates:    
            c_dt = dt.copy()
            c_dt['symbol'] = sym['symbol']
            c_dt['strike_price'] = sym['strike_price']            
            c_dt['symbol_info'] = sym['symbol_info']
            res.append(c_dt)
    return res            

def process_all(dates, symbols, process, savedf) :
    dfs = []
    dates = update_symbol_to_date(dates, symbols)
    for dt in dates:
        df = process(dt)
        if not df.empty :            
            df['symbol'] = dt['symbol']
            df['symbol_info'] = dt['symbol_info']
            df['strike_price'] = dt['strike_price']
            dt = {
                "dt" : dt,
                "symbol" : dt["symbol"].replace("NSE:", ""),
                "symbol_info" : dt['symbol_info'],
                "strike_price" : dt['strike_price'],
                "df" : df                
            }  
            if savedf :          
                savedf(dt) 
            dfs.append(dt)  
    return dfs

def merge_df(dataframes):
    # Extract the DataFrames from the list
    dfs = [entry["df"] for entry in dataframes if not entry['df'].empty]
    if not dfs:
        return {
            "min_close" : 0,
            "max_close" : 0
        }
    # Concatenate the list of DataFrames into a single DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)

    # Find the minimum and maximum values of the "Close" column
    min_close = combined_df['close'].min()
    max_close = combined_df['close'].max()
    
    return {        
        "min_close" : min_close,
        "max_close" : max_close
    }
    
def test(dt):
    print(dt)
        

if __name__ == '__main__':
    # Example usage:
    start_date_str = "2023-01-01"
    end_date_str = "2023-12-31"
    today_date_str = datetime.now().strftime('%Y-%m-%d')
    symbol = "NSE:BANKNIFTY"
    res = get_active_expires(symbol, today_date_str, 3) 
    dates = get_past_dates(6)    
    process_all(dates, res,  test)