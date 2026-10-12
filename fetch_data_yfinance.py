#!/usr/bin/env python3
"""
Portfolio Data Fetcher using yfinance (Free, no API key required)
Fetches real-time data for portfolio holdings and recommended stocks
"""

import json
import yfinance as yf
from datetime import datetime, timedelta
import time

# Portfolio tickers and recommended tickers
PORTFOLIO_TICKERS = [
    'AMCI', 'AVGO', 'AXTI', 'CRWV', 'MDA.TO', 'META', 'MRVL', 
    'MU', 'NVTS', 'QSI', 'SNDK', 'SPCX', 'WDC', 'GOLD', 'PLTO', 'SVR'
]

RECOMMENDED_TICKERS = [
    'VOO', 'ENB', 'L', 'SHOP', 'JNJ', 'FPL', 'H', 
    'MRU', 'ATD', 'PFE', 'UNH', 'GIB.A', 'VTI', 'XIC'
]

# Map CDR tickers to regular tickers for yfinance
CDR_MAPPING = {
    'AVGO': 'AVGO',
    'CRWV': 'CRWV',
    'META': 'META',
    'MU': 'MU',
    'SNDK': 'SNDK',
    'SPCX': 'SPCX',
    'WDC': 'WDC'
}

class PortfolioDataFetcher:
    def __init__(self):
        self.data = {}
        
    def fetch_stock_data(self, ticker):
        """Fetch comprehensive stock data using yfinance"""
        try:
            # Map CDR ticker to regular ticker if needed
            lookup_ticker = CDR_MAPPING.get(ticker, ticker)
            
            # Try with .TO suffix for Canadian stocks
            if not ticker.endswith('.TO') and ticker in ['ENB', 'L', 'H', 'MRU', 'ATD', 'SHOP', 'FPL', 'DOO', 'BN']:
                lookup_ticker = f"{lookup_ticker}.TO"
            
            stock = yf.Ticker(lookup_ticker)
            info = stock.info
            
            # Get recent price history
            hist = stock.history(period="5d")
            if not hist.empty:
                latest = hist.iloc[-1]
                previous = hist.iloc[-2] if len(hist) > 1 else latest
            else:
                latest = previous = None
            
            return {
                'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('volume', 0),
                'high': info.get('dayHigh', 0),
                'low': info.get('dayLow', 0),
                'open': info.get('regularMarketOpen', 0),
                'previous_close': info.get('previousClose', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'beta': info.get('beta', 0),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'recommendation': info.get('recommendationKey', 'N/A'),
                'target_price': info.get('targetMeanPrice', 0)
            }
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return {
                'price': 0.0,
                'change': 0.0,
                'change_percent': 0.0,
                'volume': 0,
                'high': 0.0,
                'low': 0.0,
                'open': 0.0,
                'previous_close': 0.0,
                'market_cap': 0,
                'pe_ratio': 0,
                'dividend_yield': 0,
                '52_week_high': 0,
                '52_week_low': 0,
                'beta': 0,
                'sector': 'N/A',
                'industry': 'N/A',
                'recommendation': 'N/A',
                'target_price': 0
            }
    
    def fetch_technical_indicators(self, ticker):
        """Fetch technical indicators using yfinance"""
        try:
            lookup_ticker = CDR_MAPPING.get(ticker, ticker)
            if not ticker.endswith('.TO') and ticker in ['ENB', 'L', 'H', 'MRU', 'ATD', 'SHOP', 'FPL', 'DOO', 'BN']:
                lookup_ticker = f"{lookup_ticker}.TO"
            
            stock = yf.Ticker(lookup_ticker)
            hist = stock.history(period="3mo")
            
            if len(hist) < 20:
                return {
                    'sma_20': 0,
                    'sma_50': 0,
                    'rsi': 50,
                    'trend': 'Neutral',
                    'above_sma_20': False
                }
            
            # Calculate SMA
            sma_20 = hist['Close'].tail(20).mean()
            sma_50 = hist['Close'].tail(50).mean() if len(hist) >= 50 else 0
            current_price = hist['Close'].iloc[-1]
            
            # Simple RSI calculation
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50
            
            # Determine trend
            if current_price > sma_20:
                trend = 'Bullish'
            elif current_price < sma_20:
                trend = 'Bearish'
            else:
                trend = 'Neutral'
            
            return {
                'sma_20': sma_20,
                'sma_50': sma_50,
                'rsi': current_rsi,
                'trend': trend,
                'above_sma_20': current_price > sma_20
            }
        except Exception as e:
            print(f"Error fetching indicators for {ticker}: {e}")
            return {
                'sma_20': 0,
                'sma_50': 0,
                'rsi': 50,
                'trend': 'Neutral',
                'above_sma_20': False
            }
    
    def fetch_all_data(self):
        """Fetch data for all tickers"""
        print("Fetching portfolio data using yfinance...")
        print("This may take a moment as we rate-limit requests...\n")
        
        all_tickers = list(set(PORTFOLIO_TICKERS + RECOMMENDED_TICKERS))
        
        for i, ticker in enumerate(all_tickers, 1):
            print(f"[{i}/{len(all_tickers)}] Fetching data for {ticker}...")
            
            self.data[ticker] = {
                'price_data': self.fetch_stock_data(ticker),
                'technical': self.fetch_technical_indicators(ticker),
                'last_updated': datetime.now().isoformat()
            }
            
            # Rate limiting
            time.sleep(0.5)
        
        return self.data
    
    def save_to_json(self, filename='portfolio_data.json'):
        """Save fetched data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"\n✅ Data saved to {filename}")
    
    def generate_market_analysis(self):
        """Generate market analysis based on fetched data"""
        analysis = {
            'market_sentiment': 'Neutral',
            'key_trends': [],
            'recommendations': [],
            'sector_analysis': {}
        }
        
        # Analyze portfolio tickers
        bullish_count = 0
        bearish_count = 0
        total_volume = 0
        
        for ticker in PORTFOLIO_TICKERS:
            if ticker in self.data:
                change_percent = self.data[ticker]['price_data'].get('change_percent', 0)
                if change_percent > 0:
                    bullish_count += 1
                elif change_percent < 0:
                    bearish_count += 1
                
                total_volume += self.data[ticker]['price_data'].get('volume', 0)
                
                # Sector analysis
                sector = self.data[ticker]['price_data'].get('sector', 'N/A')
                if sector != 'N/A':
                    if sector not in analysis['sector_analysis']:
                        analysis['sector_analysis'][sector] = []
                    analysis['sector_analysis'][sector].append(ticker)
        
        if bullish_count > bearish_count:
            analysis['market_sentiment'] = 'Bullish'
        elif bearish_count > bullish_count:
            analysis['market_sentiment'] = 'Bearish'
        
        analysis['key_trends'] = [
            f"Bullish stocks: {bullish_count}",
            f"Bearish stocks: {bearish_count}",
            f"Total volume: {total_volume:,}",
            f"Sectors tracked: {len(analysis['sector_analysis'])}"
        ]
        
        # Generate recommendations based on technical analysis
        for ticker in RECOMMENDED_TICKERS:
            if ticker in self.data:
                technical = self.data[ticker]['technical']
                price_data = self.data[ticker]['price_data']
                
                if technical['trend'] == 'Bullish' and technical['rsi'] < 70:
                    analysis['recommendations'].append({
                        'ticker': ticker,
                        'action': 'BUY',
                        'reason': f"Bullish trend, RSI at {technical['rsi']:.1f} (not overbought)",
                        'price': price_data['price'],
                        'target': price_data['target_price']
                    })
                elif technical['trend'] == 'Bearish' and technical['rsi'] > 30:
                    analysis['recommendations'].append({
                        'ticker': ticker,
                        'action': 'HOLD',
                        'reason': f"Bearish trend, RSI at {technical['rsi']:.1f} (not oversold)",
                        'price': price_data['price'],
                        'target': price_data['target_price']
                    })
        
        return analysis

def main():
    """Main function to fetch and display portfolio data"""
    print("=" * 80)
    print("PORTFOLIO DATA FETCHER")
    print("=" * 80)
    print("Using yfinance (free, no API key required)\n")
    
    try:
        import yfinance as yf
        print("✅ yfinance is installed\n")
    except ImportError:
        print("❌ yfinance is not installed")
        print("Install it with: pip install yfinance")
        return
    
    fetcher = PortfolioDataFetcher()
    
    # Fetch all data
    data = fetcher.fetch_all_data()
    
    # Save to JSON
    fetcher.save_to_json()
    
    # Generate analysis
    analysis = fetcher.generate_market_analysis()
    
    print("\n" + "=" * 80)
    print("MARKET ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Market Sentiment: {analysis['market_sentiment']}")
    print("\nKey Trends:")
    for trend in analysis['key_trends']:
        print(f"  - {trend}")
    
    print("\nSector Analysis:")
    for sector, tickers in analysis['sector_analysis'].items():
        print(f"  {sector}: {', '.join(tickers)}")
    
    print("\nTop Recommendations:")
    for rec in analysis['recommendations'][:5]:
        print(f"  {rec['ticker']}: {rec['action']} - {rec['reason']}")
    
    print("\nSample Data for META:")
    if 'META' in data:
        print(f"  Price: ${data['META']['price_data']['price']:.2f}")
        print(f"  Change: {data['META']['price_data']['change_percent']:.2f}%")
        print(f"  SMA 20: ${data['META']['technical']['sma_20']:.2f}")
        print(f"  RSI: {data['META']['technical']['rsi']:.1f}")
        print(f"  Trend: {data['META']['technical']['trend']}")
        print(f"  Sector: {data['META']['price_data']['sector']}")
        print(f"  Recommendation: {data['META']['price_data']['recommendation']}")
    
    print("\n✅ Data fetching complete!")
    print("You can now use this data to update the portfolio dashboard.")

if __name__ == "__main__":
    main()
