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
moyenneHigh = []
IT = 5

breakeven = False
gainSecure = False


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
                
                ### V2 Risk Managment Achat ###
                
                BougieAppelle = df['Close'].iloc[i]
                BougieEntre = df['Close'].iloc[i+1]
                Fibo238A = (df['Open'].iloc[i+1] - ListeBBANDS[i][0])*0.238 + ListeBBANDS[i][0]
                Fibo382A = (df['Open'].iloc[i+1] - ListeBBANDS[i][0])*0.382 + ListeBBANDS[i][0]
                
                for j in range(len(df['Close']) - i):
                        
                        # Si la bougie d'entrer est plus grande que le 0.238 et qu'elle est plus grande que la bougie d'appelle alors on laisse courir le trade sans le stop à 0.238
                        if df["Close"].iloc[i+1] - df["Open"].iloc[i+1] > (df['Open'].iloc[i+1] - ListeBBANDS[i][0])*0.238 and df["Close"].iloc[i+1] - df["Open"].iloc[i+1] > df["Close"].iloc[i] - df["Open"].iloc[i]:
                            pass
                        else:
                            # Si la bougie monte au dessus de la mèche d'entrée
                            if df["High"].iloc[i+j] >= df['High'].iloc[i+1] :
                                print("Stop loss : ", df['High'].iloc[i+1])
                                break
                            # Si la bougie descend en dessous du 23.8% alors breakeven
                            elif df["Low"].iloc[i+j] <= Fibo238A and breakeven == False:
                                print("Fibo 23.8 atteint")
                                breakeven = True
                            # Si la bougie remonte
                            elif df["Close"].iloc[i+j] >= Fibo238A and breakeven == True:
                                # Fibo à + ou - 60 points
                                if BougieEntre - Fibo238A > 60:
                                    print("Breakeven atteint : +0€")
                                    break
                                else:
                                    print("Perte Limitée : ", BougieEntre - Fibo238A - 60)
                                    break
                        # Si la bougie descend en dessous de la médiane alors gains sécurisé à 38.2%
                        if df["Low"].iloc[i+j] <= ListeMedianBands[i+j] and gainSecure == False:
                            print("Gains sécurisé sur Fibo 38.2")
                            gainSecure = True
                        elif df["Close"].iloc[i+j] >= Fibo382A and gainSecure == True:
                            print("Gains sécurisé : ", BougieEntre - Fibo382A)
                            break
                        # Si la bougie touche la bande inférieure
                        elif df["Close"].iloc[i+j] >= ListeBBANDS[i+j][0]:
                            print("Bande supérieur atteinte")
                            break
                
                
                
                ### V1 Risk Managment ###
                
                """ breakeven_reached = False
                for j in range(len(df['Close']) - i):
                    if df['Close'].iloc[i+j] >= ListeMedianBands[i+j] - 50:  # Si atteint la médiane
                        print("Temps pour toucher la médiane (breakeven):", j*IT, "minutes")
                        compteurBreakevenAchat += 1
                        breakeven_reached = True
                        print("Prix après ouverture :",df['High'].iloc[i+2]-df['Open'].iloc[i+2])
                        moyenneHigh.append(df['High'].iloc[i+2]-df['Open'].iloc[i+2])
                        break
                    elif df['Close'].iloc[i+1+j] < df['Close'].iloc[i+1]-stopLoss:
                        print("Breakeven non atteint, stop loss")
                        print(-stopLoss)
                        money.append(-stopLoss)
                        print("Prix après ouverture :",df['High'].iloc[i+2]-df['Open'].iloc[i+2])
                        moyenneHigh.append(df['High'].iloc[i+2]-df['Open'].iloc[i+2])
                        break
                    

                # Si breakeven est atteint, vérifie le temps pour atteindre la bande opposée ou revenir à la médiane
                
                if breakeven_reached:
                    for k in range(j+1, len(df['Close']) - i):
                        if df['Close'].iloc[i+k] >= ListeBBANDS[i+k][0]:  # Si touche la bande supérieure
                            print("Bande supérieure atteinte en:", k*IT, "minutes")
                            print("Résultat du trade : ",df['Close'].iloc[i+k]-df['Close'].iloc[i+1])
                            print("Prix d'ouverture : ",df['Close'][i+1])
                            compteurCompleteAchat += 1
                            break
                        
                        elif df['Close'].iloc[i+k] <= ListeMedianBands[i+k]:  # Si retourne à la médiane
                            print("Résultat du trade : ",ListeMedianBands[i+k]-df['Close'].iloc[i+1])
                            print("Mediane de cloture : ",ListeMedianBands[i+k])
                            print("Retour à la médiane en:", k*IT, "minutes")
                            print("Prix d'ouverture",df['Close'].iloc[i+1])
                            money.append(ListeMedianBands[i+k]-df['Close'].iloc[i+1])
                            break """
            
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
                
                ### V2 Risk Managment Vente ###
                
                BougieAppelle = df['Close'].iloc[i]
                BougieEntre = df['Close'].iloc[i+1]
                Fibo238V = (ListeBBANDS[i][1] - df['Open'].iloc[i+1])*0.238 + df['Open'].iloc[i+1]
                Fibo382V = (ListeBBANDS[i][1] - df['Open'].iloc[i+1])*0.382 + df['Open'].iloc[i+1]
                
                
                
                for j in range(len(df['Close']) - i):
                    
                    # Si la bougie d'entrer est plus grande que le 0.238 et qu'elle est plus grande que la bougie d'appelle alors on laisse courir le trade sans le stop à 0.238
                    if df["Close"].iloc[i+1] - df["Open"].iloc[i+1] > (ListeBBANDS[i][1] - df['Open'].iloc[i+1])*0.238 and df["Close"].iloc[i+1] - df["Open"].iloc[i+1] > df["Close"].iloc[i] - df["Open"].iloc[i]:
                        pass
                    else:
                        # Si la bougie descend en dessous de la mèche d'entrée
                        if df["Low"].iloc[i+j] <= df['Low'].iloc[i+1] :
                            print("Stop loss : ", df['Low'].iloc[i+1])
                            break
                    
                        # Si la bougie monte au dessus du 23.8% alors breakeven
                        elif df["High"].iloc[i+j] >= Fibo238V and breakeven == False:
                            print("Fibo 23.8 atteint")
                            breakeven = True
                        # Si la bougie retombe
                        elif df["Close"].iloc[i+j] <= Fibo238V and breakeven == True:
                            # Fibo à + ou - 60 points
                            if Fibo238V - BougieEntre > 60:
                                print("Breakeven atteint : +0€")
                                break
                            else:
                                print("Perte Limitée : ", Fibo238V - BougieEntre - 60)
                                break
                        
                    # Si la bougie monte au dessus de la médiane alors gains sécurisé à 38.2%
                    if df["High"].iloc[i+j] >= ListeMedianBands[i+j] and gainSecure == False:
                        print("Gains sécurisé sur Fibo 38.2")
                        gainSecure = True
                    elif df["Close"].iloc[i+j] <= Fibo382V and gainSecure == True:
                        print("Gains sécurisé : ", Fibo382V - BougieEntre)
                        break
                    
                    # Si la bougie touche la bande supérieure
                    elif df["Close"].iloc[i+j] <= ListeBBANDS[i+j][1]:
                        print("Bande inférieur atteinte")
                        break
                        
                
                ### V1 Risk Managment ###
                """ breakeven_reached = False
                for j in range(len(df['Close']) - i):
                    if df['Close'].iloc[i+j] <= ListeMedianBands[i+j] + 50 :
                        print("Temps pour toucher la médiane (breakeven):", j*IT, "minutes")
                        compteurBreakevenVente += 1
                        breakeven_reached = True
                        print("Prix après ouverture :",df['High'].iloc[i+2]-df['Open'].iloc[i+2])
                        moyenneHigh.append(df['High'].iloc[i+2]-df['Open'].iloc[i+2])
                        break
                    elif df['Close'].iloc[i+1+j] > df['Close'].iloc[i+1]+stopLoss:
                        print("Breakeven non atteint, stop loss")
                        print(-stopLoss)
                        money.append(-stopLoss)
                        print("Prix après ouverture :",df['High'].iloc[i+2]-df['Open'].iloc[i+2])
                        moyenneHigh.append(df['High'].iloc[i+2]-df['Open'].iloc[i+2])
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
                            print("Prix d'ouverture : ",df['Close'].iloc[i+1])
                            money.append(df['Close'].iloc[i+1]-ListeMedianBands[i+k])
                            break """
                
            
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