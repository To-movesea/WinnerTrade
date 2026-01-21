import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime

class StockDataClient:
    
    @staticmethod
    def _normalize_code(code):
        """
        Normalize stock code for different APIs.
        Input: "600519", "00700", "00700.HK", "sh600519"
        Output tuple: (sina_code, eastmoney_secid)
        
        Sina: sh600519, sz000001, hk00700
        Eastmoney secid: 1.600519 (SH), 0.000001 (SZ), 116.00700 (HK)
        """
        code = str(code).replace('.HK', '').replace('sh', '').replace('sz', '')
        
        # Heuristic detection
        if len(code) == 5: # HK Share
            sina_code = f"hk{code}"
            em_secid = f"116.{code}"
        elif code.startswith('6') or code.startswith('9'): # SH
            sina_code = f"sh{code}"
            em_secid = f"1.{code}"
        elif code.startswith('0') or code.startswith('3'): # SZ
            sina_code = f"sz{code}"
            em_secid = f"0.{code}"
        elif code.startswith('4') or code.startswith('8'): # BJ (Simple mapping)
             sina_code = f"bj{code}"
             em_secid = f"0.{code}" # EM mapping varies for BJ
        else:
            # Default to SH if unknown
            sina_code = f"sh{code}"
            em_secid = f"1.{code}"
            
        return sina_code, em_secid

    @staticmethod
    def get_realtime_data(code):
        """
        Fetch realtime data from Sina Finance
        """
        sina_code, _ = StockDataClient._normalize_code(code)
        url = f"http://hq.sinajs.cn/list={sina_code}"
        headers = {'Referer': 'https://finance.sina.com.cn/'}
        
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code != 200:
                return None
                
            # Parse response: var hq_str_sh600519="Moutai,..."
            content = res.text
            if '="' not in content:
                return None
                
            data_str = content.split('="')[1].strip('";\n')
            if not data_str:
                return None
                
            parts = data_str.split(',')
            
            # Parsing logic differs for A-share vs HK-share
            if sina_code.startswith('hk'):
                # HK: EnglishName, Name, Open, PrevClose, High, Low, Last, Change, Change%, Vol, Turnover...
                if len(parts) < 10: return None
                name = parts[1]
                price = float(parts[6])
                volume = float(parts[12]) # Share count
            else:
                # A-share: Name, Open, PrevClose, Price, High, Low, Buy, Sell, Vol, Turnover...
                if len(parts) < 10: return None
                name = parts[0]
                price = float(parts[3])
                volume = float(parts[8]) # Share count
                
            return {
                "name": name,
                "price": price,
                "volume": volume,
                "code": code
            }
        except Exception as e:
            print(f"Error fetching realtime data for {code}: {e}")
            return None

    @staticmethod
    def get_history_data(code, days=60):
        """
        Fetch history K-line from EastMoney
        """
        _, secid = StockDataClient._normalize_code(code)
        
        # EastMoney API
        url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": secid,
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f61", # Date, Open, Close, High, Low, Vol, Turnover...
            "klt": "101", # Daily
            "fqt": "1",   # QianFuQuan
            "end": "20500101",
            "lmt": days
        }
        
        try:
            res = requests.get(url, params=params, timeout=5)
            data = res.json()
            
            if not data or 'data' not in data or not data['data'] or 'klines' not in data['data']:
                return None
                
            klines = data['data']['klines']
            records = []
            for k in klines:
                # Format: "2023-01-01,Open,Close,High,Low,Vol,..."
                p = k.split(',')
                records.append({
                    "date": p[0],
                    "open": float(p[1]),
                    "close": float(p[2]),
                    "high": float(p[3]),
                    "low": float(p[4]),
                    "volume": float(p[5])
                })
                
            return pd.DataFrame(records)
            
        except Exception as e:
            print(f"Error fetching history for {code}: {e}")
            return None

    @staticmethod
    def calculate_indicators(df):
        """
        Calculate technical indicators: MA, MACD, RSI, BOLL
        """
        if df is None or len(df) < 20:
            return None
            
        # MA
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['VOL_MA5'] = df['volume'].rolling(window=5).mean()
        
        # BOLL (20, 2)
        df['std'] = df['close'].rolling(window=20).std()
        df['BOLL_UPPER'] = df['MA20'] + 2 * df['std']
        df['BOLL_LOWER'] = df['MA20'] - 2 * df['std']
        
        # MACD (12, 26, 9)
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['DIF'] = exp1 - exp2
        df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
        df['MACD'] = 2 * (df['DIF'] - df['DEA'])
        
        # RSI (14)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Return latest
        return df.iloc[-1]
