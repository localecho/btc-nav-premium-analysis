#!/usr/bin/env python3
"""
MicroStrategy Fair Value Model
Predicts fair MSTR price based on NAV Premium analysis and BTC price scenarios
"""

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Set style
plt.style.use('dark_background')
sns.set_palette("husl")

print("="*80)
print("MICROSTRATEGY FAIR VALUE MODEL")
print("="*80)

# ============================================================================
# CURRENT STATE (as of Nov 6, 2025)
# ============================================================================

CURRENT_DATE = "2025-11-06"
CURRENT_BTC_PRICE = 101141.77
CURRENT_MSTR_PRICE = 237.20
CURRENT_BTC_HOLDINGS = 641205
CURRENT_SHARES_OUTSTANDING = 320_000_000  # Estimated
CURRENT_NAV_PREMIUM = 1.17

# Calculate current NAV
CURRENT_BTC_NAV = (CURRENT_BTC_PRICE * CURRENT_BTC_HOLDINGS) / 1_000_000  # in millions
CURRENT_NAV_PER_SHARE = CURRENT_BTC_NAV / (CURRENT_SHARES_OUTSTANDING / 1_000_000)

print(f"\nCurrent State ({CURRENT_DATE}):")
print(f"  BTC Price: ${CURRENT_BTC_PRICE:,.2f}")
print(f"  MSTR Price: ${CURRENT_MSTR_PRICE:,.2f}")
print(f"  BTC Holdings: {CURRENT_BTC_HOLDINGS:,} BTC")
print(f"  Shares Outstanding: {CURRENT_SHARES_OUTSTANDING:,}")
print(f"  BTC NAV: ${CURRENT_BTC_NAV:,.0f}M")
print(f"  NAV per Share: ${CURRENT_NAV_PER_SHARE:,.2f}")
print(f"  Current NAV Premium: {CURRENT_NAV_PREMIUM:.2f}x")

# ============================================================================
# HISTORICAL NAV PREMIUM BENCHMARKS (from regime analysis)
# ============================================================================

NAV_PREMIUM_BENCHMARKS = {
    'historical_mean': 1.98,
    'historical_median': 1.79,
    'bull_market_mean': 2.06,
    'bull_market_median': 1.98,
    'bear_market_mean': 1.88,
    'bear_market_median': 1.62,
    'current': 1.17,
    'historical_min': 0.81,
    'historical_max': 7.42,
    'fair_value_range': (1.5, 2.5),  # Conservative fair value range
}

print(f"\nHistorical NAV Premium Benchmarks:")
for key, value in NAV_PREMIUM_BENCHMARKS.items():
    if isinstance(value, tuple):
        print(f"  {key}: {value[0]:.2f}x - {value[1]:.2f}x")
    else:
        print(f"  {key}: {value:.2f}x")

# ============================================================================
# BTC PRICE SCENARIOS FOR 2026
# ============================================================================

# Define BTC price scenarios for each quarter of 2026
BTC_SCENARIOS = {
    'Q1_2026': {
        'date': '2026-03-31',
        'bear': 75000,
        'base': 95000,
        'bull': 125000,
        'moon': 150000,
    },
    'Q2_2026': {
        'date': '2026-06-30',
        'bear': 70000,
        'base': 105000,
        'bull': 140000,
        'moon': 175000,
    },
    'Q3_2026': {
        'date': '2026-09-30',
        'bear': 65000,
        'base': 115000,
        'bull': 155000,
        'moon': 200000,
    },
    'Q4_2026': {
        'date': '2026-12-31',
        'bear': 60000,
        'base': 125000,
        'bull': 170000,
        'moon': 225000,
    },
}

print(f"\nBTC Price Scenarios for 2026:")
for quarter, scenarios in BTC_SCENARIOS.items():
    print(f"\n  {quarter} ({scenarios['date']}):")
    print(f"    Bear: ${scenarios['bear']:,}")
    print(f"    Base: ${scenarios['base']:,}")
    print(f"    Bull: ${scenarios['bull']:,}")
    print(f"    Moon: ${scenarios['moon']:,}")

# ============================================================================
# ASSUMPTIONS FOR 2026
# ============================================================================

# Bitcoin holdings growth (MSTR continues accumulating)
BTC_HOLDINGS_GROWTH_QUARTERLY = 0.03  # 3% per quarter (~12.5% annually)

# Shares outstanding growth (dilution from ATM offerings)
SHARES_DILUTION_QUARTERLY = 0.02  # 2% per quarter (~8% annually)

# Software business value (rough estimate)
SOFTWARE_BUSINESS_VALUE_PER_SHARE = 15  # Conservative estimate

print(f"\nModel Assumptions:")
print(f"  BTC Holdings Growth: {BTC_HOLDINGS_GROWTH_QUARTERLY*100:.1f}% per quarter")
print(f"  Share Dilution: {SHARES_DILUTION_QUARTERLY*100:.1f}% per quarter")
print(f"  Software Business Value: ${SOFTWARE_BUSINESS_VALUE_PER_SHARE:.0f} per share")

# ============================================================================
# FAIR VALUE CALCULATION FUNCTION
# ============================================================================

def calculate_fair_value(btc_price, btc_holdings, shares_outstanding, nav_premium_target, 
                         include_software=True, software_value_per_share=SOFTWARE_BUSINESS_VALUE_PER_SHARE):
    """
    Calculate fair MSTR price given inputs
    
    Fair Price = (BTC NAV * NAV Premium + Software Value) / Shares Outstanding
    """
    btc_nav_millions = (btc_price * btc_holdings) / 1_000_000
    nav_per_share = btc_nav_millions / (shares_outstanding / 1_000_000)
    
    btc_component = nav_per_share * nav_premium_target
    
    if include_software:
        fair_price = btc_component + software_value_per_share
    else:
        fair_price = btc_component
    
    return {
        'fair_price': fair_price,
        'btc_nav_per_share': nav_per_share,
        'btc_component': btc_component,
        'software_component': software_value_per_share if include_software else 0,
        'implied_nav_premium': nav_premium_target
    }

# ============================================================================
# TODAY'S FAIR VALUE
# ============================================================================

print(f"\n" + "="*80)
print("FAIR VALUE ANALYSIS - TODAY (Nov 6, 2025)")
print("="*80)

today_scenarios = {
    'Conservative (Bear Market Median)': calculate_fair_value(
        CURRENT_BTC_PRICE, CURRENT_BTC_HOLDINGS, CURRENT_SHARES_OUTSTANDING, 
        NAV_PREMIUM_BENCHMARKS['bear_market_median']
    ),
    'Fair Value (Historical Median)': calculate_fair_value(
        CURRENT_BTC_PRICE, CURRENT_BTC_HOLDINGS, CURRENT_SHARES_OUTSTANDING, 
        NAV_PREMIUM_BENCHMARKS['historical_median']
    ),
    'Bull Case (Bull Market Mean)': calculate_fair_value(
        CURRENT_BTC_PRICE, CURRENT_BTC_HOLDINGS, CURRENT_SHARES_OUTSTANDING, 
        NAV_PREMIUM_BENCHMARKS['bull_market_mean']
    ),
    'Optimistic (2.5x Premium)': calculate_fair_value(
        CURRENT_BTC_PRICE, CURRENT_BTC_HOLDINGS, CURRENT_SHARES_OUTSTANDING, 
        2.5
    ),
    'Current Market Price': {
        'fair_price': CURRENT_MSTR_PRICE,
        'btc_nav_per_share': CURRENT_NAV_PER_SHARE,
        'btc_component': CURRENT_NAV_PER_SHARE * CURRENT_NAV_PREMIUM,
        'software_component': 0,
        'implied_nav_premium': CURRENT_NAV_PREMIUM
    }
}

print(f"\nCurrent BTC Price: ${CURRENT_BTC_PRICE:,.2f}")
print(f"Current MSTR Price: ${CURRENT_MSTR_PRICE:,.2f}")
print(f"NAV per Share: ${CURRENT_NAV_PER_SHARE:,.2f}")
print(f"\nFair Value Scenarios:\n")

today_results = []
for scenario_name, result in today_scenarios.items():
    fair_price = result['fair_price']
    premium = result['implied_nav_premium']
    upside = ((fair_price / CURRENT_MSTR_PRICE) - 1) * 100
    
    print(f"{scenario_name}:")
    print(f"  Fair Price: ${fair_price:.2f}")
    print(f"  NAV Premium: {premium:.2f}x")
    print(f"  Upside/Downside: {upside:+.1f}%")
    print()
    
    today_results.append({
        'scenario': scenario_name,
        'fair_price': fair_price,
        'nav_premium': premium,
        'upside_pct': upside
    })

# ============================================================================
# 2026 QUARTERLY PROJECTIONS
# ============================================================================

print("="*80)
print("FAIR VALUE PROJECTIONS - 2026 QUARTERS")
print("="*80)

projections = []

for quarter_idx, (quarter, btc_prices) in enumerate(BTC_SCENARIOS.items(), start=1):
    print(f"\n{quarter} ({btc_prices['date']})")
    print("-" * 80)
    
    # Calculate holdings and shares for this quarter
    quarters_ahead = quarter_idx
    projected_btc_holdings = CURRENT_BTC_HOLDINGS * (1 + BTC_HOLDINGS_GROWTH_QUARTERLY) ** quarters_ahead
    projected_shares = CURRENT_SHARES_OUTSTANDING * (1 + SHARES_DILUTION_QUARTERLY) ** quarters_ahead
    
    print(f"Projected BTC Holdings: {projected_btc_holdings:,.0f} BTC")
    print(f"Projected Shares Outstanding: {projected_shares:,.0f}")
    print()
    
    for btc_scenario in ['bear', 'base', 'bull', 'moon']:
        btc_price = btc_prices[btc_scenario]
        
        print(f"  {btc_scenario.upper()} Scenario (BTC @ ${btc_price:,}):")
        
        # Calculate fair values at different premium levels
        conservative = calculate_fair_value(btc_price, projected_btc_holdings, projected_shares, 1.5)
        fair = calculate_fair_value(btc_price, projected_btc_holdings, projected_shares, 1.8)
        bull = calculate_fair_value(btc_price, projected_btc_holdings, projected_shares, 2.1)
        
        print(f"    Conservative (1.5x): ${conservative['fair_price']:.2f}")
        print(f"    Fair Value (1.8x):   ${fair['fair_price']:.2f}")
        print(f"    Bull Case (2.1x):    ${bull['fair_price']:.2f}")
        print()
        
        projections.append({
            'quarter': quarter,
            'date': btc_prices['date'],
            'btc_scenario': btc_scenario,
            'btc_price': btc_price,
            'btc_holdings': projected_btc_holdings,
            'shares_outstanding': projected_shares,
            'conservative_price': conservative['fair_price'],
            'fair_value_price': fair['fair_price'],
            'bull_price': bull['fair_price'],
        })

# ============================================================================
# SAVE RESULTS
# ============================================================================

results_summary = {
    'analysis_date': CURRENT_DATE,
    'current_state': {
        'btc_price': CURRENT_BTC_PRICE,
        'mstr_price': CURRENT_MSTR_PRICE,
        'btc_holdings': CURRENT_BTC_HOLDINGS,
        'shares_outstanding': CURRENT_SHARES_OUTSTANDING,
        'nav_per_share': CURRENT_NAV_PER_SHARE,
        'nav_premium': CURRENT_NAV_PREMIUM
    },
    'today_fair_values': today_results,
    'quarterly_projections_2026': projections,
    'assumptions': {
        'btc_holdings_growth_quarterly': BTC_HOLDINGS_GROWTH_QUARTERLY,
        'shares_dilution_quarterly': SHARES_DILUTION_QUARTERLY,
        'software_business_value_per_share': SOFTWARE_BUSINESS_VALUE_PER_SHARE
    }
}

with open('fair_value_projections.json', 'w') as f:
    json.dump(results_summary, f, indent=2)

print("\n" + "="*80)
print("Results saved to fair_value_projections.json")
print("="*80)

# ============================================================================
# CREATE SUMMARY TABLE
# ============================================================================

print("\n" + "="*80)
print("SUMMARY TABLE: 2026 FAIR VALUE RANGES")
print("="*80)
print()

summary_df = pd.DataFrame(projections)

for quarter in ['Q1_2026', 'Q2_2026', 'Q3_2026', 'Q4_2026']:
    quarter_data = summary_df[summary_df['quarter'] == quarter]
    print(f"{quarter}:")
    print(f"  BTC Range: ${quarter_data['btc_price'].min():,} - ${quarter_data['btc_price'].max():,}")
    print(f"  MSTR Fair Value Range: ${quarter_data['conservative_price'].min():.0f} - ${quarter_data['bull_price'].max():.0f}")
    print(f"  Base Case (BTC @ ${quarter_data[quarter_data['btc_scenario']=='base']['btc_price'].iloc[0]:,}):")
    base_case = quarter_data[quarter_data['btc_scenario'] == 'base'].iloc[0]
    print(f"    Conservative: ${base_case['conservative_price']:.2f}")
    print(f"    Fair Value:   ${base_case['fair_value_price']:.2f}")
    print(f"    Bull Case:    ${base_case['bull_price']:.2f}")
    print()

print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)
