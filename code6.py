# --- ESSENTIAL FOR INTERACTIVITY ---
import matplotlib widget
# -----------------------------------

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import sys

# clean up previous plots to prevent lag/duplication
plt.close('all') 

def load_file(filename):
    try:
        return pd.read_csv(filename, encoding='utf-8-sig', on_bad_lines='skip')
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return pd.DataFrame() # Return empty to prevent crash

# 1. Load your data
results_df = load_file('results.csv')
limits_df = load_file('limits.csv')

# Check if data loaded correctly before proceeding
if not results_df.empty and not limits_df.empty:

    # 2. Setup the "Complete" Visualization
    parameters = limits_df['param_name'].unique()
    num_params = len(parameters)

    # Determine which unique_part_id values are out of spec for any parameter
    results_with_limits = results_df.merge(
        limits_df[['param_name', 'Lower OK', 'Upper OK']],
        on='param_name',
        how='left'
    )
    results_with_limits['out_of_spec'] = (
        (results_with_limits['result'] < results_with_limits['Lower OK']) |
        (results_with_limits['result'] > results_with_limits['Upper OK'])
    )
    out_of_spec_parts = set(
        results_with_limits.loc[results_with_limits['out_of_spec'], 'uniquepart_id']
        .dropna()
        .astype(str)
        .tolist()
    )

    # Get first parameter to determine data length
    first_param = parameters[0]
    first_data = results_df[results_df['param_name'] == first_param].copy()
    data_length = len(first_data)

    # Calculate figure width
    cm_per_point = 1  
    inch_per_point = cm_per_point / 2.54 
    total_width = data_length * inch_per_point
    display_width = 15  
    window_size = max(1, int(display_width / inch_per_point))

    # Create figure
    fig_height = 2.0 * num_params 
    fig = plt.figure(figsize=(display_width, fig_height))

    # Create axes for each parameter
    axes = []
    for i in range(num_params):
        ax = fig.add_subplot(num_params, 1, i + 1)
        axes.append(ax)

    # Plot each parameter
    for i, param in enumerate(parameters):
        ax = axes[i]
        
        # Filter data for this specific parameter
        data = results_df[results_df['param_name'] == param].copy()
        if data.empty:
            ax.set_title(f"No data found for {param}")
            continue
        
        # Get limits
        low = limits_df.loc[limits_df['param_name'] == param, 'Lower OK'].values[0]
        high = limits_df.loc[limits_df['param_name'] == param, 'Upper OK'].values[0]
        
        # Sort data sequentially
        data = data.reset_index(drop=True)
        
        # Plot the trend line
        ax.plot(range(len(data)), data['result'], marker='o', color='#007acc', label='Result', linewidth=1, markersize=4)
        
        # Add the OK Range (Green shade and Red/Green lines)
        ax.axhline(y=high, color='red', linestyle='--', alpha=0.6, label=f'Upper: {high}')
        ax.axhline(y=low, color='green', linestyle='--', alpha=0.6, label=f'Lower: {low}')
        ax.fill_between(range(len(data)), low, high, color='green', alpha=0.1)
        
        # Mark Out-of-Spec points in Red
        outliers = data[(data['result'] < low) | (data['result'] > high)]
        ax.scatter(outliers.index, outliers['result'], color='red', s=15, zorder=5, label='Out of Limit')
        
        # Set X-axis ticks with unique_part_id only on the last subplot
        if i == num_params - 1:
            tick_positions = list(range(0, len(data)))
            tick_labels = [
                str(data['uniquepart_id'].iloc[j]) if j < len(data) else ''
                for j in tick_positions
            ]
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=90, fontsize=8)
            for label in ax.get_xticklabels():
                if label.get_text() in out_of_spec_parts:
                    label.set_color('red')
            ax.set_xlabel("Unique Part ID")
        else:
            ax.set_xticklabels([])
        
        # Labeling
        unit = data['unit'].iloc[0] if 'unit' in data.columns else "Value"
        ax.set_ylabel(f"{param}\n({unit})", fontweight='bold', fontsize=7)
        ax.grid(True, linestyle=':', alpha=0.5)
        # Move legend out to prevent overlapping data
        ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize='x-small', frameon=False)
        
        # Set initial X-axis limits
        ax.set_xlim(0, min(len(data), window_size))

    # Adjust layout
    # Increased bottom margin to give scrollbar room
    plt.subplots_adjust(left=0.05, right=0.90, top=0.95, bottom=0.20, hspace=0.1)

    # Add horizontal scrollbar
    ax_scroll = plt.axes([0.1, 0.05, 0.8, 0.03]) # Adjusted position [left, bottom, width, height]
    max_scroll = max(0, data_length - window_size)
    
    # Define slider
    slider = Slider(
        ax_scroll,
        'Scroll',
        0,
        max_scroll,
        valinit=0,
        valstep=1,
        color='steelblue'
    )

    def update_scroll(val):
        scroll_pos = slider.val
        for ax in axes:
            ax.set_xlim(scroll_pos, scroll_pos + window_size)
        fig.canvas.draw_idle()

    slider.on_changed(update_scroll)

    plt.show()

else:
    print("Could not load data. Please check 'results.csv' and 'limits.csv'.")