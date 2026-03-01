import pandas as pd
import matplotlib.pyplot as plt
import math
import os

def load_data(filename): 
    df = pd.read_csv(filename)
    # target index
    df = df.set_index("country")
    
    return df


def compute_growth(row):
    values = row.dropna()
    values = values[values > 0]

    if len(values) < 2:
        return None

    return values.iloc[-1] - values.iloc[0]


# Find highest, lowest, median, US, and fastest growing countries
def get_special_countries(df):
    growth = df.apply(compute_growth, axis=1)
    growth = growth.dropna()

    # Sort growth
    growth_sorted = growth.sort_values()

    # Select countries
    slowest = growth_sorted.index[0]
    median = growth_sorted.index[len(growth_sorted)//2]
    fastest = growth_sorted.index[-1]
    us = "United States"

    countries = [slowest, median, fastest, us]

    print("Slowest growth:", slowest)
    print("Median growth:", median)
    print("Fastest growth:", fastest)
    print("United States:", us)

    return countries


# plot selected countries for trends
def plot_countries(df, countries):
    plt.figure(figsize=(10, 7))
    plt.suptitle(
        "Cell Phone Adoption Over Time: Comparing Slowest, Median, Fastest Growth, and US",
        fontsize=14,
        fontweight='bold'
    )

    # convert columns to integers for easier manipulation later
    years = df.columns.astype(int)

    # dynamically allocating even spaced ticks based on last year in dataset 
    # Find first >0 values year for each special country
    first_years = []
    for country in countries:
        if country in df.index:
            nonzero = df.loc[country][df.loc[country] > 0]
            if len(nonzero) > 0:
                first_years.append(int(nonzero.index[0]))

    # determine the first year of data
    earliest_data = min(first_years) if first_years else years.min()
    
    # Set tick step
    step = 5
    max_year = years.max()  # rightmost tick
    # Calculate min_year so that it is <= earliest_data and aligns with step counting back from max_year
    n_steps = (max_year - earliest_data) // step + 1
    min_year = max_year - n_steps * step
    if min_year < years.min():
        min_year = years.min()

    # mask to plot only years within this range
    mask = (years >= min_year) & (years <= max_year)
    plot_years = years[mask]

    color_map = {
        countries[0]: "#ff7f0e",  # slowest
        countries[1]: "#1f77b4",  # median
        countries[2]: "#2ca02c",  # fastest
        countries[3]: "#d62728"   # United States as relevant baseline
    }

    plt.xlim(min_year, max_year)
    data_subset = df.loc[countries, mask].ffill(axis=1)

    # snap y axis to nearest 50 multiple
    raw_y_max = data_subset.max().max()
    y_max = math.ceil(raw_y_max / 50) * 50
    plt.ylim(-10, y_max)

    # Plot each country
    for country in countries:
        if country in df.index:
            data = df.loc[country][mask].copy()
            # fill forward missing values to extend line to the end
            data = data.ffill()
            plt.plot(plot_years, data, label=country, color=color_map[country])
            # plot country names at end of plot line and outside box
            plt.text(plot_years[-1] + 0.2, data.iloc[-1], country,
                 color=color_map[country], fontsize=12, fontweight=500, va='center', ha='left')

    plt.xlabel("Year", fontsize=12, fontweight='semibold',)
    plt.ylabel("Cell Phones per 100 People", fontsize=12, fontweight='semibold',)
    
    # generate ticks counting down from max_year to min_year
    ticks = list(range(max_year, min_year - 1, -step))
    plt.xticks(ticks, rotation=45)

    plt.tight_layout()

    folder = "plots"
    filename = "cell_phone_country_comparison.png"
    os.makedirs(folder, exist_ok=True)
    plt.savefig(os.path.join(folder, filename))
    print("Saved plot to cell_phone_comparison.png")


def main():
    filename = "data/cell_phones_per_100_people.csv"
    df = load_data(filename)
    countries = get_special_countries(df)
    
    plot_countries(df, countries)


if __name__ == "__main__":
    main()