# Messy CSV to SQLite ETL Pipeline

A Python pipeline that takes a messy sales CSV, cleans it with pandas, checks the data quality, and loads it into a SQLite database.

## Problems it fixes
- Extra spaces and inconsistent capitalisation in names, cities and status
- Amounts written as `1,200` or `Rs 2500`
- Three different date formats in one column
- Invalid (negative) quantities
- Missing values
- Duplicate rows

## Pipeline
1. **Extract:** read the CSV with pandas
2. **Transform:** clean text, amounts, dates and quantities, and remove duplicates
3. **Validate:** stop the pipeline if IDs are duplicated or dates cannot be parsed
4. **Load:** write the clean table to SQLite and run a check query

## Project structure
```
csv_etl/
├── make_data.py       # creates the messy practice CSV
├── etl.py             # the ETL pipeline
├── messy_sales.csv    # sample input
├── requirements.txt
└── README.md
```

## How to run
```
pip install -r requirements.txt
python make_data.py
python etl.py
```

## Sample output
```
INFO | Extracted 10 rows from messy_sales.csv
INFO | Removed 1 duplicate rows
INFO | Missing amounts: 2 | Missing quantities: 1
INFO | Data quality checks passed
INFO | Loaded 9 rows into table 'sales'

        city  orders  total_sales
0  Bengaluru       2       5700.0
1      Delhi       2       2400.0
2     Mumbai       1        950.0
3    Kolkata       1        780.0
```

## Design decisions
- **Invalid quantities** (zero or negative) are set to missing instead of guessed.
- **Missing amounts** are left empty so totals are not distorted.
- **Dates** are parsed with explicit formats instead of letting pandas guess, so `07-01-2026` is never read as 1 July.
- **Duplicates** are removed after text cleaning, so `Rahul Sharma` and `rahul sharma` match.

## If the pipeline runs twice
The table is replaced on each run, so no duplicate rows are created.

## Tech
Python, pandas, SQLite, logging