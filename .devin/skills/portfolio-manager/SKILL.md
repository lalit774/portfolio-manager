# Portfolio Manager

Manages a trading portfolio by ingesting buy (long) and short signals derived from market analysis, sizing positions per risk rules, tracking portfolio state, producing trade confirmations + snapshots, and fetching real-time market data for comprehensive portfolio analysis.

## When to Use

Trigger this skill whenever the user:
- Sends a signal to add/long or short a stock
- Asks for portfolio status, exposure, or P&L
- Wants trades logged over time
- Requests a portfolio snapshot or summary
- Wants to view charts or portfolio visualization
- Requests market news or analysis
- Wants stock recommendations by sector
- Needs to update portfolio from CSV data
- Wants to fetch real-time market data

## Portfolio Tickers

**Original Holdings:**
AMCI, AVGO, AXTI, CRWV, MDA.TO, META, MRVL, MU, NVTS, QSI, SNDK, SPCX, WDC

**Additional Holdings (from CSV):**
GOLD, PLTO, SVR

**CDR Holdings (Canadian):**
AVGO CDR, CRWV CDR, META CDR, MU CDR, SNDK CDR, SPCX CDR, WDC CDR

## Signal Schema

Each incoming signal must include:
- **ticker**: Stock symbol (must be from portfolio tickers list)
- **direction**: `long` | `short`
- **conviction**: 1–5 (integer) or percentage (e.g., 0.75) [default: 3]
- **size**: % of portfolio (e.g., 5%) or $ amount (e.g., $5000) [default: 5%]
- **rationale**: Brief market analysis summary [default: "User-provided signal"]
- **stop-loss level**: Price level for stop-loss [default: -10% from entry price]
- **target / take-profit**: Price target [default: +20% from entry price]
- **timeframe**: `day` | `swing` | `multi-week` [default: swing]
- **timestamp**: When the signal was generated [default: current time]
- **currency**: `CAD` | `USD` [optional, auto-detected if not provided]
- **asset_type**: `equity` | `etf` | `precious_metal` | `currency` [optional, default: equity]

## Workflow

1. **Validate the signal**: Check ticker format, required fields present, ticker is in allowed list
2. **Check against risk rules**: Validate signal against all risk rules before accepting
3. **Calculate order size**: Determine exact order size from current portfolio value
4. **Log the trade**: Write to persistent portfolio ledger (`.devin/portfolio_ledger.json`)
5. **Recalculate portfolio state**: Update cash, positions, net exposure, sector weights
6. **Return trade confirmation + portfolio snapshot**: Show trade details and updated portfolio state
7. **Flag open positions**: Check any open position that has hit its stop-loss or target
8. **Fetch market data** (optional): Get real-time prices, technical indicators, and news
9. **Generate market analysis**: Provide sentiment, trends, and recommendations
10. **Update dashboard**: Refresh HTML dashboard with latest data

## Risk Rules (Defaults)

- **Max position size per name**: 8% of portfolio (excluding precious metals and currency)
- **Max aggregate short exposure**: 20% of portfolio
- **Max single-sector concentration**: 25%
- **Every short MUST have a stop-loss**: Uncapped downside otherwise
- **Minimum cash/margin buffer**: 10%
- **Reject signals that breach any rule**: Provide clear reason for rejection

## Data Fetching

### Real-Time Market Data

**Script:** `fetch_data_yfinance.py` (recommended - free, no API key)

**Features:**
- Real-time stock prices via yfinance
- Technical indicators (SMA 20/50, RSI, trend analysis)
- Company fundamentals (P/E ratio, market cap, sector, beta)
- Analyst recommendations and target prices
- 52-week high/low data
- Automatic handling of Canadian stocks (.TO suffix)
- CDR ticker mapping

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

### Alternative: Alpha Vantage + News API

**Script:** `fetch_portfolio_data.py`

**Features:**
- Real-time stock prices via Alpha Vantage
- News articles via News API
- Technical indicators
- Rate limiting included

**Setup:** Requires API keys (see DATA_FETCHING.md for details)

## Currency Tracking

The portfolio supports multi-currency holdings:
- **CAD**: Canadian dollar positions (Canadian CDRs, Canadian stocks)
- **USD**: US dollar positions (US stocks)
- Currency is determined by ticker or explicitly specified
- Portfolio totals calculated in CAD (USD converted at 1.35 exchange rate)
- No artificial CAD/USD currency positions (currency is metadata on holdings)

## Asset Types

Supported asset types:
- **equity**: Standard stock positions
- **etf**: Exchange-traded funds
- **precious_metal**: Gold, silver, etc.
- **currency**: Cash holdings (rarely used as positions)

## Market Analysis & Recommendations

### Analysis Output Includes:
- Portfolio sentiment (Bullish/Bearish/Neutral)
- Winning vs losing positions
- Sector concentration analysis
- Volatility assessment
- Growth potential indicators

### Stock Recommendations by Sector:

**1. Defensive Positions (Utilities & Consumer Staples)**
- Utilities: FPL.TO, ENB.TO, H.TO
- Consumer Staples: L.TO, MRU.TO, ATD.TO

**2. Healthcare Sector**
- Large Cap: JNJ, PFE, UNH
- Canadian: GIB.A.TO, LIF.TO

**3. ETFs for Broad Market Exposure**
- Broad Market: VOO, VTI, XIC.TO
- Sector ETFs: XLV, XLU, XLP
- Dividend ETFs: SCHD, VYM

**4. Small Cap Growth Stocks (High Risk/High Reward)**
- Technology: COIN, PLTR, UPST
- Canadian: SHOP.TO, DOO.TO, BN.TO

### Top 5 Recommended Stocks:
1. VOO (Vanguard S&P 500 ETF) - 10-15% allocation, Low risk
2. ENB.TO (Enbridge) - 5-8% allocation, Low-Medium risk
3. L.TO (Loblaw Companies) - 5-8% allocation, Low risk
4. SHOP.TO (Shopify) - 3-5% allocation, High risk
5. JNJ (Johnson & Johnson) - 5-8% allocation, Low-Medium risk

## Output Format

### Trade Confirmation
- Ticker
- Direction
- Size (shares and $ value)
- Entry price
- Stop-loss level
- Target / take-profit
- Timestamp
- Currency
- Asset type

### Portfolio Table
- Ticker
- Currency
- Shares
- Entry price
- Current price
- Total Cost (in local currency)
- % of portfolio
- Stop-loss
- Target
- Recommendation (Bullish/Neutral/Bearish)
- Market Analysis

### Market Analysis
- Overall market sentiment
- Position-by-position analysis
- Sector breakdown
- Currency allocation (CAD/USD)
- Technical indicators
- News updates

### Charts & Visualization
- Portfolio allocation pie chart
- Position size vs risk limit bar chart
- Conviction distribution
- Unrealized P&L by position
- Text-based charts in terminal
- Interactive HTML dashboard

## Data Storage

Portfolio state is stored in `.devin/portfolio_ledger.json` with structure:
```json
{
  "portfolio_value": 13760.67,
  "cash": 0,
  "positions": [
    {
      "ticker": "META CDR",
      "direction": "long",
      "shares": 26.3896,
      "entry_price": 26.65,
      "current_price": 38.04,
      "book_cost_cad": 1070.10,
      "book_cost_usd": 0,
      "stop_loss": 23.99,
      "target": 31.98,
      "conviction": 3,
      "timeframe": "swing",
      "entry_timestamp": "2026-10-10T00:00:00Z",
      "asset_type": "equity",
      "market_analysis": "Strong recovery from entry, social media/ads demand resilient. AI investments driving growth.",
      "recommendation": "BULLISH"
    }
  ],
  "trade_log": []
}
```

## Additional Files

- **portfolio_analysis.py**: Terminal-based portfolio analysis with text charts
- **portfolio_dashboard.html**: Interactive browser dashboard with charts
- **update_portfolio.py**: CSV import/update script
- **fetch_data_yfinance.py**: Real-time market data fetcher
- **fetch_portfolio_data.py**: Alternative data fetcher (requires API keys)
- **DATA_FETCHING.md**: Documentation for data fetching
- **PORTFOLIO_REPORT.md**: Generated portfolio report

## CSV Import

The portfolio can be updated from CSV files:
- Supports holdings report CSVs
- Excludes PII (account name, type, number)
- Updates current prices and market values
- Adds new positions from CSV
- Handles CDR ticker normalization
- Adds asset type classification

## PII Protection

The portfolio system excludes:
- Account name
- Account type
- Account number
- Any other personally identifiable information

## Guardrails

- This skill tracks/simulates based on signals the user supplies — it does not generate buy/sell recommendations itself (except for sector-based recommendations based on market analysis)
- It does not place real trades unless explicitly wired to a connected brokerage API
- Always show risk-rule check results before confirming a trade
- Maintain a clear audit trail of all trades and portfolio state changes
- Protect user privacy by excluding PII from all data storage
- Currency tracking does not create artificial currency positions - currency is metadata on holdings
- Technical analysis and recommendations are for informational purposes only, not financial advice

## Automation

The system supports automated data fetching:
- Daily data updates via cron jobs or task scheduler
- Automatic portfolio recalculation
- Dashboard refresh capabilities
- See DATA_FETCHING.md for setup instructions
