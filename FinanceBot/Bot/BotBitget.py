import websocket
import json
import pandas as pd
import datetime
from datetime import timezone
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
TailleBougieEntree = None
PointEntree = None
last_added_minute = None

def on_message(ws, message):
    global df, DataFive, last_added_minute, startTradeAchat, startTradeVente, breakeven, newStopLoss, TailleBougieEntree, PointEntree
    data = json.loads(message)
    if data.get("action") == "update":
        candle_data = data.get("data")[0]

        timestamp_ms = int(candle_data[0])
        timestamp_ms = 1623215223000  # Example timestamp in milliseconds
        time_utc = datetime.datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        Time = time_utc.strftime('%Y-%m-%d %H:%M:%S')
        Open, High, Low, Close, Volume = map(float, candle_data[1:6])

        DataFive.append([Time,Open, High, Low, Close, Volume])

        # Garder seulement les deux dernières entrées pour comparaison
        DataFive = DataFive[-2:]
        
        try:
            BougieActuelle = DataFive[1]
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
                
                AvantPointEntree = df['Close'].iloc[-2]
                MedianBands = np.median(BBANDS)
            
                if len(df) > 16: 
            
                    ############### Achat ###############  
        
                    if df['WILLIAMS_R'].iloc[-1] > -80 and \
                    df['WILLIAMS_R'].iloc[-2] < -80 and \
                    df['BBANDS'].iloc[-2][1] > AvantPointEntree and \
                    df['RSI'].iloc[-2] < 30 :
                    
                    #if df['WILLIAMS_R'].iloc[-1] > -80 and df['WILLIAMS_R'].iloc[-2] < -80:
                            
                        startTradeAchat = True
                            
                        with open("FinanceBot\Bot\signal.txt", "w") as file:
                            file.write(f"Achat : {Time}")
                        
                        print("")
                        print("Achat")
                        print("RSI: ", RSI, "MME: ", MME, "BBANDS: ", BBANDS, "WILLIAMS: ", df['WILLIAMS_R'].iloc[-2], "Time: ", Time)
                        print("")
                        TailleBougieEntree = abs(df['Close'].iloc[-1] - df['Open'].iloc[-1])
                        PointEntree = df['Close'].iloc[-1]
                        
                            
                    ############### Vente ###############      
                    
                      
                    
                    if df['WILLIAMS_R'].iloc[-1] < -20 and \
                    df['WILLIAMS_R'].iloc[-2] > -20 and \
                    df['BBANDS'].iloc[-2][0] < AvantPointEntree and \
                    df['RSI'].iloc[-2] > 70 :
                    
                    #if df['WILLIAMS_R'].iloc[-1] < -20 and df['WILLIAMS_R'].iloc[-2] > -20:    
                    
                        startTradeVente = True
                        
                        with open("FinanceBot\Bot\signal.txt", "w") as file:
                            file.write(f"Vente : {Time}")
                            
                        print("")
                        print("Vente")
                        print("Prix de fermeture : ", PointEntree, "RSI: ", RSI, "MME: ", MME, "BBANDS: ", BBANDS, "WILLIAMS: ", df['WILLIAMS_R'].iloc[-2], "Time: ", Time)
                        print("")
                        TailleBougieEntree = abs(df['Close'].iloc[-1] - df['Open'].iloc[-1])
                        PointEntree = df['Close'].iloc[-1]
                        
                        
                    ########################################
            else:
                df.loc[df.index[-1], 'RSI'] = 0
                df.loc[df.index[-1], 'MME'] = 0                
                df.loc[df.index[-1], 'WILLIAMS_R'] = 0
                df.at[df.index[-1], 'BBANDS'] = (0,0)
                print(df)
                
        ### Les trades en cours : Achat et Vente ###

        if len(df) > 15 and TailleBougieEntree != None and PointEntree != None:

            MedianBands = np.median(df['BBANDS'].iloc[-1])
            
            print("")
            print("Taille de la bougie d'entrée : ", TailleBougieEntree)
            print("Point d'entrée : ", PointEntree)
            print("Médiane des bandes de Bollinger : ", MedianBands)
            print("Open : ", Open)  
            print("Close : ", Close)
            print("High : ", High)
            print("Low : ", Low)
            print("")
        
                        
            if startTradeAchat :
                with open("FinanceBot\Bot\signal.txt", "a") as file:   
                    # Stop Loss primaire
                    if PointEntree-abs(TailleBougieEntree/2) > Low and breakeven == False:
                        file.write(f"Stop Loss, -{abs(TailleBougieEntree/2)}€")
                        print(f"Stop Loss, -{abs(TailleBougieEntree/2)}€")
                        startTradeAchat = False
                        TailleBougieEntree = None
                        PointEntree = None
                    
                    # Logique Breakeven, Trade Gratuit
                    elif High > PointEntree + 60 and breakeven == False and newStopLoss == False:
                        file.write("Breakeven")
                        print("Breakeven")
                        breakeven = True
                    elif Close > PointEntree + 60 and breakeven and newStopLoss == False:
                        #file.write("Entre breakeven et newStopLoss, attendre...")
                        print("Entre breakeven et newStopLoss, attendre...")
                    elif Close < PointEntree + 60 and breakeven and newStopLoss == False:
                        file.write("Retour breakeven, +0€")
                        print("Retour breakeven, +0€")
                        startTradeAchat = False
                        breakeven = False
                        TailleBougieEntree = None
                        PointEntree = None
                        
                    # Logique New Stop Loss, Trade partiel mais gaganant
                    elif High > MedianBands and breakeven and newStopLoss == False:
                        file.write("Nouveau Stop Loss")
                        print("Nouveau Stop Loss")
                        newStopLoss = True
                    elif Close > MedianBands and breakeven and newStopLoss:
                        #file.write("Entre newStopLoss et Cloture Trade complet, attendre...")
                        print("Entre newStopLoss et Cloture Trade complet, attendre...")
                    elif Close < MedianBands and newStopLoss:
                        file.write(f"Retour New Stop Loss, +{PointEntree - MedianBands}€")
                        print(f"Retour New Stop Loss, +{PointEntree - MedianBands}€")
                        startTradeAchat = False
                        breakeven = False
                        newStopLoss = False
                        TailleBougieEntree = None
                        PointEntree = None
                        
                    # Logique Cloture Trade complet
                    elif Close > df['BBANDS'].iloc[-1][1] and newStopLoss:
                        file.write(f"Cloture Trade complet +{PointEntree - df['BBANDS'].iloc[-1][1]}€")
                        print(f"Cloture Trade complet +{PointEntree - df['BBANDS'].iloc[-1][1]}€")
                        startTradeAchat = False
                        breakeven = False
                        newStopLoss = False
                        TailleBougieEntree = None
                        PointEntree = None

                    # Trade en cours
                    else:   
                        print("En cours...")     
                            
                            
            if startTradeVente : 
                with open("FinanceBot\Bot\signal.txt", "a") as file:
                    # Stop Loss primaire
                    if PointEntree+abs(TailleBougieEntree/2) < High and breakeven == False:
                        file.write(f"Stop Loss, -{abs(TailleBougieEntree/2)}€")
                        print(f"Stop Loss, -{abs(TailleBougieEntree/2)}€")
                        startTradeVente = False
                        TailleBougieEntree = None
                        PointEntree = None
                    
                    # Logique Breakeven, Trade Gratuit
                    elif Low < PointEntree - 60 and breakeven == False and newStopLoss == False:
                        file.write("Breakeven")
                        print("Breakeven")
                        breakeven = True
                    elif Close < PointEntree - 60 and breakeven and newStopLoss == False:
                        #file.write("Entre breakeven et newStopLoss, attendre...")
                        print("Entre breakeven et newStopLoss, attendre...")
                    elif Close > PointEntree - 60 and breakeven and newStopLoss == False:
                        file.write("Retour breakeven, +0€")
                        print("Retour breakeven, +0€")
                        startTradeVente = False
                        breakeven = False
                        TailleBougieEntree = None
                        PointEntree = None
                        
                    # Logique New Stop Loss, Trade partiel mais gaganant
                    elif Low < MedianBands and breakeven and newStopLoss == False:
                        file.write("Nouveau Stop Loss")
                        print("Nouveau Stop Loss")
                        newStopLoss = True
                    elif Close < MedianBands and breakeven and newStopLoss:
                        #file.write("Entre newStopLoss et Cloture Trade complet, attendre...")
                        print("Entre newStopLoss et Cloture Trade complet, attendre...")
                    elif Close > MedianBands and newStopLoss:
                        file.write(f"Retour New Stop Loss, +{MedianBands - PointEntree}€")
                        print(f"Retour New Stop Loss, +{MedianBands - PointEntree}€")
                        startTradeVente = False
                        breakeven = False
                        newStopLoss = False
                        TailleBougieEntree = None
                        PointEntree = None
                        
                    # Logique Cloture Trade complet
                    elif Close < df['BBANDS'].iloc[-1][0] and newStopLoss:
                        file.write(f"Cloture Trade complet +{df['BBANDS'].iloc[-1][0] - PointEntree}€")
                        print(f"Cloture Trade complet +{df['BBANDS'].iloc[-1][0] - PointEntree}€")
                        startTradeVente = False
                        breakeven = False
                        newStopLoss = False
                        TailleBougieEntree = None
                        PointEntree = None

                    # Trade en cours
                    else:
                        print("En cours...")
        
                
    
         
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
    from datetime import datetime  # Ajoutez ceci en haut de votre fichier si ce n'est pas déjà fait
    print(error)
    with open("FinanceBot/Bot/logs.txt", "w") as fileDebug:
        # Obtenez l'heure actuelle
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(error, Exception):
            import traceback
            # Écrire l'erreur avec l'horodatage
            fileDebug.write(f"{current_time} - {traceback.format_exc()}")
        else:
            # Si l'erreur n'est pas une instance d'Exception, écrivez l'erreur directement avec un horodatage.
            fileDebug.write(f"{current_time} - {error}\n")

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