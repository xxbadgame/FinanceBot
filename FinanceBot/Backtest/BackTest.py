import json
import pandas as pd
from IndicateursBackTest import *
from HistoricalBitget import *

# voir le cas du 20 à 13:40
# plus souple sur les 10min du début, passer à 20 voir 30

hd = HistoricalBitget(IT = 15)
df = hd.fetch_bitget_candles(50000)

# Initialisation des indicateurs
indicateurs = IndicateursBackTest()
ListeRSI = indicateurs.RSI(df['Close'].to_list())
ListeMME = indicateurs.MME(df['Close'].to_list())
ListeBBANDS = indicateurs.BBANDS(df['Close'].to_list())
ListeWILLIAMS = indicateurs.WILLIAMS(df['High'].to_list(), df['Low'].to_list(), df['Close'].to_list())
ListeMedianBands = indicateurs.medianBBANDS(df['Close'].to_list())
ListeVolume = df['Volume'].to_list()
stopLoss = 0

compteurAchat = 0
compteurVente = 0
compteurBreakevenAchat = 0
compteurBreakevenVente = 0
compteurCompleteAchat = 0
compteurCompleteVente = 0
money = []
moyenneHigh = []

secure = False
Mediane = False

for i in range(len(df['Close'])):
    
    ## On veut à chaque fois tester le breakeven (SMA), si ok alors laisser courir jusqu'au trade complet peut importe le temps que ça prend car dans le pire des 
    ## cas on a fait un breakeven et donc bouger le stop loss à l'achat ou à la vente pour protéger le capital.

        
    ### Achat ###
    
    try:
        BougieEntree = df['Close'].iloc[i+1] - df['Open'].iloc[i+1]
        BougieAppelle = df['Close'].iloc[i] - df['Open'].iloc[i]
        Fibo382Achat = df['Open'].iloc[i+1] + (ListeBBANDS[i][0] - df['Open'].iloc[i+1])*0.236
        Fibo382Vente = df['Open'].iloc[i+1] - (df['Open'].iloc[i+1] - ListeBBANDS[i][1])*0.236
    except IndexError:
        print("Actuellement en recherche d'un point d'entrée")

    if ListeRSI[i] < 30 and \
    ListeMME[i] > df['Close'].iloc[i] and \
    ListeBBANDS[i][1] > df['Close'].iloc[i] and \
    ListeWILLIAMS[i] < -70:
        try:
            if ListeWILLIAMS[i+1] > -70 and BougieEntree > 0 and BougieAppelle < 0 and abs(BougieEntree) > abs(BougieAppelle):
                print("")
                print("Achat")
                compteurAchat += 1
                print("Prix de fermeture : ", df["Close"].iloc[i], "RSI: ", ListeRSI[i], "MME: ", ListeMME[i], "BBANDS: ", ListeBBANDS[i], "Mediane BBANDS : ",ListeMedianBands[i], "WILLIAMS: ", ListeWILLIAMS[i], "Time: ", df.index[i])
                
                ### V2 Risk Managment Achat : One Life Trade ###
                
                # for j in range(len(df['Close']) - i):
                #     if df['Low'].iloc[i+2+j] <= df['Close'].iloc[i+1]-100:
                #         print("Stop Loss: ", -100)
                #         money.append(-100)
                #         break
                #     elif df['High'].iloc[i+j] >= df['Close'].iloc[i+1] + 100:
                #         print("Take Profit: 100 ")
                #         money.append(100)
                #         break
                    
                ################################
                
                ### One Oportunity Trade ###
                
                
                for j in range(len(df['Close']) - i):
                    
                    # Stop Loss

                    if df['Close'].iloc[i+2] < (df['Close'].iloc[i+1]-abs(BougieEntree)*0.25) and secure == False:
                        print("Stop Loss :", df['Close'].iloc[i+2]-df['Close'].iloc[i+1])
                        money.append(df['Close'].iloc[i+2+j]-df['Close'].iloc[i+1])
                        break

                    # Take Profit si peu de puissance et positif
                    
                    elif abs(df['Close'].iloc[i+2+j]-df['Open'].iloc[i+2+j]) <= BougieEntree and secure == False:
                        if df['Close'].iloc[i+2]-df['Open'].iloc[i+2] > 0:
                            print("Peu de puissance, Take profit", df['Close'].iloc[i+2]-df['Open'].iloc[i+2])
                            money.append(df['Close'].iloc[i+2]-df['Open'].iloc[i+2])
                            break

                    # Bougie Post entrée supérieur à l'entrée
                    
                    elif abs(df['Close'].iloc[i+2]-df['Open'].iloc[i+2]) >= BougieEntree and secure == False:
                        print("Secure")
                        secure = True

                    # Si la bougie retombe sur sécure
                    
                    elif df['Low'].iloc[i+3+j] <= df['Close'].iloc[i+1]+100 and secure == True:
                        print("Secure", 100)
                        money.append(100)
                        secure = False
                        break

                    ### Mediane BBANDS atteinte
                    ### Retombe sur la médiane

                    # Trade complet si la bougie atteint la bande supérieur
                    
                    elif df['High'].iloc[i+j] >= ListeBBANDS[i][0]:
                        print("Bande supérieur atteinte : ",ListeBBANDS[i][0] - df['Close'].iloc[i+1])
                        money.append(ListeBBANDS[i][0] - df['Close'].iloc[i+1])
                        secure = False
                        break
    
                        
            
        except IndexError:
            print("Actuellement en recherche d'un point d'entrée")
            
     
    ### Vente ###      
            
    elif ListeRSI[i] > 70 and \
    ListeMME[i] < df['Close'].iloc[i] and \
    ListeBBANDS[i][0] < df['Close'].iloc[i] and \
    ListeWILLIAMS[i] > -20:
        try:
            if ListeWILLIAMS[i+1] < -20 and BougieEntree < 0 and BougieAppelle > 0 and abs(BougieEntree) > abs(BougieAppelle):
                print("")
                print("Vente")
                compteurVente += 1
                print("Prix de fermeture : ", df["Close"].iloc[i], "RSI: ", ListeRSI[i], "MME: ", ListeMME[i], "BBANDS: ", ListeBBANDS[i], "Mediane BBANDS : ",ListeMedianBands[i], "WILLIAMS: ", ListeWILLIAMS[i], "Time: ", df.index[i])
                
                ### V2 Risk Managment Vente : One Life Trade ###
                
                # for j in range(len(df['Close']) - i):
                #     if df['High'].iloc[i+2+j] >= df['Close'].iloc[i+1]+100:
                #         print("Stop Loss: ", -100)
                #         money.append(-100)
                #         break
                #     elif df['Low'].iloc[i+j] <= df['Close'].iloc[i+1] - 100:
                #         print("Take Profit: 100 ")
                #         money.append(100)
                #         break
                    
                ################################
                
                ### One Oportunity Trade ###
                
                for j in range(len(df['Close']) - i):

                    # Stop Loss
                    
                    if df['Close'].iloc[i+2] > (df['Close'].iloc[i+1]+abs(BougieEntree)*0.25) and secure == False:
                        print("Stop Loss :", df['Close'].iloc[i+1]-df['Close'].iloc[i+2+j])
                        money.append(df['Close'].iloc[i+1]-df['Close'].iloc[i+2+j])
                        break

                    # Take Profit si peu de puissance
                    
                    elif abs(df['Close'].iloc[i+2]-df['Open'].iloc[i+2]) <= BougieEntree and secure == False:
                        if df['Close'].iloc[i+2]-df['Open'].iloc[i+2] > 0:
                            print("Peu de puissance, Take profit", df['Open'].iloc[i+2]-df['Close'].iloc[i+2])
                            money.append(df['Open'].iloc[i+2]-df['Close'].iloc[i+2])
                            break

                    # Bougie Post entrée supérieur à l'entrée
                    
                    elif abs(df['Close'].iloc[i+2]-df['Open'].iloc[i+2]) >= BougieEntree and secure == False:
                        print("Secure")
                        secure = True

                    # Si la bougie retombe sur sécure
                    
                    elif df['High'].iloc[i+3+j] >= df['Close'].iloc[i+1]+100 and secure == True:
                        print("Secure", 100)
                        money.append(100)
                        secure = False
                        break

                    ### Mediane BBANDS atteinte
                    ### Retombe sur la médiane

                    # Trade complet si la bougie atteint la bande inférieur
                    
                    elif df['Low'].iloc[i+j] <= ListeBBANDS[i][1]:
                        print("Bande inférieur atteinte : ",df['Close'].iloc[i+1] - ListeBBANDS[i][1])
                        money.append(df['Close'].iloc[i+1] - ListeBBANDS[i][1])
                        secure = False
                        break
                    
                    
                
                
                    
                    
        except IndexError:
            print("Actuellement en recherche d'un point d'entrée")
            
print("")
# print("Nombre de bougies: ", len(df['Close']))
# print("Nombre d'achats: ", compteurAchat)
# print("Nombre de ventes: ", compteurVente)
# print("Nombre de breakeven achats: ", compteurBreakevenAchat)
# print("Nombre de breakeven ventes: ", compteurBreakevenVente)
# print("Nombre de trades complets achats: ", compteurCompleteAchat)
# print("Nombre de trades complets ventes: ", compteurCompleteVente)

print(money)
result = sum(money) - 60*len(money)
print("Résultat final: ", result)
print("")