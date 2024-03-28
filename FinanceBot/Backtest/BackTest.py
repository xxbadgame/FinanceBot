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
ListeATR = indicateurs.ATR(df['High'].to_list(), df['Low'].to_list(), df['Close'].to_list())

compteurAchat = 0
compteurVente = 0
compteurBreakevenAchat = 0
compteurBreakevenVente = 0
compteurCompleteAchat = 0
compteurCompleteVente = 0
money = []
moyenneHigh = []

secure = False
mediane = False

for i in range(len(df['Close'])):
    
    ## On veut à chaque fois tester le breakeven (SMA), si ok alors laisser courir jusqu'au trade complet peut importe le temps que ça prend car dans le pire des 
    ## cas on a fait un breakeven et donc bouger le stop loss à l'achat ou à la vente pour protéger le capital.

        
    ### Achat ###

    if ListeRSI[i] < 30 and \
    ListeMME[i] > df['Close'].iloc[i] and \
    ListeBBANDS[i][1] > df['Close'].iloc[i] and \
    ListeWILLIAMS[i] < -70 and \
    ListeATR[i] > 250:
        try:
            
            BougieEntreeA = df['Close'].iloc[i+1] - df['Open'].iloc[i+1]
            BougieAppelleA = df['Close'].iloc[i] - df['Open'].iloc[i]
            
            if ListeWILLIAMS[i+1] > -70 and BougieEntreeA > 0 and BougieAppelleA < 0 and abs(BougieEntreeA) > abs(BougieAppelleA):
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
                    
                    # Stop Loss début de trade

                    if df['Close'].iloc[i+2+j] < (df['Close'].iloc[i+1]-abs(BougieEntreeA)*0):
                        print("Stop Loss :", df['Close'].iloc[i+2+j]-df['Close'].iloc[i+1])
                        money.append(df['Close'].iloc[i+2+j]-df['Close'].iloc[i+1])
                        break

                    # Si peu de puissance, Take profit
                    
                    elif abs(df['Close'].iloc[i+2]-df['Open'].iloc[i+2]) <= BougieEntreeA//2 and df['Close'].iloc[i+2]-df['Open'].iloc[i+2] >= 0:
                        print("Peu de puissance, Take profit", df['Close'].iloc[i+2]-df['Open'].iloc[i+2])
                        money.append(df['Close'].iloc[i+2]-df['Open'].iloc[i+2])
                        break
                    
                    # Bougie post entrée
                    
                    elif abs(df['Close'].iloc[i+2]-df['Open'].iloc[i+2]) >= BougieEntreeA//2 and secure == False:
                        print("Secure")
                        secure = True
                        
                    # Bougie post médiane
                    
                    elif df['High'].iloc[i+2+j] >= ListeMedianBands[i] and secure == True and mediane == False:
                        print("Passage Médiane")
                        mediane = True

                    # Si la bougie retombe sur sécure
                    
                    elif df['Low'].iloc[i+2+j] <= df['Close'].iloc[i+1]+100 and secure == True and mediane == False:
                        print("Retour secure : ", 100)
                        money.append(100)
                        secure = False
                        break
                    
                    # Si la bougie retombe sur médiane
                    
                    elif df['Low'].iloc[i+2+j] <= ListeMedianBands[i+2+j] and secure == True and mediane == True:
                        print("Retour médiane : ",ListeMedianBands[i+2+j]-df['Close'].iloc[i+1])
                        money.append(ListeMedianBands[i+2+j]-df['Close'].iloc[i+1])
                        secure = False
                        mediane = False
                        break

                    # Trade complet si la bougie atteint la bande supérieur
                    
                    elif df['High'].iloc[i+2+j] >= ListeBBANDS[i+2+j][0] and secure == True and mediane == False:
                        print("Bande supérieur atteinte : ",ListeBBANDS[i+2+j][0] - df['Close'].iloc[i+1])
                        money.append(ListeBBANDS[i+2+j][0] - df['Close'].iloc[i+1])
                        secure = False
                        mediane = False
                        break
    
                        
            
        except IndexError:
            print("Actuellement en recherche d'un point d'entrée")
            
     
    ### Vente ###
    
            
    if ListeRSI[i] > 70 and \
    ListeMME[i] < df['Close'].iloc[i] and \
    ListeBBANDS[i][0] < df['Close'].iloc[i] and \
    ListeWILLIAMS[i] > -20 and \
    ListeATR[i] > 250:
        try:
            
            BougieEntreeV= df['Close'].iloc[i+1] - df['Open'].iloc[i+1]
            BougieAppelleV = df['Close'].iloc[i] - df['Open'].iloc[i]
            
            if ListeWILLIAMS[i+1] < -20 and BougieEntreeV < 0 and BougieAppelleV > 0 and abs(BougieEntreeV) > abs(BougieAppelleV):
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

                    # Stop Loss début de trade

                    if df['Close'].iloc[i+2+j] > (df['Close'].iloc[i+1]+abs(BougieEntreeV)*0):
                        print("Stop Loss :", df['Close'].iloc[i+1]-df['Close'].iloc[i+2+j])
                        money.append(df['Close'].iloc[i+1]-df['Close'].iloc[i+2+j])
                        break

                    # Si peu de puissance, Take profit
                    
                    elif abs(df['Close'].iloc[i+2]-df['Open'].iloc[i+2]) <= abs(BougieEntreeV)//2 and df['Close'].iloc[i+2]-df['Open'].iloc[i+2] <= 0:
                        print("Peu de puissance, Take profit", df['Open'].iloc[i+2]-df['Close'].iloc[i+2])
                        money.append(df['Open'].iloc[i+2]-df['Close'].iloc[i+2])
                        break
                    
                    # Bougie post entrée
                    
                    elif abs(df['Close'].iloc[i+2]-df['Open'].iloc[i+2]) >= abs(BougieEntreeV)//2 and secure == False:
                        print("Secure")
                        secure = True
                        
                    # Bougie post médiane
                    
                    elif df['Low'].iloc[i+2+j] <= ListeMedianBands[i] and secure == True and mediane == False:
                        print("Passage Médiane")
                        mediane = True
                        

                    # Si la bougie retombe sur sécure
                    
                    elif df['High'].iloc[i+2+j] >= df['Close'].iloc[i+1]-100 and secure == True and mediane == False:
                        print("Retour secure : ", 100)
                        money.append(100)
                        secure = False
                        break
                    
                    # Si la bougie retombe sur médiane
                    
                    elif df['High'].iloc[i+2+j] >= ListeMedianBands[i+2+j] and secure == True and mediane == True:
                        print("Retour médiane : ",df['Close'].iloc[i+1]-ListeMedianBands[i+2+j])
                        money.append(df['Close'].iloc[i+1]-ListeMedianBands[i+2+j])
                        secure = False
                        mediane = False
                        break

                    # Trade complet si la bougie atteint la bande inférieur
                    
                    elif df['Low'].iloc[i+2+j] <= ListeBBANDS[i+2+j][1] and secure == True and mediane == True:
                        print("Bande inférieur atteinte : ",df['Close'].iloc[i+1]-ListeBBANDS[i+2+j][1])
                        money.append(df['Close'].iloc[i+1]-ListeBBANDS[i+2+j][1])
                        secure = False
                        mediane = False
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