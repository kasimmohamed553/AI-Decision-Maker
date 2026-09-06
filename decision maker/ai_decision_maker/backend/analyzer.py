import re
import pandas as pd

# ------------------------------------------------------------------
# Alias tables: many different real-world header names map to the
# "role" the decision engine actually needs. This is what lets the
# analyzer accept ANY CSV, not just ones shaped like our own sample.
# ------------------------------------------------------------------
AMOUNT_ALIASES = [
    "order_amount", "amount", "amt", "sales", "sale", "revenue",
    "total", "total_amount", "total_sales", "net_amount", "gross_amount",
    "price", "unit_price", "value", "cost", "sale_amount", "amount_paid",
    "grand_total", "order_total", "payment", "transaction_amount",
]
PRODUCT_ALIASES = ["product", "item", "product_name", "item_name", "sku", "product_id"]
CATEGORY_ALIASES = ["category", "type", "product_category", "segment", "class"]
REGION_ALIASES = ["region", "location", "state", "city", "country", "area", "territory", "zone"]
DATE_ALIASES = ["order_date", "date", "transaction_date", "purchase_date", "created_at", "timestamp"]

# Column-name fragments that suggest an identifier column, which
# should never be auto-picked as the "amount" column even if numeric.
ID_LIKE_HINTS = ["id", "index", "code", "zip", "postal", "phone", "no.", "number", "#"]


def _normalize(col):
    """Lowercase, strip, collapse whitespace/punctuation to underscores."""
    return re.sub(r"[^a-z0-9]+", "_", str(col).strip().lower()).strip("_")


def _find_column(columns, normalized_map, aliases):
    """Return the original column name whose normalized form matches an alias."""
    for alias in aliases:
        for norm, original in normalized_map.items():
            if norm == alias:
                return original
    # loose/partial match as a second pass (e.g. "total_order_amount")
    for alias in aliases:
        for norm, original in normalized_map.items():
            if alias in norm:
                return original
    return None


def _best_numeric_fallback(df, exclude=None):
    """
    If no aliased 'amount' column exists, pick the most plausible
    numeric column in the file: highest non-null count, not ID-like.
    """
    exclude = exclude or set()
    candidates = []
    for col in df.columns:
        if col in exclude:
            continue
        norm = _normalize(col)
        if any(hint in norm for hint in ID_LIKE_HINTS):
            continue
        numeric = pd.to_numeric(df[col], errors="coerce")
        non_null = numeric.notna().sum()
        if non_null > 0:
            candidates.append((non_null, numeric.std(skipna=True) or 0, col))
    if not candidates:
        return None
    candidates.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return candidates[0][2]


def _read_any(filepath):
    if filepath.lower().endswith(".csv"):
        # sep=None + engine='python' auto-detects delimiter (comma, semicolon, tab, etc.)
        return pd.read_csv(filepath, sep=None, engine="python")
    return pd.read_excel(filepath)


def analyze_sales_data(filepath):
    """
    Reads ANY CSV/XLSX file and returns a best-effort summary dict.
    No specific column names are required. The analyzer auto-detects
    an amount-like numeric column plus optional Product/Category/
    Region/Date columns by common aliases, and gracefully skips any
    insight it can't build instead of rejecting the file.
    """
    df = _read_any(filepath)
    df.columns = [str(c).strip() for c in df.columns]

    if df.empty or len(df.columns) == 0:
        raise ValueError("The file appears to be empty or has no columns.")

    normalized_map = {_normalize(c): c for c in df.columns}

    amount_col = _find_column(df.columns, normalized_map, AMOUNT_ALIASES)
    used_fallback_amount = False
    if amount_col is None:
        amount_col = _best_numeric_fallback(df)
        used_fallback_amount = amount_col is not None

    if amount_col is None:
        raise ValueError(
            "Couldn't find any usable numeric column to analyze. "
            f"Found columns: {list(df.columns)}. "
            "Include at least one numeric column (e.g. an amount, price, or total)."
        )

    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
    df = df.dropna(subset=[amount_col])

    if df.empty:
        raise ValueError(f"No valid numeric data found in the '{amount_col}' column.")

    total_sales = float(df[amount_col].sum())
    avg_order_value = float(df[amount_col].mean())
    total_orders = int(len(df))
    max_order = float(df[amount_col].max())
    min_order = float(df[amount_col].min())

    product_col = _find_column(df.columns, normalized_map, PRODUCT_ALIASES)
    category_col = _find_column(df.columns, normalized_map, CATEGORY_ALIASES)
    region_col = _find_column(df.columns, normalized_map, REGION_ALIASES)
    date_col = _find_column(df.columns, normalized_map, DATE_ALIASES)

    detected = {
        "amount_column_used": amount_col,
        "amount_column_auto_detected": used_fallback_amount,
        "product_column_used": product_col,
        "category_column_used": category_col,
        "region_column_used": region_col,
        "date_column_used": date_col,
    }

    summary = {
        "total_sales": round(total_sales, 2),
        "average_order_value": round(avg_order_value, 2),
        "total_orders": total_orders,
        "max_order": round(max_order, 2),
        "min_order": round(min_order, 2),
        "detected_columns": detected,
    }

    if product_col:
        product_sales = df.groupby(product_col)[amount_col].sum().sort_values(ascending=False)
        if len(product_sales) > 0:
            summary["top_product"] = str(product_sales.index[0])
            summary["top_product_sales"] = round(float(product_sales.iloc[0]), 2)
            summary["product_breakdown"] = {
                str(k): round(float(v), 2) for k, v in product_sales.head(5).items()
            }

    if category_col:
        category_sales = df.groupby(category_col)[amount_col].sum().sort_values(ascending=False)
        if len(category_sales) > 0:
            summary["top_category"] = str(category_sales.index[0])
            summary["category_breakdown"] = {
                str(k): round(float(v), 2) for k, v in category_sales.items()
            }

    if region_col:
        region_sales = df.groupby(region_col)[amount_col].sum().sort_values(ascending=False)
        if len(region_sales) > 0:
            summary["top_region"] = str(region_sales.index[0])
            summary["region_breakdown"] = {
                str(k): round(float(v), 2) for k, v in region_sales.items()
            }

    if date_col:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            trend_df = df.dropna(subset=[date_col]).sort_values(date_col)
            if len(trend_df) >= 4:
                midpoint = len(trend_df) // 2
                first_half = trend_df.iloc[:midpoint][amount_col].sum()
                second_half = trend_df.iloc[midpoint:][amount_col].sum()
                if first_half > 0:
                    growth_pct = ((second_half - first_half) / first_half) * 100
                    summary["growth_rate_pct"] = round(float(growth_pct), 2)
        except Exception:
            pass  # trend analysis is best-effort, never fails the whole request

    return summary
