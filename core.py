"""Core logic: turn a flat sequence of numbers into OHLC candles."""

import pandas as pd


def numbers_to_ohlc(numbers, group_size, start_date=None, freq="D"):
    """
    Convert a flat list of numbers into an OHLC DataFrame.

    Each consecutive chunk of `group_size` numbers becomes one candle:
      Open  = first number in the chunk
      High  = max number in the chunk
      Low   = min number in the chunk
      Close = last number in the chunk

    A trailing chunk smaller than group_size is dropped (incomplete candle).

    Returns a DataFrame indexed by DatetimeIndex (needed by mplfinance),
    with columns Open, High, Low, Close.
    """
    if group_size < 1:
        raise ValueError("group_size باید حداقل ۱ باشد")

    numbers = [float(n) for n in numbers]
    n_candles = len(numbers) // group_size
    if n_candles == 0:
        raise ValueError(
            f"تعداد اعداد ({len(numbers)}) برای ساخت حتی یک کندل با اندازه {group_size} کافی نیست"
        )

    rows = []
    for i in range(n_candles):
        chunk = numbers[i * group_size:(i + 1) * group_size]
        rows.append({
            "Open": chunk[0],
            "High": max(chunk),
            "Low": min(chunk),
            "Close": chunk[-1],
        })

    df = pd.DataFrame(rows)

    if start_date is None:
        start_date = pd.Timestamp.today().normalize()
    df.index = pd.date_range(start=start_date, periods=len(df), freq=freq)
    df.index.name = "Date"

    return df


def load_numbers_from_file(path, column=None):
    """
    Load a flat sequence of numbers from a CSV or Excel file.

    If `column` is given, that column is used; otherwise the first
    numeric column found is used.
    """
    if str(path).lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    if column is not None:
        series = df[column]
    else:
        numeric_cols = df.select_dtypes(include="number").columns
        if len(numeric_cols) == 0:
            raise ValueError("هیچ ستون عددی در فایل پیدا نشد")
        series = df[numeric_cols[0]]

    return series.dropna().astype(float).tolist()


def parse_numbers_text(text):
    """Parse free-form text (comma / space / newline separated) into a list of floats."""
    import re
    tokens = re.split(r"[\s,;]+", text.strip())
    numbers = [float(t) for t in tokens if t != ""]
    if not numbers:
        raise ValueError("هیچ عددی وارد نشده است")
    return numbers
