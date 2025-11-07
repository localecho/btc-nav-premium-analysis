#!/usr/bin/env python3
"""
Market Regime Analysis and NAV Premium Correlation
Identifies bull/bear markets and analyzes NAV Premium behavior
"""

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import seaborn as sns
from scipy import stats

# Set style
plt.style.use('dark_background')
sns.set_palette("husl")

print("Loading data...")

# Load all data
with open('btc_historical_data.json', 'r') as f:
    btc_data = json.load(f)
with open('mstr_historical_data.json', 'r') as f:
    mstr_data = json.load(f)
with open('mstr_btc_holdings.json', 'r') as f:
    holdings_data = json.load(f)

# Create dataframes
btc_df = pd.DataFrame(btc_data)
btc_df['date'] = pd.to_datetime(btc_df['date'])
btc_df = btc_df.sort_values('date')

mstr_df = pd.DataFrame(mstr_data)
mstr_df['date'] = pd.to_datetime(mstr_df['date'])
mstr_df = mstr_df.sort_values('date')

holdings_df = pd.DataFrame(holdings_data)
holdings_df['date'] = pd.to_datetime(holdings_df['date'])
holdings_df = holdings_df.sort_values('date')

# Merge datasets
merged_df = pd.merge(btc_df[['date', 'close']], 
                     mstr_df[['date', 'close']], 
                     on='date', 
                     how='inner',
                     suffixes=('_btc', '_mstr'))

all_dates = pd.DataFrame({'date': merged_df['date'].unique()})
holdings_filled = pd.merge(all_dates, holdings_df[['date', 'cumulative_btc_holdings']], 
                          on='date', how='left')
holdings_filled['cumulative_btc_holdings'] = holdings_filled['cumulative_btc_holdings'].ffill()

merged_df = pd.merge(merged_df, holdings_filled, on='date', how='left')
merged_df = merged_df[merged_df['cumulative_btc_holdings'].notna()]

# Calculate NAV Premium
def estimate_shares_outstanding(date):
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

print(f"Total records: {len(merged_df)}")

# ============================================================================
# REGIME IDENTIFICATION
# ============================================================================

print("\n" + "="*80)
print("IDENTIFYING MARKET REGIMES")
print("="*80)

# Calculate moving averages for regime identification
merged_df['btc_ma_50'] = merged_df['close_btc'].rolling(window=50, min_periods=1).mean()
merged_df['btc_ma_200'] = merged_df['close_btc'].rolling(window=200, min_periods=1).mean()

# Method 1: Moving Average Crossover (50-day vs 200-day)
# Bull: 50-day MA > 200-day MA
# Bear: 50-day MA < 200-day MA
merged_df['regime_ma'] = np.where(merged_df['btc_ma_50'] > merged_df['btc_ma_200'], 'Bull', 'Bear')

# Method 2: Price momentum (30-day return)
merged_df['btc_return_30d'] = merged_df['close_btc'].pct_change(30)
merged_df['regime_momentum'] = np.where(merged_df['btc_return_30d'] > 0, 'Bull', 'Bear')

# Method 3: Distance from all-time high
merged_df['btc_ath'] = merged_df['close_btc'].expanding().max()
merged_df['drawdown'] = (merged_df['close_btc'] - merged_df['btc_ath']) / merged_df['btc_ath']
# Bull: within 20% of ATH, Bear: more than 20% below ATH
merged_df['regime_ath'] = np.where(merged_df['drawdown'] > -0.20, 'Bull', 'Bear')

# Combined regime (majority vote)
merged_df['regime_combined'] = merged_df.apply(
    lambda row: 'Bull' if [row['regime_ma'], row['regime_momentum'], row['regime_ath']].count('Bull') >= 2 else 'Bear',
    axis=1
)

# Print regime statistics
print("\nRegime Distribution (Combined Method):")
regime_counts = merged_df['regime_combined'].value_counts()
print(regime_counts)
print(f"\nBull Market Days: {regime_counts.get('Bull', 0)} ({regime_counts.get('Bull', 0)/len(merged_df)*100:.1f}%)")
print(f"Bear Market Days: {regime_counts.get('Bear', 0)} ({regime_counts.get('Bear', 0)/len(merged_df)*100:.1f}%)")

# ============================================================================
# NAV PREMIUM DERIVATIVE (TREND)
# ============================================================================

print("\n" + "="*80)
print("CALCULATING NAV PREMIUM DERIVATIVES")
print("="*80)

# Calculate derivatives (rate of change)
merged_df['nav_premium_derivative'] = merged_df['nav_premium'].diff()
merged_df['nav_premium_derivative_pct'] = merged_df['nav_premium'].pct_change()

# Smooth derivative using rolling mean
merged_df['nav_premium_derivative_smooth'] = merged_df['nav_premium_derivative'].rolling(window=7, min_periods=1).mean()

print(f"\nNAV Premium Derivative Statistics:")
print(merged_df['nav_premium_derivative'].describe())

# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("CORRELATION ANALYSIS: NAV PREMIUM TREND vs MARKET REGIME")
print("="*80)

# Filter out NaN values
analysis_df = merged_df[['date', 'close_btc', 'nav_premium', 'nav_premium_derivative', 
                          'nav_premium_derivative_smooth', 'regime_combined']].dropna()

# Encode regime as numeric (Bull=1, Bear=0)
analysis_df['regime_numeric'] = (analysis_df['regime_combined'] == 'Bull').astype(int)

# Calculate correlations
corr_derivative_regime = analysis_df['nav_premium_derivative'].corr(analysis_df['regime_numeric'])
corr_derivative_smooth_regime = analysis_df['nav_premium_derivative_smooth'].corr(analysis_df['regime_numeric'])

print(f"\nCorrelation between NAV Premium Derivative and Regime:")
print(f"  Raw Derivative: {corr_derivative_regime:.4f}")
print(f"  Smoothed Derivative (7-day): {corr_derivative_smooth_regime:.4f}")

# Statistics by regime
print("\n" + "-"*80)
print("NAV Premium Statistics by Market Regime:")
print("-"*80)

for regime in ['Bull', 'Bear']:
    regime_data = analysis_df[analysis_df['regime_combined'] == regime]
    print(f"\n{regime} Market:")
    print(f"  Average NAV Premium: {regime_data['nav_premium'].mean():.3f}x")
    print(f"  Median NAV Premium: {regime_data['nav_premium'].median():.3f}x")
    print(f"  Std Dev NAV Premium: {regime_data['nav_premium'].std():.3f}x")
    print(f"  Average Derivative: {regime_data['nav_premium_derivative'].mean():.6f}")
    print(f"  Median Derivative: {regime_data['nav_premium_derivative'].median():.6f}")
    print(f"  Days: {len(regime_data)}")

# Statistical test (t-test)
bull_derivatives = analysis_df[analysis_df['regime_combined'] == 'Bull']['nav_premium_derivative'].dropna()
bear_derivatives = analysis_df[analysis_df['regime_combined'] == 'Bear']['nav_premium_derivative'].dropna()

t_stat, p_value = stats.ttest_ind(bull_derivatives, bear_derivatives)
print(f"\n" + "-"*80)
print(f"T-test: NAV Premium Derivatives (Bull vs Bear)")
print(f"  t-statistic: {t_stat:.4f}")
print(f"  p-value: {p_value:.6f}")
print(f"  Significant difference: {'Yes' if p_value < 0.05 else 'No'} (α=0.05)")

# ============================================================================
# VISUALIZATION 1: Timeline with Regime Coloring
# ============================================================================

print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

fig, axes = plt.subplots(3, 1, figsize=(18, 14), sharex=True)

# Subplot 1: BTC Price with regime coloring
ax1 = axes[0]
for regime, color in [('Bull', 'green'), ('Bear', 'red')]:
    regime_data = analysis_df[analysis_df['regime_combined'] == regime]
    ax1.scatter(regime_data['date'], regime_data['close_btc'], 
               c=color, s=10, alpha=0.6, label=f'{regime} Market')

ax1.set_ylabel('BTC Price ($)', fontsize=12, weight='bold')
ax1.set_title('Market Regime Analysis: BTC Price, NAV Premium, and Derivatives', 
             fontsize=16, weight='bold', pad=20)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}k'))
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper left', fontsize=10)
ax1.set_facecolor('#1a1a1a')

# Subplot 2: NAV Premium with regime coloring
ax2 = axes[1]
for regime, color in [('Bull', 'green'), ('Bear', 'red')]:
    regime_data = analysis_df[analysis_df['regime_combined'] == regime]
    ax2.scatter(regime_data['date'], regime_data['nav_premium'], 
               c=color, s=10, alpha=0.6, label=f'{regime} Market')

ax2.axhline(y=1.0, color='white', linestyle='--', linewidth=1, alpha=0.5, label='Fair Value (1.0x)')
ax2.axhline(y=1.7, color='orange', linestyle='--', linewidth=1, alpha=0.7, label='Reference (1.7x)')
ax2.set_ylabel('NAV Premium (x)', fontsize=12, weight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper left', fontsize=10)
ax2.set_facecolor('#1a1a1a')

# Subplot 3: NAV Premium Derivative
ax3 = axes[2]
ax3.plot(analysis_df['date'], analysis_df['nav_premium_derivative_smooth'], 
        color='cyan', linewidth=1.5, label='NAV Premium Derivative (7-day smooth)')
ax3.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.5)

# Color background by regime
for regime, color, alpha in [('Bull', 'green', 0.1), ('Bear', 'red', 0.1)]:
    regime_data = analysis_df[analysis_df['regime_combined'] == regime]
    if len(regime_data) > 0:
        for i in range(len(regime_data) - 1):
            ax3.axvspan(regime_data.iloc[i]['date'], regime_data.iloc[i+1]['date'], 
                       color=color, alpha=alpha)

ax3.set_xlabel('Date', fontsize=12, weight='bold')
ax3.set_ylabel('NAV Premium Derivative', fontsize=12, weight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend(loc='upper left', fontsize=10)
ax3.set_facecolor('#1a1a1a')

# Format x-axis
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xticks(rotation=45)

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
plt.savefig('regime_analysis_timeline.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Saved: regime_analysis_timeline.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: Distribution Comparison
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# NAV Premium distribution by regime
ax1 = axes[0, 0]
bull_nav = analysis_df[analysis_df['regime_combined'] == 'Bull']['nav_premium']
bear_nav = analysis_df[analysis_df['regime_combined'] == 'Bear']['nav_premium']

ax1.hist(bull_nav, bins=50, alpha=0.6, color='green', label='Bull Market', density=True)
ax1.hist(bear_nav, bins=50, alpha=0.6, color='red', label='Bear Market', density=True)
ax1.set_xlabel('NAV Premium (x)', fontsize=11, weight='bold')
ax1.set_ylabel('Density', fontsize=11, weight='bold')
ax1.set_title('NAV Premium Distribution by Regime', fontsize=13, weight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_facecolor('#1a1a1a')

# Derivative distribution by regime
ax2 = axes[0, 1]
ax2.hist(bull_derivatives, bins=50, alpha=0.6, color='green', label='Bull Market', density=True)
ax2.hist(bear_derivatives, bins=50, alpha=0.6, color='red', label='Bear Market', density=True)
ax2.set_xlabel('NAV Premium Derivative', fontsize=11, weight='bold')
ax2.set_ylabel('Density', fontsize=11, weight='bold')
ax2.set_title('NAV Premium Derivative Distribution by Regime', fontsize=13, weight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_facecolor('#1a1a1a')

# Box plot comparison
ax3 = axes[1, 0]
box_data = [bull_nav, bear_nav]
bp = ax3.boxplot(box_data, labels=['Bull Market', 'Bear Market'], patch_artist=True)
bp['boxes'][0].set_facecolor('green')
bp['boxes'][1].set_facecolor('red')
for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
    plt.setp(bp[element], color='white')
ax3.set_ylabel('NAV Premium (x)', fontsize=11, weight='bold')
ax3.set_title('NAV Premium Box Plot by Regime', fontsize=13, weight='bold')
ax3.grid(True, alpha=0.3, axis='y')
ax3.set_facecolor('#1a1a1a')

# Scatter: Derivative vs BTC Price colored by regime
ax4 = axes[1, 1]
for regime, color in [('Bull', 'green'), ('Bear', 'red')]:
    regime_data = analysis_df[analysis_df['regime_combined'] == regime]
    ax4.scatter(regime_data['close_btc'], regime_data['nav_premium_derivative_smooth'],
               c=color, s=20, alpha=0.5, label=f'{regime} Market')
ax4.axhline(y=0, color='white', linestyle='--', linewidth=1, alpha=0.5)
ax4.set_xlabel('BTC Price ($)', fontsize=11, weight='bold')
ax4.set_ylabel('NAV Premium Derivative (smoothed)', fontsize=11, weight='bold')
ax4.set_title('Derivative vs BTC Price by Regime', fontsize=13, weight='bold')
ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}k'))
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.set_facecolor('#1a1a1a')

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
plt.savefig('regime_analysis_distributions.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Saved: regime_analysis_distributions.png")
plt.close()

# ============================================================================
# SAVE RESULTS
# ============================================================================

# Save analysis results
results = {
    'correlation': {
        'nav_derivative_vs_regime_raw': float(corr_derivative_regime),
        'nav_derivative_vs_regime_smooth': float(corr_derivative_smooth_regime)
    },
    'regime_statistics': {
        'bull_market': {
            'days': int(regime_counts.get('Bull', 0)),
            'percentage': float(regime_counts.get('Bull', 0)/len(merged_df)*100),
            'avg_nav_premium': float(analysis_df[analysis_df['regime_combined'] == 'Bull']['nav_premium'].mean()),
            'median_nav_premium': float(analysis_df[analysis_df['regime_combined'] == 'Bull']['nav_premium'].median()),
            'avg_derivative': float(bull_derivatives.mean()),
            'median_derivative': float(bull_derivatives.median())
        },
        'bear_market': {
            'days': int(regime_counts.get('Bear', 0)),
            'percentage': float(regime_counts.get('Bear', 0)/len(merged_df)*100),
            'avg_nav_premium': float(analysis_df[analysis_df['regime_combined'] == 'Bear']['nav_premium'].mean()),
            'median_nav_premium': float(analysis_df[analysis_df['regime_combined'] == 'Bear']['nav_premium'].median()),
            'avg_derivative': float(bear_derivatives.mean()),
            'median_derivative': float(bear_derivatives.median())
        }
    },
    'statistical_test': {
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'significant': bool(p_value < 0.05)
    }
}

with open('regime_analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nSaved: regime_analysis_results.json")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
