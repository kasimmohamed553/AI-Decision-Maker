def generate_recommendations(summary):
    """Short, practical tips derived directly from the summary stats."""
    tips = []

    if summary.get("growth_rate_pct") is not None:
        if summary["growth_rate_pct"] < 0:
            tips.append("Investigate recent drop-off - check for seasonality, stockouts, or pricing changes.")
        else:
            tips.append("Growth is positive - consider locking in current suppliers/pricing before scaling up.")

    if summary.get("top_region"):
        tips.append(f"'{summary['top_region']}' is your strongest region - consider replicating what's working there elsewhere.")

    if summary.get("top_category"):
        tips.append(f"'{summary['top_category']}' is your best-performing category - feature it more prominently.")

    if summary.get("average_order_value", 0) < 500:
        tips.append("Average order value is low - consider bundling products or a minimum-order incentive.")

    if not tips:
        tips.append("Add more columns (Product, Category, Region, Order_Date) to your dataset for deeper insights.")

    return tips
