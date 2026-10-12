#!/usr/bin/env python3
"""
Update portfolio ledger with current market data from CSV
Excludes PII (account name, type, number)
"""

import json
import csv
from datetime import datetime

# Load current portfolio
with open('.devin/portfolio_ledger.json', 'r') as f:
    portfolio = json.load(f)

# Load CSV data
csv_data = []
with open('/Users/lalitkumar/Downloads/holdings-report-2026-10-11.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_data.append(row)

# Approved ticker list from skill
approved_tickers = ['AMCI', 'AVGO', 'AXTI', 'CRWV', 'MDA.TO', 'META', 'MRVL', 'MU', 'NVTS', 'QSI', 'SNDK', 'SPCX', 'WDC']

# Create mapping from CSV data (excluding PII)
csv_positions = {}
cash_cad = 0.0
cash_usd = 0.0
new_equity_positions = []

for row in csv_data:
    symbol = row['Symbol']
    security_type = row['Security Type']

    # Skip empty symbols
    if not symbol:
        continue

    # Handle currency positions as cash
    if security_type == 'CURRENCY':
        if symbol == 'CAD':
            cash_cad += float(row['Market Value'])
        elif symbol == 'USD':
            cash_usd += float(row['Market Value'])
        continue

    # Handle other non-equity securities
    if security_type not in ['EQUITY', 'EXCHANGE_TRADED_FUND']:
        continue

    # Normalize ticker (add CDR suffix if in CSV but not in symbol)
    ticker = symbol
    if row['Name'] and 'CDR' in row['Name'] and 'CDR' not in ticker:
        ticker = f"{symbol} CDR"

    # Store position data
    csv_positions[ticker] = {
        'shares': float(row['Quantity']),
        'current_price': float(row['Market Price']),
        'price_currency': row['Market Price Currency'],
        'book_cost_cad': float(row['Book Value (CAD)']) if row['Book Value (CAD)'] else 0,
        'book_cost_usd': float(row['Book Value (Market)']) if row['Book Value (Market)'] and row['Book Value Currency (Market)'] == 'USD' else 0,
        'market_value': float(row['Market Value']),
        'market_currency': row['Market Value Currency'],
        'unrealized_pnl': float(row['Market Unrealized Returns']),
        'pnl_currency': row['Market Unrealized Returns Currency']
    }

    # Track new equity positions not in approved list
    if ticker not in approved_tickers and ticker.replace(' CDR', '') not in approved_tickers:
        new_equity_positions.append(ticker)

# Update existing positions
updated_positions = []
total_market_value = 0

for pos in portfolio['positions']:
    ticker = pos['ticker']

    if ticker in csv_positions:
        # Update with current market data
        csv_pos = csv_positions[ticker]
        pos['current_price'] = csv_pos['current_price']
        pos['book_cost_cad'] = csv_pos['book_cost_cad']
        pos['book_cost_usd'] = csv_pos['book_cost_usd']
        total_market_value += csv_pos['market_value']
        updated_positions.append(pos)
    else:
        # Position not in CSV, keep existing
        print(f"Warning: {ticker} not found in CSV, keeping existing data")
        total_market_value += pos['shares'] * pos['current_price']
        updated_positions.append(pos)

# Add new equity positions from approved list that are in CSV
for ticker in csv_positions:
    if ticker not in [p['ticker'] for p in updated_positions]:
        # Check if it's in approved list
        base_ticker = ticker.replace(' CDR', '')
        if ticker in approved_tickers or base_ticker in approved_tickers:
            csv_pos = csv_positions[ticker]
            new_pos = {
                'ticker': ticker,
                'direction': 'long',
                'shares': csv_pos['shares'],
                'entry_price': csv_pos['current_price'],  # Using current as entry since we don't have historical
                'current_price': csv_pos['current_price'],
                'book_cost_cad': csv_pos['book_cost_cad'],
                'book_cost_usd': csv_pos['book_cost_usd'],
                'stop_loss': round(csv_pos['current_price'] * 0.9, 2),  # Default -10%
                'target': round(csv_pos['current_price'] * 1.2, 2),  # Default +20%
                'conviction': 3,
                'timeframe': 'swing',
                'entry_timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            updated_positions.append(new_pos)
            total_market_value += csv_pos['market_value']
            print(f"Added new position: {ticker}")

# Calculate total cash (CAD + USD converted to CAD roughly)
# Assuming 1 USD = 1.35 CAD for rough conversion
total_cash = cash_cad + (cash_usd * 1.35)

# Update portfolio
portfolio['positions'] = updated_positions
portfolio['portfolio_value'] = total_market_value + total_cash
portfolio['cash'] = total_cash

# Save updated portfolio
with open('.devin/portfolio_ledger.json', 'w') as f:
    json.dump(portfolio, f, indent=2)

print("\n" + "="*80)
print("PORTFOLIO UPDATE COMPLETE")
print("="*80)
print(f"Total Market Value: ${total_market_value:,.2f}")
print(f"Cash (CAD): ${cash_cad:,.2f}")
print(f"Cash (USD): ${cash_usd:,.2f}")
print(f"Total Cash: ${total_cash:,.2f}")
print(f"Total Portfolio Value: ${portfolio['portfolio_value']:,.2f}")
print(f"Number of Positions: {len(updated_positions)}")

if new_equity_positions:
    print(f"\nNew equity positions found (not in approved list):")
    for ticker in new_equity_positions:
        print(f"  - {ticker}")

print("\nUpdated positions with current market prices from CSV")
print("PII data (account name, type, number) excluded")
