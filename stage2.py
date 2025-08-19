# ─── Stage 2: Build Tail Hedge Strategy ───

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load SPX daily data (reuse your Stage 1 cleaned file)
spx = pd.read_csv(r'C:\Users\kirth\Downloads\spx(in).csv')
spx['date'] = pd.to_datetime(spx['date'])
spx = spx.sort_values('date')
spx['closeprice'] = pd.to_numeric(spx['closeprice'], errors='coerce')
spx = spx[['date', 'closeprice']].dropna()

# 2. Setup initial Portfolio

start_date = pd.to_datetime('2008-03-31')
initial_cash = 100  # Start with $100
spx_start_price = spx.loc[spx['date'] == start_date, 'closeprice'].values[0]

# How many SPX units we can buy initially
spx_units = initial_cash / spx_start_price

# Portfolio dictionary
portfolio = {
    'cash': 0,
    'spx_units': spx_units,
    'option_positions': {},  # Will fill later
}

print(f"Initial SPX units purchased: {spx_units:.4f}")

# 3. Find Rolling Dates (one day before third Friday every 3 months)

def third_friday(year, month):
    """Return the 3rd Friday of a given month."""
    first_day = pd.Timestamp(year=year, month=month, day=1)
    fridays = pd.date_range(start=first_day, end=first_day + pd.offsets.MonthEnd(0), freq='W-FRI')
    return fridays[2]

# Generate roll dates
roll_months = pd.date_range(start='2008-03-01', end='2025-02-28', freq='3MS')  # every 3 months start
roll_dates = []

for dt in roll_months:
    third_fri = third_friday(dt.year, dt.month)
    roll_day = third_fri - pd.Timedelta(days=1)  # roll 1 day before
    roll_dates.append(roll_day)

roll_dates = pd.to_datetime(roll_dates)
print("\nRoll Dates Sample:")
print(roll_dates[:5])  # Show first 5 roll dates

# 4. Define Rolling Function for Buying New Options

def roll_options(current_date, portfolio_value):
    """Simulate buying 3 SPX put options for protection."""
    budget_per_leg = 0.005 * portfolio_value  # 0.5% of portfolio per leg
    option_positions = {}
    
    for leg in ['leg_1', 'leg_2', 'leg_3']:
        # In real strategy: find nearest -0.1 delta option
        # Here for mockup: assume dummy option price like $2
        
        dummy_option_price = 2  # Assume simple flat $2 cost per put option
        
        units = budget_per_leg / dummy_option_price
        
        option_positions[leg] = {
            'price': dummy_option_price,
            'units': units,
            'initial_price': dummy_option_price,
            'roll_date': current_date
        }
        
    return option_positions

# 5. Daily Portfolio Value Update Function

def calculate_portfolio_value(spx_price, option_positions):
    """Calculate total portfolio value today."""
    total_value = spx_units * spx_price  # SPX position
    
    for leg, pos in option_positions.items():
        # Assume option price decays slowly
        today_option_price = max(0.5, pos['initial_price'] * 0.95)  # decay by 5% as mock
        
        total_value += pos['units'] * today_option_price
    
    return total_value

# 6. Simulate Daily Portfolio Value

portfolio_history = []

option_positions = {}
portfolio_value = initial_cash

for idx, row in spx.iterrows():
    today = row['date']
    spx_price = row['closeprice']
    
    # Roll if today matches a roll date
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

# 8. Plot Portfolio vs SPX Only

portfolio_df['spx_only_value'] = portfolio_df['spx_price'] / portfolio_df['spx_price'].iloc[0] * initial_cash

plt.figure(figsize=(14,7))
plt.plot(portfolio_df['date'], portfolio_df['portfolio_value'], label='Tail Hedge Portfolio', linewidth=2)
plt.plot(portfolio_df['date'], portfolio_df['spx_only_value'], label='SPX Only', linestyle='--')
plt.xlabel('Date')
plt.ylabel('Portfolio Value')
plt.title('Tail Hedge Portfolio vs SPX Only')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

