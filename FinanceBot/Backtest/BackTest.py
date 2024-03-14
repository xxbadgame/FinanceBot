import json
import pandas as pd
from IndicateursBackTest import *
from HistoricalBitget import *

# voir le cas du 20 à 13:40
# plus souple sur les 10min du début, passer à 20 voir 30

hd = HistoricalBitget()
df = hd.fetch_bitget_candles()

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
IT = 1


for i in range(len(df['Close'])):
    
    ## On veut à chaque fois tester le breakeven (SMA), si ok alors laisser courir jusqu'au trade complet peut importe le temps que ça prend car dans le pire des 
    ## cas on a fait un breakeven et donc bouger le stop loss à l'achat ou à la vente pour protéger le capital.
    
    ### Achat ###
    
    
    if ListeRSI[i] < 30 and \
    ListeMME[i] > df['Close'].iloc[i] and \
    ListeBBANDS[i][1] > df['Close'].iloc[i] and \
    ListeWILLIAMS[i] < -80:
        try:
            if ListeWILLIAMS[i+1] > -80:
                print("")
                print("Achat")
                compteurAchat += 1
                print("Prix de fermeture : ", df["Close"].iloc[i], "RSI: ", ListeRSI[i], "MME: ", ListeMME[i], "BBANDS: ", ListeBBANDS[i], "Mediane BBANDS : ",ListeMedianBands[i], "WILLIAMS: ", ListeWILLIAMS[i], "Time: ", df.index[i])
                ### combien de temps pour toucher le SMA ###
                # Vérifie si le breakeven est atteint dans les 10 prochaines minutes
                breakeven_reached = False
                for j in range(len(df['Close']) - i):  # Vérifie les 30 prochaines minutes
                    if df['Close'].iloc[i+j] >= ListeMedianBands[i+j] - 50:  # Si atteint la médiane
                        print("Temps pour toucher la médiane (breakeven):", j*IT, "minutes")
                        compteurBreakevenAchat += 1
                        breakeven_reached = True
                        break
                    elif df['Close'].iloc[i+1+j] < df['Close'].iloc[i+1]-stopLoss:
                        print("Breakeven non atteint, stop loss")
                        print(-stopLoss)
                        money.append(-stopLoss)
                        break
                    

                # Si breakeven est atteint, vérifie le temps pour atteindre la bande opposée ou revenir à la médiane
                
                if breakeven_reached:
                    for k in range(j+1, len(df['Close']) - i):
                        if df['Close'].iloc[i+k] >= ListeBBANDS[i+k][0]:  # Si touche la bande supérieure
                            print("Bande supérieure atteinte en:", k*IT, "minutes")
                            print("Résultat du trade : ",df['Close'].iloc[i+k]-df['Close'].iloc[i+1])
                            print("Prix d'ouverture : ",df['Close'][i+1])
                            money.append(df['Close'].iloc[i+k]-df['Close'].iloc[i+1])
                            compteurCompleteAchat += 1
                            break
                        
                        elif df['Close'].iloc[i+k] <= ListeMedianBands[i+k]:  # Si retourne à la médiane
                            print("Résultat du trade : ",ListeMedianBands[i+k]-df['Close'].iloc[i+1])
                            print("Mediane de cloture : ",ListeMedianBands[i+k])
                            print("Retour à la médiane en:", k*IT, "minutes")
                            print("Prix d'ouverture",df['Close'].iloc[i+1])
                            money.append(ListeMedianBands[i+k]-df['Close'].iloc[i+1])
                            break
            
        except IndexError:
            print("Actuellement en recherche d'un point d'entrée")
            
     
     ### Vente ###      
            
    elif ListeRSI[i] > 70 and \
    ListeMME[i] < df['Close'].iloc[i] and \
    ListeBBANDS[i][0] < df['Close'].iloc[i] and \
    ListeWILLIAMS[i] > -20:
        try:
            if ListeWILLIAMS[i+1] < -20:
                print("")
                print("Vente")
                compteurVente += 1
                print("Prix de fermeture : ", df["Close"].iloc[i] ,"RSI: ", ListeRSI[i], "MME: ", ListeMME[i], "BBANDS: ", ListeBBANDS[i], "Mediane BBANDS : ",ListeMedianBands[i], "WILLIAMS: ", ListeWILLIAMS[i], "Time: ", df.index[i])
                ### combien de temps pour toucher le SMA ###
                # Vérifie si le breakeven est atteint dans les 10 prochaines minutes
                breakeven_reached = False
                for j in range(len(df['Close']) - i):
                    if df['Close'].iloc[i+j] <= ListeMedianBands[i+j] + 50 :
                        print("Temps pour toucher la médiane (breakeven):", j*IT, "minutes")
                        compteurBreakevenVente += 1
                        breakeven_reached = True
                        break
                    elif df['Close'].iloc[i+1+j] > df['Close'].iloc[i+1]+stopLoss:
                        print("Breakeven non atteint, stop loss")
                        print(-stopLoss)
                        money.append(-stopLoss)
                        break
                    
                    
                # Si breakeven est atteint, vérifie le temps pour atteindre la bande opposée ou revenir à la médiane
                
                if breakeven_reached:
                    for k in range(j+1, len(df['Close']) - i):
                        if df['Close'].iloc[i+k] <= ListeBBANDS[i+k][1]:
                            print("Bande inférieure atteinte en:", k*IT, "minutes")
                            print("Résultat du trade : ",df['Close'].iloc[i+1]-df['Close'].iloc[i+k])
                            print("Prix d'ouverture : ",df['Close'].iloc[i+1])
                            money.append(df['Close'].iloc[i+1]-df['Close'].iloc[i+k])
                            compteurCompleteVente += 1
                            break
                        
                        elif df['Close'].iloc[i+k] >= ListeMedianBands[i+k]:
                            print("Résultat du trade : ",df['Close'].iloc[i+1]-ListeMedianBands[i+k])
                            print("Mediane de cloture : ",ListeMedianBands[i+k])
                            print("Retour à la médiane en:", k*IT, "minutes")
                            print("Prix d'ouverture",df['Close'].iloc[i+1])
                            money.append(df['Close'].iloc[i+1]-ListeMedianBands[i+k])
                            break
                
            
        except IndexError:
            print("Actuellement en recherche d'un point d'entrée")
        
    
            
print("")
print("Nombre de bougies: ", len(df['Close']))
print("Nombre d'achats: ", compteurAchat)
print("Nombre de ventes: ", compteurVente)
print("Nombre de breakeven achats: ", compteurBreakevenAchat)
print("Nombre de breakeven ventes: ", compteurBreakevenVente)
print("Nombre de trades complets achats: ", compteurCompleteAchat)
print("Nombre de trades complets ventes: ", compteurCompleteVente)

print(money)
result = sum(money) - 60*(compteurAchat+compteurVente)
print("Résultat final: ", result)
print("")