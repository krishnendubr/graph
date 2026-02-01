import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# 1. Load Data
# 'utf-8-sig' handles the BOM issue we found earlier
results_df = pd.read_csv('results.csv', encoding='utf-8-sig')
limits_df = pd.read_csv('limits.csv').set_index('param_name')

# 2. Setup Plot
params = results_df['param_name'].unique()
window_size = 50  # Show 50 points at a time
fig, axes = plt.subplots(len(params), 1, figsize=(12, 3 * len(params)), sharex=True)

# Handle case if there is only 1 parameter (makes axes iterable)
if len(params) == 1: axes = [axes]

# 3. Plot Loop
for ax, param in zip(axes, params):
    # Prepare data for this parameter
    data = results_df[results_df['param_name'] == param].reset_index(drop=True)
    lower = limits_df.loc[param, 'Lower OK']
    upper = limits_df.loc[param, 'Upper OK']

    # Plot Lines and Limits
    ax.plot(data.index, data['result'], marker='o', markersize=4)
    ax.axhline(upper, color='r', linestyle='--', alpha=0.5, label='Upper')
    ax.axhline(lower, color='g', linestyle='--', alpha=0.5, label='Lower')
    ax.fill_between(data.index, lower, upper, color='green', alpha=0.1)

    # Highlight Outliers
    outliers = data[(data['result'] < lower) | (data['result'] > upper)]
    ax.scatter(outliers.index, outliers['result'], color='red', zorder=5)

    ax.set_ylabel(param, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # Set initial view limit
    ax.set_xlim(0, window_size)

# 4. Configure X-Axis (Bottom plot only)
# Map the numeric index (0, 1, 2) back to 'uniquepart_id' strings
last_ax = axes[-1]
last_ax.set_xticks(data.index)
last_ax.set_xticklabels(data['uniquepart_id'], rotation=90)
last_ax.set_xlabel("Unique Part ID")

# 5. Add Slider for Scrolling
plt.subplots_adjust(bottom=0.2) # Make room for slider
ax_scroll = plt.axes([0.15, 0.05, 0.7, 0.03]) # [left, bottom, width, height]
slider = Slider(ax_scroll, 'Scroll', 0, len(data) - window_size, valinit=0, valstep=1)

def update(val):
    pos = slider.val
    for ax in axes:
        ax.set_xlim(pos, pos + window_size)
    fig.canvas.draw_idle()

slider.on_changed(update)

plt.show()