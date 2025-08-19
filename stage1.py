# ─── Stage 1: Understand and Measure Tail Risk ───

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# 1. Load SPX data
# IMPORTANT: Make sure spx.csv is saved correctly
# Corrected path format
spx = pd.read_csv(r'C:\Users\kirth\Downloads\spx(in).csv')  # <-- correct path

# 2. Clean and prepare
spx['date'] = pd.to_datetime(spx['date'], errors='coerce')  # parse dates safely
spx = spx.sort_values('date')
spx['closeprice'] = pd.to_numeric(spx['closeprice'], errors='coerce')  # parse prices safely
spx = spx[['date', 'closeprice']].dropna()

# 3. Calculate daily returns
spx['daily_return'] = spx['closeprice'].pct_change()

# 4. Historical VaR (5% level)
historical_var_5pct = spx['daily_return'].quantile(0.05)
print(f"Historical VaR at 5% level: {historical_var_5pct:.4f}")

# 5. Variance-Covariance VaR (assuming normal distribution)
mean_return = spx['daily_return'].mean()
std_return = spx['daily_return'].std()
z_score_5pct = stats.norm.ppf(0.05)  # z = -1.645
var_cov_var_5pct = mean_return + z_score_5pct * std_return
print(f"Variance-Covariance VaR at 5% level: {var_cov_var_5pct:.4f}")

# 6. Expected Shortfall (Conditional VaR)
expected_shortfall_5pct = spx[spx['daily_return'] <= historical_var_5pct]['daily_return'].mean()
print(f"Expected Shortfall at 5%: {expected_shortfall_5pct:.4f}")

# 7. Identify Tail Events
spx['is_tail_event'] = spx['daily_return'] < historical_var_5pct

# 8. Segment by Time Periods
conditions = [
    (spx['date'] < '2009-06-01'),  # Financial Crisis
    (spx['date'] >= '2009-06-01') & (spx['date'] < '2020-02-01'),  # Post Crisis Recovery
    (spx['date'] >= '2020-02-01') & (spx['date'] < '2020-08-01'),  # COVID Crash
    (spx['date'] >= '2020-08-01')  # Post COVID Recovery
]
choices = ['Financial Crisis', 'Post Crisis Recovery', 'COVID Crash', 'Post COVID Recovery']

spx['period'] = np.select(conditions, choices, default='Other')

# 9. Tail Events Count per Period
tail_events_count = spx[spx['is_tail_event']].groupby('period').size()
print("\nTail events by period:")
print(tail_events_count)

# 10. OPTIONAL: Plot Daily Returns Distribution
plt.figure(figsize=(10,6))
plt.hist(spx['daily_return'].dropna(), bins=100, edgecolor='k', alpha=0.7)
plt.axvline(historical_var_5pct, color='r', linestyle='--', label=f'Historical VaR 5%: {historical_var_5pct:.2%}')
plt.title('Distribution of SPX Daily Returns')
plt.xlabel('Daily Return')
plt.ylabel('Frequency')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
