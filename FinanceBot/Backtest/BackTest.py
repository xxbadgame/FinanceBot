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

bougieSup238 = False
bougieInf238 = False
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
            if ListeWILLIAMS[i+1] > -80 and df['Close'].iloc[i+1] - df['Open'].iloc[i+1] > 0 and df['Close'].iloc[i] - df['Open'].iloc[i] < 0:
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
                        
                    # Si la bougie d'entrer est plus grande que le 0.238 et qu'elle est plus grande que la bougie d'appelle alors on laisse courir le trade sans le stop à 0.238
                    if df["Close"].iloc[i+1] - df["Open"].iloc[i+1] > (ListeBBANDS[i][0] - df['Open'].iloc[i+1])*0.238 and df["Close"].iloc[i+1] - df["Open"].iloc[i+1] > df["Close"].iloc[i] - df["Open"].iloc[i] and bougieSup238 == False:
                        print("Bougie d'entrée plus grande que 0.238")
                        bougieSup238 = True
                        
                    elif bougieSup238 == False:
                        if df["Low"].iloc[i+2+j] <= df['Low'].iloc[i+1] and breakeven == False:
                            print("Stop loss : ", df['Low'].iloc[i+1]- df['Close'].iloc[i+1])
                            print('test')
                            print(df['Low'].iloc[i+1])
                            print(df["Low"].iloc[i+1+j])
                            break
                    
                        # Si la bougie monte au dessus du 23.8% alors breakeven
                        elif df["High"].iloc[i+j] >= Fibo238A and breakeven == False:
                            print("Fibo 23.8 atteint")
                            breakeven = True
                        # Si la bougie retombe
                        elif df["Close"].iloc[i+j] <= Fibo238A and breakeven == True:
                            # Fibo à + ou - 60 points
                            if Fibo238A - BougieEntre < 60:
                                print("Perte Limitée : ", Fibo238A - BougieEntre - 60)
                                breakeven = False
                                break
                            elif Fibo238A - BougieEntre > 100:
                                print("Breakeven atteint avec marge de sécu : +40€")
                                breakeven = False
                                break
                            else:
                                print("Breakeven atteint : +0€")
                                breakeven = False
                                break
                        
                        # Si la bougie monte au dessus de la médiane alors gains sécurisé à 38.2%
                        elif df["High"].iloc[i+j] >= ListeMedianBands[i+j] and gainSecure == False:
                            print("Gains sécurisé sur Fibo 38.2")
                            gainSecure = True
                        elif df["Low"].iloc[i+j] <= Fibo382A and gainSecure == True:
                            print("Gains sécurisé : ", Fibo382A - BougieEntre)
                            gainSecure = False
                            break
                        elif df["High"].iloc[i+j] >= ListeBBANDS[i+j][0] and gainSecure == True:
                            print("Bande supérieure atteinte")
                            print("Résultat du trade : ",df['Close'].iloc[i+j]-df['Close'].iloc[i+1])
                            gainSecure = False
                            break
                            
                    elif bougieSup238 == True:
                        if df["Low"].iloc[i+2+j] <= df['Low'].iloc[i+1]:
                            print("Stop loss : ", df['Low'].iloc[i+1]- df['Close'].iloc[i+1])
                            bougieSup238 = False
                            break
                        
                        elif df["High"].iloc[i+j] >= ListeMedianBands[i+j] and gainSecure == False:
                            print("Gains sécurisé sur Fibo 38.2")
                            gainSecure = True
                        elif df["Low"].iloc[i+j] <= Fibo382A and gainSecure == True:
                            print("Gains sécurisé : ", Fibo382A - BougieEntre)
                            bougieSup238 = False
                            gainSecure = False
                            break
                        elif df["High"].iloc[i+j] >= ListeBBANDS[i+j][0] and gainSecure == True:
                            print("Bande supérieure atteinte")
                            print("Résultat du trade : ",df['Close'].iloc[i+j]-df['Close'].iloc[i+1])
                            bougieSup238 = False
                            gainSecure = False
                            break 
            
        except IndexError:
            print("Actuellement en recherche d'un point d'entrée")
            
     
    ### Vente ###      
            
    elif ListeRSI[i] > 70 and \
    ListeMME[i] < df['Close'].iloc[i] and \
    ListeBBANDS[i][0] < df['Close'].iloc[i] and \
    ListeWILLIAMS[i] > -20:
        try:
            if ListeWILLIAMS[i+1] < -20 and df['Close'].iloc[i+1] - df['Open'].iloc[i+1] < 0 and df['Close'].iloc[i] - df['Open'].iloc[i] > 0:
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
                    
                    # Si la bougie d'entrer est plus grande que le 0.238 et qu'elle est plus grande que la bougie d'appelle alors on laisse courir le trade sans le stop à 0.238
                    if df["Open"].iloc[i+1] - df["Close"].iloc[i+1] > (df['Open'].iloc[i+1] - ListeBBANDS[i][0])*0.238 and df["Open"].iloc[i+1] - df["Close"].iloc[i+1] > df["Open"].iloc[i] - df["Close"].iloc[i] and bougieInf238 == False:
                        print("Bougie d'entrée plus grande que 0.238")
                        bougieInf238 = True
                        
                    elif bougieInf238 == False:
                        if df["High"].iloc[i+2+j] >= df['High'].iloc[i+1] and breakeven == False:
                            print("Stop loss : ", df['High'].iloc[i+1]- df['Close'].iloc[i+1])
                            print('test')
                            break
                    
                        # Si la bougie monte au dessus du 23.8% alors breakeven
                        elif df["Low"].iloc[i+j] <= Fibo238V and breakeven == False:
                            print("Fibo 23.8 atteint")
                            breakeven = True
                        # Si la bougie retombe
                        elif df["Close"].iloc[i+j] >= Fibo238V and breakeven == True:
                            # Fibo à + ou - 60 points
                            if BougieEntre - Fibo238V < 60:
                                print("Perte Limitée : ", BougieEntre - Fibo238V - 60)
                                breakeven = False
                                break
                            elif BougieEntre - Fibo238V > 100:
                                print("Breakeven atteint avec marge de sécu : +40€")
                                breakeven = False
                                break
                            else:
                                print("Breakeven atteint : +0€")
                                breakeven = False
                                break
                        
                        # Si la bougie monte au dessus de la médiane alors gains sécurisé à 38.2%
                        elif df["Low"].iloc[i+j] <= ListeMedianBands[i+j] and gainSecure == False:
                            print("Gains sécurisé sur Fibo 38.2")
                            gainSecure = True
                        elif df["High"].iloc[i+j] >= Fibo382V and gainSecure == True:
                            print("Gains sécurisé : ", BougieEntre - Fibo382V)
                            gainSecure = False
                            break
                        elif df["Low"].iloc[i+j] <= ListeBBANDS[i+j][1] and gainSecure == True:
                            print("Bande inférieure atteinte")
                            print("Résultat du trade : ",df['Close'].iloc[i+1]-df['Close'].iloc[i])
                            gainSecure = False
                            break
                        
                    elif bougieInf238 == True:
                        if df["High"].iloc[i+2+j] >= df['High'].iloc[i+1]:
                            print("Stop loss : ", df['High'].iloc[i+1]- df['Close'].iloc[i+1])
                            bougieInf238 = False
                            break
                        
                        elif df["Low"].iloc[i+j] <= ListeMedianBands[i+j] and gainSecure == False:
                            print("Gains sécurisé sur Fibo 38.2")
                            gainSecure = True
                        elif df["High"].iloc[i+j] >= Fibo382V and gainSecure == True:
                            print("Gains sécurisé : ", BougieEntre - Fibo382V)
                            bougieInf238 = False
                            gainSecure = False
                            break
                        elif df["Low"].iloc[i+j] <= ListeBBANDS[i+j][1] and gainSecure == True:
                            print("Bande inférieure atteinte")
                            print("Résultat du trade : ",df['Close'].iloc[i+1]-df['Close'].iloc[i])
                            bougieInf238 = False
                            gainSecure = False
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