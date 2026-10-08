# Axis

**A Python exploration of market data, technical signals, and charting.**

Axis processes Indian and US equity data using Heikin-Ashi candles and smoothed moving-average calculations. It generates experimental signals, visualizes price data with Plotly, and stores results as CSV files.

## Technical focus

- Retrieve historical market data with yfinance.
- Transform OHLC data into Heikin-Ashi values.
- Calculate exponential moving averages and derived trend signals.
- Generate charts and save analysis outputs for later inspection.

## Repository guide

| Path | Role |
| --- | --- |
| `indian.py` | Analysis workflow for Indian equities |
| `us.py` | Analysis workflow for US equities |
| `get_stocks.py` | Stock-list utilities |
| `DATA/` | Stored price data |
| `PREDICTIONS/` | Historical signal outputs |
| `templates/` | Web interface templates |

**Stack:** Python, pandas, NumPy, yfinance, Plotly, and supporting web and email utilities.

## Working with the project

The repository includes `requirements.txt`, historical data, and experimental scripts. Review the configured paths and output handling before running the analysis; the scripts include data-cleanup operations.

The saved outputs document an exploratory project. They do not establish predictive performance.

Built by [Arya Prabhu](https://github.com/WILDROP321).
