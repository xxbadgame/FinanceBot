import numpy as np

class Indicateurs():
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
            return 0

        # Détermine le plus haut des prix les plus hauts et le plus bas des prix les plus bas sur la période
        highest_high = max(highs[-period:])
        lowest_low = min(lows[-period:])
        # Utilise le dernier prix de clôture
        current_close = closes[-1]

        # Calcule le Williams %R
        try:
            williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
        except ZeroDivisionError:
            print("Division par zéro rencontrée dans le calcul de Williams %R.")
            return 0

        return williams_r
    

    #### MME ####
    
    def MME(self, closes, period=9):
        k = 2 / (period + 1)
        ema = [np.mean(closes[:period])]  # Commencer avec une moyenne simple pour le premier EMA
        for price in closes[period:]:
            ema.append((price * k) + (ema[-1] * (1 - k)))
        return ema[-1]  # Retourne la dernière valeur de l'EMA calculée
    
    
    
    #### BBANDS ####
    
    def BBANDS(self, closes, period=20, num_std_dev=2):
        # Calculer la bande médiane comme étant la moyenne mobile simple (MMS) des prix de clôture
        sma = np.mean(closes[-period:])
        
        # Calculer l'écart-type des prix de clôture sur la période spécifiée
        std_dev = np.std(closes[-period:])
        
        # Calculer les bandes supérieure et inférieure
        upper_band = sma + (num_std_dev * std_dev)
        lower_band = sma - (num_std_dev * std_dev)
        
        return upper_band, lower_band
    
    
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
    
    

   