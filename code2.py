import pandas as pd
import matplotlib.pyplot as plt
import os

def load_data(file_name):
    """Robustly loads data whether it is a true Excel file or a CSV."""
    try:
        # Check the extension
        if file_name.lower().endswith('.xlsx'):
            # Try reading as a true Excel file first
            try:
                return pd.read_excel(file_name)
            except Exception:
                # If that fails, it might be a CSV renamed to .xlsx
                # 'ISO-8859-1' fixes the UnicodeDecodeError you encountered
                return pd.read_csv(file_name, encoding='ISO-8859-1', on_bad_lines='skip')
        else:
            return pd.read_csv(file_name, encoding='ISO-8859-1', on_bad_lines='skip')
    except Exception as e:
        print(f"Could not load {file_name}: {e}")
        return None

# 1. Load the data
results_df = load_data('results.xlsx')
limits_df = load_data('limits.xlsx')

if results_df is not None and limits_df is not None:
    # Clean limits data
    limits_df = limits_df.dropna(subset=['Parameter'])

    def create_control_chart(param_name):
        # Filter results
        data = results_df[results_df['param_name'] == param_name].copy()
        if data.empty:
            return
        
        # Get limits
        limit_row = limits_df[limits_df['Parameter'] == param_name]
        if limit_row.empty:
            return
            
        lower = limit_row['Lower OK'].values[0]
        upper = limit_row['Upper OK'].values[0]
        unit = data['unit'].iloc[0] if 'unit' in data.columns else ""
        
        # Sort by ID
        if 'uniquepart_id' in data.columns:
            data = data.sort_values('uniquepart_id').reset_index(drop=True)
        else:
            data = data.reset_index(drop=True)
        
        plt.figure(figsize=(10, 5))
        
        # Plot
        plt.plot(data.index, data['result'], marker='o', linestyle='-', color='#007acc', 
                 label='Actual Value', linewidth=1, markersize=4)
        
        plt.axhline(y=upper, color='#e74c3c', linestyle='--', label=f'Upper Limit ({upper})')
        plt.axhline(y=lower, color='#2ecc71', linestyle='--', label=f'Lower Limit ({lower})')
        plt.fill_between(range(len(data)), lower, upper, color='#2ecc71', alpha=0.1, label='OK Zone')
        
        outliers = data[(data['result'] < lower) | (data['result'] > upper)]
        plt.scatter(outliers.index, outliers['result'], color='#c0392b', s=40, zorder=5, label='Out of Spec')

        plt.title(f'Process Control Chart: {param_name}', fontsize=12, fontweight='bold')
        plt.xlabel('Sample Sequence', fontsize=10)
        plt.ylabel(f'Value ({unit})', fontsize=10)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend(loc='upper right', fontsize='small')
        
        plt.tight_layout()
        plt.show()

    # Generate charts
    for parameter in limits_df['Parameter'].unique():
        print(f"Generating chart for {parameter}...")
        create_control_chart(parameter)
else:
    print("Failed to initialize dataframes. Please check your file paths and formats.")