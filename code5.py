import pandas as pd
import matplotlib.pyplot as plt

# ------------------------
# Load CSV files
# ------------------------
# Use 'utf-8-sig' to handle hidden BOM characters in the first column
results_df = pd.read_csv("results.csv", encoding="utf-8-sig")
limits_df  = pd.read_csv("limits.csv")

# ------------------------
# Clean data
# ------------------------
# Standardize column names: remove whitespace and lowercase
results_df.columns = results_df.columns.str.strip().str.lower()
limits_df.columns  = limits_df.columns.str.strip()

# Check for existence before dropping (Safety check)
required_cols = ["uniquepart_id", "param_name", "result"]
for col in required_cols:
    if col not in results_df.columns:
        print(f"Error: Could not find column '{col}'")
        print(f"Available columns: {results_df.columns.tolist()}")
        exit()

results_df = results_df.dropna(subset=required_cols)


# Aggregate (1 value per part + parameter)
results_df = (
    results_df
    .groupby(["uniquepart_id", "param_name"], as_index=False)
    .agg({"result": "mean"})
)

# Convert uniquepart_id to string for proper categorical x-axis
results_df["uniquepart_id"] = results_df["uniquepart_id"].astype(str)

# ------------------------
# Parameter order (top → bottom)
# ------------------------
params = limits_df["Parameter"].tolist()
lane_height = 100
y_offset = {p: i * lane_height for i, p in enumerate(params)}

# ------------------------
# Plot
# ------------------------
fig, ax = plt.subplots(figsize=(18, 7))

for param in params:
    data = results_df[results_df["param_name"] == param]
    if data.empty:
        continue

    data = data.sort_values("uniquepart_id").reset_index(drop=True)
    x_labels = data["uniquepart_id"].values
    x_positions = list(range(len(x_labels)))
    y0 = y_offset[param]
    y = data["result"] + y0

    # Actual line
    ax.plot(x_positions, y, marker="o", linewidth=2, color="navy")

    # Limits
    lim = limits_df[limits_df["Parameter"] == param]
    lower = lim["Lower OK"].values[0]
    upper = lim["Upper OK"].values[0]

    # OK band
    ax.fill_between(x_positions, y0 + lower, y0 + upper, color="lightgreen", alpha=0.3)

    # Limit lines
    ax.hlines(y0 + lower, x_positions[0] - 0.5, x_positions[-1] + 0.5,
              colors="black", linestyles="dashed", linewidth=1)
    ax.hlines(y0 + upper, x_positions[0] - 0.5, x_positions[-1] + 0.5,
              colors="black", linestyles="dashed", linewidth=1)

    # Out-of-spec points
    out_mask = (data["result"] < lower) | (data["result"] > upper)
    out_positions = [x_positions[i] for i in data[out_mask].index]
    ax.scatter(out_positions,
               data[out_mask]["result"] + y0,
               color="red", s=30, zorder=5)

# ------------------------
# Axis formatting
# ------------------------
ax.set_xlabel("Unique Part ID")
ax.set_ylabel("Plasma Parameters")

ax.set_yticks([y_offset[p] for p in params])
ax.set_yticklabels(params)
# Set x-axis to show unique part IDs
unique_parts = sorted(results_df["uniquepart_id"].unique())
x_tick_positions = range(len(unique_parts))
ax.set_xticks(x_tick_positions)
ax.set_xticklabels(unique_parts, rotation=90)


ax.tick_params(axis="x", rotation=90)
ax.grid(axis="x", linestyle=":", alpha=0.4)

plt.tight_layout()
plt.savefig("plasma_process_overview.png", dpi=300)
plt.show()
