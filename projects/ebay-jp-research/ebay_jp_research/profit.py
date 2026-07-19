"""利益額・利益率の計算と候補判定（F3）。"""


def to_jpy(amount, currency, rates):
    """通貨建て金額を円換算する。レート未定義なら (None, 警告) を返す。"""
    if amount is None:
        return None, None
    rate = rates.get(currency)
    if rate is None:
        return None, f"通貨 '{currency}' の為替レートが未設定のため利益計算をスキップしました。"
    return amount * rate, None


def compute_profit(row, config):
    """1行分の利益計算を行い、計算結果を dict で返す。

    仕入値(estimated_cost_jpy)が無い行は profit 系を None で返す（未入力扱い）。
    利益率 = 利益 / 売上(円)。
    """
    fees = config["fees"]
    rates = config["exchange"]["rates"]
    threshold = config["profit"]["threshold_rate"]

    result = {
        "sold_price_jpy": None,
        "ebay_fee_jpy": None,
        "payment_fee_jpy": None,
        "intl_shipping_jpy": fees["international_shipping_jpy"],
        "profit_jpy": None,
        "profit_rate": None,
        "is_candidate": False,
        "warning": None,
    }

    revenue_jpy, warn = to_jpy(row.get("sold_price"), row.get("currency", "USD"), rates)
    if warn:
        result["warning"] = warn
    result["sold_price_jpy"] = revenue_jpy

    cost = row.get("estimated_cost_jpy")
    if revenue_jpy is None or cost is None:
        # 売価が取れない、または仕入値が未入力 → 利益は計算しない
        return result

    ebay_fee = revenue_jpy * fees["ebay_final_value_fee_rate"]
    payment_fee = revenue_jpy * fees["payment_processing_fee_rate"]
    intl_shipping = fees["international_shipping_jpy"]
    profit = revenue_jpy - ebay_fee - payment_fee - intl_shipping - cost
    profit_rate = profit / revenue_jpy if revenue_jpy else 0.0

    result.update({
        "ebay_fee_jpy": round(ebay_fee, 2),
        "payment_fee_jpy": round(payment_fee, 2),
        "profit_jpy": round(profit, 2),
        "profit_rate": round(profit_rate, 4),
        "is_candidate": profit_rate >= threshold,
    })
    return result
