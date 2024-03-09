import websocket
import json
import pandas as pd
import datetime
from Indicateurs import *
import numpy as np


df = pd.DataFrame(columns=["Time", "Open", "High", "Low", "Close", "Volume", "WILLIAMS_R", "RSI", "MME", "BBANDS"])
DataFive = []
startTrade = False
breakeven_reached = False

# Variable pour suivre la dernière minute ajoutée à df
last_added_minute = None

def on_message(ws, message):
    global df, DataFive, last_added_minute, startTrade, breakeven_reached
    data = json.loads(message)
    if data.get("action") == "update":
        candle_data = data.get("data")[0]

        timestamp_ms = int(candle_data[0])
        Time = datetime.datetime.utcfromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
        Open, High, Low, Close, Volume = candle_data[1:6]

        DataFive.append([Time, Open, High, Low, Close, Volume])

        # Garder seulement les deux dernières entrées pour comparaison
        DataFive = DataFive[-2:]
        
        try :
            print(DataFive[1])
        except:
            pass

        current_candle_minute = datetime.datetime.strptime(Time, '%Y-%m-%d %H:%M:%S').minute

        
        # Vérifier si la minute actuelle est différente de la dernière minute ajoutée
        if last_added_minute is not None and current_candle_minute != last_added_minute:
            # Ajouter la dernière valeur de la minute précédente
            last_candle = DataFive[-2]  # Prend la dernière valeur de la minute précédente
            new_row = {
                "Time": last_candle[0], "Open": float(last_candle[1]), "High": float(last_candle[2]),
                "Low": float(last_candle[3]), "Close": float(last_candle[4]), "Volume": float(last_candle[5])
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Vérifie si suffisamment de données pour les indicateurs
            if len(df) > 14: 

                RSI = Indicateurs().RSI(df['Close'].tolist())[-1]
                MME = Indicateurs().MME(df['Close'].tolist())
                BBANDS = Indicateurs().BBANDS(df['Close'].tolist())
                WILLIAM_R = Indicateurs().WILLIAMS(df['High'].tolist(), df['Low'].tolist(), df['Close'].tolist())
            
                print(df)
                
                print("RSI: ", RSI)
                print("MME: ", MME)
                print("BBANDS: ", BBANDS)
                print("MedianBands: ", np.median(BBANDS))
                print("WILLIAMS_R: ", WILLIAM_R)

                df.loc[df.index[-1], 'RSI'] = RSI
                df.loc[df.index[-1], 'MME'] = MME 
                df.loc[df.index[-1], 'WILLIAMS_R'] = WILLIAM_R
                df.at[df.index[-1], 'BBANDS'] = BBANDS
                    
                DernierClose = df['Close'].iloc[-1]
                AvantDernierClose = df['Close'].iloc[-2]
                MedianBands = np.median(BBANDS)
            
            
                ############### Achat ###############  
    
                if df['WILLIAMS_R'].iloc[-1] > -80:
                    startTrade = False
                    # 40 pour tester 
                    if df['RSI'].iloc[-2] < 30 and \
                    df['MME'].iloc[-2] > AvantDernierClose and \
                    df['BBANDS'].iloc[-2][1] > AvantDernierClose and \
                    df['WILLIAMS_R'].iloc[-2] < -80:
                            startTrade = True
                            signal = f"Achat : {Time}"
                            with open("FinanceBot\Bot\signal.txt", "w") as file:
                                file.write(signal)
                            print("")
                            print("Achat")
                            print("Prix de fermeture : ", DernierClose, "RSI: ", RSI, "MME: ", MME, "BBANDS: ", BBANDS, "WILLIAMS: ", df['WILLIAMS_R'].iloc[-2], "Time: ", Time)
                       
            
                ### Effectuer des actions pendant le trade ###
                # Si dans les bougies post achat : une bougie atteint tailleBougieEntrer/2 alors stop loss
                # Si dans les bougies post achat : une bougie atteint clotureAchat + 60 alors breakeven
                # Si dans les bougies post achat : une bougie atteint la médiane des bandes de Bollinger alors nouveau stop loss
                # Si dans les bougies post achat : une bougie atteint la bande supérieure de Bollinger alors cloture trade
                           
                ############### Vente ###############      
                
                if df['WILLIAMS_R'].iloc[-1] < -20:
                    startTrade = False
                    # 60 pour tester
                    if df['RSI'].iloc[-2] > 70 and \
                    df['MME'].iloc[-2] < AvantDernierClose and \
                    df['BBANDS'].iloc[-2][0] < AvantDernierClose and \
                    df['WILLIAMS_R'].iloc[-2] > -20:
                            startTrade = True
                            signal = f"Vente : {Time} "
                            with open("FinanceBot\Bot\signal.txt", "w") as file:
                                file.write(signal)
                            print("")
                            print("Vente")
                            print("Prix de fermeture : ", DernierClose, "RSI: ", RSI, "MME: ", MME, "BBANDS: ", BBANDS, "WILLIAMS: ", df['WILLIAMS_R'].iloc[-2], "Time: ", Time)
                    
                ####################################
            else:
                df.loc[df.index[-1], 'RSI'] = 0
                df.loc[df.index[-1], 'MME'] = 0                
                df.loc[df.index[-1], 'WILLIAMS_R'] = 0
                df.at[df.index[-1], 'BBANDS'] = (0,0)
                print(df)
                
    
         
        # Mise à jour de la dernière minute ajoutée
        last_added_minute = current_candle_minute
        
        # Ajustement pour la conversion des types après l'ajout des données
        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(float)
        
        print("")
    

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    # Attendre avant de se reconnecter
    connect_websocket()

def on_open(ws):
    print("Connection opened")
    # S'abonner à la bougie de 1 minute pour BTCUSDT
    subscribe_message = json.dumps({
        "op": "subscribe",
        "args": [
            {
                "instType": "USDT-FUTURES",
                "channel": "candle1m",
                "instId": "BTCUSDT"
            }
        ]
    })
    ws.send(subscribe_message)

def connect_websocket():
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://ws.bitget.com/v2/ws/public",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(ping_interval=30)

if __name__ == "__main__":
    connect_websocket()