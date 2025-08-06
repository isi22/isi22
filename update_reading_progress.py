import os
import re
import math
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import calendar

# --- Configuration and Scrape function (unchanged) ---
# ... (The first half of the code remains the same) ...
GOODREADS_USER_ID = os.environ.get("GOODREADS_USER_ID")
SHELF_NAME = "read"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def scrape_goodreads_profile(user_id, shelf_name):
    """
    Scrapes the 'read' shelf from a public Goodreads user profile page.
    """
    if not user_id:
        print("Error: GOODREADS_USER_ID environment variable not set.")
        return []

    base_url = f"https://www.goodreads.com/review/list/{user_id}"
    all_books = []
    page = 1
    print(f"Starting scrape for Goodreads user ID: {user_id}...")

    while True:
        url = f"{base_url}?page={page}&shelf={shelf_name}&sort=date_read"
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during scraping: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        book_rows = soup.find_all("tr", class_="bookalike review")
        if not book_rows:
            print(f"Finished scraping. Found a total of {len(all_books)} books.")
            break

        for row in book_rows:
            print(row)
            title_elem = row.select_one("td.title a")
            date_read_elem = row.select_one("td.date_read span.date_read_value")
            pages_elem = row.select_one("td.num_pages div")

            if all([title_elem, date_read_elem, pages_elem]):
                page_count_text = pages_elem.text.strip()
                page_count = (
                    int(re.search(r"\d+", page_count_text).group())
                    if re.search(r"\d+", page_count_text)
                    else 0
                )
                all_books.append(
                    {
                        "title": title_elem.get("title", "").strip(),
                        "dateRead": date_read_elem.text.strip(),
                        "pageCount": page_count,
                    }
                )

        print(f"Scraped page {page}. Found {len(book_rows)} books on this page.")
        page += 1

    return all_books


def create_and_save_plot(books_read):
    """
    Generates and saves a plot of cumulative pages read over time.
    """
    if not books_read:
        print("No books found to process. Exiting.")
        return

    # Process data with pandas
    df = pd.DataFrame(books_read)
    df["dateRead"] = pd.to_datetime(df["dateRead"], format="%b %d, %Y", errors="coerce")
    df.dropna(subset=["dateRead"], inplace=True)
    df.sort_values(by="dateRead", inplace=True)
    df["cumulativePages"] = df["pageCount"].cumsum()

    # Add data points for the start of the year and the current date
    current_year = datetime.now().year
    start_of_year = pd.to_datetime(f"{current_year}-01-01")

    start_data = pd.DataFrame([{"dateRead": start_of_year, "cumulativePages": 0}])
    today_data = pd.DataFrame(
        [
            {
                "dateRead": pd.to_datetime("today").normalize(),
                "cumulativePages": df["cumulativePages"].max() or 0,
            }
        ]
    )

    df = pd.concat([start_data, df, today_data], ignore_index=True)

    print("\nProcessed data for plotting:")
    print(df[["dateRead", "cumulativePages"]].tail())

    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 3))
    ax.plot(
        df["dateRead"],
        df["cumulativePages"],
        drawstyle="steps-post",
        color="#007acc",
        linewidth=2,
    )

    # Configure plot aesthetics
    max_y_lim = math.ceil((df["cumulativePages"].max() or 1) / 1000) * 1000
    ax.set_ylim(-0.10 * max_y_lim, max_y_lim)

    today = datetime.now()
    _, last_day = calendar.monthrange(today.year, today.month)
    end_of_current_month = datetime(today.year, today.month, last_day)
    ax.set_xlim(
        start_of_year, end_of_current_month + timedelta(days=1)
    )  # Add a day to include the full end of month

    # --- NEW: Manually calculate and set centered labels ---
    month_midpoints = []
    month_labels = []

    # Get the start of each month and the start of the next month
    month_starts = pd.to_datetime(
        pd.date_range(
            start=f"{current_year}-01-01", end=end_of_current_month, freq="MS"
        )
    )

    # Calculate the midpoint and label for each month
    for i in range(len(month_starts) - 1):
        start = month_starts[i]
        end = month_starts[i + 1]
        midpoint = start + (end - start) / 2
        month_midpoints.append(midpoint)
        month_labels.append(start.strftime("%b %Y"))

    # Set the tick locations and labels
    ax.set_xticks(month_midpoints)
    ax.set_xticklabels(month_labels, ha="center", va="top", rotation=0)

    # --- Dotted gridlines at the start of each month (from the previous attempt) ---
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.grid(which="minor", axis="x", linestyle=":", color="#e0e0e0", linewidth=0.5)

    # Clean up axes
    ax.tick_params(axis="x", which="both", length=0, colors="#66a9d9")
    ax.tick_params(axis="y", which="both", length=0, colors="#66a9d9")

    # Add cumulative page count annotation
    last_cumulative_pages = df["cumulativePages"].max()
    ax.annotate(
        f"Total Pages Read: {last_cumulative_pages:,}",
        xy=(today_data["dateRead"].iloc[-1], last_cumulative_pages),
        xytext=(0, 10),
        textcoords="offset points",
        ha="right",
        va="bottom",
        fontsize=12,
        color="#66a9d9",
    )

    # Set up grid and remove spines
    ax.grid(
        True, which="both", axis="y", linestyle="--", linewidth=0.5, color="#e0e0e0"
    )
    ax.spines[["top", "right", "bottom", "left"]].set_visible(False)
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    plt.tight_layout()
    plt.savefig("reading_progress.png", dpi=300, transparent=True)
    print("Plot saved to reading_progress.png")


# --- Main execution block (unchanged) ---
if __name__ == "__main__":
    books_read = scrape_goodreads_profile(GOODREADS_USER_ID, SHELF_NAME)
    if books_read:
        create_and_save_plot(books_read)
