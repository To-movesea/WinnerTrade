
@app.route('/api/debug', methods=['GET'])
def debug_status():
    """
    Debug endpoint to check environment variables and database connection.
    WARNING: Do not expose sensitive full keys in production output.
    """
    import os
    from supabase_client import get_supabase_client
    
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    
    # Mask key for safety
    masked_key = f"{key[:5]}...{key[-5:]}" if key and len(key) > 10 else "Not Set"
    masked_url = f"{url[:15]}..." if url else "Not Set"
    
    status = {
        "env": {
            "SUPABASE_URL_SET": bool(url),
            "SUPABASE_KEY_SET": bool(key),
            "URL_PREVIEW": masked_url,
            "KEY_PREVIEW": masked_key,
            "IS_SERVERLESS": bool(os.environ.get('VERCEL')),
        },
        "db_connection": "Unknown"
    }
    
    try:
        supabase = get_supabase_client()
        # Try a simple lightweight query
        res = supabase.table('experience_rules').select('count', count='exact').execute()
        status["db_connection"] = "Success"
        status["record_count"] = res.count
    except Exception as e:
        status["db_connection"] = f"Failed: {str(e)}"
        
    return jsonify(status)
