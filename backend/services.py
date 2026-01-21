
from supabase_client import get_supabase_client

class StockService:
    @staticmethod
    def analyze_stock(stock_code):
        # ... (keep existing analyze_stock logic) ...
        # Need to re-import dependencies inside or ensure they are available
        import random
        from datetime import datetime
        from stock_api import StockDataClient
        
        # 1. Fetch Realtime Data
        realtime = StockDataClient.get_realtime_data(stock_code)
        
        if not realtime:
            # Fallback if API fails (or for invalid codes)
            return {
                "stock_code": stock_code,
                "stock_name": "未知/获取失败",
                "pressure_level": 0,
                "support_level": 0,
                "score": 0,
                "recommendation": "数据获取失败",
                "volume_status": "未知",
                "sector_flow": "未知",
                "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        # 2. Fetch History & Calculate Indicators
        history_df = StockDataClient.get_history_data(stock_code, days=60)
        latest_indicators = StockDataClient.calculate_indicators(history_df)
        
        # 3. Analyze Logic
        current_price = realtime['price']
        
        # Defaults
        pressure = current_price * 1.1
        support = current_price * 0.9
        score = 60
        volume_status = "正常"
        
        if latest_indicators is not None:
            # Pressure/Support from BOLL
            pressure = round(latest_indicators['BOLL_UPPER'], 2)
            support = round(latest_indicators['BOLL_LOWER'], 2)
            
            # If price broke BOLL Upper, next pressure is high of recent history
            if current_price > pressure:
                pressure = round(history_df['high'].max(), 2)
            
            # If price broke BOLL Lower, next support is low of recent history
            if current_price < support:
                support = round(history_df['low'].min(), 2)
                
            # Volume Analysis
            vol_ma5 = latest_indicators['VOL_MA5']
            curr_vol = realtime['volume'] # Note: Realtime volume is accumulated for today.
            # Simple approximation: If today is closed, compare directly. If mid-day, project it?
            # Let's just compare with yesterday's volume for simplicity or use simple ratio
            # Actually, comparing to MA5 is better.
            if curr_vol > vol_ma5 * 1.5:
                volume_status = "放量"
            elif curr_vol < vol_ma5 * 0.6:
                volume_status = "缩量"
            
            # Scoring Logic (0-100)
            base_score = 50
            
            # Trend Score
            if current_price > latest_indicators['MA20']:
                base_score += 10
            if latest_indicators['MA5'] > latest_indicators['MA20']: # Golden Cross area
                base_score += 10
                
            # MACD Score
            if latest_indicators['DIF'] > latest_indicators['DEA']:
                base_score += 10
            if latest_indicators['MACD'] > 0:
                base_score += 5
                
            # RSI Score
            rsi = latest_indicators['RSI']
            if 30 <= rsi <= 70:
                base_score += 5
            elif rsi < 30: # Oversold, chance to buy
                base_score += 15
            elif rsi > 80: # Overbought, risk
                base_score -= 10
                
            # Price Position Score
            if current_price < support * 1.02: # Near support
                base_score += 10
            if current_price > pressure * 0.98: # Near pressure
                base_score -= 5
                
            score = min(100, max(0, int(base_score)))
            
        # Recommendation
        recommendation = "观望"
        if score >= 80:
            recommendation = "强烈推荐"
        elif score >= 70:
            recommendation = "推荐买入"
        elif score <= 40:
            recommendation = "建议卖出"
        elif score <= 50:
            recommendation = "谨慎持有"
            
        # Sector Flow (Mocked for now as real API is complex)
        # Make it deterministic based on stock code and date so it doesn't change on every refresh
        date_str = datetime.now().strftime("%Y%m%d")
        seed_str = f"{stock_code}_{date_str}"
        # Use a local random instance to avoid affecting global state
        local_random = random.Random(seed_str)
        
        flow_dir = "净流入" if score > 50 else "净流出"
        flow_amt = round(local_random.uniform(1000, 50000), 2)
        sector_flow = f"{flow_dir}{flow_amt}万"
        
        return {
            "stock_code": stock_code,
            "stock_name": realtime['name'],
            "current_price": current_price,
            "pressure_level": pressure,
            "support_level": support,
            "score": score,
            "recommendation": recommendation,
            "volume_status": volume_status,
            "sector_flow": sector_flow,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def get_portfolio():
        """
        Get portfolio stocks from Supabase DB.
        """
        supabase = get_supabase_client()
        try:
            response = supabase.table('portfolio_stocks').select('*').order('created_at', desc=True).execute()
            
            # Convert to expected format
            portfolio = []
            for row in response.data:
                portfolio.append({
                    "code": row['stock_code'],
                    "name": row['stock_name'] or "未知",
                    "add_time": row['created_at'],
                    "cost": row.get('cost', '未知'),
                    "motivation": row.get('motivation', '无'),
                    "risk_sell_time": row.get('risk_sell_time', '无')
                })
            return portfolio
        except Exception as e:
            print(f"Error fetching portfolio: {e}")
            return []
