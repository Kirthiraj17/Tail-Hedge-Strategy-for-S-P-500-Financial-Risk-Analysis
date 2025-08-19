import pandas as pd
import numpy as np
from datetime import date, datetime

# 1. Load SPX index prices
spx = pd.read_csv(r'c:\Users\kirth\Downloads\spx_selected_option_daily_price_202502(in).csv')
spx['date'] = pd.to_datetime(spx['date'])
spx = spx[['date', 'closeprice']]

# 2. Load SPX options data
option_prices = pd.read_csv(r'c:\Users\kirth\Downloads\spx_selected_option_daily_price_202502(in).csv')
option_info = pd.read_csv(r'c:\Users\kirth\Downloads\spx_selected_option_202502(in).csv')

option_prices['date'] = pd.to_datetime(option_prices['date'])
option_info['expiration_date'] = pd.to_datetime(option_info['expiration_date'])

print("Data Loaded Successfully")
# 1. Define your Roll Day helper functions

def get_month_nth_weekday(year, month, week, day):
    target_date = date(year, month, (week - 1) * 7 + 1)
    temp = target_date.weekday()
    if temp != day:
        target_date = target_date.replace(day=(week - 1) * 7 + 1 + (day - temp) % 7)
    return target_date

def get_target_date_masterdates(masterdates, target_date):
    i = 0
    while target_date >= masterdates[i]:
        i += 1
        if i > len(masterdates) - 1:
            return datetime.strptime('2040-12-31', '%Y-%m-%d').date()
    return masterdates[i - 1]

# 2. Get available expirations
masterdates = option_info['expiration_date'].sort_values().to_list()

# 3. Generate real Roll Dates
roll_dates = []
start_year = 2008
end_year = 2025

for year in range(start_year, end_year + 1):
    for month in [3, 6, 9, 12]:  # Quarterly
        try:
            third_friday = get_month_nth_weekday(year, month, 3, 4)  # 3rd Friday
            roll_day = third_friday - pd.Timedelta(days=1)  # Roll 1 day before
            adjusted_roll_day = get_target_date_masterdates(masterdates, roll_day)
            roll_dates.append(adjusted_roll_day)
        except:
            pass

roll_dates = pd.to_datetime(roll_dates)
print(" Roll Dates Generated Successfully")
# 1. Portfolio Setup
initial_cash = 100
start_date = pd.to_datetime('2008-03-31')
spx_start_price = spx.loc[spx['date'] == start_date, 'closeprice'].values[0]
spx_units = initial_cash / spx_start_price
portfolio_value = initial_cash

option_positions = {}  # dictionary to store active options
portfolio_history = []

# 2. Helper function to find real option to buy
def find_target_put_option(current_date):
    """Find the best -10% OTM PUT option to hedge."""
    target_expiry = current_date + pd.DateOffset(months=3)
    expiries = option_info['expiration_date']
    expiry = expiries[np.abs(expiries - target_expiry).idxmin()]
    
    spx_today = spx[spx['date'] == current_date]['closeprice'].values[0]
    target_strike = spx_today * 0.9  # -10% OTM strike
    
    options_on_expiry = option_info[option_info['expiration_date'] == expiry]
    chosen_option = options_on_expiry.iloc[(options_on_expiry['strike_price'] - target_strike).abs().argsort()[:1]]
    
    option_id = chosen_option['option_id'].values[0]
    return option_id

# 3. Daily simulation loop
for idx, row in spx.iterrows():
    today = row['date']
    spx_price = row['closeprice']
    
    # If today is a roll date
    if today in roll_dates:
        # Find new put option
        option_id = find_target_put_option(today)
        
        # Get today's option mid_price
        today_option_price = option_prices[
            (option_prices['option_id'] == option_id) &
            (option_prices['date'] == today)
        ]['mid_price'].values
        
        if len(today_option_price) == 0:
            today_option_price = 0
        else:
            today_option_price = today_option_price[0]
        
        # Spend 1.5% of portfolio value to buy puts
        budget_per_leg = 0.005 * portfolio_value
        units = budget_per_leg / today_option_price if today_option_price > 0 else 0
        
        option_positions = {
            'option_id': option_id,
            'purchase_date': today,
            'units': units,
            'purchase_price': today_option_price
        }
    
    # Calculate portfolio value daily
    spx_position_value = spx_units * spx_price
    option_position_value = 0
    
    if option_positions:
        current_option_price = option_prices[
            (option_prices['option_id'] == option_positions['option_id']) &
            (option_prices['date'] == today)
        ]['mid_price'].values
        if len(current_option_price) > 0:
            current_option_price = current_option_price[0]
            option_position_value = option_positions['units'] * current_option_price
    
    portfolio_value = spx_position_value + option_position_value
    
    portfolio_history.append({
        'date': today,
        'portfolio_value': portfolio_value,
        'spx_price': spx_price
    })

# 4. Save the simulation results
portfolio_df = pd.DataFrame(portfolio_history)
portfolio_df['spx_only_value'] = portfolio_df['spx_price'] / portfolio_df['spx_price'].iloc[0] * initial_cash

portfolio_df.to_csv('portfolio_real_simulation.csv', index=False)
print("✅ Portfolio Simulation with Real Option Prices Saved!")
# Load real simulation
portfolio_df = pd.read_csv('portfolio_real_simulation.csv')
portfolio_df['date'] = pd.to_datetime(portfolio_df['date'])

# Then same Stage 4 analysis (returns, volatility, drawdown, plots!)
