import requests
import json
from datetime import datetime
import os

def fetch_live_rates():
    """
    Fetches live 24K gold & silver rates in INR from multiple sources.
    Auto-fallback if one fails. Returns per-gram rates.
    """
    rates = {'gold_24k_per_g': 0, 'silver_per_g': 0, 'source': '', 'usd_inr': 85.5}

    # Try 1: metals.dev free API - direct INR per gram
    try:
        url = "https://api.metals.dev/v1/latest?api_key=demo&currency=INR&unit=g"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            data = r.json()
            rates['gold_24k_per_g'] = data['metals']['gold']
            rates['silver_per_g'] = data['metals']['silver']
            rates['source'] = "Live API - metals.dev"
            return rates
    except:
        pass

    # Try 2: International spot + USDINR conversion
    try:
        fx = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5).json()
        rates['usd_inr'] = fx['rates']['INR']
        spot = requests.get("https://api.metals.live/v1/spot", timeout=5).json()
        gold_usd_oz = next(i['price'] for i in spot if i['metal'] == 'gold')
        silver_usd_oz = next(i['price'] for i in spot if i['metal'] == 'silver')
        rates['gold_24k_per_g'] = gold_usd_oz * rates['usd_inr'] / 31.1035
        rates['silver_per_g'] = silver_usd_oz * rates['usd_inr'] / 31.1035
        rates['source'] = "Live Spot USD + FX"
        return rates
    except:
        pass

    # Try 3: Fallback to hardcoded rates from 3rd July 2026
    rates['gold_24k_per_g'] = 14379.0
    rates['silver_per_g'] = 233.0
    rates['source'] = "Fallback - 3 July 2026 market data"
    return rates

def display_prices():
    data = fetch_live_rates()
    g24_1g = data['gold_24k_per_g']
    g22_1g = g24_1g * 0.916
    s_1g = data['silver_per_g']

    output = {
        'timestamp': datetime.now().strftime('%d %B %Y, %I:%M %p IST'),
        'source': data['source'],
        'usd_inr': round(data['usd_inr'], 2),
        '24k_gold_1g': round(g24_1g, 2),
        '24k_gold_10g': round(g24_1g * 10, 2),
        '22k_gold_1g': round(g22_1g, 2),
        '22k_gold_10g': round(g22_1g * 10, 2),
        'silver_1g': round(s_1g, 2),
        'silver_1kg': round(s_1g * 1000, 2)
    }

    # Print for logs
    print(f"""
{'='*55}
  Realtime Gold & Silver Price - India
  {output['timestamp']}
  Source: {output['source']}
{'='*55}
  24K Gold 10g : ₹{output['24k_gold_10g']:>10,.2f}
  22K Gold 10g : ₹{output['22k_gold_10g']:>10,.2f}
  Silver 1kg : ₹{output['silver_1kg']:>10,.2f}
{'='*55}
""")

    # Save to JSON for GitHub Actions
    with open('latest_rates.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    return output

if __name__ == "__main__":
    display_prices()
