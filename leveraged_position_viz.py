#!/usr/bin/env python3
"""
Visualize Leveraged Position Returns
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
SHARES = POSITION_SIZE / CURRENT_MSTR_PRICE

# Scenarios
scenarios = {
    'Today\nConservative': 343.32,
    'Today\nFair Value': 377.77,
    'Today\nBull Case': 432.49,
    'Q1 2026\nBase': 361.00,
    'Q2 2026\nBase': 401.17,
    'Q3 2026\nBase': 442.10,
    'Q4 2026\nBase': 483.79,
    'Q4 2026\nBull': 652.55,
    'Q4 2026\nMoon': 858.82,
}

# Calculate returns
results = []
for name, price in scenarios.items():
    position_value = SHARES * price
    borrowed = POSITION_SIZE - CAPITAL
    net_equity = position_value - borrowed
    net_profit = net_equity - CAPITAL
    leveraged_return = (net_profit / CAPITAL) * 100
    
    results.append({
        'name': name,
        'price': price,
        'equity': net_equity,
        'profit': net_profit,
        'return': leveraged_return
    })

# ============================================================================
# VISUALIZATION 1: Equity Growth
# ============================================================================

fig, ax = plt.subplots(figsize=(16, 10))

names = [r['name'] for r in results]
equities = [r['equity'] for r in results]
colors = ['#ff6b6b', '#ff8c69', '#ffa566', 
          '#4ecdc4', '#45b7d1', '#5390d9',
          '#48bfe3', '#72efdd', '#64dfdf']

bars = ax.bar(range(len(names)), equities, color=colors, alpha=0.85, 
              edgecolor='white', linewidth=2)

# Add initial capital line
ax.axhline(y=CAPITAL, color='red', linestyle='--', linewidth=2.5, 
          label=f'Initial Capital: ${CAPITAL/1e6:.1f}M', alpha=0.9)

# Add value labels
for i, (bar, result) in enumerate(zip(bars, results)):
    height = bar.get_height()
    profit = result['profit']
    return_pct = result['return']
    
    # Equity value on top
    ax.text(bar.get_x() + bar.get_width()/2., height + 200000,
           f'${height/1e6:.2f}M',
           ha='center', va='bottom', fontsize=11, weight='bold')
    
    # Profit and return inside bar
    ax.text(bar.get_x() + bar.get_width()/2., height/2,
           f'+${profit/1e6:.2f}M\n({return_pct:.0f}%)',
           ha='center', va='center', fontsize=10, weight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.7))

ax.set_ylabel('Total Equity Value ($)', fontsize=14, weight='bold')
ax.set_xlabel('Scenario', fontsize=14, weight='bold')
ax.set_title('$2.5M Leveraged MSTR Position (1.26x) - Equity Growth by Scenario', 
            fontsize=18, weight='bold', pad=20)
ax.set_xticks(range(len(names)))
ax.set_xticklabels(names, fontsize=11, rotation=0)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
ax.legend(loc='upper left', fontsize=12)
ax.grid(True, alpha=0.3, axis='y')
ax.set_facecolor('#1a1a1a')
fig.patch.set_facecolor('#0a0a0a')

plt.tight_layout()
plt.savefig('leveraged_position_equity.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Saved: leveraged_position_equity.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: Return Comparison
# ============================================================================

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

# Unleveraged vs Leveraged returns
unleveraged_returns = [((r['price'] / CURRENT_MSTR_PRICE) - 1) * 100 for r in results]
leveraged_returns = [r['return'] for r in results]

x = np.arange(len(names))
width = 0.35

bars1 = ax1.bar(x - width/2, unleveraged_returns, width, label='Unleveraged (1.0x)', 
               color='#4ecdc4', alpha=0.8, edgecolor='white', linewidth=1)
bars2 = ax1.bar(x + width/2, leveraged_returns, width, label='Leveraged (1.26x)', 
               color='#ff6b6b', alpha=0.8, edgecolor='white', linewidth=1)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
               f'{height:.0f}%',
               ha='center', va='bottom', fontsize=9, weight='bold')

ax1.set_ylabel('Return (%)', fontsize=13, weight='bold')
ax1.set_xlabel('Scenario', fontsize=13, weight='bold')
ax1.set_title('Return Comparison: Unleveraged vs 1.26x Leveraged', 
             fontsize=16, weight='bold', pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(names, fontsize=10)
ax1.legend(loc='upper left', fontsize=11)
ax1.grid(True, alpha=0.3, axis='y')
ax1.set_facecolor('#1a1a1a')
ax1.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.5)

# Profit comparison
unleveraged_profits = [CAPITAL * (r / 100) for r in unleveraged_returns]
leveraged_profits = [r['profit'] for r in results]

bars3 = ax2.bar(x - width/2, [p/1e6 for p in unleveraged_profits], width, 
               label='Unleveraged (1.0x)', color='#4ecdc4', alpha=0.8, 
               edgecolor='white', linewidth=1)
bars4 = ax2.bar(x + width/2, [p/1e6 for p in leveraged_profits], width, 
               label='Leveraged (1.26x)', color='#ff6b6b', alpha=0.8, 
               edgecolor='white', linewidth=1)

# Add value labels
for bars in [bars3, bars4]:
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
               f'${height:.2f}M',
               ha='center', va='bottom', fontsize=9, weight='bold')

ax2.set_ylabel('Profit ($ Millions)', fontsize=13, weight='bold')
ax2.set_xlabel('Scenario', fontsize=13, weight='bold')
ax2.set_title('Profit Comparison: Unleveraged vs 1.26x Leveraged', 
             fontsize=16, weight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(names, fontsize=10)
ax2.legend(loc='upper left', fontsize=11)
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_facecolor('#1a1a1a')
ax2.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.5)

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
plt.savefig('leveraged_vs_unleveraged.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Saved: leveraged_vs_unleveraged.png")
plt.close()

# ============================================================================
# VISUALIZATION 3: Timeline Projection
# ============================================================================

fig, ax = plt.subplots(figsize=(16, 10))

# Timeline scenarios
timeline_scenarios = [
    ('Today', CAPITAL),
    ('Today\nConservative', results[0]['equity']),
    ('Q1 2026', results[3]['equity']),
    ('Q2 2026', results[4]['equity']),
    ('Q3 2026', results[5]['equity']),
    ('Q4 2026\nBase', results[6]['equity']),
    ('Q4 2026\nBull', results[7]['equity']),
    ('Q4 2026\nMoon', results[8]['equity']),
]

timeline_labels = [s[0] for s in timeline_scenarios]
timeline_values = [s[1] for s in timeline_scenarios]

# Plot line
ax.plot(range(len(timeline_labels)), [v/1e6 for v in timeline_values], 
       marker='o', markersize=12, linewidth=3, color='#4ecdc4', 
       markerfacecolor='#ff6b6b', markeredgecolor='white', markeredgewidth=2)

# Fill area
ax.fill_between(range(len(timeline_labels)), 
               [CAPITAL/1e6]*len(timeline_labels),
               [v/1e6 for v in timeline_values],
               alpha=0.3, color='#4ecdc4')

# Add value labels
for i, (label, value) in enumerate(zip(timeline_labels, timeline_values)):
    profit = value - CAPITAL
    ax.text(i, value/1e6 + 0.3, f'${value/1e6:.2f}M\n(+${profit/1e6:.2f}M)',
           ha='center', va='bottom', fontsize=11, weight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.7))

# Add initial capital line
ax.axhline(y=CAPITAL/1e6, color='red', linestyle='--', linewidth=2, 
          label=f'Initial Capital: ${CAPITAL/1e6:.1f}M', alpha=0.7)

ax.set_ylabel('Portfolio Value ($ Millions)', fontsize=14, weight='bold')
ax.set_xlabel('Timeline', fontsize=14, weight='bold')
ax.set_title('$2.5M Leveraged Position Growth Timeline (1.26x Leverage)', 
            fontsize=18, weight='bold', pad=20)
ax.set_xticks(range(len(timeline_labels)))
ax.set_xticklabels(timeline_labels, fontsize=11)
ax.legend(loc='upper left', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_facecolor('#1a1a1a')
fig.patch.set_facecolor('#0a0a0a')

plt.tight_layout()
plt.savefig('leveraged_position_timeline.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Saved: leveraged_position_timeline.png")
plt.close()

print("\nAll visualizations created successfully!")
