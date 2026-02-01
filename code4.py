import pandas as pd
import matplotlib.pyplot as plt

# ------------------------
# Load CSV files
# ------------------------
results_df = pd.read_csv("results.csv", encoding="ISO-8859-1")
limits_df  = pd.read_csv("limits.csv")

# ------------------------
# Clean data
# ------------------------
results_df.columns = results_df.columns.str.strip().str.lower()
limits_df.columns  = limits_df.columns.str.strip()

results_df = results_df.dropna(subset=["uniquepart_id", "param_name", "result"])
results_df["uniquepart_id"] = results_df["uniquepart_id"].astype(str)
results_df["result"] = pd.to_numeric(results_df["result"], errors="coerce")

# Aggregate (1 value per part + parameter)
results_df = (
    results_df
    .groupby(["uniquepart_id", "param_name"], as_index=False)
    .agg({"result": "mean"})
)

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

    data = data.sort_values("uniquepart_id")
    x = data["uniquepart_id"]
    y0 = y_offset[param]
    y = data["result"] + y0

    # Actual line
    ax.plot(x, y, marker="o", linewidth=2, color="navy")

    # Limits
    lim = limits_df[limits_df["Parameter"] == param]
    lower = lim["Lower OK"].values[0]
    upper = lim["Upper OK"].values[0]

    # OK band
    ax.fill_between(x, y0 + lower, y0 + upper, color="lightgreen", alpha=0.3)

    # Limit lines
    ax.hlines(y0 + lower, x.iloc[0], x.iloc[-1],
              colors="black", linestyles="dashed", linewidth=1)
    ax.hlines(y0 + upper, x.iloc[0], x.iloc[-1],
              colors="black", linestyles="dashed", linewidth=1)

    # Out-of-spec points
    out = data[(data["result"] < lower) | (data["result"] > upper)]
    ax.scatter(out["uniquepart_id"],
               out["result"] + y0,
               color="red", s=30, zorder=5)

# ------------------------
# Axis formatting
# ------------------------
ax.set_xlabel("Unique Part ID")
ax.set_ylabel("Plasma Parameters")

ax.set_yticks([y_offset[p] for p in params])
ax.set_yticklabels(params)

ax.tick_params(axis="x", rotation=90)
ax.grid(axis="x", linestyle=":", alpha=0.4)

plt.tight_layout()
plt.savefig("plasma_process_overview.png", dpi=300)
plt.show()
