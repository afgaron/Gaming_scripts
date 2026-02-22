import matplotlib.pyplot as plt
import pandas as pd


def load_file(tmnt_bool: bool) -> pd.DataFrame:
    filename = "MTG Turtles.xlsx"
    df1 = pd.read_excel(filename, sheet_name="All Cards", usecols="A:E")

    if tmnt_bool:
        df2 = pd.read_excel(filename, sheet_name="TMNT", usecols="A:E")
        return pd.concat([df1, df2])

    else:
        return df1


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    # Add count column
    count = {"no": 1, "yes": 2, "foil only": 1}
    df["count"] = df["Foil?"].map(count)

    # Aggregate by release date
    daily_df = df.groupby("Released").sum("count")

    # Create initial value on game's release
    start = pd.DataFrame([["1993-08-05", 0]], columns=["Released", "count"])
    start["Released"] = pd.to_datetime(start["Released"])
    start = start.groupby("Released").sum("count")

    # Combine the data and sort it
    daily_df = pd.concat([daily_df, start])
    daily_df.sort_values("Released", inplace=True)
    daily_df["cumulative"] = daily_df["count"].cumsum()

    return daily_df


def plot_data(df: pd.DataFrame) -> None:
    plt.plot(df["cumulative"])
    plt.xlabel("Release date")
    plt.ylabel("Number of unique cards")
    plt.title("Cumulative number of unique turtle cards printed")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    tmnt = input("Include TMNT? (y)es/(N)o: ")
    tmnt_bool = tmnt.upper() == "Y"

    df = load_file(tmnt_bool)
    df = prepare_data(df)
    plot_data(df)
