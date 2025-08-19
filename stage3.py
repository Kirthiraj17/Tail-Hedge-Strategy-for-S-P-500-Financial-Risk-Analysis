# ─── Stage 3: Implement Tail Hedge Strategy ───

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load SPX Data
spx = pd.read_csv(r'C:\Users\kirth\Downloads\spx(in).csv')
spx['date'] = pd.to_datetime(spx['date'])
spx = spx.sort_values('date')
spx['closeprice'] = pd.to_numeric(spx['closeprice'], errors='coerce')
spx = spx[['date', 'closeprice']].dropna()

# 2. Set Initial Portfolio
start_date = pd.to_datetime('2008-03-31')
initial_cash = 100
spx_start_price = spx.loc[spx['date'] == start_date, 'closeprice'].values[0]

spx_units = initial_cash / spx_start_price  # initial SPX units
portfolio_value = initial_cash
option_positions = {}

portfolio = {
    'cash': 0,
    'spx_units': spx_units,
    'option_positions': option_positions,
}

# 3. Find Roll Dates (same as Stage 2)
def third_friday(year, month):
    first_day = pd.Timestamp(year=year, month=month, day=1)
    fridays = pd.date_range(start=first_day, end=first_day + pd.offsets.MonthEnd(0), freq='W-FRI')
    return fridays[2]

roll_months = pd.date_range(start='2008-03-01', end='2025-02-28', freq='3MS')
roll_dates = []

for dt in roll_months:
    third_fri = third_friday(dt.year, dt.month)
    roll_day = third_fri - pd.Timedelta(days=1)
    roll_dates.append(roll_day)

roll_dates = pd.to_datetime(roll_dates)

# 4. Define Rolling Function
def roll_options(current_date, portfolio_value):
    """Simulate buying 3 SPX put options for protection."""
    budget_per_leg = 0.005 * portfolio_value
    option_positions = {}
    
    for leg in ['leg_1', 'leg_2', 'leg_3']:
        dummy_option_price = 2  # Use flat $2 for testing
        units = budget_per_leg / dummy_option_price
        
        option_positions[leg] = {
            'price': dummy_option_price,
            'units': units,
            'initial_price': dummy_option_price,
            'roll_date': current_date
        }
    
    return option_positions

# 5. Define Portfolio Value Update
def calculate_portfolio_value(spx_price, option_positions):
    """Calculate today's portfolio value."""
    total_value = spx_units * spx_price  # SPX value
    
    for leg, pos in option_positions.items():
        # Option decay: assume slow price decay by 1% every day after roll
        days_passed = (today - pos['roll_date']).days
        decay_factor = 0.99 ** days_passed
        today_option_price = max(0.5, pos['initial_price'] * decay_factor)  # Never fall below $0.5
        
        total_value += pos['units'] * today_option_price
    
    return total_value

# 6. Simulation: Loop through Each Day
portfolio_history = []

for idx, row in spx.iterrows():
    today = row['date']
    spx_price = row['closeprice']
    
    # Roll if today is a roll date
    if today in roll_dates:
        option_positions = roll_options(today, portfolio_value)
        print(f"Rolled Options on: {today.date()}")
    
    # Update daily portfolio value
    portfolio_value = calculate_portfolio_value(spx_price, option_positions)
    
    portfolio_history.append({
        'date': today,
        'portfolio_value': portfolio_value,
        'spx_price': spx_price
    })

# 7. Save Results
portfolio_df = pd.DataFrame(portfolio_history)
portfolio_df = portfolio_df.sort_values('date')

# 8. Add SPX Benchmark
portfolio_df['spx_only_value'] = portfolio_df['spx_price'] / portfolio_df['spx_price'].iloc[0] * initial_cash

# 9. Plot Portfolio Value vs SPX Benchmark
plt.figure(figsize=(14,7))
plt.plot(portfolio_df['date'], portfolio_df['portfolio_value'], label='Tail Hedge Portfolio', linewidth=2)
plt.plot(portfolio_df['date'], portfolio_df['spx_only_value'], label='SPX Only', linestyle='--')
plt.xlabel('Date')
plt.ylabel('Portfolio Value ($)')
plt.title('Tail Hedge Portfolio vs SPX Benchmark')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
# Save the simulation output
portfolio_df.to_csv('portfolio_simulation.csv', index=False)
print("Portfolio simulation saved to portfolio_simulation.csv")
