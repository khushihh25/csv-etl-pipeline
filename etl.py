import logging
import sqlite3

import pandas as pd

# ---- Settings ----
SOURCE_FILE = "messy_sales.csv"
DB_FILE = "sales.db"
TABLE = "sales"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("etl.log"),  # saves the log to etl.log
        logging.StreamHandler(),         # also shows it in the terminal
    ],
)
log = logging.getLogger(__name__)


def parse_date(text):
    """Try each known date format and return the first one that fits."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return pd.to_datetime(text, format=fmt)
        except ValueError:
            pass
    return pd.NaT


def extract(path):
    """Read the raw CSV into a DataFrame."""
    df = pd.read_csv(path)
    log.info("Extracted %d rows from %s", len(df), path)
    return df


def transform(df):
    """Clean the raw data: text, amounts, dates, quantities, duplicates."""
    df = df.copy()

    # Text columns
    df["customer_name"] = df["customer_name"].str.strip().str.title().fillna("Unknown")
    df["city"] = df["city"].str.strip().str.title()
    df["status"] = df["status"].str.strip().str.lower()

    # Amount: keep digits and dot only, then convert to a number
    df["amount"] = df["amount"].str.replace(r"[^\d.]", "", regex=True)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Dates: parse each value with its own format
    raw_dates = df["order_date"].str.strip()
    df["order_date"] = raw_dates.apply(parse_date)
    bad = df["order_date"].isna()
    if bad.any():
        log.warning("Could not parse these dates: %s", raw_dates[bad].tolist())

    # Quantity: zero or negative is invalid, so mark it as missing
    df.loc[df["quantity"] <= 0, "quantity"] = None

    # Duplicates: removed last, after the text has been standardised
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    log.info("Removed %d duplicate rows", before - len(df))

    log.info(
        "Missing amounts: %d | Missing quantities: %d",
        df["amount"].isna().sum(),
        df["quantity"].isna().sum(),
    )
    return df


def validate(df):
    """Stop the pipeline if the cleaned data breaks basic rules."""
    problems = []
    if not df["order_id"].is_unique:
        problems.append("duplicate order_id values")
    if df["order_date"].isna().any():
        problems.append("unparsed dates")
    if (df["amount"].dropna() < 0).any():
        problems.append("negative amounts")
    if problems:
        raise ValueError("Data quality check failed: " + ", ".join(problems))
    log.info("Data quality checks passed")


def load(df):
    """Write the clean table to SQLite and run a check query."""
    conn = sqlite3.connect(DB_FILE)
    try:
        df.to_sql(TABLE, conn, if_exists="replace", index=False)
        log.info("Loaded %d rows into table '%s'", len(df), TABLE)

        check = pd.read_sql(
            f"""
            SELECT city,
                   COUNT(*) AS orders,
                   SUM(amount) AS total_sales
            FROM {TABLE}
            WHERE status = 'delivered'
            GROUP BY city
            ORDER BY total_sales DESC
            """,
            conn,
        )
        print(check)
    finally:
        conn.close()


def main():
    raw = extract(SOURCE_FILE)
    clean = transform(raw)
    validate(clean)
    load(clean)


if __name__ == "__main__":
    main()

















# import sqlite3
# import pandas as pd
# pd.set_option("display.width", 200)
# pd.set_option("display.max_columns", None)
# df = pd.read_csv("messy_sales.csv") #extract
# # print(df) #transform
# # print()
# # print(df.info())
# # print()
# # print("Missing values per column:")
# # print(df.isna().sum())
# # print()
# # print("Duplicate rows: ", df.duplicated().sum())
# df["customer_name"] = df["customer_name"]. str.strip().str.title()
# df["customer_name"] = df["customer_name"].fillna("Unknown")
# df["city"] = df["city"].str.strip().str.title()
# df["status"] = df["status"].str.strip().str.lower()

# #amount
# df["amount"] = df["amount"].str.replace(r"[^\d.]", "", regex= True)
# df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
# # print(df)


# #date time
# df["order_date"] = pd.to_datetime(df["order_date"].str.strip(), format="mixed", dayfirst=True)
# # print(df)
# df.loc[df["quantity"]<= 0, "quantity"] = None
# df=df.drop_duplicates().reset_index(drop=True)
# print(df)
# print()
# print(df.info())
# print()
# #load
# conn = sqlite3.connect("sales.db")
# df.to_sql("sales", conn, if_exists="replace", index=False)

# check = pd.read_sql(
#     """
#     Select city, count(*) as orders, sum(amount) as total_sales
#      from sales
#       where status = 'delivered'
#        group by city
#         order by total_sales desc """, conn,
# )
# print(check)
# conn.close()