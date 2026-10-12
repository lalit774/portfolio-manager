# Portfolio Data Fetching

This directory contains scripts to fetch real-time market data for your portfolio dashboard.

## Options

### Option 1: yfinance (Recommended - Free, No API Key)

**Script:** `fetch_data_yfinance.py`

**Features:**
- ✅ Free to use
- ✅ No API key required
- ✅ Real-time stock prices
- ✅ Technical indicators (SMA, RSI)
- ✅ Company fundamentals (P/E, market cap, sector)
- ✅ Analyst recommendations
- ✅ 52-week high/low

**Installation:**
```bash
pip install yfinance
```

**Usage:**
```bash
python3 fetch_data_yfinance.py
```

**Output:**
- `portfolio_data.json` - Contains all fetched data
- Console output with market analysis summary

---

### Option 2: Alpha Vantage + News API (Requires API Keys)

**Script:** `fetch_portfolio_data.py`

**Features:**
- Real-time stock prices via Alpha Vantage
- News articles via News API
- Technical indicators
- Rate limiting included

**API Keys Required:**
1. **Alpha Vantage:** Get free key at https://www.alphavantage.co/support/#api-key
2. **News API:** Get free key at https://newsapi.org/

**Setup:**
```bash
# Edit the script and add your API keys:
API_KEYS = {
    'alpha_vantage': 'YOUR_KEY_HERE',
    'news_api': 'YOUR_KEY_HERE'
}
```

**Usage:**
```bash
python3 fetch_portfolio_data.py
```

---

## Data Output Structure

The `portfolio_data.json` file contains:

```json
{
  "META": {
    "price_data": {
      "price": 380.40,
      "change": 5.30,
      "change_percent": 1.41,
      "volume": 15000000,
      "high": 385.00,
      "low": 375.00,
      "market_cap": 950000000000,
      "pe_ratio": 25.5,
      "dividend_yield": 0.0,
      "52_week_high": 400.00,
      "52_week_low": 250.00,
      "beta": 1.2,
      "sector": "Technology",
      "industry": "Internet Content & Information",
      "recommendation": "buy",
      "target_price": 425.00
    },
    "technical": {
      "sma_20": 365.50,
      "sma_50": 340.20,
      "rsi": 58.3,
      "trend": "Bullish",
      "above_sma_20": true
    },
    "last_updated": "2026-10-11T20:30:00"
  }
}
```

---

## Integration with Portfolio Dashboard

### Step 1: Fetch Data
```bash
python3 fetch_data_yfinance.py
```

### Step 2: Update Portfolio Ledger
Use the fetched data to update `portfolio_ledger.json`:

```python
import json

# Load fetched data
with open('portfolio_data.json', 'r') as f:
    data = json.load(f)

# Load portfolio ledger
with open('.devin/portfolio_ledger.json', 'r') as f:
    portfolio = json.load(f)

# Update current prices
for position in portfolio['positions']:
    ticker = position['ticker']
    if ticker in data:
        position['current_price'] = data[ticker]['price_data']['price']
        # Add technical indicators
        position['technical'] = data[ticker]['technical']
        # Add fundamentals
        position['fundamentals'] = {
            'pe_ratio': data[ticker]['price_data']['pe_ratio'],
            'market_cap': data[ticker]['price_data']['market_cap'],
            'sector': data[ticker]['price_data']['sector']
        }

# Save updated ledger
with open('.devin/portfolio_ledger.json', 'w') as f:
    json.dump(portfolio, f, indent=2)
```

### Step 3: Run Analysis
```bash
python3 portfolio_analysis.py
```

### Step 4: View Dashboard
Open `portfolio_dashboard.html` in your browser.

---

## Automated Updates

To automate daily data fetching, create a cron job or use a task scheduler:

**Linux/Mac (cron):**
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/portfolio-manager && python3 fetch_data_yfinance.py
```

**Windows (Task Scheduler):**
- Create a scheduled task to run `fetch_data_yfinance.py` daily

---

## Recommended Tickers

The scripts fetch data for:

**Portfolio Holdings:**
- AMCI, AVGO, AXTI, CRWV, MDA.TO, META, MRVL, MU, NVTS, QSI, SNDK, SPCX, WDC, GOLD, PLTO, SVR

**Recommended Stocks:**
- VOO, ENB, L, SHOP, JNJ, FPL, H, MRU, ATD, PFE, UNH, GIB.A, VTI, XIC

---

## Troubleshooting

**Issue:** `ModuleNotFoundError: No module named 'yfinance'`
**Solution:** `pip install yfinance`

**Issue:** Rate limiting errors
**Solution:** The scripts include rate limiting (0.5s delay between requests). If you still hit limits, increase the delay.

**Issue:** Canadian stocks not found
**Solution:** The script automatically adds `.TO` suffix for Canadian tickers.

**Issue:** CDR stocks
**Solution:** The script has a mapping to convert CDR tickers to regular tickers for data fetching.

---

## Next Steps

1. Install yfinance: `pip install yfinance`
2. Run the fetcher: `python3 fetch_data_yfinance.py`
3. Integrate with update_portfolio.py to auto-update the ledger
4. Set up automated daily fetching
5. Update the dashboard to display the new data fields (technical indicators, fundamentals)
