import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load the simulated portfolio data
portfolio_df = pd.read_csv('portfolio_simulation.csv')  # <-- Load saved simulation
portfolio_df['date'] = pd.to_datetime(portfolio_df['date'])  # convert dates


# 2. Calculate Daily Returns
portfolio_df['portfolio_daily_return'] = portfolio_df['portfolio_value'].pct_change()
portfolio_df['spx_only_daily_return'] = portfolio_df['spx_only_value'].pct_change()

# 3. Cumulative Returns
final_portfolio_return = (portfolio_df['portfolio_value'].iloc[-1] / portfolio_df['portfolio_value'].iloc[0]) - 1
final_spx_return = (portfolio_df['spx_only_value'].iloc[-1] / portfolio_df['spx_only_value'].iloc[0]) - 1

print(f"Tail Hedge Portfolio Cumulative Return: {final_portfolio_return:.2%}")
print(f"SPX Only Cumulative Return: {final_spx_return:.2%}")

# 4. Annualized Volatility
portfolio_volatility = portfolio_df['portfolio_daily_return'].std() * np.sqrt(252)
spx_volatility = portfolio_df['spx_only_daily_return'].std() * np.sqrt(252)

print(f"Tail Hedge Portfolio Annualized Volatility: {portfolio_volatility:.2%}")
print(f"SPX Only Annualized Volatility: {spx_volatility:.2%}")

# 5. Maximum Drawdown
def calculate_max_drawdown(series):
    cumulative_max = series.cummax()
    drawdown = (series - cumulative_max) / cumulative_max
    max_drawdown = drawdown.min()
    return max_drawdown

portfolio_max_drawdown = calculate_max_drawdown(portfolio_df['portfolio_value'])
spx_max_drawdown = calculate_max_drawdown(portfolio_df['spx_only_value'])

print(f"Tail Hedge Portfolio Maximum Drawdown: {portfolio_max_drawdown:.2%}")
print(f"SPX Only Maximum Drawdown: {spx_max_drawdown:.2%}")

# 6. Cost of Hedging
# (simple approximation: 1.5% per roll multiplied by number of rolls)

number_of_rolls = len(portfolio_df[portfolio_df['date'].isin(portfolio_df['date'][portfolio_df['date'].isin(portfolio_df['date']) & portfolio_df['portfolio_value'].notna()])])
approximate_total_cost_percentage = number_of_rolls * 0.015
approximate_total_cost_dollars = approximate_total_cost_percentage * 100

print(f"Approximate Hedging Cost: ${approximate_total_cost_dollars:.2f}")
print(f"Approximate Cost as % of Initial Portfolio: {approximate_total_cost_percentage:.2%}")

# 7. Crisis Period Performance (example: COVID Crash Feb 2020 to Apr 2020)
covid_start = pd.to_datetime('2020-02-01')
covid_end = pd.to_datetime('2020-04-30')

covid_data = portfolio_df[(portfolio_df['date'] >= covid_start) & (portfolio_df['date'] <= covid_end)]

covid_portfolio_return = (covid_data['portfolio_value'].iloc[-1] / covid_data['portfolio_value'].iloc[0]) - 1
covid_spx_return = (covid_data['spx_only_value'].iloc[-1] / covid_data['spx_only_value'].iloc[0]) - 1

print(f"Tail Hedge Portfolio Return During COVID Crash: {covid_portfolio_return:.2%}")
print(f"SPX Only Return During COVID Crash: {covid_spx_return:.2%}")



# 8. Plotting Cumulative Portfolio Value and SPX Benchmark
plt.figure(figsize=(14,7))
plt.plot(portfolio_df['date'], portfolio_df['portfolio_value'], label='Tail Hedge Portfolio', linewidth=2)
plt.plot(portfolio_df['date'], portfolio_df['spx_only_value'], label='SPX Only', linestyle='--')
plt.xlabel('Date')
plt.ylabel('Portfolio Value ($)')
plt.title('Tail Hedge Portfolio vs SPX Benchmark - Cumulative Value')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# 9. Plotting Drawdowns
portfolio_df['portfolio_cummax'] = portfolio_df['portfolio_value'].cummax()
portfolio_df['portfolio_drawdown'] = (portfolio_df['portfolio_value'] - portfolio_df['portfolio_cummax']) / portfolio_df['portfolio_cummax']

portfolio_df['spx_cummax'] = portfolio_df['spx_only_value'].cummax()
portfolio_df['spx_drawdown'] = (portfolio_df['spx_only_value'] - portfolio_df['spx_cummax']) / portfolio_df['spx_cummax']

plt.figure(figsize=(14,7))
plt.plot(portfolio_df['date'], portfolio_df['portfolio_drawdown'], label='Tail Hedge Drawdown', linewidth=2)
plt.plot(portfolio_df['date'], portfolio_df['spx_drawdown'], label='SPX Only Drawdown', linestyle='--')
plt.xlabel('Date')
plt.ylabel('Drawdown (%)')
plt.title('Drawdown Comparison: Tail Hedge vs SPX')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
