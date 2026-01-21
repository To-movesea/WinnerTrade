# PyWencai Integration Plan

This document outlines the plan to integrate `pywencai` into the `WinnerTrain` project to enable natural language stock queries using Tonghuashun Wencai data.

## 1. Overview

`pywencai` is a Python library that interfaces with Tonghuashun Wencai (iWencai) to fetch stock data using natural language queries (e.g., "high dividend yield stocks", "P/E ratio < 20"). This integration will add a new capability to the backend to perform these searches.

**Note:** `pywencai` requires a valid cookie from iWencai to function correctly due to recent security updates. It also requires a Node.js environment.

## 2. Dependencies

The following changes are needed in `stock_assistant/backend/requirements.txt`:
- Add `pywencai`

**System Requirement:**
- Node.js (v16+) must be installed on the machine running the backend.

## 3. Configuration

We need to store the Wencai cookie securely.
- Update `stock_assistant/backend/.env` to include:
  ```
  WENCAI_COOKIE="your_cookie_here"
  ```

## 4. Code Architecture

### New Module / Class
We will extend `stock_assistant/backend/stock_api.py` (or create a new file if preferred, but extending is simpler for now) to include a `WencaiClient` class.

**Proposed Class Structure:**

```python
import pywencai
import os

class WencaiClient:
    @staticmethod
    def search(query, sort_key=None, sort_order='asc'):
        """
        Execute a Wencai natural language query.
        
        Args:
            query (str): The search query (e.g., "退市股票")
            sort_key (str): Column name to sort by
            sort_order (str): 'asc' or 'desc'
            
        Returns:
            dict: Result data (records) or None if failed
        """
        cookie = os.environ.get('WENCAI_COOKIE')
        if not cookie:
            print("Warning: WENCAI_COOKIE not set")
            # You might want to raise error or return None
        
        try:
            # pywencai.get returns a DataFrame or dict
            res = pywencai.get(
                query=query, 
                sort_key=sort_key, 
                sort_order=sort_order, 
                cookie=cookie,
                loop=True # Optional: to get all pages
            )
            
            if res is None:
                return None
                
            # Convert DataFrame to list of dicts for JSON API response
            if hasattr(res, 'to_dict'):
                return res.to_dict(orient='records')
            return res
            
        except Exception as e:
            print(f"Error querying Wencai: {e}")
            return None
```

## 5. API Integration (Optional / Future)

To expose this to the frontend, we would update `app.py` to add a route:
- `POST /api/wencai/search`
  - Body: `{ "query": "..." }`

## 6. Modification Points Summary

1.  **Modify `stock_assistant/backend/requirements.txt`**: Add `pywencai`.
2.  **Modify `stock_assistant/backend/.env`**: Add `WENCAI_COOKIE` placeholder.
3.  **Modify `stock_assistant/backend/stock_api.py`**: Add `WencaiClient` class.
