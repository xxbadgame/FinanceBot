import requests
import pandas as pd
from tqdm import tqdm
import time



class HistoricalBitget:
    def __init__(self, IT=1):
        self.IT = IT

    def fetch_bitget_candles(self,target_bougies=1000):
        bougies_per_request = 200
        total_iterations = target_bougies // bougies_per_request

        all_data_frames = []
        current_time_milliseconds = int(time.time() * 1000)
        endTime = current_time_milliseconds  # Commencer par l'heure actuelle

        for i in tqdm(range(total_iterations), desc="Fetching candles"):
            # Ajuster endTime pour couvrir exactement 200 bougies de 5 minutes
            if i > 0:
                endTime -= bougies_per_request * self.IT * 60000  # 200 bougies * 5 minutes * 60000 ms

            url = "https://api.bitget.com/api/v2/mix/market/history-candles"
            params = {
                "symbol": "BTCUSDT",
                "granularity": str(self.IT)+"m",  # Granularité de 5 minutes
                "productType": "usdt-futures",
                "limit": bougies_per_request,
                "endTime": str(endTime)
            }

            response = requests.get(url, params=params)
            data = response.json().get('data', [])
            
            if not data:
                print(f"No data returned for iteration {i+1}.")
                break

            df = pd.DataFrame(data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'VolumeQuote'])
            df['Time'] = pd.to_numeric(df['Time'])
            df['Time'] = pd.to_datetime(df['Time'], unit='ms')
            df.set_index('Time', inplace=True)
            df = df.astype(float)

            all_data_frames.append(df)

        if all_data_frames:
            final_df = pd.concat(all_data_frames)
            final_df = final_df.sort_index(ascending=True)  # S'assurer que les données les plus récentes sont en haut
        else:
            final_df = pd.DataFrame()

        return final_df