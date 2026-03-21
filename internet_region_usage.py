import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import numpy as np
import os

def lighten_color(color, amount=0.5):
    """
    Lightens the given color.
    amount=0 → original color
    amount=1 → white
    """
    c = mcolors.to_rgb(color)
    white = (1, 1, 1)
    return tuple((1 - amount) * c[i] + amount * white[i] for i in range(3))

# Read CSV
input = "data/share-of-individuals-using-the-internet.csv"
df = pd.read_csv(input)

geo_areas = [
    "Arab World",
    "Caribbean small states",
    "Central Europe and the Baltics",
    "East Asia & Pacific",
    "Europe & Central Asia",
    "Latin America & Caribbean",
    "Middle East & North Africa",
    "Pacific island small states",
    "South Asia",
    "Sub-Saharan Africa"
]

region_group = {
    "Arab World": "Middle East & North Africa",
    "Middle East & North Africa": "Middle East & North Africa",

    "Caribbean small states": "Americas",
    "Latin America & Caribbean": "Americas",

    "Central Europe and the Baltics": "Europe",
    "Europe & Central Asia": "Europe",

    "East Asia & Pacific": "Asia",
    "Pacific island small states": "Asia",
    "South Asia": "Asia",

    "Sub-Saharan Africa": "Africa"
}

# color palette by category 
color_map = {
    "Europe": "#4E79A7",               # muted blue
    "Americas": "#F28E2B",             # warm orange
    "Middle East & North Africa": "#E15759", # soft red
    "Asia": "#59A14F",                  # muted teal
    "Africa": "#AF7AA1"                 # soft purple
}

# get regions from dataset
df_regions = df[df["Entity"].isin(geo_areas)]

# assign regions into continents
df_regions['Region Group'] = df_regions['Entity'].map(region_group)

# Filter by latest year for region
latest_year = df_regions.groupby("Entity")["Year"].max().min()
df_latest = df_regions[df_regions["Year"] == latest_year]

# map color onto category
df_latest['Color'] = df_latest['Region Group'].map(color_map)

# --- Compute category order by max value ---
category_max = df_latest.groupby('Region Group')['Individuals using the Internet (% of population)'].max()
category_order = category_max.sort_values(ascending=False).index

# --- Sort within category ---
df_latest_sorted = pd.DataFrame()
for cat in category_order:
    cat_df = df_latest[df_latest['Region Group'] == cat].sort_values(
        'Individuals using the Internet (% of population)', ascending=False
    )
    df_latest_sorted = pd.concat([df_latest_sorted, cat_df])

# variables for plotting 
labels = df_latest_sorted['Entity']
values = df_latest_sorted['Individuals using the Internet (% of population)']
colors = df_latest_sorted['Color']

folder = "plots"

# --- Bar chart ---
plt.figure(figsize=(12,7))
bars = plt.bar(labels, values, color=colors)

plt.ylim(0, max(values)*1.15)
plt.xticks(rotation=45, ha='right')
plt.ylabel("Internet Usage (% of population)",fontsize=11, fontweight='semibold')
plt.xlabel("Region", fontsize=11, fontweight='semibold')
plt.title(f"Internet Usage by Region in {latest_year}", fontweight='bold', fontsize=14, pad=20)

handles = [plt.Rectangle((0,0),1,1,color=color) for color in color_map.values()]
plt.legend(handles, color_map.keys(), title="Region Group", title_fontsize = 11)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 1, f"{height:.1f}%", ha='center', va='bottom')

plt.tight_layout(pad=2)

filename = "internet_usage_bar.png"
os.makedirs(folder, exist_ok=True)
plt.savefig(os.path.join(folder, filename))
plt.close()


# --- Pie chart ---

# --- Inner circle data ---
group_values = df_latest_sorted.groupby('Region Group')[
    'Individuals using the Internet (% of population)'
].sum()

group_order = group_values.index.tolist()
group_colors = [color_map[g] for g in group_order]

# --- Outer circle data (MUST follow group order exactly) ---
outer_labels = []
outer_values = []
outer_colors = []

for group in group_order:

    group_df = df_latest_sorted[df_latest_sorted['Region Group'] == group]

    base_color = color_map[group]

    n = len(group_df)

    for i, (_, row) in enumerate(group_df.iterrows()):

        outer_labels.append(row['Entity'])
        outer_values.append(row['Individuals using the Internet (% of population)'])

        # progressively lighter shades within group
        if n == 1:
            amount = 0.35
        else:
            amount = 0.2 + (0.35 * i / (n - 1))

        lighter = lighten_color(base_color, amount)

        outer_colors.append(lighter)

# --- Plot ---
fig, ax = plt.subplots(figsize=(10, 8))

# Outer pie (regions)
ax.pie(
    outer_values,
    radius=1,
    labels=outer_labels,
    labeldistance=1.05,
    colors=outer_colors,
    wedgeprops=dict(width=0.3, edgecolor='white'),
    startangle=90,
    autopct='%1.1f%%',
    pctdistance=0.85
)

# Inner pie (groups)
ax.pie(
    group_values,
    radius=0.7,
    colors=group_colors,
    wedgeprops=dict(width=0.4, edgecolor='white'),
    startangle=90
)


# --- Create legend handles ---
handles = [plt.Rectangle((0,0),1,1,color=color_map[g]) for g in group_values.index]
leg = plt.legend(handles, group_values.index, title="Region Group", title_fontsize=11, 
           loc='upper center', bbox_to_anchor=(0.5, 0), labelspacing=1.2,
           ncol=len(group_values), frameon=False)

plt.tight_layout(pad=3)

plt.title(f"Internet Usage by Region in {latest_year}", y=0.98,fontweight='bold')

filename = "internet_usage_pie.png"
os.makedirs(folder, exist_ok=True)
plt.savefig(os.path.join(folder, filename))
plt.close()