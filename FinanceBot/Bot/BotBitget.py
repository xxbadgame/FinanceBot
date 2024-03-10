import websocket
import json
import pandas as pd
import datetime
from Indicateurs import *
import numpy as np
import requests


# Configuration initiale pour la requête API
url = "https://api.bitget.com/api/v2/mix/market/history-candles"
params = {
    "symbol": "BTCUSDT",
    "granularity": "1m",  
    "productType": "usdt-futures",
    "limit": 14,
}

# Effectuer la requête
response = requests.get(url, params=params)
data = response.json().get('data', [])

# Préparer les données pour le DataFrame
rows = []  # Cette liste va contenir les dictionnaires pour chaque ligne du DataFrame

for candle in data:
    dicoCandle = {
        "Time": pd.to_datetime(int(candle[0]), unit='ms'),
        "Open": float(candle[1]),
        "High": float(candle[2]),
        "Low": float(candle[3]),
        "Close": float(candle[4]),
        "Volume": float(candle[5]),
        "WILLIAMS_R": 0.0,
        "RSI": 0.0,
        "MME": 0.0,
        "BBANDS": (0.0, 0.0)  # En supposant que BBANDS est un tuple de deux zéros
    }
    rows.append(dicoCandle)

# Créer le DataFrame directement à partir de la liste des dictionnaires
df = pd.DataFrame(rows)

print(df)


DataFive = []
startTradeAchat = False
startTradeVente = False
breakeven = False
newStopLoss = False
bougieEntree = None
last_added_minute = None

def on_message(ws, message):
    global df, DataFive, last_added_minute, startTradeAchat, startTradeVente, breakeven, newStopLoss, bougieEntree
    data = json.loads(message)
    if data.get("action") == "update":
        candle_data = data.get("data")[0]

        timestamp_ms = int(candle_data[0])
        Time = datetime.datetime.utcfromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
        Open, High, Low, Close, Volume = map(float, candle_data[1:6])

        DataFive.append([Time,Open, High, Low, Close, Volume])

        # Garder seulement les deux dernières entrées pour comparaison
        DataFive = DataFive[-2:]
        try:
            BougieActuelle = DataFive[1]
        except:
            pass
        
        
        try :
            print(BougieActuelle)
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
                
                print("RSI: ", RSI)
                print("MME: ", MME)
                print("BBANDS: ", BBANDS)
                print("MedianBands: ", np.median(BBANDS))
                print("WILLIAMS_R: ", WILLIAM_R)

                df.loc[df.index[-1], 'RSI'] = RSI
                df.loc[df.index[-1], 'MME'] = MME 
                df.loc[df.index[-1], 'WILLIAMS_R'] = WILLIAM_R
                df.at[df.index[-1], 'BBANDS'] = BBANDS
                
                print(df)    
                
                PointEntree = df['Close'].iloc[-1]
                AvantPointEntree = df['Close'].iloc[-2]
                MedianBands = np.median(BBANDS)
            
            
                ############### Achat ###############  
                
                #df['BBANDS'].iloc[-2][1] > AvantPointEntree and \ df['MME'].iloc[-2] > AvantPointEntree and \ if df['RSI'].iloc[-2] < 40 and \
    
                if df['WILLIAMS_R'].iloc[-1] > -80 and startTradeAchat == False:
                    if df['WILLIAMS_R'].iloc[-2] < -80:
                            startTradeAchat = True
                            signal = f"Achat : {Time}"
                            with open("FinanceBot\Bot\signal.txt", "w") as file:
                                file.write(signal)
                            print("")
                            print("Achat")
                            print("RSI: ", RSI, "MME: ", MME, "BBANDS: ", BBANDS, "WILLIAMS: ", df['WILLIAMS_R'].iloc[-2], "Time: ", Time)
                       
                            bougieEntree = BougieActuelle
                            TailleBougieEntree = Open - Close
                            PointEntree = Close

                                
                    """ # Stop Loss primaire
                    if PointEntree-TailleBougieEntree/2 > PointEntree-Low and breakeven == False:
                        print(f"Stop Loss, -{PointEntree - TailleBougieEntree/2}€")
                        startTrade = False
                    
                    # Logique Breakeven, Trade Gratuit
                    elif High > PointEntree + 60 and newStopLoss == False:
                        print("Breakeven")
                        breakeven = True
                    elif Close > PointEntree + 60 and breakeven and newStopLoss == False:
                        print("Entre breakeven et newStopLoss, attendre...")
                    elif Close < PointEntree + 60 and breakeven and newStopLoss == False:
                        print("Retour breakeven, +0€")
                        startTrade = False
                        
                    # Logique New Stop Loss, Trade partiel mais gaganant
                    elif High > MedianBands and breakeven and newStopLoss == False:
                        print("Nouveau Stop Loss")
                        newStopLoss = True
                    elif Close > MedianBands and breakeven and newStopLoss:
                        print("Entre newStopLoss et Cloture Trade complet, attendre...")
                    elif Close < MedianBands and newStopLoss:
                        print(f"Retour New Stop Loss, +{PointEntree - MedianBands}€")
                        startTrade = False
                        
                    # Logique Cloture Trade complet
                    elif Close > BBANDS[1] and newStopLoss:
                        print(f"Cloture Trade complet +{PointEntree - BBANDS[1]}€")
                        startTrade = False

                    # Trade en cours
                    else:
                        print("En cours...") """
                           
                ############### Vente ###############      
                
                #df['MME'].iloc[-2] < AvantPointEntree and \ df['BBANDS'].iloc[-2][0] < AvantPointEntree and \ if df['RSI'].iloc[-2] > 60 and \
                
                if df['WILLIAMS_R'].iloc[-1] < -20 and startTradeVente == False:
                    if df['WILLIAMS_R'].iloc[-2] > -20:
                            startTradeVente = True
                            signal = f"Vente : {Time} "
                            with open("FinanceBot\Bot\signal.txt", "w") as file:
                                file.write(signal)
                            print("")
                            print("Vente")
                            print("Prix de fermeture : ", PointEntree, "RSI: ", RSI, "MME: ", MME, "BBANDS: ", BBANDS, "WILLIAMS: ", df['WILLIAMS_R'].iloc[-2], "Time: ", Time)
                    
                        
                    """ # Stop Loss primaire
                    if PointEntree+TailleBougieEntree/2 < PointEntree-High and breakeven == False:
                        print(f"Stop Loss, -{PointEntree + TailleBougieEntree/2}€")
                        startTrade = False
                    
                    # Logique Breakeven, Trade Gratuit
                    elif Low < PointEntree - 60 and newStopLoss == False:
                        print("Breakeven")
                        breakeven = True
                    elif Close < PointEntree - 60 and breakeven and newStopLoss == False:
                        print("Entre breakeven et newStopLoss, attendre...")
                    elif Close > PointEntree - 60 and breakeven and newStopLoss == False:
                        print("Retour breakeven, +0€")
                        startTrade = False
                        
                    # Logique New Stop Loss, Trade partiel mais gaganant
                    elif Low < MedianBands and breakeven and newStopLoss == False:
                        print("Nouveau Stop Loss")
                        newStopLoss = True
                    elif Close < MedianBands and breakeven and newStopLoss:
                        print("Entre newStopLoss et Cloture Trade complet, attendre...")
                    elif Close > MedianBands and newStopLoss:
                        print(f"Retour New Stop Loss, +{MedianBands - PointEntree}€")
                        startTrade = False
                        
                    # Logique Cloture Trade complet
                    elif Close < BBANDS[0] and newStopLoss:
                        print(f"Cloture Trade complet +{BBANDS[0] - PointEntree}€")
                        startTrade = False 

                    # Trade en cours
                    else:
                        print("En cours...")
                    """
                    
                ####################################
            else:
                df.loc[df.index[-1], 'RSI'] = 0
                df.loc[df.index[-1], 'MME'] = 0                
                df.loc[df.index[-1], 'WILLIAMS_R'] = 0
                df.at[df.index[-1], 'BBANDS'] = (0,0)
                print(df)
        
        if len(df) > 16:
            if startTradeAchat :
                        if Close > Open + 30:
                            print("Trade fini")
                            startTradeAchat = False
                        else:
                            print("Trade en cours...")          
                            
            if startTradeVente :
                        if Close < Open - 30:
                            print("Trade fini")
                            startTradeVente = False
                        else:
                            print("Trade en cours...")     
        
                
    
         
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
    # if isinstance(error, Exception):
    #     import traceback
    #     traceback.print_exc()

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