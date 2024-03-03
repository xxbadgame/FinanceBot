import time
import json
import numpy as np
from Indicateurs import *
from HistoricalBitget import *
import pandas as pd
import datetime

hd = HistoricalBitget()
df = hd.fetch_bitget_candles()
DataFive = []
startTrade = False
breakeven_reached = False

def SimulationBot(df):
    global DataFive, last_added_minute, startTrade, breakeven_reached
    dfSimulation = pd.DataFrame(columns=["Time", "Open", "High", "Low", "Close", "Volume", "WILLIAMS_R", "RSI", "MME", "BBANDS"])

    for i in range(0, len(df)):
        dfSimulation = pd.concat([dfSimulation, pd.DataFrame([df.iloc[i]])], ignore_index=True)
        
        timestamp_ms = int(df.iloc[i].name.timestamp() * 1000)
        Time = datetime.datetime.utcfromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
        Open = df['Open'].iloc[i]
        High = df['High'].iloc[i]
        Low = df['Low'].iloc[i]
        Close = df['Close'].iloc[i]
        Volume = df['Volume'].iloc[i]

        DataFive.append([Time, Open, High, Low, Close, Volume])

        # Garder seulement les deux dernières entrées pour comparaison
        DataFive = DataFive[-2:]

        try :
            print(DataFive[1])
        except:
            pass

        if len(dfSimulation) > 14: 
       
            RSI = Indicateurs().RSI(dfSimulation['Close'].tolist())[-1]
            MME = Indicateurs().MME(dfSimulation['Close'].tolist())
            BBANDS = Indicateurs().BBANDS(dfSimulation['Close'].tolist())
            WILLIAM_R = Indicateurs().WILLIAMS(dfSimulation['High'].tolist(), dfSimulation['Low'].tolist(), dfSimulation['Close'].tolist())
            
            print(dfSimulation)

            print("RSI: ", RSI)
            print("MME: ", MME)
            print("BBANDS: ", BBANDS)
            print("MedianBands: ", np.median(BBANDS))
            print("WILLIAMS_R: ", WILLIAM_R)
        
            dfSimulation.loc[dfSimulation.index[-1], 'RSI'] = RSI
            dfSimulation.loc[dfSimulation.index[-1], 'MME'] = MME 
            dfSimulation.loc[dfSimulation.index[-1], 'WILLIAMS_R'] = WILLIAM_R
            dfSimulation.at[dfSimulation.index[-1], 'BBANDS'] = BBANDS


            DernierClose = dfSimulation['Close'].iloc[-1]
            AvantDernierClose = dfSimulation['Close'].iloc[-2]
            MedianBands = np.median(BBANDS)
            
            ############### Achat ###############  

            if dfSimulation['WILLIAMS_R'].iloc[-1] > -80:
                startTrade = False
                if dfSimulation['RSI'].iloc[-2] < 30 and \
                dfSimulation['MME'].iloc[-2] > AvantDernierClose and \
                dfSimulation['BBANDS'].iloc[-2][1] > AvantDernierClose and \
                dfSimulation['WILLIAMS_R'].iloc[-2] < -80:
                        startTrade = True
                        print("")
                        print("Achat")
                        print("Prix de fermeture : ", DernierClose, "RSI: ", RSI, "MME: ", MME, "BBANDS: ", BBANDS, "WILLIAMS: ", dfSimulation['WILLIAMS_R'].iloc[-2], "Time: ", Time)
                
            ############### Vente ###############      
            
            if dfSimulation['WILLIAMS_R'].iloc[-1] < -20:
                startTrade = False
                if dfSimulation['RSI'].iloc[-2] > 70 and \
                dfSimulation['MME'].iloc[-2] < AvantDernierClose and \
                dfSimulation['BBANDS'].iloc[-2][0] < AvantDernierClose and \
                dfSimulation['WILLIAMS_R'].iloc[-2] > -20:
                        startTrade = True
                        print("")
                        print("Vente")
                        print("Prix de fermeture : ", DernierClose, "RSI: ", RSI, "MME: ", MME, "BBANDS: ", BBANDS, "WILLIAMS: ", dfSimulation['WILLIAMS_R'].iloc[-2], "Time: ", Time)
       
            ########################################

        else:
            print("Pas assez de données pour calculer les indicateurs")

        time.sleep(0.1)
        # Ajustement pour la conversion des types après l'ajout des données
        dfSimulation['Open'] = dfSimulation['Open'].astype(float)
        dfSimulation['High'] = dfSimulation['High'].astype(float)
        dfSimulation['Low'] = dfSimulation['Low'].astype(float)
        dfSimulation['Close'] = dfSimulation['Close'].astype(float)
        dfSimulation['Volume'] = dfSimulation['Volume'].astype(float)

        print("")



SimulationBot(df)