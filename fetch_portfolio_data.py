#!/usr/bin/env python3
"""
Portfolio Data Fetcher
Fetches real-time data for portfolio holdings and recommended stocks
"""

import json
import requests
from datetime import datetime, timedelta
import time

# Configuration - Add your API keys here
API_KEYS = {
    'alpha_vantage': '',  # Get from https://www.alphavantage.co/support/#api-key
    'news_api': '',       # Get from https://newsapi.org/
    'yahoo_finance': ''   # Consider using yfinance library (free)
}

# Portfolio tickers and recommended tickers
PORTFOLIO_TICKERS = [
    'AMCI', 'AVGO', 'AXTI', 'CRWV', 'MDA.TO', 'META', 'MRVL', 
    'MU', 'NVTS', 'QSI', 'SNDK', 'SPCX', 'WDC', 'GOLD', 'PLTO', 'SVR'
]

RECOMMENDED_TICKERS = [
    'VOO', 'ENB.TO', 'L.TO', 'SHOP.TO', 'JNJ', 'FPL.TO', 'H.TO', 
    'MRU.TO', 'ATD.TO', 'PFE', 'UNH', 'GIB.A.TO', 'VTI', 'XIC.TO'
]

class PortfolioDataFetcher:
    def __init__(self):
        self.data = {}
        
    def fetch_stock_price(self, ticker):
        """Fetch current stock price using Alpha Vantage or Yahoo Finance"""
        if API_KEYS['alpha_vantage']:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker,
                'apikey': API_KEYS['alpha_vantage']
            }
            try:
                response = requests.get(url, params=params)
                data = response.json()
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    return {
                        'price': float(quote['05. price']),
                        'change': float(quote['09. change']),
                        'change_percent': quote['10. change percent'].replace('%', ''),
                        'volume': int(quote['06. volume']),
                        'high': float(quote['03. high']),
                        'low': float(quote['04. low']),
                        'open': float(quote['02. open']),
                        'previous_close': float(quote['08. previous close'])
                    }
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")
        
        # Fallback to placeholder if no API key
        return {
            'price': 0.0,
            'change': 0.0,
            'change_percent': '0.00%',
            'volume': 0,
            'high': 0.0,
            'low': 0.0,
            'open': 0.0,
            'previous_close': 0.0
        }
    
    def fetch_technical_indicators(self, ticker):
        """Fetch technical indicators using Alpha Vantage"""
        if API_KEYS['alpha_vantage']:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'SMA',
                'symbol': ticker,
                'interval': 'daily',
                'time_period': '20',
                'series_type': 'close',
                'apikey': API_KEYS['alpha_vantage']
            }
            try:
                response = requests.get(url, params=params)
                data = response.json()
                # Parse SMA data
                if 'Technical Analysis: SMA' in data:
                    sma_data = data['Technical Analysis: SMA']
                    latest_date = list(sma_data.keys())[0]
                    return {
                        'sma_20': float(sma_data[latest_date]['SMA']),
                        'trend': 'Bullish' if 'Bullish' in str(sma_data) else 'Bearish'
                    }
            except Exception as e:
                print(f"Error fetching indicators for {ticker}: {e}")
        
        return {
            'sma_20': 0.0,
            'trend': 'Neutral'
        }
    
    def fetch_news(self, ticker):
        """Fetch news for a specific ticker"""
        if API_KEYS['news_api']:
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': ticker,
                'apiKey': API_KEYS['news_api'],
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 5
            }
            try:
                response = requests.get(url, params=params)
                data = response.json()
                if data.get('status') == 'ok':
                    articles = []
                    for article in data['articles'][:5]:
                        articles.append({
                            'title': article['title'],
                            'description': article['description'],
                            'url': article['url'],
                            'publishedAt': article['publishedAt'],
                            'source': article['source']['name']
                        })
                    return articles
            except Exception as e:
                print(f"Error fetching news for {ticker}: {e}")
        
        return []
    
    def fetch_market_news(self):
        """Fetch general market news"""
        if API_KEYS['news_api']:
            url = f"https://newsapi.org/v2/top-headlines"
            params = {
                'category': 'business',
                'apiKey': API_KEYS['news_api'],
                'language': 'en',
                'pageSize': 10
            }
            try:
                response = requests.get(url, params=params)
                data = response.json()
                if data.get('status') == 'ok':
                    articles = []
                    for article in data['articles'][:10]:
                        articles.append({
                            'title': article['title'],
                            'description': article['description'],
                            'url': article['url'],
                            'publishedAt': article['publishedAt'],
                            'source': article['source']['name']
                        })
                    return articles
            except Exception as e:
                print(f"Error fetching market news: {e}")
        
        return []
    
    def fetch_all_data(self):
        """Fetch data for all tickers"""
        print("Fetching portfolio data...")
        
        all_tickers = list(set(PORTFOLIO_TICKERS + RECOMMENDED_TICKERS))
        
        for ticker in all_tickers:
            print(f"Fetching data for {ticker}...")
            
            self.data[ticker] = {
                'price_data': self.fetch_stock_price(ticker),
                'technical': self.fetch_technical_indicators(ticker),
                'news': self.fetch_news(ticker),
                'last_updated': datetime.now().isoformat()
            }
            
            # Rate limiting to avoid API limits
            time.sleep(1)
        
        # Fetch general market news
        print("Fetching market news...")
        self.data['market_news'] = self.fetch_market_news()
        
        return self.data
    
    def save_to_json(self, filename='portfolio_data.json'):
        """Save fetched data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"Data saved to {filename}")
    
    def generate_market_analysis(self):
        """Generate market analysis based on fetched data"""
        analysis = {
            'market_sentiment': 'Neutral',
            'key_trends': [],
            'recommendations': []
        }
        
        # Analyze portfolio tickers
        bullish_count = 0
        bearish_count = 0
        
        for ticker in PORTFOLIO_TICKERS:
            if ticker in self.data:
                change_percent = self.data[ticker]['price_data'].get('change_percent', '0%')
                if float(change_percent.replace('%', '')) > 0:
                    bullish_count += 1
                elif float(change_percent.replace('%', '')) < 0:
                    bearish_count += 1
        
        if bullish_count > bearish_count:
            analysis['market_sentiment'] = 'Bullish'
        elif bearish_count > bullish_count:
            analysis['market_sentiment'] = 'Bearish'
        
        analysis['key_trends'] = [
            f"Bullish stocks: {bullish_count}",
            f"Bearish stocks: {bearish_count}",
            f"Total analyzed: {len(PORTFOLIO_TICKERS)}"
        ]
        
        return analysis

def main():
    """Main function to fetch and display portfolio data"""
    fetcher = PortfolioDataFetcher()
    
    # Check if API keys are configured
    if not any(API_KEYS.values()):
        print("⚠️  WARNING: No API keys configured.")
        print("Please add your API keys to the API_KEYS dictionary:")
        print("  - Alpha Vantage: https://www.alphavantage.co/support/#api-key")
        print("  - News API: https://newsapi.org/")
        print("\nWithout API keys, only placeholder data will be returned.")
        print("\nTo use with yfinance (free, no API key needed),")
        print("install it with: pip install yfinance")
        print("\nProceeding with placeholder data...")
    
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
    
    print("\nSample Data for META:")
    if 'META' in data:
        print(f"  Price: ${data['META']['price_data']['price']:.2f}")
        print(f"  Change: {data['META']['price_data']['change_percent']}")
        print(f"  SMA 20: ${data['META']['technical']['sma_20']:.2f}")
        print(f"  Trend: {data['META']['technical']['trend']}")
        print(f"  News Articles: {len(data['META']['news'])}")
    
    print("\n✅ Data fetching complete!")
    print("Update portfolio_ledger.json with new prices using update_portfolio.py")

if __name__ == "__main__":
    main()
