import pandas as pd
import matplotlib.pyplot as plt

def load_file(filename):
    return pd.read_csv(filename, encoding='utf-8-sig', on_bad_lines='skip')

# 1. Load your data
results_df = load_file('results.csv')
limits_df = load_file('limits.csv')

# 2. Setup the "Complete" Visualization
parameters = limits_df['param_name'].unique()
num_params = len(parameters)

# Create a figure with a subplot for each parameter
fig, axes = plt.subplots(nrows=num_params, ncols=1, figsize=(12, 4 * num_params))

# If there is only one parameter, axes won't be a list, so we fix that
if num_params == 1:
    axes = [axes]

# 3. Plot each parameter
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
    ax.plot(range(len(data)), data['result'], marker='o', color='#007acc', label='Result', linewidth=1, markersize=3)
    
    # Set X-axis ticks with unique_part_id only on the last subplot
    if i == num_params - 1:
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels(data['uniquepart_id'].astype(str), rotation=90, ha='right', fontsize=8)
    else:
        ax.set_xticks([])  # Hide X-axis labels for non-bottom subplots
    
    # Add the OK Range (Green shade and Red/Green lines)
    ax.axhline(y=high, color='red', linestyle='--', alpha=0.6, label=f'Upper: {high}')
    ax.axhline(y=low, color='green', linestyle='--', alpha=0.6, label=f'Lower: {low}')
    ax.fill_between(range(len(data)), low, high, color='green', alpha=0.1)
    
    # Mark Out-of-Spec points in Red
    outliers = data[(data['result'] < low) | (data['result'] > high)]
    ax.scatter(outliers.index, outliers['result'], color='red', s=30, zorder=5, label='Out of Spec')
    
    # Labeling
    ax.set_ylabel(f"{param}\n({data['unit'].iloc[0] if 'unit' in data.columns else 'Value'})", fontweight='bold', rotation=0, ha='right', va='center', labelpad=80)
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.legend(loc='upper right', fontsize='x-small')

plt.xlabel("Unique Part ID")
plt.tight_layout()

# 4. Save and Show
plt.savefig('complete_process_graphs.png', dpi=300)
plt.show()