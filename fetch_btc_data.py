#!/usr/bin/env python3
"""
Fetch Bitcoin historical price data using Yahoo Finance API
"""

import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json
from datetime import datetime

def fetch_btc_historical_data():
    """
    Fetch Bitcoin historical price data from Yahoo Finance
    """
    client = ApiClient()
    
    print("Fetching Bitcoin historical price data...")
    
    try:
        # Fetch BTC-USD data with maximum range
        response = client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': 'BTC-USD',
            'region': 'US',
            'interval': '1d',
            'range': '5y',  # Get 5 years of daily data
            'includeAdjustedClose': True
        })
        
        if response and 'chart' in response and 'result' in response['chart']:
            result = response['chart']['result'][0]
            meta = result['meta']
            
            print(f"Symbol: {meta['symbol']}")
            print(f"Currency: {meta['currency']}")
            print(f"Current Price: ${meta.get('regularMarketPrice', 'N/A')}")
            
            # Extract time series data
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            # Prepare data for export
            data_records = []
            for i in range(len(timestamps)):
                date = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
                open_price = quotes['open'][i] if quotes['open'][i] else None
                high_price = quotes['high'][i] if quotes['high'][i] else None
                low_price = quotes['low'][i] if quotes['low'][i] else None
                close_price = quotes['close'][i] if quotes['close'][i] else None
                volume = quotes['volume'][i] if quotes['volume'][i] else None
                
                data_records.append({
                    'date': date,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                })
            
            print(f"Total data points retrieved: {len(data_records)}")
            
            # Save to JSON file
            with open('/home/ubuntu/btc_historical_data.json', 'w') as f:
                json.dump(data_records, f, indent=2)
            
            print("Data saved to btc_historical_data.json")
            
            # Also save metadata
            metadata = {
                'symbol': meta['symbol'],
                'currency': meta['currency'],
                'exchange': meta.get('exchangeName', 'N/A'),
                'data_points': len(data_records),
                'first_date': data_records[0]['date'] if data_records else None,
                'last_date': data_records[-1]['date'] if data_records else None,
                'current_price': meta.get('regularMarketPrice', None)
            }
            
            with open('/home/ubuntu/btc_metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Date range: {metadata['first_date']} to {metadata['last_date']}")
            
            return True
            
        else:
            print("No data found in the response")
            return False
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fetch_btc_historical_data()
    sys.exit(0 if success else 1)
