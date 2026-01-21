
from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
from datetime import datetime
from supabase_client import get_supabase_client
from services import StockService
from stock_api import StockDataClient

app = Flask(__name__)
CORS(app)

# Scheduler
scheduler = BackgroundScheduler()

def daily_analysis_task():
    print(f"[{datetime.now()}] Starting daily portfolio analysis...")
    portfolio = StockService.get_portfolio()
    if not portfolio:
        print("No stocks in portfolio.")
        return

    supabase = get_supabase_client()
    
    # Get active rules
    try:
        response = supabase.table('experience_rules').select('*').eq('is_active', True).execute()
        rules = response.data
    except Exception as e:
        print(f"Error fetching rules: {e}")
        rules = []
    
    results = []
    for stock in portfolio:
        analysis = StockService.analyze_stock(stock['code'])
        analysis['stock_name'] = stock['name']
        
        # Match rules (Mock matching logic)
        matched = []
        for rule in rules:
            # Simple keyword matching for demo purposes
            if "尾盘" in rule['rule_content'] and datetime.now().hour >= 14:
                matched.append(rule['rule_content'])
            if "成交量" in rule['rule_content'] and "放量" in analysis['volume_status']:
                matched.append(rule['rule_content'])
            if "买入" in rule['rule_content'] and analysis['score'] > 80:
                matched.append(rule['rule_content'])
                
        matched_str = "|".join(matched)
        
        # Save to DB
        try:
            data = {
                'stock_code': analysis['stock_code'],
                'stock_name': analysis['stock_name'],
                'pressure_level': analysis['pressure_level'],
                'support_level': analysis['support_level'],
                'score': analysis['score'],
                'recommendation': analysis['recommendation'],
                'volume_status': analysis['volume_status'],
                'sector_flow': analysis['sector_flow'],
                'analysis_time': analysis['analysis_time'],
                'matched_rules': matched_str,
                # Note: analysis_results table might not have current_price column yet
                # We can choose to alter table or just return it in API response
            }
            # Remove keys that might not be in DB yet if schema is strict, or add migration
            # For now, let's assume we just want to DISPLAY it, so we don't save it to historical analysis table unless we migrate
            # But the API /api/portfolio/analysis returns what's in DB.
            # So if we want to show it, we must either:
            # 1. Save it to DB (Requires Migration)
            # 2. Or fetch it in real-time when calling the API (Better for "Current Price")
            
            supabase.table('analysis_results').insert(data).execute()
        except Exception as e:
            print(f"Error saving analysis for {stock['code']}: {e}")
            
        results.append(analysis)
        
    print(f"[{datetime.now()}] Daily analysis completed.")

# Schedule task daily at 15:00 (or every minute for demo)
scheduler.add_job(daily_analysis_task, 'cron', hour=15, minute=0)
# For demo/testing, run every 5 minutes
scheduler.add_job(daily_analysis_task, 'interval', minutes=5)
scheduler.start()

# API Routes

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    portfolio = StockService.get_portfolio()
    return jsonify(portfolio)

@app.route('/api/portfolio', methods=['POST'])
def add_portfolio_stock():
    data = request.json
    stock_code = data.get('stock_code')
    if not stock_code:
        return jsonify({"error": "Stock code is required"}), 400
        
    # Verify stock code and get name
    realtime = StockDataClient.get_realtime_data(stock_code)
    if not realtime:
        return jsonify({"error": "Invalid stock code or data unavailable"}), 404
        
    stock_name = realtime['name']
    
    supabase = get_supabase_client()
    try:
        new_stock = {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'cost': data.get('cost', '未知'),
            'motivation': data.get('motivation', '无'),
            'risk_sell_time': data.get('risk_sell_time', '无')
        }
        # Check if already exists to provide a better error message, or use upsert
        # Upsert: insert or update if conflict. Here we just want to ensure it's there.
        # But for 'add', maybe we want to tell user it's already there?
        # Let's check first.
        existing = supabase.table('portfolio_stocks').select('id').eq('stock_code', stock_code).execute()
        if existing.data:
             return jsonify({"message": "Stock already in portfolio", "stock": new_stock})
             
        supabase.table('portfolio_stocks').insert(new_stock).execute()
        
        # Trigger immediate analysis for this new stock
        analysis = StockService.analyze_stock(stock_code)
        
        return jsonify({"message": "Stock added successfully", "stock": new_stock})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/portfolio/<stock_code>', methods=['PUT'])
def update_portfolio_stock(stock_code):
    data = request.json
    supabase = get_supabase_client()
    try:
        update_data = {}
        if 'cost' in data:
            update_data['cost'] = data['cost']
        if 'motivation' in data:
            update_data['motivation'] = data['motivation']
        if 'risk_sell_time' in data:
            update_data['risk_sell_time'] = data['risk_sell_time']
            
        if not update_data:
             return jsonify({"message": "No data to update"})

        supabase.table('portfolio_stocks').update(update_data).eq('stock_code', stock_code).execute()
        return jsonify({"message": "Stock updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/portfolio/<stock_code>', methods=['DELETE'])
def delete_portfolio_stock(stock_code):
    supabase = get_supabase_client()
    try:
        supabase.table('portfolio_stocks').delete().eq('stock_code', stock_code).execute()
        return jsonify({"message": "Stock deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/portfolio/analysis', methods=['GET'])
def get_portfolio_analysis():
    # Trigger analysis if needed or just return latest results
    supabase = get_supabase_client()
    
    # 1. Get current portfolio stocks first to filter results
    current_portfolio = StockService.get_portfolio()
    valid_stock_codes = set(item['code'] for item in current_portfolio)
    
    try:
        # Fetch all results, ordered by time desc
        response = supabase.table('analysis_results').select('*').order('analysis_time', desc=True).limit(100).execute()
        all_rows = response.data
    except Exception as e:
        print(f"Error fetching analysis: {e}")
        all_rows = []
    
    # Filter to get only the latest unique record for each stock AND ensure it's in current portfolio
    seen_stocks = set()
    unique_rows = []
    for row in all_rows:
        stock_code = row['stock_code']
        if stock_code not in seen_stocks and stock_code in valid_stock_codes:
            unique_rows.append(row)
            seen_stocks.add(stock_code)
            
    # If no results for current portfolio (or missing some), trigger a fresh analysis
    # We check if we have results for all current stocks.
    # If the number of unique results is less than current portfolio size, some might be missing.
    if len(unique_rows) < len(valid_stock_codes):
        daily_analysis_task()
        try:
            response = supabase.table('analysis_results').select('*').order('analysis_time', desc=True).limit(100).execute()
            all_rows = response.data
            # Re-filter after fresh analysis
            seen_stocks = set()
            unique_rows = []
            for row in all_rows:
                stock_code = row['stock_code']
                if stock_code not in seen_stocks and stock_code in valid_stock_codes:
                    unique_rows.append(row)
                    seen_stocks.add(stock_code)
        except Exception as e:
            print(f"Error fetching analysis after task: {e}")
            unique_rows = []
            
    # Inject Real-time Price into the historical/saved analysis results
    # Because "Current Price" should be CURRENT, not when the analysis was saved
    for row in unique_rows:
        stock_code = row['stock_code']
        # Fetch simple realtime price
        realtime = StockDataClient.get_realtime_data(stock_code)
        if realtime:
            row['current_price'] = realtime['price']
        else:
            row['current_price'] = '--'
        
    return jsonify({"stocks": unique_rows, "timestamp": datetime.now().isoformat(), "status": "success"})

@app.route('/api/stock/analysis/<stock_code>', methods=['GET'])
def analyze_single_stock(stock_code):
    analysis = StockService.analyze_stock(stock_code)
    
    # Check rules
    supabase = get_supabase_client()
    try:
        response = supabase.table('experience_rules').select('*').eq('is_active', True).execute()
        rules = response.data
    except Exception as e:
        print(f"Error fetching rules: {e}")
        rules = []
    
    matched = []
    for rule in rules:
        # Mock matching
        if "买入" in rule['rule_content'] and analysis['score'] > 80:
            matched.append(rule['rule_content'])
            
    analysis['matched_rules'] = "|".join(matched)
    return jsonify(analysis)

@app.route('/api/experience/rules', methods=['GET'])
def get_rules():
    supabase = get_supabase_client()
    try:
        response = supabase.table('experience_rules').select('*').order('created_at', desc=True).execute()
        rules = response.data
    except Exception as e:
        print(f"Error fetching rules: {e}")
        rules = []
    return jsonify(rules)

@app.route('/api/experience/rules', methods=['POST'])
def add_rule():
    data = request.json
    supabase = get_supabase_client()
    try:
        new_rule = {
            'rule_content': data['rule'],
            'category': data.get('category', 'general'),
            'description': data.get('description', '')
        }
        response = supabase.table('experience_rules').insert(new_rule).execute()
        return jsonify({"message": "Rule added successfully", "data": response.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/experience/rules/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    data = request.json
    supabase = get_supabase_client()
    try:
        update_data = {
            'rule_content': data['rule'],
            'category': data.get('category', 'general'),
            'description': data.get('description', '')
        }
        supabase.table('experience_rules').update(update_data).eq('id', rule_id).execute()
        return jsonify({"message": "Rule updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/experience/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    supabase = get_supabase_client()
    try:
        supabase.table('experience_rules').delete().eq('id', rule_id).execute()
        return jsonify({"message": "Rule deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/experience/export', methods=['GET'])
def export_rules():
    supabase = get_supabase_client()
    try:
        response = supabase.table('experience_rules').select('*').execute()
        rules = response.data
        
        # On Vercel, we cannot write to disk. Return file directly.
        json_str = json.dumps(rules, ensure_ascii=False, indent=2)
        mem = BytesIO()
        mem.write(json_str.encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem,
            mimetype='application/json',
            as_attachment=True,
            download_name='experience_rules_backup.json'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/experience/import', methods=['POST'])
def import_rules():
    # Support file upload or existing logic
    # If a file is uploaded in request.files
    supabase = get_supabase_client()
    rules = []
    
    try:
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            content = file.read()
            rules = json.loads(content.decode('utf-8'))
        else:
            # Fallback to local file if available (only for local dev)
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            json_path = os.path.join(data_dir, 'experience_rules_backup.json')
            if os.path.exists(json_path):
                 with open(json_path, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
            else:
                 return jsonify({"error": "No file uploaded and no local backup found"}), 400
            
        count = 0
        for rule in rules:
            # Check if exists
            res = supabase.table('experience_rules').select('id').eq('rule_content', rule['rule_content']).execute()
            if not res.data:
                new_rule = {
                    'rule_content': rule['rule_content'],
                    'category': rule.get('category', 'general'),
                    'description': rule.get('description', '')
                }
                supabase.table('experience_rules').insert(new_rule).execute()
                count += 1
                
        return jsonify({"message": f"Imported {count} new rules"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    supabase = get_supabase_client()
    try:
        # Get count
        response = supabase.table('experience_rules').select('id', count='exact').execute()
        total_rules = response.count if response.count is not None else len(response.data)
        
        return jsonify({
            "last_analysis": datetime.now().strftime("%Y-%m-%d 15:00:00"), # Mock
            "next_analysis": "Tomorrow 15:00:00",
            "api_status": "Connected (Supabase)",
            "total_rules": total_rules
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
