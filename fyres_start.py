import webbrowser
import pandas as pd
import os
import sys
from fyers_apiv3 import fyersModel
from fyres_downloader import *
from https_listener import *
from datetime import datetime
from option_prices import *
from config import *
from logger import *

#### Generate an authcode and then make a request to generate an accessToken (Login Flow)
config = get_config("config.csv")    
redirect_uri= config["redirect_uri"]                     ## redircet_uri you entered while creating APP.
client_id = config["client_id"]                                        ## Client_id here refers to APP_ID of the created app
secret_key = config["secret_key"]                                          ## app_secret key which you got after creating the app 
grant_type = config["grant_type"]                  ## The grant_type always has to be "authorization_code"
response_type = config["response_type"]                             ## The response_type always has to be "code"
state = config["state"]    
appSession = fyersModel.SessionModel(client_id = client_id, redirect_uri = redirect_uri,response_type=response_type,state=state,secret_key=secret_key,grant_type=grant_type)    
global fyers
fyers = None

def generate_auth_token() :
    generateTokenUrl = appSession.generate_authcode()
    print((generateTokenUrl))  
    webbrowser.open(generateTokenUrl,new=1)
    start_server()    
    
def generate_access_token(ath_code):        
    appSession.set_token(ath_code)
    response = appSession.generate_token()
    try: 
        access_token =  response["access_token"]   
        save_text_to_file("access_token.txt", access_token)     
    except Exception as e:
        print(e,response)
    set_fyers_model(access_token)
    process_download()
    
def set_fyers_model(access_token):
    global fyers 
    try:
        fyers = fyersModel.FyersModel(token=access_token,is_async=False,client_id=client_id,log_path="/home/downloads/")
        profile = fyers.get_profile()
        print(profile)
        if profile['s'] == 'error':
            return False
    except Exception as e:
        print(e, access_token)
        return False
    return True 
    
def process_download():    
    res = process_fut_download()
    current_date = datetime.now()
    start_date = datetime(current_date.year, current_date.month, 1) - timedelta(days=1)
    dates = get_past_dates(datetime.now(), 8)    
    dfs = process_all(dates, res,  start_process, save_df)
    print(len(dfs))
    save_result(current_date, dfs, "FUT")
    res = process_options_download(dfs)
    dfs = process_all(dates, res,  start_process, save_df)
    print(len(dfs))
    save_result(current_date, dfs, "OPTIONS")
    
def save_result(current_date, dts, sym):
    result_df = get_result_dfs(dts)
    result_file_path = os.path.join("data", current_date.strftime("%d%m%Y_%H%M%S_INDEX_{}.CSV".format(sym)))
    result_df.to_csv(result_file_path)
    
def get_result_dfs(dts):
    rows = []    
    for dt in dts:        
        row_data = {
            'start_date': dt['dt']['start_date'],
            'end_date': dt['dt']['end_date'],
            'month': dt['dt']['month'],
            'symbol': dt['dt']['symbol'],
            'symbol_info': dt['symbol_info'],
            'strike_price': dt['strike_price']
        }
        rows.append(row_data) 
    df = pd.DataFrame(rows)    
    return df
    
def process_fut_download():
    today_date_str = datetime.now().strftime('%Y-%m-%d')
    symbol = "BANKNIFTY"
    res = get_active_futures(symbol) 
    return res
    
def process_options_download(dfs):
    symbol = "BANKNIFTY"
    df = merge_df(dfs)
    res = get_options_by_range(symbol, df['min_close'], df['max_close'])
    return res

def save_df(d):
    df = d["df"]
    dt = d["dt"]
    sym = d["symbol_info"]
    strike = round(d["strike_price"])
    # Check if strike is equal to -1
    if strike == -1:
        strike = "FUT"
    # Ensure the directory exists
    directory = os.path.join("data", dt["month"], str(strike))
    os.makedirs(directory, exist_ok=True)

    df.to_csv(os.path.join(directory, f"{sym}.csv"))
        
def start_process(dt) :
    return historical_bydate(dt['symbol'], dt['start_date'], dt['end_date'])
    
def historical_bydate(symbol,sd,ed, interval = 1):
    global fyers
    data = {"symbol":symbol, "resolution":"1","date_format":"1","range_from":str(sd),"range_to":str(ed),"cont_flag":"1"}
    nx = fyers.history(data)
    if nx['s'] == 'error':
        print("{}, {}".format(nx, data))
        return pd.DataFrame()
    if nx['s'] == 'no_data' :
        print('no data: {}'.format(data))
        return pd.DataFrame()        
    if nx :
        print('data: {}'.format(data))
        return formated_df(nx)        
    return pd.DataFrame()

def formated_df(nx):
    cols = ['datetime','open','high','low','close','volume']
    df = pd.DataFrame.from_dict(nx['candles'])
    df.columns = cols
    df['datetime'] = pd.to_datetime(df['datetime'],unit = "s")
    df['datetime'] = df['datetime'].dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata')
    df['datetime'] = df['datetime'].dt.tz_localize(None)    
    df = df.set_index('datetime')   
    return df

if __name__ == '__main__':  
    access_token = read_text_from_file("access_token.txt")
    if access_token:
        if set_fyers_model(access_token) == False :
            generate_auth_token()
        else:
            process_download()
    else:        
        generate_auth_token()  
    sys.exit()     