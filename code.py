import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Load Excel files
# =========================
results = pd.read_excel("results.xlsx")
limits = pd.read_excel("limits.xlsx")

# =========================
# Clean column names
# =========================
results.columns = results.columns.str.strip().str.lower()
limits.columns = limits.columns.str.strip()

# Rename for consistency
results.rename(columns={"param_name": "parameter"}, inplace=True)

# =========================
# Basic cleaning
# =========================
results = results.dropna(subset=["uniquepart_id", "parameter", "result"])

results["uniquepart_id"] = results["uniquepart_id"].astype(str)
results["result"] = pd.to_numeric(results["result"], errors="coerce")

# =========================
# Aggregate:
# one value per part + parameter
# =========================
results_clean = (
    results
    .groupby(["uniquepart_id", "parameter"], as_index=False)
    .agg({"result": "mean"})
)

# =========================
# Parameter order (Y lanes)
# =========================
params = [
    "Plasma Pressure",
    "Plasma Voltage",
    "Plasma Frequency",
    "Plasma Current",
    "Plasma WorkingHours",
    "Plasma RecipeActual"
]

lane_height = 100
param_y = {p: i * lane_height for i, p in enumerate(params)}

# =========================
# Plot
# =========================
fig, ax = plt.subplots(figsize=(18, 7))

for param in params:
    data_p = results_clean[results_clean["parameter"] == param]
    if data_p.empty:
        continue

    data_p = data_p.sort_values("uniquepart_id")
    y0 = param_y[param]

    x = data_p["uniquepart_id"]
    y = data_p["result"] + y0

    # ---- Actual line ----
    ax.plot(
        x, y,
        marker="o",
        linewidth=2,
        color="navy"
    )

    # ---- Limits ----
    lim = limits[limits["Parameter"] == param]
    if not lim.empty:
        lower = lim["Lower OK"].values[0]
        upper = lim["Upper OK"].values[0]

        # OK band (shaded area)
        ax.fill_between(
            x,
            y0 + lower,
            y0 + upper,
            color="lightgray",
            alpha=0.3
        )

        # Lower limit line
        ax.hlines(
            y=y0 + lower,
            xmin=x.iloc[0],
            xmax=x.iloc[-1],
            colors="black",
            linestyles="dashed",
            linewidth=1
        )

        # Upper limit line
        ax.hlines(
            y=y0 + upper,
            xmin=x.iloc[0],
            xmax=x.iloc[-1],
            colors="black",
            linestyles="dashed",
            linewidth=1
        )

# =========================
# Axis formatting
# =========================
ax.set_xlabel("Unique Part ID")
ax.set_ylabel("Plasma Parameters")

ax.set_yticks([param_y[p] for p in params])
ax.set_yticklabels(params)

ax.tick_params(axis="x", rotation=90)
ax.grid(axis="x", linestyle=":", alpha=0.3)

plt.tight_layout()
plt.show()
