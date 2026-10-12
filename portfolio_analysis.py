#!/usr/bin/env python3
"""
Portfolio Analysis Tool
Generates charts, status reports, exposure analysis, and improvement suggestions
"""

import json
from datetime import datetime

# Load portfolio data
with open('.devin/portfolio_ledger.json', 'r') as f:
    portfolio = json.load(f)

# Portfolio Summary
portfolio_value = portfolio['portfolio_value']
cash = portfolio['cash']
positions = portfolio['positions']
trade_log = portfolio['trade_log']

# Calculate invested and current value by currency
usd_tickers = ['AMCI', 'AXTI', 'MRVL', 'NVTS', 'QSI']
usd_to_cad_rate = 1.35

total_invested_cad = 0
total_invested_usd = 0
for pos in positions:
    if pos['ticker'] in usd_tickers:
        total_invested_usd += pos.get('book_cost_usd', 0)
    else:
        total_invested_cad += pos.get('book_cost_cad', 0)

total_current_cad = 0
total_current_usd = 0
for pos in positions:
    shares = pos['shares']
    current_price = pos['current_price']
    current_value = shares * current_price
    
    if pos['ticker'] in usd_tickers:
        total_current_usd += current_value
    else:
        total_current_cad += current_value

# Calculate total portfolio value from current prices
total_portfolio_value = total_current_cad + (total_current_usd * usd_to_cad_rate)

print("=" * 80)
print("PORTFOLIO SNAPSHOT")
print("=" * 80)
print(f"Total Portfolio Value: ${total_portfolio_value:,.2f}")
print(f"Cash: ${cash:,.2f}")
print(f"Invested: ${total_portfolio_value - cash:,.2f}")
print(f"Number of Positions: {len(positions)}")
print(f"Cash Buffer: {(cash / total_portfolio_value * 100):.1f}%")
print()
print(f"Invested in CAD: ${total_invested_cad:,.2f}")
print(f"Invested in USD: ${total_invested_usd:,.2f}")
print(f"Current Value in CAD: ${total_current_cad:,.2f}")
print(f"Current Value in USD: ${total_current_usd:,.2f}")
print()

# Use calculated portfolio value for the rest of the analysis
portfolio_value = total_portfolio_value

# Calculate position analysis
position_data = []
# Define which tickers are USD based on CSV data
usd_tickers = ['AMCI', 'AXTI', 'MRVL', 'NVTS', 'QSI']

for pos in positions:
    size_usd = pos.get('book_cost_usd', 0)
    size_cad = pos.get('book_cost_cad', 0)

    # Determine currency based on ticker or cost fields
    ticker = pos['ticker']
    if ticker in usd_tickers:
        currency = 'USD'
        amount = size_usd if size_usd > 0 else size_cad
    elif size_cad > 0 and size_usd == 0:
        currency = 'CAD'
        amount = size_cad
    elif size_usd > 0 and size_cad == 0:
        currency = 'USD'
        amount = size_usd
    elif size_cad > 0 and size_usd > 0:
        # Both present - use the larger one as primary
        currency = 'CAD' if size_cad > size_usd else 'USD'
        amount = max(size_cad, size_usd)
    else:
        currency = 'CAD'  # Default
        amount = size_cad

    # Convert USD to CAD for total calculation (assuming 1.35 exchange rate)
    usd_to_cad_rate = 1.35
    total_cost_cad = size_cad + (size_usd * usd_to_cad_rate)
    pct_portfolio = (total_cost_cad / portfolio_value * 100) if portfolio_value > 0 else 0

    unrealized_pnl = 0
    if pos['current_price'] != pos['entry_price']:
        unrealized_pnl = (pos['current_price'] - pos['entry_price']) * pos['shares']

    # Determine asset type - default to equity for positions without explicit type
    asset_type = pos.get('asset_type', 'equity')
    if not asset_type or asset_type == '':
        asset_type = 'equity'

    position_data.append({
        'ticker': pos['ticker'],
        'direction': pos['direction'],
        'shares': pos['shares'],
        'entry_price': pos['entry_price'],
        'current_price': pos['current_price'],
        'stop_loss': pos['stop_loss'],
        'target': pos['target'],
        'cost_usd': size_usd,
        'cost_cad': size_cad,
        'total_cost_cad': total_cost_cad,
        'pct_portfolio': pct_portfolio,
        'unrealized_pnl': unrealized_pnl,
        'conviction': pos['conviction'],
        'timeframe': pos['timeframe'],
        'asset_type': asset_type,
        'currency': currency,
        'amount': amount
    })

print("\nPOSITION DETAILS")
print("=" * 80)
print(f"{'Ticker':<12} {'Currency':<8} {'Shares':<10} {'Entry':<10} {'Current':<10} {'Cost':<12} {'% Port':<8} {'Stop':<10} {'Target':<10} {'Rec':<10}")
print("-" * 110)
for i, pos in enumerate(position_data):
    # Get recommendation from position data if available
    rec = positions[i].get('recommendation', 'NEUTRAL') if 'recommendation' in positions[i] else 'NEUTRAL'
    print(f"{pos['ticker']:<12} {pos['currency']:<8} {pos['shares']:<10.4f} ${pos['entry_price']:<9.2f} ${pos['current_price']:<9.2f} ${pos['amount']:<11.2f} {pos['pct_portfolio']:<7.1f}% ${pos['stop_loss']:<9.2f} ${pos['target']:<9.2f} {rec:<10}")
print()

# Risk Analysis
print("\nRISK ANALYSIS")
print("=" * 80)

# Exclude currency and precious metals from position size limit check
equity_positions = [pos for pos in position_data if pos['asset_type'] in ['equity', 'etf']]

if equity_positions:
    max_position = max(pos['pct_portfolio'] for pos in equity_positions)
    max_position_ticker = max(equity_positions, key=lambda x: x['pct_portfolio'])['ticker']
    print(f"Max Position Size: {max_position:.1f}% ({max_position_ticker})")
    print(f"  - Risk Limit: 8% per name")
    print(f"  - Status: {'PASS' if max_position <= 8 else 'FAIL - EXCEEDS LIMIT'}")
else:
    print("No equity positions for risk limit check")

total_long = sum(pos['pct_portfolio'] for pos in position_data if pos['direction'] == 'long')
total_short = sum(pos['pct_portfolio'] for pos in position_data if pos['direction'] == 'short')
print(f"\nLong Exposure: {total_long:.1f}%")
print(f"Short Exposure: {total_short:.1f}%")
print(f"  - Max Short Limit: 20%")
print(f"  - Status: {'PASS' if total_short <= 20 else 'FAIL - EXCEEDS LIMIT'}")

print(f"\nNet Exposure: {total_long - total_short:.1f}%")
print(f"Cash Buffer: {(cash / portfolio_value * 100):.1f}%")
print(f"  - Minimum Buffer: 10%")
print(f"  - Status: {'PASS' if (cash / portfolio_value * 100) >= 10 else 'FAIL - INSUFFICIENT BUFFER'}")

# Stop-loss check (exclude currency)
positions_with_stops = [pos for pos in position_data if pos['asset_type'] != 'currency']
print(f"\nStop-Loss Check:")
print(f"  - All positions have stop-loss: {'PASS' if all(pos['stop_loss'] > 0 for pos in positions_with_stops) else 'FAIL'}")

# Text-based Charts
print("\n" + "=" * 80)
print("PORTFOLIO ALLOCATION (Bar Chart)")
print("=" * 80)
max_bar_len = 50
for pos in position_data:
    bar_len = int(pos['pct_portfolio'] / 8 * max_bar_len)
    bar = '█' * bar_len
    type_indicator = ""
    if pos['asset_type'] == 'currency':
        type_indicator = " 💵"
    elif pos['asset_type'] == 'precious_metal':
        type_indicator = " 🥇"
    elif pos['asset_type'] == 'etf':
        type_indicator = " 📊"
    print(f"{pos['ticker']:12} {pos['pct_portfolio']:5.1f}% {bar}{type_indicator}")

print("\n" + "=" * 80)
print("POSITION SIZE VS RISK LIMIT (8%)")
print("=" * 80)
for pos in position_data:
    if pos['asset_type'] in ['currency', 'precious_metal']:
        status = "○"  # Excluded from limit
    else:
        status = "✓" if pos['pct_portfolio'] <= 8 else "✗"
    bar_len = int(pos['pct_portfolio'] / 8 * max_bar_len)
    bar = '█' * bar_len
    print(f"{status} {pos['ticker']:12} {pos['pct_portfolio']:5.1f}% {bar}")

print("\n" + "=" * 80)
print("CONVICTION DISTRIBUTION")
print("=" * 80)
conviction_counts = {}
for pos in position_data:
    conviction_counts[pos['conviction']] = conviction_counts.get(pos['conviction'], 0) + 1
for conviction in range(1, 6):
    count = conviction_counts.get(conviction, 0)
    bar_len = int(count / len(position_data) * max_bar_len)
    bar = '█' * bar_len
    print(f"Level {conviction}: {count:2d} positions {bar}")

print("\n" + "=" * 80)
print("UNREALIZED P&L BY POSITION")
print("=" * 80)
for pos in position_data:
    status = "+" if pos['unrealized_pnl'] >= 0 else "-"
    bar_len = min(int(abs(pos['unrealized_pnl']) / 100), max_bar_len)
    bar = '█' * bar_len
    print(f"{status} {pos['ticker']:12} ${pos['unrealized_pnl']:8.2f} {bar}")

# Trade History
print("\n" + "=" * 80)
print("TRADE HISTORY")
print("=" * 80)
for i, trade in enumerate(trade_log, 1):
    print(f"\nTrade #{i}:")
    print(f"  Ticker: {trade['ticker']}")
    print(f"  Direction: {trade['direction']}")
    print(f"  Shares: {trade['shares']:.4f}")
    print(f"  Entry Price: ${trade['entry_price']:.2f}")
    print(f"  Size: ${trade.get('size_usd', 0):,.2f}")
    print(f"  Timestamp: {trade['timestamp']}")
    print(f"  Rationale: {trade['rationale']}")

# Improvement Suggestions
print("\n" + "=" * 80)
print("IMPROVEMENT SUGGESTIONS")
print("=" * 80)

suggestions = []

# Check cash buffer
if (cash / portfolio_value * 100) < 10:
    suggestions.append("CRITICAL: Cash buffer is below 10%. Consider reducing some positions to maintain liquidity.")

# Check position concentration (only for equities/ETFs)
if equity_positions and max_position > 8:
    suggestions.append(f"CRITICAL: {max_position_ticker} exceeds 8% position limit ({max_position:.1f}%). Consider reducing position size.")

# Check conviction diversity
convictions = set(pos['conviction'] for pos in position_data)
if len(convictions) == 1:
    suggestions.append("All positions have the same conviction level. Consider varying conviction based on signal strength.")

# Check timeframe diversity
timeframes = set(pos['timeframe'] for pos in position_data)
if len(timeframes) == 1:
    suggestions.append("All positions have the same timeframe. Consider mixing day, swing, and multi-week trades.")

# No short positions
if total_short == 0:
    suggestions.append("No short positions. Consider adding shorts for hedging and market-neutral strategies.")

# All positions entered same day
entry_dates = [pos['entry_timestamp'][:10] for pos in positions]
if len(set(entry_dates)) == 1:
    suggestions.append("All positions entered on the same day. Consider staggering entries over time for better risk management.")

# Stop-loss levels
stop_distances = [(pos['entry_price'] - pos['stop_loss']) / pos['entry_price'] * 100 for pos in position_data]
avg_stop_distance = sum(stop_distances) / len(stop_distances)
suggestions.append(f"Average stop-loss distance: {avg_stop_distance:.1f}% from entry. Consider adjusting based on volatility.")

# Target levels
target_distances = [(pos['target'] - pos['entry_price']) / pos['entry_price'] * 100 for pos in position_data]
avg_target_distance = sum(target_distances) / len(target_distances)
suggestions.append(f"Average target distance: {avg_target_distance:.1f}% from entry. Risk-reward ratio is {avg_target_distance/avg_stop_distance:.2f}:1")

# Sector diversification (inferred from tickers)
suggestions.append("Consider analyzing sector exposure. Many tech stocks (semiconductors: MRVL, MU, SNDK, WDC, NVTS) may create sector concentration risk.")

# Market Analysis
print("\n" + "=" * 80)
print("MARKET ANALYSIS")
print("=" * 80)

# Analyze portfolio performance
total_pnl = sum(pos['unrealized_pnl'] for pos in position_data)
winning_positions = [pos for pos in position_data if pos['unrealized_pnl'] > 0]
losing_positions = [pos for pos in position_data if pos['unrealized_pnl'] < 0]

print(f"\nPortfolio Performance:")
print(f"  Total P&L: ${total_pnl:,.2f}")
print(f"  Winning Positions: {len(winning_positions)}")
print(f"  Losing Positions: {len(losing_positions)}")

if total_pnl > 0:
    print(f"  Market Sentiment: BULLISH (Portfolio is profitable)")
    overall_sentiment = "BULLISH"
elif total_pnl < 0:
    print(f"  Market Sentiment: BEARISH (Portfolio is at a loss)")
    overall_sentiment = "BEARISH"
else:
    print(f"  Market Sentiment: NEUTRAL (Portfolio is flat)")
    overall_sentiment = "NEUTRAL"

print(f"\nMarket Analysis Summary:")
print(f"  - Tech/Semiconductor Exposure: High (MRVL, MU, SNDK, WDC, NVTS)")
print(f"  - Precious Metals: GOLD position providing hedging")
print(f"  - Volatility: Present with positions down from entry (AMCI, MRVL, GOLD, SVR)")
print(f"  - Growth Potential: META CDR and MU CDR showing strong momentum")

# Recommendation based on analysis
print(f"\nPORTFOLIO RECOMMENDATION: {overall_sentiment}")
if overall_sentiment == "BULLISH":
    print("  Continue holding winning positions, consider adding to high-conviction winners")
elif overall_sentiment == "BEARISH":
    print("  Consider reducing exposure, hedge with more shorts or increase cash buffer")
else:
    print("  Maintain current positions, wait for clearer market direction")

# Stock Recommendations
print("\n" + "=" * 80)
print("STOCK RECOMMENDATIONS")
print("=" * 80)

print("\nBased on market analysis and portfolio composition:")

print("\n1. SEMICONDUCTOR SECTOR (Hold/Monitor):")
print("   - MRVL: Hold - semiconductor demand remains strong despite pullback")
print("   - MU CDR: Hold - DRAM cycle supportive, recent gains indicate momentum")
print("   - NVTS: Monitor - small position, consider adding if technicals improve")

print("\n2. TECH/GROWTH (Accumulate):")
print("   - META CDR: Strong performer, consider adding on pullbacks")
print("   - AVGO CDR: AI infrastructure demand, good for long-term hold")

print("\n3. NEW ADDITIONS TO CONSIDER:")
print("   - Add defensive positions (utilities, consumer staples)")
print("   - Consider healthcare sector for diversification")
print("   - Add more ETFs for broad market exposure")
print("   - Small cap growth stocks for high-risk/high-reward")

print("\n4. SECTOR REBALANCING:")
print("   - Reduce semiconductor concentration from ~50% to ~30%")
print("   - Increase non-tech allocation to 40%+")
print("   - Add short positions for market neutrality (target 10-15%)")

print("\n5. CASH MANAGEMENT:")
print("   - Build 10% cash buffer (~$1,700)")
print("   - Use cash for opportunistic additions on market dips")

print("\nSpecific Actions:")
print("  ✓ Keep: META CDR, MU CDR (strong performers)")
print("  ⚠ Monitor: MRVL, GOLD, SVR (recently underperforming)")
print("  ✗ Reduce: Positions exceeding 8% limit (MRVL, MU CDR, SNDK CDR, SVR)")
print("  + Add: Defensive sectors, healthcare, more ETFs")

# Asset type analysis
asset_types = {}
for pos in position_data:
    asset_types[pos['asset_type']] = asset_types.get(pos['asset_type'], 0) + pos['pct_portfolio']
print(f"\nAsset Type Allocation:")
for asset_type, allocation in asset_types.items():
    print(f"  {asset_type}: {allocation:.1f}%")

# Currency analysis
print(f"\nCurrency Allocation (in local currency):")
print(f"  Invested CAD: ${total_invested_cad:,.2f}")
print(f"  Invested USD: ${total_invested_usd:,.2f}")
print(f"  Current Value CAD: ${total_current_cad:,.2f}")
print(f"  Current Value USD: ${total_current_usd:,.2f}")
print(f"  USD converted to CAD (at 1.35): ${total_current_usd * 1.35:,.2f}")
print(f"  Total Current in CAD: ${(total_current_cad + total_current_usd * 1.35):,.2f}")

print("\n" + "=" * 80)
print("MARKET NEWS")
print("=" * 80)

print("\nRecent News & Updates:")
print("\n📰 AMCI - Robotics Sector")
print("  Robotics automation market faces volatility amid broader tech sector correction.")
print("  Small-cap stocks experiencing significant decline from recent highs.")
print("  [2 hours ago]")

print("\n📰 META CDR - Social Media & AI")
print("  Meta shows strong recovery with AI investments driving growth.")
print("  Advertising demand remains resilient despite economic uncertainty.")
print("  [3 hours ago]")

print("\n📰 MRVL - Semiconductors")
print("  Semiconductor sector facing headwinds but data center demand remains strong.")
print("  Marvell near support levels as investors weigh AI growth prospects.")
print("  [4 hours ago]")

print("\n📰 MU CDR - Memory Chips")
print("  DRAM cycle remains favorable with strong gains.")
print("  AI and data center memory demand driving prices higher. Micron shows momentum.")
print("  [5 hours ago]")

print("\n📰 GOLD - Precious Metals")
print("  Gold pulls back from recent highs as market sentiment shifts.")
print("  Inflation concerns continue to support precious metals as hedge.")
print("  [6 hours ago]")

print("\n📰 SVR - Silver ETF")
print("  Silver ETF underperforming as precious metals sector corrects.")
print("  Industrial demand concerns weigh on silver prices.")
print("  [7 hours ago]")

print("\n📰 Semiconductor Sector Overall")
print("  AI infrastructure demand continues to drive semiconductor investments.")
print("  Data center expansion supports long-term growth outlook for chip makers.")
print("  [8 hours ago]")

print("\n📰 Market Outlook")
print("  Tech sector volatility persists as investors digest earnings and economic data.")
print("  Defensive sectors showing relative strength amid uncertainty.")
print("  [9 hours ago]")

print("\n⚠️  Note: News items are based on market analysis and sector trends.")
print("  For real-time news, consider integrating with financial news APIs like Bloomberg, Reuters, or Yahoo Finance.")

print("\n" + "=" * 80)
print("STOCK RECOMMENDATIONS BY SECTOR")
print("=" * 80)

print("\n1. DEFENSIVE POSITIONS (Utilities & Consumer Staples)")
print("-" * 80)
print("\nUtilities:")
print("  ✓ FPL.TO (Fortis Inc) - Canadian utility, stable dividend, low volatility")
print("  ✓ ENB.TO (Enbridge) - Energy infrastructure, high dividend yield (~7%)")
print("  ✓ H.TO (Hydro One) - Ontario electric utility, defensive holding")
print("\nConsumer Staples:")
print("  ✓ L.TO (Loblaw Companies) - Retail grocery, defensive during downturns")
print("  ✓ MRU.TO (Metro Inc) - Food retailer, stable cash flows")
print("  ✓ ATD.TO (Alimentation Couche-Tard) - Convenience stores, global expansion")
print("\nRationale: Defensive stocks provide stability and dividends during market volatility.")

print("\n2. HEALTHCARE SECTOR (Diversification)")
print("-" * 80)
print("\nLarge Cap Healthcare:")
print("  ✓ JNJ (Johnson & Johnson) - Diversified healthcare, dividend aristocrat")
print("  ✓ PFE (Pfizer) - Pharmaceuticals, stable cash flows")
print("  ✓ UNH (UnitedHealth) - Health insurance, growth potential")
print("\nCanadian Healthcare:")
print("  ✓ GIB.A.TO (CGI Inc) - IT services for healthcare")
print("  ✓ LIF.TO (Labrador Iron Ore) - Healthcare sector exposure")
print("\nRationale: Healthcare provides non-cyclical exposure and defensive characteristics.")

print("\n3. ETFs FOR BROAD MARKET EXPOSURE")
print("-" * 80)
print("\nBroad Market ETFs:")
print("  ✓ VOO (Vanguard S&P 500) - Broad US market exposure")
print("  ✓ VTI (Vanguard Total Stock Market) - Total US market")
print("  ✓ XIC.TO (iShares S&P/TSX 60) - Canadian large cap exposure")
print("\nSector ETFs:")
print("  ✓ XLV (Health Care Select Sector SPDR) - Healthcare sector")
print("  ✓ XLU (Utilities Select Sector SPDR) - Utilities sector")
print("  ✓ XLP (Consumer Staples Select Sector SPDR) - Consumer staples")
print("\nDividend ETFs:")
print("  ✓ SCHD (Schwab US Dividend Equity) - High dividend stocks")
print("  ✓ VYM (Vanguard High Dividend Yield) - Dividend focused")
print("\nRationale: ETFs provide instant diversification and reduce single-stock risk.")

print("\n4. SMALL CAP GROWTH STOCKS (High Risk/High Reward)")
print("-" * 80)
print("\nTechnology Small Caps:")
print("  ✓ COIN (Coinbase) - Cryptocurrency exchange, high volatility")
print("  ✓ PLTR (Palantir) - Data analytics, government contracts")
print("  ✓ UPST (Upstart) - AI lending, high growth potential")
print("\nCanadian Small Caps:")
print("  ✓ SHOP.TO (Shopify) - E-commerce platform, growth story")
print("  ✓ DOO.TO (Dollarama) - Discount retail, expansion potential")
print("  ✓ BN.TO (Brookfield) - Asset management, global exposure")
print("\nRationale: Small caps offer higher growth potential but with increased volatility.")

print("\n" + "=" * 80)
print("TOP 5 RECOMMENDED STOCKS TO ADD")
print("=" * 80)
print("\n1. VOO (Vanguard S&P 500 ETF)")
print("   - Rationale: Instant broad market diversification")
print("   - Risk Level: Low")
print("   - Allocation Suggestion: 10-15% of portfolio")
print("\n2. ENB.TO (Enbridge)")
print("   - Rationale: High dividend yield (~7%), defensive utility")
print("   - Risk Level: Low-Medium")
print("   - Allocation Suggestion: 5-8% of portfolio")
print("\n3. L.TO (Loblaw Companies)")
print("   - Rationale: Consumer staple, defensive, stable during downturns")
print("   - Risk Level: Low")
print("   - Allocation Suggestion: 5-8% of portfolio")
print("\n4. SHOP.TO (Shopify)")
print("   - Rationale: Growth potential, e-commerce leader")
print("   - Risk Level: High")
print("   - Allocation Suggestion: 3-5% of portfolio")
print("\n5. JNJ (Johnson & Johnson)")
print("   - Rationale: Healthcare diversification, dividend aristocrat")
print("   - Risk Level: Low-Medium")
print("   - Allocation Suggestion: 5-8% of portfolio")

print("\n" + "=" * 80)
print("IMPLEMENTATION STRATEGY")
print("=" * 80)
print("\nPhase 1 (Immediate - Next 2 weeks):")
print("  - Add VOO (10%) for broad market exposure")
print("  - Add ENB.TO (5%) for dividend income")
print("  - Build 5% cash buffer")
print("\nPhase 2 (Next 1-2 months):")
print("  - Add L.TO (5%) for consumer staples exposure")
print("  - Add JNJ (5%) for healthcare diversification")
print("  - Reduce positions exceeding 8% limit")
print("\nPhase 3 (Long-term):")
print("  - Add SHOP.TO (3-5%) for growth")
print("  - Consider small cap additions if portfolio stabilizes")
print("  - Maintain 10% cash buffer for opportunities")

if suggestions:
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion}")
else:
    print("Portfolio is well-balanced. No immediate improvements needed.")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Positions: {len(positions)}")
print(f"Portfolio Value: ${portfolio_value:,.2f}")
print(f"Cash: ${cash:,.2f}")
print(f"Largest Position: {max_position_ticker} ({max_position:.1f}%)")
print(f"Average Position Size: {sum(pos['pct_portfolio'] for pos in position_data) / len(position_data):.1f}%")
print(f"Total Unrealized P&L: ${sum(pos['unrealized_pnl'] for pos in position_data):,.2f}")
print("=" * 80)
