#!/usr/bin/env python3
"""
Visualize Fair Value Projections
"""

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('dark_background')
sns.set_palette("husl")

# Load results
with open('fair_value_projections.json', 'r') as f:
    results = json.load(f)

current_price = results['current_state']['mstr_price']
projections = pd.DataFrame(results['quarterly_projections_2026'])

# ============================================================================
# VISUALIZATION 1: Today's Fair Value Range
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

today_values = results['today_fair_values']
scenarios = [v['scenario'] for v in today_values if v['scenario'] != 'Current Market Price']
prices = [v['fair_price'] for v in today_values if v['scenario'] != 'Current Market Price']
premiums = [v['nav_premium'] for v in today_values if v['scenario'] != 'Current Market Price']

y_pos = np.arange(len(scenarios))
colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']

bars = ax.barh(y_pos, prices, color=colors, alpha=0.8, edgecolor='white', linewidth=1.5)

# Add current price line
ax.axvline(x=current_price, color='red', linestyle='--', linewidth=2, 
           label=f'Current Price: ${current_price:.2f}', alpha=0.9)

# Add price labels
for i, (price, premium) in enumerate(zip(prices, premiums)):
    upside = ((price / current_price) - 1) * 100
    ax.text(price + 10, i, f'${price:.2f} ({premium:.2f}x NAV)\n{upside:+.1f}% upside', 
           va='center', fontsize=10, weight='bold')

ax.set_yticks(y_pos)
ax.set_yticklabels(scenarios, fontsize=11)
ax.set_xlabel('MSTR Fair Price ($)', fontsize=13, weight='bold')
ax.set_title('MicroStrategy Fair Value Analysis - Today (Nov 6, 2025)', 
            fontsize=16, weight='bold', pad=20)
ax.legend(loc='lower right', fontsize=11)
ax.grid(True, alpha=0.3, axis='x')
ax.set_facecolor('#1a1a1a')
fig.patch.set_facecolor('#0a0a0a')

plt.tight_layout()
plt.savefig('fair_value_today.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Saved: fair_value_today.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: 2026 Quarterly Projections - Base Case
# ============================================================================

fig, ax = plt.subplots(figsize=(16, 10))

quarters = ['Q1_2026', 'Q2_2026', 'Q3_2026', 'Q4_2026']
quarter_labels = ['Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026']
x = np.arange(len(quarters))
width = 0.2

# Extract base case data
base_data = projections[projections['btc_scenario'] == 'base']
conservative = base_data['conservative_price'].values
fair_value = base_data['fair_value_price'].values
bull_case = base_data['bull_price'].values

# Create bars
bars1 = ax.bar(x - width, conservative, width, label='Conservative (1.5x NAV)', 
              color='#ff6b6b', alpha=0.8, edgecolor='white', linewidth=1)
bars2 = ax.bar(x, fair_value, width, label='Fair Value (1.8x NAV)', 
              color='#4ecdc4', alpha=0.8, edgecolor='white', linewidth=1)
bars3 = ax.bar(x + width, bull_case, width, label='Bull Case (2.1x NAV)', 
              color='#45b7d1', alpha=0.8, edgecolor='white', linewidth=1)

# Add current price line
ax.axhline(y=current_price, color='red', linestyle='--', linewidth=2, 
          label=f'Current Price: ${current_price:.2f}', alpha=0.9)

# Add value labels on bars
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 10,
               f'${height:.0f}',
               ha='center', va='bottom', fontsize=9, weight='bold')

# Add BTC prices as annotations
for i, quarter in enumerate(quarters):
    btc_price = base_data[base_data['quarter'] == quarter]['btc_price'].iloc[0]
    ax.text(i, ax.get_ylim()[1] * 0.95, f'BTC: ${btc_price:,}',
           ha='center', fontsize=10, weight='bold', 
           bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.7))

ax.set_xlabel('Quarter', fontsize=13, weight='bold')
ax.set_ylabel('MSTR Fair Price ($)', fontsize=13, weight='bold')
ax.set_title('MicroStrategy Fair Value Projections - 2026 Base Case Scenario', 
            fontsize=16, weight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(quarter_labels, fontsize=11)
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.3, axis='y')
ax.set_facecolor('#1a1a1a')
fig.patch.set_facecolor('#0a0a0a')

plt.tight_layout()
plt.savefig('fair_value_2026_base.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Saved: fair_value_2026_base.png")
plt.close()

# ============================================================================
# VISUALIZATION 3: Full Range of Scenarios
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(18, 14))
axes = axes.flatten()

for idx, quarter in enumerate(quarters):
    ax = axes[idx]
    quarter_data = projections[projections['quarter'] == quarter]
    
    scenarios = ['bear', 'base', 'bull', 'moon']
    scenario_labels = ['Bear', 'Base', 'Bull', 'Moon']
    
    x_pos = np.arange(len(scenarios))
    width = 0.25
    
    conservative_vals = [quarter_data[quarter_data['btc_scenario'] == s]['conservative_price'].iloc[0] for s in scenarios]
    fair_vals = [quarter_data[quarter_data['btc_scenario'] == s]['fair_value_price'].iloc[0] for s in scenarios]
    bull_vals = [quarter_data[quarter_data['btc_scenario'] == s]['bull_price'].iloc[0] for s in scenarios]
    
    ax.bar(x_pos - width, conservative_vals, width, label='Conservative (1.5x)', 
          color='#ff6b6b', alpha=0.8)
    ax.bar(x_pos, fair_vals, width, label='Fair Value (1.8x)', 
          color='#4ecdc4', alpha=0.8)
    ax.bar(x_pos + width, bull_vals, width, label='Bull Case (2.1x)', 
          color='#45b7d1', alpha=0.8)
    
    ax.axhline(y=current_price, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    
    ax.set_xlabel('BTC Price Scenario', fontsize=11, weight='bold')
    ax.set_ylabel('MSTR Fair Price ($)', fontsize=11, weight='bold')
    ax.set_title(f'{quarter_labels[idx]}', fontsize=13, weight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(scenario_labels)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_facecolor('#1a1a1a')
    
    # Add BTC prices as text
    for i, scenario in enumerate(scenarios):
        btc_price = quarter_data[quarter_data['btc_scenario'] == scenario]['btc_price'].iloc[0]
        ax.text(i, ax.get_ylim()[0] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05,
               f'${btc_price/1000:.0f}k',
               ha='center', fontsize=8, style='italic')

fig.suptitle('MicroStrategy Fair Value - All Scenarios 2026', 
            fontsize=18, weight='bold', y=0.995)
fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
plt.savefig('fair_value_2026_all_scenarios.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Saved: fair_value_2026_all_scenarios.png")
plt.close()

# ============================================================================
# VISUALIZATION 4: Price Range Heatmap
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 10))

# Create matrix for heatmap
quarters_list = ['Q1_2026', 'Q2_2026', 'Q3_2026', 'Q4_2026']
scenarios_list = ['bear', 'base', 'bull', 'moon']

# Use fair value prices for heatmap
matrix = []
for quarter in quarters_list:
    row = []
    for scenario in scenarios_list:
        price = projections[(projections['quarter'] == quarter) & 
                          (projections['btc_scenario'] == scenario)]['fair_value_price'].iloc[0]
        row.append(price)
    matrix.append(row)

matrix = np.array(matrix)

# Create heatmap
im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', alpha=0.8)

# Set ticks and labels
ax.set_xticks(np.arange(len(scenarios_list)))
ax.set_yticks(np.arange(len(quarters_list)))
ax.set_xticklabels(['Bear', 'Base', 'Bull', 'Moon'], fontsize=12)
ax.set_yticklabels(['Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026'], fontsize=12)

# Add text annotations
for i in range(len(quarters_list)):
    for j in range(len(scenarios_list)):
        text = ax.text(j, i, f'${matrix[i, j]:.0f}',
                      ha="center", va="center", color="white", 
                      fontsize=11, weight='bold',
                      bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))

# Add colorbar
cbar = plt.colorbar(im, ax=ax, pad=0.02)
cbar.set_label('Fair Value Price ($)', rotation=270, labelpad=25, fontsize=12, weight='bold')

ax.set_xlabel('BTC Price Scenario', fontsize=13, weight='bold')
ax.set_ylabel('Quarter', fontsize=13, weight='bold')
ax.set_title('MicroStrategy Fair Value Heatmap - 2026 (1.8x NAV Premium)', 
            fontsize=16, weight='bold', pad=20)

ax.set_facecolor('#1a1a1a')
fig.patch.set_facecolor('#0a0a0a')

plt.tight_layout()
plt.savefig('fair_value_heatmap.png', dpi=300, facecolor='#0a0a0a', edgecolor='none')
print("Saved: fair_value_heatmap.png")
plt.close()

print("\nAll visualizations created successfully!")
