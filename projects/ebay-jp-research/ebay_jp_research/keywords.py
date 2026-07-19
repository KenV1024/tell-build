"""商品タイトルから国内フリマ用の検索キーワードを生成する（F2-1）。"""

import re

# 型番らしいトークン（英字+数字の組み合わせ、またはハイフン付き）を検出
_MODEL_RE = re.compile(r"^(?=.*\d)[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
# 単語分割: 英数字・ハイフン・スラッシュを許容
_TOKEN_RE = re.compile(r"[A-Za-z0-9\-/]+", re.UNICODE)


def extract_model_numbers(title):
    """タイトルから型番らしいトークンを抽出して返す。"""
    models = []
    for token in _TOKEN_RE.findall(title or ""):
        if _MODEL_RE.match(token) and any(c.isdigit() for c in token) and any(c.isalpha() for c in token):
            if token not in models:
                models.append(token)
    return models


def generate_keywords(title, stopwords=None, max_keywords=6):
    """タイトルから不要語を除いた検索キーワード文字列を生成する。

    - 不要語(stopwords)を除去
    - 型番は保持
    - 元の語順を維持しつつ重複を除去
    - 最大 max_keywords 語まで
    """
    if not title:
        return ""

    stop = {w.lower() for w in (stopwords or [])}
    result = []
    seen = set()

    for raw in _TOKEN_RE.findall(title):
        token = raw.strip("-/")
        if not token:
            continue
        low = token.lower()
        if low in stop:
            continue
        # 記号だけ・1文字の無意味な語は除外（数字1桁や型番は残す）
        if len(token) == 1 and not token.isdigit():
            continue
        if low in seen:
            continue
        seen.add(low)
        result.append(token)
        if len(result) >= max_keywords:
            break

    return " ".join(result)
