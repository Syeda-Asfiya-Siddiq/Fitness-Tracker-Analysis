import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# 1. AESTHETICS & CONFIGURATION
# ==============================================================================
sns.set_theme(style="whitegrid")
PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"]
GENDER_P = {"Male": "#4C72B0", "Female": "#DD8452"}

plt.rcParams.update({
    "figure.facecolor": "#F8F9FA",
    "axes.facecolor":    "#F8F9FA",
    "axes.edgecolor":    "#CCCCCC",
    "grid.color":        "#E0E0E0",
    "font.family":       "DejaVu Sans",
    "axes.titlesize":    13,
    "axes.labelsize":    11,
})

# ==============================================================================
# 2. LOAD & CLEAN DATA
# ==============================================================================
DATA_PATH = "gym_members_exercise_tracking_synthetic_data.csv"

try:
    df = pd.read_csv(DATA_PATH, skipinitialspace=True)
except FileNotFoundError:
    print(f"Error: {DATA_PATH} not found. Please ensure the file is in the directory.")
    exit()

# Strip whitespace and clean escape characters from strings
df.columns = df.columns.str.strip()
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].astype(str).str.strip().str.replace(r"[\t\n]", "", regex=True)
    df[col] = df[col].replace({"nan": np.nan, "": np.nan})

# Coerce numeric columns safely
num_cols = [
    "Age", "Weight (kg)", "Height (m)", "Max_BPM", "Avg_BPM",
    "Resting_BPM", "Session_Duration (hours)", "Calories_Burned",
    "Fat_Percentage", "Water_Intake (liters)",
    "Workout_Frequency (days/week)", "Experience_Level", "BMI"
]
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Drop rows missing critical analytical data
df.dropna(subset=["Age", "Calories_Burned"], inplace=True)

# Dataset Summary
print("=" * 60)
print("  DATASET OVERVIEW")
print("=" * 60)
print(f"  Shape            : {df.shape[0]} rows × {df.shape[1]} columns")
print(f"  Numeric columns : {df.select_dtypes(include='number').shape[1]}")
print(f"  Missing values  : {df.isnull().sum().sum()}")
print("=" * 60)

# Helper function to save plots
def save_plot(fig, name):
    fig.savefig(name, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"  ✔ Saved → {name}")

# ==============================================================================
# 3. EXPLORATORY DATA ANALYSIS (GRAPHS 1-10)
# ==============================================================================

# G1: Age Distribution
fig, ax = plt.subplots(figsize=(9, 5))
sns.histplot(df["Age"].dropna(), bins=20, kde=True, color="#4C72B0", edgecolor="white", ax=ax)
ax.axvline(df["Age"].mean(), color="#C44E52", linestyle="--", label=f"Mean: {df['Age'].mean():.1f}")
ax.set_title("Graph 1 – Age Distribution of Gym Members", fontweight="bold")
ax.legend()
save_plot(fig, "graph1_age_distribution.png")

# G2: Workout Type Frequency
wt_counts = df["Workout_Type"].value_counts().dropna()
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(wt_counts.index, wt_counts.values, color=PALETTE, edgecolor="white", width=0.6)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
            str(int(bar.get_height())), ha="center", va="bottom", fontweight="bold")
ax.set_title("Graph 2 – Workout Type Frequency", fontweight="bold")
save_plot(fig, "graph2_workout_type_distribution.png")

# G3: Calories vs Duration (Scatter)
fig, ax = plt.subplots(figsize=(9, 6))
sns.scatterplot(data=df, x="Session_Duration (hours)", y="Calories_Burned", hue="Gender", palette=GENDER_P, alpha=0.55, ax=ax)
m, b = np.polyfit(df["Session_Duration (hours)"], df["Calories_Burned"], 1)
ax.plot(df["Session_Duration (hours)"], m*df["Session_Duration (hours)"] + b, color="#2d2d2d", linestyle="--", label="Trend")
ax.set_title("Graph 3 – Calories Burned vs Session Duration", fontweight="bold")
save_plot(fig, "graph3_calories_vs_duration.png")

# G4: Calories by Workout Type (Boxplot)
fig, ax = plt.subplots(figsize=(9, 5))
order = df.groupby("Workout_Type")["Calories_Burned"].median().sort_values(ascending=False).index
sns.boxplot(data=df, x="Workout_Type", y="Calories_Burned", order=order, palette=PALETTE, ax=ax)
ax.set_title("Graph 4 – Calories Burned Distribution by Workout Type", fontweight="bold")
save_plot(fig, "graph4_calories_by_workout.png")

# G5: BMI by Gender (Violin)
fig, ax = plt.subplots(figsize=(8, 5))
sns.violinplot(data=df, x="Gender", y="BMI", palette=GENDER_P, inner="quartile", ax=ax)
ax.axhline(18.5, color="#55A868", linestyle=":", label="Underweight")
ax.axhline(25.0, color="#DD8452", linestyle=":", label="Overweight")
ax.axhline(30.0, color="#C44E52", linestyle=":", label="Obese")
ax.set_title("Graph 5 – BMI Distribution by Gender", fontweight="bold")
ax.legend(fontsize=9, loc='upper right')
save_plot(fig, "graph5_bmi_by_gender.png")

# G6: Heart-Rate by Experience (Grouped Bar)
hr_agg = df.groupby("Experience_Level")[["Avg_BPM", "Resting_BPM", "Max_BPM"]].mean()
fig, ax = plt.subplots(figsize=(9, 5))
hr_agg.plot(kind='bar', ax=ax, color=PALETTE, edgecolor="white", width=0.8)
ax.set_title("Graph 6 – Heart-Rate Profile by Experience Level", fontweight="bold")
ax.set_xticklabels([f"Level {int(i)}" for i in hr_agg.index], rotation=0)
save_plot(fig, "graph6_heart_rate_by_experience.png")

# G7: Fat % vs BMI (Colored by Workout)
fig, ax = plt.subplots(figsize=(9, 6))
sns.scatterplot(data=df, x="BMI", y="Fat_Percentage", hue="Workout_Type", palette=PALETTE, alpha=0.55, ax=ax)
ax.set_title("Graph 7 – Body Fat % vs BMI (by Workout Type)", fontweight="bold")
save_plot(fig, "graph7_fat_vs_bmi.png")

# G8: Workout Frequency vs Calories (Line)
fig, ax = plt.subplots(figsize=(9, 5))
sns.lineplot(data=df, x="Workout_Frequency (days/week)", y="Calories_Burned", marker="o", color="#4C72B0", ax=ax)
ax.set_title("Graph 8 – Workout Frequency vs Average Calories Burned", fontweight="bold")
save_plot(fig, "graph8_frequency_vs_calories.png")

# G9: Correlation Heatmap
fig, ax = plt.subplots(figsize=(11, 9))
corr = df[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Graph 9 – Correlation Heatmap of Fitness Metrics", fontweight="bold")
save_plot(fig, "graph9_correlation_heatmap.png")

# G10: Water Intake vs Calories (Bubble Chart)
fig, ax = plt.subplots(figsize=(9, 6))
for g, color in GENDER_P.items():
    sub = df[df["Gender"] == g]
    ax.scatter(sub["Water_Intake (liters)"], sub["Calories_Burned"], 
               s=sub["Session_Duration (hours)"] * 100, alpha=0.45, color=color, label=g)
ax.set_title("Graph 10 – Water Intake vs Calories (Bubble Size = Duration)", fontweight="bold")
ax.legend(title="Gender", loc='upper right')
save_plot(fig, "graph10_water_vs_calories_bubble.png")

plt.close('all')
print("\n All 10 graphs saved successfully!")
