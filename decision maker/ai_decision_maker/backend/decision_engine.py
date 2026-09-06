"""
Rule-based Decision Engine
--------------------------
This makes business decisions from the analyzed summary using a
transparent, self-contained scoring system - no external AI API,
no API keys, no rate limits, no internet dependency.

The engine scores several signals (growth, order value, order volume,
concentration risk) into a single confidence score from -100 to +100,
then maps that score onto a verdict: EXPAND / MAINTAIN / REDUCE,
along with the human-readable reasoning behind it.
"""


def _score_growth(summary):
    growth = summary.get("growth_rate_pct")
    reasons = []
    if growth is None:
        return 0, reasons

    if growth >= 20:
        reasons.append(f"Strong sales growth of {growth}% between the first and second half of the period.")
        return 35, reasons
    elif growth >= 5:
        reasons.append(f"Healthy positive growth of {growth}%.")
        return 20, reasons
    elif growth >= -5:
        reasons.append(f"Sales are roughly flat ({growth}% change).")
        return 0, reasons
    elif growth >= -20:
        reasons.append(f"Sales are declining moderately ({growth}%).")
        return -20, reasons
    else:
        reasons.append(f"Sales are declining sharply ({growth}%).")
        return -35, reasons


def _score_order_value(summary):
    avg = summary.get("average_order_value", 0)
    reasons = []
    if avg >= 2000:
        reasons.append(f"Average order value is high (${avg:,.2f}), indicating strong customer spend.")
        return 15, reasons
    elif avg >= 500:
        reasons.append(f"Average order value is moderate (${avg:,.2f}).")
        return 5, reasons
    else:
        reasons.append(f"Average order value is low (${avg:,.2f}), which may limit margins.")
        return -10, reasons


def _score_volume(summary):
    orders = summary.get("total_orders", 0)
    reasons = []
    if orders >= 500:
        reasons.append(f"High order volume ({orders} orders) shows strong demand.")
        return 15, reasons
    elif orders >= 50:
        reasons.append(f"Moderate order volume ({orders} orders).")
        return 5, reasons
    else:
        reasons.append(f"Low order volume ({orders} orders) - dataset may be too small for a confident call.")
        return -5, reasons


def _score_concentration(summary):
    """Penalize over-reliance on a single product (concentration risk)."""
    breakdown = summary.get("product_breakdown")
    total = summary.get("total_sales", 0)
    reasons = []
    if not breakdown or total <= 0:
        return 0, reasons

    top_value = max(breakdown.values())
    share = top_value / total

    if share >= 0.6:
        reasons.append(
            f"Over {share*100:.0f}% of sales come from a single product - high concentration risk."
        )
        return -15, reasons
    elif share >= 0.4:
        reasons.append(f"A single product drives {share*100:.0f}% of sales - moderate concentration.")
        return -5, reasons
    else:
        reasons.append("Sales are reasonably diversified across products.")
        return 5, reasons


def _verdict_from_score(score):
    if score >= 30:
        return "EXPAND", "go"
    elif score >= -10:
        return "MAINTAIN", "caution"
    else:
        return "REDUCE", "stop"


def generate_ai_decision(summary):
    """
    Takes the summary dict produced by analyzer.py and returns a
    structured decision. This is entirely self-contained - it never
    calls out to any external service.
    """
    try:
        score = 0
        reasons = []

        for scorer in (_score_growth, _score_order_value, _score_volume, _score_concentration):
            points, r = scorer(summary)
            score += points
            reasons.extend(r)

        score = max(-100, min(100, score))
        verdict, signal = _verdict_from_score(score)

        confidence = min(100, abs(score) + 40)  # baseline confidence, scaled by signal strength

        action_map = {
            "EXPAND": "Consider increasing inventory, marketing spend, or expanding into top-performing regions/products.",
            "MAINTAIN": "Hold current strategy steady while monitoring the metrics driving this score.",
            "REDUCE": "Consider cutting underperforming lines, reducing spend, or reassessing pricing and product mix.",
        }

        top_driver = None
        if summary.get("top_product"):
            top_driver = f"Top product: {summary['top_product']} (${summary.get('top_product_sales', 0):,.2f})"

        return {
            "status": "success",
            "engine": "rule-based",
            "verdict": verdict,
            "signal": signal,          # "go" | "caution" | "stop" - drives the frontend decision meter
            "confidence": round(confidence, 1),
            "score": score,            # -100 to +100
            "reasons": reasons,
            "recommended_action": action_map[verdict],
            "top_driver": top_driver,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
