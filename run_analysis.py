#!/usr/bin/env python3
"""
Run BTC NAV Premium Analysis
"""

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import seaborn as sns

# Set style
plt.style.use('dark_background')
sns.set_palette("husl")

print("Loading data...")

# Load Bitcoin historical data
with open('btc_historical_data.json', 'r') as f:
    btc_data = json.load(f)

btc_df = pd.DataFrame(btc_data)
btc_df['date'] = pd.to_datetime(btc_df['date'])
btc_df = btc_df.sort_values('date')

print(f"Bitcoin data: {len(btc_df)} records from {btc_df['date'].min()} to {btc_df['date'].max()}")

# Load MicroStrategy stock data
with open('mstr_historical_data.json', 'r') as f:
    mstr_data = json.load(f)

mstr_df = pd.DataFrame(mstr_data)
mstr_df['date'] = pd.to_datetime(mstr_df['date'])
mstr_df = mstr_df.sort_values('date')

print(f"MSTR data: {len(mstr_df)} records from {mstr_df['date'].min()} to {mstr_df['date'].max()}")

# Load MicroStrategy Bitcoin holdings
with open('mstr_btc_holdings.json', 'r') as f:
    holdings_data = json.load(f)

holdings_df = pd.DataFrame(holdings_data)
holdings_df['date'] = pd.to_datetime(holdings_df['date'])
holdings_df = holdings_df.sort_values('date')

print(f"MSTR BTC Holdings: {len(holdings_df)} purchase events from {holdings_df['date'].min()} to {holdings_df['date'].max()}")
print(f"Current holdings: {holdings_df['cumulative_btc_holdings'].iloc[-1]:,} BTC")

print("\nMerging datasets...")

# Merge datasets
merged_df = pd.merge(btc_df[['date', 'close']], 
                     mstr_df[['date', 'close']], 
                     on='date', 
                     how='inner',
                     suffixes=('_btc', '_mstr'))

# Forward fill BTC holdings
all_dates = pd.DataFrame({'date': merged_df['date'].unique()})
holdings_filled = pd.merge(all_dates, holdings_df[['date', 'cumulative_btc_holdings']], 
                          on='date', how='left')
holdings_filled['cumulative_btc_holdings'] = holdings_filled['cumulative_btc_holdings'].ffill()

# Merge with holdings
merged_df = pd.merge(merged_df, holdings_filled, on='date', how='left')

# Filter to dates where MSTR held Bitcoin
merged_df = merged_df[merged_df['cumulative_btc_holdings'].notna()]

print(f"Merged data: {len(merged_df)} records")

print("\nCalculating NAV Premium...")

# Calculate NAV Premium
def estimate_shares_outstanding(date):
    """Estimate shares outstanding based on date"""
    if date < pd.Timestamp('2020-08-01'):
        return 160_000_000
    elif date < pd.Timestamp('2021-01-01'):
        return 165_000_000
    elif date < pd.Timestamp('2022-01-01'):
        return 170_000_000
    elif date < pd.Timestamp('2023-01-01'):
        return 180_000_000
    elif date < pd.Timestamp('2024-01-01'):
        return 190_000_000
    elif date < pd.Timestamp('2024-11-01'):
        return 220_000_000
    elif date < pd.Timestamp('2025-01-01'):
        return 280_000_000
    else:
        return 320_000_000

merged_df['shares_outstanding'] = merged_df['date'].apply(estimate_shares_outstanding)
merged_df['market_cap_millions'] = (merged_df['close_mstr'] * merged_df['shares_outstanding']) / 1_000_000
merged_df['btc_nav_millions'] = (merged_df['close_btc'] * merged_df['cumulative_btc_holdings']) / 1_000_000
merged_df['nav_premium'] = merged_df['market_cap_millions'] / merged_df['btc_nav_millions']

print(f"NAV Premium statistics:")
print(merged_df['nav_premium'].describe())

# Filter data to the relevant range
chart_df = merged_df[(merged_df['close_btc'] >= 50000) & (merged_df['close_btc'] <= 150000)].copy()

# Add color mapping based on date
chart_df['days_since_start'] = (chart_df['date'] - chart_df['date'].min()).dt.days.astype(float)
chart_df['color_value'] = chart_df['days_since_start'] / chart_df['days_since_start'].max()

print(f"\nChart data: {len(chart_df)} records")
print(f"Date range: {chart_df['date'].min()} to {chart_df['date'].max()}")
print(f"BTC price range: ${chart_df['close_btc'].min():,.0f} to ${chart_df['close_btc'].max():,.0f}")
print(f"NAV Premium range: {chart_df['nav_premium'].min():.2f}x to {chart_df['nav_premium'].max():.2f}x")

print("\nCreating main visualization...")

# Create the visualization
fig, ax = plt.subplots(figsize=(16, 10))

# Create scatter plot with color gradient based on time
scatter = ax.scatter(chart_df['close_btc'], 
                    chart_df['nav_premium'],
                    c=chart_df['color_value'],
                    cmap='rainbow',
                    s=50,
                    alpha=0.7,
                    edgecolors='none')

# Add trend lines
x_trend = np.array([60000, 140000])
y_upper = np.array([2.0, 2.3])
ax.plot(x_trend, y_upper, 'g-', linewidth=2, alpha=0.7, label='Upper Trend')

y_lower = np.array([2.0, 1.0])
ax.plot(x_trend, y_lower, color='orange', linewidth=2, alpha=0.7, label='Lower Trend')

# Reference line at 1.7x
ax.axhline(y=1.7, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Reference: 1.7x')

# Get current values
current_btc = chart_df['close_btc'].iloc[-1]
current_nav = chart_df['nav_premium'].iloc[-1]
current_mstr = chart_df['close_mstr'].iloc[-1]

# Add annotation
annotation_text = f"BTC: ${current_btc:,.2f}\nNAV Prem: {current_nav:.2f}x\nEst. MSTR Price: ${current_mstr:.0f}"
ax.annotate(annotation_text, 
           xy=(current_btc, current_nav),
           xytext=(65000, 1.8),
           bbox=dict(boxstyle='round,pad=0.5', facecolor='black', edgecolor='white', alpha=0.8),
           fontsize=12,
           color='white',
           weight='bold',
           arrowprops=dict(arrowstyle='->', color='white', lw=2))

# Add watermark
ax.text(0.95, 0.05, 'strategy.bit',
       transform=ax.transAxes,
       fontsize=60,
       color='gray',
       alpha=0.2,
       ha='right',
       va='bottom',
       weight='bold',
       rotation=0)

# Formatting
ax.set_xlabel('BTC Price ($)', fontsize=14, weight='bold')
ax.set_ylabel('NAV Premium (x)', fontsize=14, weight='bold')
ax.set_title('MicroStrategy Bitcoin NAV Premium vs BTC Price', fontsize=18, weight='bold', pad=20)

# Format x-axis
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}k'))
ax.set_xlim(55000, 145000)
ax.set_ylim(0.5, 2.8)

# Grid
ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
ax.set_facecolor('#1a1a1a')
fig.patch.set_facecolor('#0a0a0a')

# Legend
ax.legend(loc='upper right', fontsize=10, framealpha=0.8)

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax, pad=0.02)
cbar.set_label('Time Progression (Blue=Earlier, Red=Recent)', fontsize=10)

plt.tight_layout()
plt.savefig('btc_nav_premium_chart.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Chart saved as 'btc_nav_premium_chart.png'")
plt.close()

print("\nCreating timeline visualization...")

# Timeline chart
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)

# Plot 1: BTC Price over time
ax1.plot(chart_df['date'], chart_df['close_btc'], color='orange', linewidth=2)
ax1.set_ylabel('BTC Price ($)', fontsize=12, weight='bold')
ax1.set_title('Bitcoin Price and NAV Premium Over Time', fontsize=16, weight='bold', pad=20)
ax1.grid(True, alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}k'))
ax1.set_facecolor('#1a1a1a')

# Plot 2: NAV Premium over time
ax2.plot(chart_df['date'], chart_df['nav_premium'], color='cyan', linewidth=2)
ax2.axhline(y=1.0, color='white', linestyle='--', linewidth=1, alpha=0.5, label='1.0x (Fair Value)')
ax2.axhline(y=1.7, color='red', linestyle='--', linewidth=1, alpha=0.7, label='1.7x Reference')
ax2.set_xlabel('Date', fontsize=12, weight='bold')
ax2.set_ylabel('NAV Premium (x)', fontsize=12, weight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper right', fontsize=10)
ax2.set_facecolor('#1a1a1a')

# Format x-axis
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xticks(rotation=45)

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
plt.savefig('btc_nav_premium_timeline.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Timeline chart saved as 'btc_nav_premium_timeline.png'")
plt.close()

# Summary statistics
print("\n=== Summary Statistics ===")
print(f"\nCurrent Metrics (as of {chart_df['date'].iloc[-1].strftime('%Y-%m-%d')}):")
print(f"  BTC Price: ${current_btc:,.2f}")
print(f"  MSTR Price: ${current_mstr:,.2f}")
print(f"  NAV Premium: {current_nav:.2f}x")
print(f"  BTC Holdings: {chart_df['cumulative_btc_holdings'].iloc[-1]:,.0f} BTC")
print(f"  BTC NAV: ${chart_df['btc_nav_millions'].iloc[-1]:,.0f}M")
print(f"  Market Cap: ${chart_df['market_cap_millions'].iloc[-1]:,.0f}M")

print(f"\nHistorical NAV Premium (BTC Price Range $50k-$150k):")
print(f"  Mean: {chart_df['nav_premium'].mean():.2f}x")
print(f"  Median: {chart_df['nav_premium'].median():.2f}x")
print(f"  Min: {chart_df['nav_premium'].min():.2f}x")
print(f"  Max: {chart_df['nav_premium'].max():.2f}x")
print(f"  Std Dev: {chart_df['nav_premium'].std():.2f}x")

print("\n=== Analysis Complete ===")
