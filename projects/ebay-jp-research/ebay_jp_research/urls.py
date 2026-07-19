"""メルカリ／ヤフーフリマ／楽天ラクマの検索URLを生成する（F2-2）。"""

from urllib.parse import quote


def build_search_urls(keywords, templates):
    """キーワード文字列から3サイトの検索URLを生成して dict で返す。

    templates: {"mercari": "...{keyword}...", "yahoo_flea": ..., "rakuma": ...}
    """
    encoded = quote(keywords or "", safe="")
    urls = {}
    for site, template in templates.items():
        urls[site] = template.replace("{keyword}", encoded)
    return urls
