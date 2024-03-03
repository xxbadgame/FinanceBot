import numpy as np
import pandas as pd

class IndicateursBackTest():
    def __init__(self):
        pass
    
    #### RSI ####

    def RSI(self, closes, period=14):
        if len(closes) < period:
            # Retourne une liste de zéros si pas assez de données
            return [0] * len(closes)
        
        gains = [0] * len(closes)
        losses = [0] * len(closes)

        # Calcul initial des gains et des pertes pour chaque jour
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i - 1]
            if diff > 0:
                gains[i] = diff
            else:
                losses[i] = -diff

        avg_gains = []
        avg_losses = []

        # Calcul des moyennes des gains et des pertes sur la période spécifiée
        for i in range(period, len(closes)):
            if i == period:
                avg_gains.append(sum(gains[:period]) / period)
                avg_losses.append(sum(losses[:period]) / period)
            else:
                avg_gains.append((avg_gains[-1] * (period - 1) + gains[i]) / period)
                avg_losses.append((avg_losses[-1] * (period - 1) + losses[i]) / period)

        rsi = [0] * period  # Préfixe avec des zéros pour les périodes où le RSI n'est pas calculé

        # Calcul du RSI pour chaque période
        for i in range(len(avg_gains)):
            rs = avg_gains[i] / (avg_losses[i] + 1e-10)  # Ajoute un petit nombre pour éviter la division par zéro
            rsi.append(100 - (100 / (1 + rs)))

        return rsi

    
    #### Williams %R ####
    

    def WILLIAMS(self, highs, lows, closes, period=14):
        # Vérifie s'il y a suffisamment de données pour le calcul
        if len(closes) < period or len(highs) < period or len(lows) < period:
            print("Pas assez de données pour calculer Williams %R.")
            return [0] * len(closes)

        williams_list = []

        for i in range(len(closes) - period + 1):
            # Détermine le plus haut des prix les plus hauts et le plus bas des prix les plus bas sur la période
            highest_high = max(highs[i:i + period])
            lowest_low = min(lows[i:i + period])
            # Utilise le dernier prix de clôture
            current_close = closes[i + period - 1]

            # Calcule le Williams %R
            try:
                williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
            except ZeroDivisionError:
                print("Division par zéro rencontrée dans le calcul de Williams %R.")
                williams_list.append(0)
            else:
                williams_list.append(williams_r)
                
        williams_list = [0] * (period - 1) + williams_list  # Préfixe avec des zéros pour les périodes où le Williams %R n'est pas calculé

        return williams_list

    

    #### MME ####
    
    def MME(self, closes, period=9):
        k = 2 / (period + 1)
        ema = [np.mean(closes[:period])]  # Commencer avec une moyenne simple pour le premier EMA
        for price in closes[period:]:
            ema.append((price * k) + (ema[-1] * (1 - k)))
            
        ema = [0] * (period - 1) + ema  # Préfixe avec des zéros pour les périodes où l'EMA n'est pas calculé
        return ema  # Retourne la liste de toutes les valeurs de l'EMA calculées
    
    
    def SMA(self,closes, period=9):
        sma = []
        for i in range(len(closes)):
            if i+1 >= period:
                # Calcule la SMA avec une période complète de données
                sma.append(np.mean(closes[i+1-period:i+1]))
    
        return sma
    
    
    #### BBANDS ####
    
    def BBANDS(self, closes, period=20, num_std_dev=2):
        BBANDS = []
        for i in range(len(closes)):
            if i >= period:  # Assurez-vous d'avoir suffisamment de données pour calculer les bandes de Bollinger
                sma = np.mean(closes[i-period+1:i+1])
                std_dev = np.std(closes[i-period+1:i+1])

                upper_band = sma + (num_std_dev * std_dev)
                lower_band = sma - (num_std_dev * std_dev)
                BBANDS.append((upper_band, lower_band))
            else:
                BBANDS.append((0, 0))  # Ajoute des zéros au début lorsque les données sont insuffisantes pour le calcul

        return BBANDS
    
    
    def medianBBANDS(self, closes, period=20, num_std_dev=2):
        medBands = []
        BBANDS = self.BBANDS(closes, period, num_std_dev)
        for i in range(len(BBANDS)):
            BBANDS[i] = np.median(BBANDS[i]) 
            medBands.append(BBANDS[i])
        return medBands   

    
    
    #### VOLUMES ####
    
    def VOLUMES(self, volumes):
        return volumes.iloc[-1]
    
    #### Average True Range ####
    def ATR(self, highs, lows, closes, period=14):
        # Calculer les valeurs de l'ATR
        tr = []
        for i in range(1, len(closes)):
            high = highs[i]
            low = lows[i]
            close = closes[i-1]
            tr.append(max(high - low, abs(high - close), abs(low - close)))
        
        atr = np.mean(tr[-period:])
        
        return atr