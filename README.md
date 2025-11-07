# Bitcoin NAV Premium Analysis for MicroStrategy

This repository contains a comprehensive analysis of MicroStrategy's Net Asset Value (NAV) Premium relative to Bitcoin price movements. The analysis recreates and extends the popular "Strategy NAV Premium vs BTC Price" chart that tracks how MSTR stock trades relative to its underlying Bitcoin holdings.

## Overview

MicroStrategy (MSTR) is the largest corporate holder of Bitcoin, making it a popular proxy for Bitcoin exposure in traditional equity markets. The company's stock often trades at a premium or discount to its Net Asset Value (NAV), which is primarily driven by its Bitcoin holdings.

This project analyzes the relationship between Bitcoin price and MSTR's NAV Premium using historical data from 2020 to 2025.

## Key Metrics

**NAV Premium** is calculated as:
```
NAV Premium = (MSTR Market Cap) / (BTC Holdings Value)
```

Where:
- **MSTR Market Cap** = Stock Price × Shares Outstanding
- **BTC Holdings Value** = BTC Holdings × BTC Price

A NAV Premium of:
- **1.0x** means MSTR trades at fair value (market cap equals Bitcoin holdings value)
- **>1.0x** means MSTR trades at a premium (investors pay more than the underlying Bitcoin value)
- **<1.0x** means MSTR trades at a discount (investors pay less than the underlying Bitcoin value)

## Current Statistics (as of November 6, 2025)

- **BTC Price**: $101,141.77
- **MSTR Price**: $237.20
- **NAV Premium**: 1.17x
- **BTC Holdings**: 641,205 BTC
- **BTC NAV**: $64,853M
- **Market Cap**: $75,904M

## Historical Analysis (BTC Price Range $50k-$150k)

- **Mean NAV Premium**: 2.15x
- **Median NAV Premium**: 2.15x
- **Min NAV Premium**: 1.16x
- **Max NAV Premium**: 4.07x
- **Standard Deviation**: 0.49x

## Repository Contents

### Jupyter Notebook
- **`btc_nav_premium_analysis.ipynb`** - Interactive Jupyter notebook with full analysis and visualizations

### Python Scripts
- **`run_analysis.py`** - Standalone script to generate all charts and statistics
- **`fetch_btc_data.py`** - Fetches historical Bitcoin price data from Yahoo Finance
- **`fetch_mstr_data.py`** - Fetches historical MicroStrategy stock price data
- **`parse_mstr_holdings.py`** - Parses MSTR Bitcoin purchase history

### Data Files
- **`btc_historical_data.json`** - Bitcoin daily price data (5 years)
- **`mstr_historical_data.json`** - MicroStrategy daily stock price data (5 years)
- **`mstr_btc_holdings.json`** - MicroStrategy Bitcoin purchase history and cumulative holdings

### Generated Charts
- **`btc_nav_premium_chart.png`** - Main scatter plot showing NAV Premium vs BTC Price
- **`btc_nav_premium_timeline.png`** - Time series showing BTC price and NAV Premium evolution

## Installation & Usage

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn jupyter
```

### Running the Analysis

#### Option 1: Run the standalone script
```bash
python run_analysis.py
```

This will generate both PNG charts and print summary statistics.

#### Option 2: Use the Jupyter Notebook
```bash
jupyter notebook btc_nav_premium_analysis.ipynb
```

This provides an interactive environment to explore the data and modify the analysis.

### Fetching Fresh Data

To update the data with the latest prices:
```bash
python fetch_btc_data.py
python fetch_mstr_data.py
python parse_mstr_holdings.py
```

Note: The `parse_mstr_holdings.py` script contains hardcoded purchase history that should be updated manually from [Strategy.com](https://www.strategy.com/purchases).

## Data Sources

1. **Bitcoin Price Data**: Yahoo Finance API (BTC-USD)
2. **MicroStrategy Stock Price**: Yahoo Finance API (MSTR)
3. **Bitcoin Holdings**: [Strategy.com](https://www.strategy.com/) - Official MicroStrategy Bitcoin tracker

## Methodology

The analysis uses the following approach:

1. **Data Collection**: Historical daily prices for both BTC and MSTR are fetched from Yahoo Finance covering the past 5 years.

2. **Holdings Tracking**: MicroStrategy's Bitcoin purchases are tracked from their first acquisition in August 2020 through November 2025, with cumulative holdings forward-filled between purchase dates.

3. **Shares Outstanding Estimation**: Since MSTR has been issuing shares to fund Bitcoin purchases, shares outstanding are estimated based on historical patterns:
   - 2020: ~165M shares
   - 2021: ~170M shares
   - 2022: ~180M shares
   - 2023: ~190M shares
   - 2024: ~220-280M shares
   - 2025: ~320M shares

4. **NAV Premium Calculation**: For each date, the NAV Premium is calculated by dividing market capitalization by the value of Bitcoin holdings.

5. **Visualization**: Data is plotted as a scatter chart with color-coded time progression, showing the relationship between BTC price and NAV Premium.

## Key Insights

1. **Premium Compression**: The NAV Premium has generally compressed from peaks above 4x in early 2021 to around 1.2x in late 2025, suggesting market maturation.

2. **Price Correlation**: There is a clear inverse relationship between BTC price and NAV Premium - as BTC price increases, the premium tends to decrease.

3. **Volatility**: The NAV Premium is highly volatile, ranging from 1.16x to 4.07x in the analyzed period, reflecting changing market sentiment toward MSTR as a Bitcoin proxy.

4. **Current State**: As of November 2025, MSTR trades near its historical low premium of 1.17x, suggesting either fair valuation or potential undervaluation compared to historical norms.

## Chart Interpretation

The main scatter plot shows:
- **X-axis**: Bitcoin price in USD
- **Y-axis**: NAV Premium (multiple)
- **Color gradient**: Time progression (blue = earlier dates, red = recent dates)
- **Green line**: Upper trend boundary
- **Orange line**: Lower trend boundary
- **Red dashed line**: 1.7x reference level

The clustering and trends reveal how market sentiment toward MSTR has evolved as Bitcoin price has changed over time.

## Limitations

1. **Shares Outstanding**: The analysis uses estimated shares outstanding rather than exact historical data, which may introduce minor inaccuracies.

2. **Simplified NAV**: The calculation focuses solely on Bitcoin holdings and doesn't account for MSTR's software business, debt, cash, or other assets.

3. **Market Hours**: Stock prices are only available during market hours, while Bitcoin trades 24/7, creating some temporal mismatches.

4. **Historical Data**: Yahoo Finance API provides limited historical data granularity for cryptocurrency prices.

## Future Enhancements

Potential improvements to this analysis:
- Incorporate MSTR's debt and cash positions for a more accurate NAV calculation
- Add MSTR's software business valuation
- Include options market data and implied volatility
- Analyze correlation with broader crypto market indices
- Add predictive modeling for NAV Premium trends

## License

This project is open source and available for educational and research purposes.

## Acknowledgments

- Data sourced from Yahoo Finance and Strategy.com
- Inspired by the original Strategy NAV Premium charts
- Built with Python, pandas, matplotlib, and seaborn

## Contact

For questions or suggestions, please open an issue in this repository.

---

**Disclaimer**: This analysis is for educational and informational purposes only. It does not constitute financial advice. Always conduct your own research before making investment decisions.
