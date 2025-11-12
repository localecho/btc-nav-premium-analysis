#!/usr/bin/env python3
"""
Enhanced Leveraged Position Visualization with BTC Price Overlay
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Set style
plt.style.use('dark_background')

# Position parameters
CAPITAL = 2_500_000
LEVERAGE = 1.26
POSITION_SIZE = CAPITAL * LEVERAGE
CURRENT_MSTR_PRICE = 237.20
CURRENT_BTC_PRICE = 101141.77
SHARES = POSITION_SIZE / CURRENT_MSTR_PRICE

# Scenarios with BTC prices
scenarios_data = [
    ('Today\nConservative', 343.32, 101141.77, 'Today'),
    ('Today\nFair Value', 377.77, 101141.77, 'Today'),
    ('Today\nBull Case', 432.49, 101141.77, 'Today'),
    ('Q1 2026\nBase', 361.00, 95000, 'Q1 2026'),
    ('Q2 2026\nBase', 401.17, 105000, 'Q2 2026'),
    ('Q3 2026\nBase', 442.10, 115000, 'Q3 2026'),
    ('Q4 2026\nBase', 483.79, 125000, 'Q4 2026'),
    ('Q4 2026\nBull', 652.55, 170000, 'Q4 2026'),
    ('Q4 2026\nMoon', 858.82, 225000, 'Q4 2026'),
]

# Calculate equity values
results = []
for name, mstr_price, btc_price, period in scenarios_data:
    position_value = SHARES * mstr_price
    borrowed = POSITION_SIZE - CAPITAL
    net_equity = position_value - borrowed
    net_profit = net_equity - CAPITAL
    leveraged_return = (net_profit / CAPITAL) * 100
    
    results.append({
        'name': name,
        'mstr_price': mstr_price,
        'btc_price': btc_price,
        'equity': net_equity,
        'profit': net_profit,
        'return': leveraged_return,
        'period': period
    })

# ============================================================================
# ENHANCED VISUALIZATION: Equity Growth with BTC Price Overlay
# ============================================================================

fig, ax1 = plt.subplots(figsize=(18, 11))

names = [r['name'] for r in results]
equities = [r['equity'] for r in results]
btc_prices = [r['btc_price'] for r in results]

# Color scheme
colors = ['#ff6b6b', '#ff8c69', '#ffa566', 
          '#4ecdc4', '#45b7d1', '#5390d9',
          '#48bfe3', '#72efdd', '#64dfdf']

# Plot equity bars
x_pos = np.arange(len(names))
bars = ax1.bar(x_pos, equities, color=colors, alpha=0.85, 
              edgecolor='white', linewidth=2, width=0.6)

# Add initial capital line
ax1.axhline(y=CAPITAL, color='red', linestyle='--', linewidth=2.5, 
          label=f'Initial Capital: ${CAPITAL/1e6:.1f}M', alpha=0.9, zorder=5)

# Add equity value labels
for i, (bar, result) in enumerate(zip(bars, results)):
    height = bar.get_height()
    profit = result['profit']
    return_pct = result['return']
    
    # Equity value on top
    ax1.text(bar.get_x() + bar.get_width()/2., height + 250000,
           f'${height/1e6:.2f}M',
           ha='center', va='bottom', fontsize=11, weight='bold', color='white')
    
    # Profit and return inside bar
    if height > 3000000:  # Only show if bar is tall enough
        ax1.text(bar.get_x() + bar.get_width()/2., height/2,
               f'+${profit/1e6:.2f}M\n({return_pct:.0f}%)',
               ha='center', va='center', fontsize=9, weight='bold',
               bbox=dict(boxstyle='round,pad=0.4', facecolor='black', alpha=0.7))

# Configure left y-axis (Equity)
ax1.set_ylabel('Your Portfolio Value ($)', fontsize=14, weight='bold', color='white')
ax1.set_xlabel('Scenario', fontsize=14, weight='bold')
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
ax1.tick_params(axis='y', labelcolor='white')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(names, fontsize=11, rotation=0)
ax1.grid(True, alpha=0.3, axis='y', zorder=0)
ax1.set_facecolor('#1a1a1a')

# Create second y-axis for BTC price
ax2 = ax1.twinx()

# Plot BTC price line
btc_line = ax2.plot(x_pos, btc_prices, color='#f39c12', marker='D', 
                    markersize=10, linewidth=3, label='BTC Price',
                    markerfacecolor='#f39c12', markeredgecolor='white', 
                    markeredgewidth=2, zorder=10)

# Add BTC price labels
for i, (x, btc_price) in enumerate(zip(x_pos, btc_prices)):
    # Position label above the marker
    y_offset = 8000 if i < 3 else 12000  # Different offset for different scenarios
    ax2.text(x, btc_price + y_offset, f'${btc_price/1000:.0f}k',
           ha='center', va='bottom', fontsize=10, weight='bold',
           color='#f39c12',
           bbox=dict(boxstyle='round,pad=0.4', facecolor='black', 
                    edgecolor='#f39c12', alpha=0.8, linewidth=1.5))

# Configure right y-axis (BTC Price)
ax2.set_ylabel('Bitcoin Price ($)', fontsize=14, weight='bold', color='#f39c12')
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}k'))
ax2.tick_params(axis='y', labelcolor='#f39c12')
ax2.spines['right'].set_color('#f39c12')
ax2.spines['right'].set_linewidth(2)

# Add current BTC price reference line
ax2.axhline(y=CURRENT_BTC_PRICE, color='#f39c12', linestyle=':', 
           linewidth=2, alpha=0.5, label=f'Current BTC: ${CURRENT_BTC_PRICE/1000:.0f}k',
           zorder=5)

# Title and legends
ax1.set_title('$2.5M Leveraged MSTR Position (1.26x) - Portfolio Growth & Bitcoin Price Trajectory', 
            fontsize=18, weight='bold', pad=25, color='white')

# Combine legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12,
          framealpha=0.9, edgecolor='white')

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
plt.savefig('leveraged_position_with_btc.png', dpi=300, facecolor='#0a0a0a', edgecolor='none', bbox_inches='tight')
print("Saved: leveraged_position_with_btc.png")
plt.close()

# ============================================================================
# DUAL TIMELINE: Side-by-side comparison
# ============================================================================

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 14), sharex=True)

# Top panel: Portfolio Value
bars1 = ax1.bar(x_pos, [e/1e6 for e in equities], color=colors, alpha=0.85, 
               edgecolor='white', linewidth=2, width=0.7)

ax1.axhline(y=CAPITAL/1e6, color='red', linestyle='--', linewidth=2.5, 
           label=f'Initial Capital: ${CAPITAL/1e6:.1f}M', alpha=0.9)

# Add value labels
for i, (bar, result) in enumerate(zip(bars1, results)):
    height = bar.get_height()
    profit = result['profit']/1e6
    return_pct = result['return']
    
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.2,
           f'${height:.2f}M\n+{return_pct:.0f}%',
           ha='center', va='bottom', fontsize=10, weight='bold')

ax1.set_ylabel('Portfolio Value ($ Millions)', fontsize=13, weight='bold')
ax1.set_title('Your $2.5M Leveraged Position Growth & Bitcoin Price Scenarios', 
             fontsize=18, weight='bold', pad=20)
ax1.legend(loc='upper left', fontsize=11)
ax1.grid(True, alpha=0.3, axis='y')
ax1.set_facecolor('#1a1a1a')

# Bottom panel: BTC Price
bars2 = ax2.bar(x_pos, [b/1000 for b in btc_prices], color='#f39c12', alpha=0.85,
               edgecolor='white', linewidth=2, width=0.7)

ax2.axhline(y=CURRENT_BTC_PRICE/1000, color='#f39c12', linestyle='--', 
           linewidth=2.5, label=f'Current BTC: ${CURRENT_BTC_PRICE/1000:.0f}k', alpha=0.9)

# Add BTC price labels
for i, (bar, btc_price) in enumerate(zip(bars2, btc_prices)):
    height = bar.get_height()
    change_pct = ((btc_price / CURRENT_BTC_PRICE) - 1) * 100
    
    ax2.text(bar.get_x() + bar.get_width()/2., height + 5,
           f'${height:.0f}k\n({change_pct:+.0f}%)',
           ha='center', va='bottom', fontsize=10, weight='bold', color='#f39c12')

ax2.set_ylabel('Bitcoin Price ($ Thousands)', fontsize=13, weight='bold', color='#f39c12')
ax2.set_xlabel('Scenario', fontsize=13, weight='bold')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(names, fontsize=11)
ax2.legend(loc='upper left', fontsize=11)
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_facecolor('#1a1a1a')
ax2.tick_params(axis='y', labelcolor='#f39c12')

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
plt.savefig('leveraged_position_dual_panel.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Saved: leveraged_position_dual_panel.png")
plt.close()

# ============================================================================
# CORRELATION SCATTER: Portfolio Value vs BTC Price
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 10))

# Create scatter plot
scatter = ax.scatter([b/1000 for b in btc_prices], [e/1e6 for e in equities],
                    s=500, c=range(len(results)), cmap='viridis',
                    alpha=0.8, edgecolors='white', linewidth=2.5, zorder=5)

# Add connecting line
ax.plot([b/1000 for b in btc_prices], [e/1e6 for e in equities],
       color='cyan', linewidth=2, alpha=0.5, linestyle='--', zorder=3)

# Add labels for each point
for i, result in enumerate(results):
    ax.annotate(result['name'].replace('\n', ' '),
               xy=(result['btc_price']/1000, result['equity']/1e6),
               xytext=(10, 10), textcoords='offset points',
               fontsize=9, weight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='black', 
                        alpha=0.8, edgecolor='white'),
               arrowprops=dict(arrowstyle='->', color='white', lw=1.5))

# Add reference lines
ax.axhline(y=CAPITAL/1e6, color='red', linestyle='--', linewidth=2, 
          label=f'Initial Capital: ${CAPITAL/1e6:.1f}M', alpha=0.7)
ax.axvline(x=CURRENT_BTC_PRICE/1000, color='#f39c12', linestyle='--', 
          linewidth=2, label=f'Current BTC: ${CURRENT_BTC_PRICE/1000:.0f}k', alpha=0.7)

ax.set_xlabel('Bitcoin Price ($ Thousands)', fontsize=14, weight='bold')
ax.set_ylabel('Your Portfolio Value ($ Millions)', fontsize=14, weight='bold')
ax.set_title('Portfolio Value vs Bitcoin Price - Correlation Analysis', 
            fontsize=18, weight='bold', pad=20)
ax.legend(loc='upper left', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_facecolor('#1a1a1a')
fig.patch.set_facecolor('#0a0a0a')

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax, pad=0.02)
cbar.set_label('Scenario Progression', rotation=270, labelpad=25, fontsize=12, weight='bold')

plt.tight_layout()
plt.savefig('portfolio_btc_correlation.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Saved: portfolio_btc_correlation.png")
plt.close()

print("\nAll enhanced visualizations created successfully!")
