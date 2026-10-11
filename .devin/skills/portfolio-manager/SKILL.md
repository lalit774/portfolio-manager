# Portfolio Manager

Manages a trading portfolio by ingesting buy (long) and short signals derived from market analysis, sizing positions per risk rules, tracking portfolio state, and producing trade confirmations + snapshots.

## When to Use

Trigger this skill whenever the user:
- Sends a signal to add/long or short a stock
- Asks for portfolio status, exposure, or P&L
- Wants trades logged over time
- Requests a portfolio snapshot or summary

## Portfolio Tickers

AMCI, AVGO, AXTI, CRWV, MDA.TO, META, MRVL, MU, NVTS, QSI, SNDK, SPCX, WDC

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

## Workflow

1. **Validate the signal**: Check ticker format, required fields present, ticker is in allowed list
2. **Check against risk rules**: Validate signal against all risk rules before accepting
3. **Calculate order size**: Determine exact order size from current portfolio value
4. **Log the trade**: Write to persistent portfolio ledger (`.devin/portfolio_ledger.json`)
5. **Recalculate portfolio state**: Update cash, positions, net exposure, sector weights
6. **Return trade confirmation + portfolio snapshot**: Show trade details and updated portfolio state
7. **Flag open positions**: Check any open position that has hit its stop-loss or target

## Risk Rules (Defaults)

- **Max position size per name**: 8% of portfolio
- **Max aggregate short exposure**: 20% of portfolio
- **Max single-sector concentration**: 25%
- **Every short MUST have a stop-loss**: Uncapped downside otherwise
- **Minimum cash/margin buffer**: 10%
- **Reject signals that breach any rule**: Provide clear reason for rejection

## Output Format

### Trade Confirmation
- Ticker
- Direction
- Size (shares and $ value)
- Entry price
- Stop-loss level
- Target / take-profit
- Timestamp

### Portfolio Table
- Ticker
- Direction
- Shares
- Entry price
- Current price
- Unrealized P&L
- % of portfolio

### Running Realized P&L Log
- Historical log of closed trades with realized gains/losses

## Data Storage

Portfolio state is stored in `.devin/portfolio_ledger.json` with structure:
```json
{
  "portfolio_value": 100000,
  "cash": 50000,
  "positions": [
    {
      "ticker": "NVDA",
      "direction": "long",
      "shares": 10,
      "entry_price": 450.00,
      "current_price": 480.00,
      "stop_loss": 420.00,
      "target": 550.00,
      "conviction": 4,
      "timeframe": "swing",
      "entry_timestamp": "2026-10-10T10:00:00Z"
    }
  ],
  "realized_pnl": [],
  "trade_log": []
}
```

## Guardrails

- This skill tracks/simulates based on signals the user supplies — it does not generate buy/sell recommendations itself
- It does not place real trades unless explicitly wired to a connected brokerage API
- Always show risk-rule check results before confirming a trade
- Maintain a clear audit trail of all trades and portfolio state changes
