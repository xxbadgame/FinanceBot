import json
import pandas as pd
from IndicateursBackTest import *
from HistoricalBitget import *

# voir le cas du 20 à 13:40
# plus souple sur les 10min du début, passer à 20 voir 30

hd = HistoricalBitget()
df = hd.fetch_bitget_candles(100000)

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
IT = 5

NewStop = False


for i in range(len(df['Close'])):
    
    ## On veut à chaque fois tester le breakeven (SMA), si ok alors laisser courir jusqu'au trade complet peut importe le temps que ça prend car dans le pire des 
    ## cas on a fait un breakeven et donc bouger le stop loss à l'achat ou à la vente pour protéger le capital.
    
    ### Achat ###
    
    
    if ListeRSI[i] < 30 and \
    ListeRSI[i-1] < 30 and \
    ListeMME[i] > df['Close'].iloc[i] and \
    ListeBBANDS[i][1] > df['Close'].iloc[i] and \
    ListeWILLIAMS[i] < -80:
        try:
            if ListeWILLIAMS[i+1] > -80 and df['Close'].iloc[i+2] - df['Open'].iloc[i+2] > 0 and df['Close'].iloc[i+1] - df['Open'].iloc[i+1] > 0 and df['Close'].iloc[i] - df['Open'].iloc[i] < 0:
                print("")
                print("Achat")
                compteurAchat += 1
                print("Prix de fermeture : ", df["Close"].iloc[i], "RSI: ", ListeRSI[i], "MME: ", ListeMME[i], "BBANDS: ", ListeBBANDS[i], "Mediane BBANDS : ",ListeMedianBands[i], "WILLIAMS: ", ListeWILLIAMS[i], "Time: ", df.index[i])
                
                ### V2 Risk Managment Achat ###
                
                BougieAppelle = df['Close'].iloc[i]
                BougieEntre = df['Close'].iloc[i+1]
                Fibo238A = (ListeBBANDS[i+1][0] - df['Open'].iloc[i+1])*0.238 + df['Open'].iloc[i+1]
                Fibo382A = (ListeBBANDS[i+1][0] - df['Open'].iloc[i+1])*0.382 + df['Open'].iloc[i+1]
                
                for j in range(len(df['Close']) - i):
                        
                    # Stop loss mèche basse entrée
                    if df["Low"].iloc[i+2+j] <= df['Low'].iloc[i+1] and NewStop == False:
                        print("Stop loss : ", df['Low'].iloc[i+1] - df['Close'].iloc[i+1])
                        money.append(df['Low'].iloc[i+1] - df['Close'].iloc[i+1])
                        break
                    # Si Médiane alors stop loss à 0.238
                    elif df["High"].iloc[i+j] >= ListeMedianBands[i+j] and NewStop == False:
                        print("Gain sécurisé sur Fibo 23.8")
                        NewStop = True
                    # Sinon Bande opposé, jackpot
                    elif df["High"].iloc[i+j] >= ListeBBANDS[i+j][0] and NewStop == True:
                        print("Bande supérieure atteinte")
                        print("Résultat du trade : ",df['Close'].iloc[i+j]-df['Close'].iloc[i+1])
                        NewStop = False
                        money.append(df['Close'].iloc[i+j]-df['Close'].iloc[i+1])
                        break
                    elif df["Low"].iloc[i+j] <= Fibo238A and NewStop == True:
                        print("Retour sur Fibo : ", BougieEntre - Fibo238A)
                        NewStop = False
                        money.append(Fibo238A - df['Close'].iloc[i+1])
                        break
                        
                    
            
        except IndexError:
            print("Actuellement en recherche d'un point d'entrée")
            
     
    ### Vente ###      
            
    elif ListeRSI[i] > 70 and \
    ListeRSI[i-1] > 70 and \
    ListeMME[i] < df['Close'].iloc[i] and \
    ListeBBANDS[i][0] < df['Close'].iloc[i] and \
    ListeWILLIAMS[i] > -20:
        try:
            if ListeWILLIAMS[i+1] < -20 and df['Close'].iloc[i+2] - df['Open'].iloc[i+2] < 0 and df['Close'].iloc[i+1] - df['Open'].iloc[i+1] < 0 and df['Close'].iloc[i] - df['Open'].iloc[i] > 0:
                print("")
                print("Vente")
                compteurVente += 1
                print("Prix de fermeture : ", df["Close"].iloc[i], "RSI: ", ListeRSI[i], "MME: ", ListeMME[i], "BBANDS: ", ListeBBANDS[i], "Mediane BBANDS : ",ListeMedianBands[i], "WILLIAMS: ", ListeWILLIAMS[i], "Time: ", df.index[i])
                
                ### V2 Risk Managment Vente ###
                
                BougieAppelle = df['Close'].iloc[i]
                BougieEntre = df['Close'].iloc[i+1]
                Fibo238V = (df['Open'].iloc[i+1] - ListeBBANDS[i+1][0])*0.238 + ListeBBANDS[i+1][0]
                Fibo382V = (df['Open'].iloc[i+1] - ListeBBANDS[i+1][0])*0.382 + ListeBBANDS[i+1][0]
                
                for j in range(len(df['Close']) - i):
                    
                    if df["High"].iloc[i+2+j] >= df['High'].iloc[i+1] and NewStop == False:
                        print("Stop loss : ", df['Close'].iloc[i+1] - df['High'].iloc[i+1])
                        money.append(df['Close'].iloc[i+1] - df['High'].iloc[i+1])
                        break
                    elif df["Low"].iloc[i+j] <= ListeMedianBands[i+j] and NewStop == False:
                        print("Gain sécurisé sur Fibo 23.8")
                        NewStop = True
                    elif df["Low"].iloc[i+j] <= ListeBBANDS[i+j][1] and NewStop == True:
                        print("Bande inférieure atteinte")
                        print("Résultat du trade : ",df['Close'].iloc[i+1]-df['Close'].iloc[i+j])
                        NewStop = False
                        money.append(df['Close'].iloc[i+1]-df['Close'].iloc[i+j])
                        break
                    elif df["High"].iloc[i+j] >= Fibo238V and NewStop == True:
                        print("Retour sur Fibo : ", BougieEntre-Fibo238V)
                        NewStop = False
                        money.append(df['Close'].iloc[i+1]-Fibo238V)
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