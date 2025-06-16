# 仮の既存記事データ（article_id: キーワードリスト）
existing_articles = {
    "001": ["猫", "夏目漱石", "吾輩"],
    "002": ["犬", "村上春樹", "走ることについて"],
    "003": ["猫", "小説", "日本文学"],
    "004": ["プログラミング", "Python", "AWS"]
}

# 新規記事のキーワード
new_article_keywords = ["猫", "日本文学", "走ることについて"]

def calculate_related_articles(new_article_keywords, existing_articles):
    related_scores = {}

    for article_id, article_keywords in existing_articles.items():
        common_keywords = set(new_article_keywords) & set(article_keywords)
        related_scores[article_id] = len(common_keywords)

    # スコアが高い順に並べる
    sorted_related = sorted(related_scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_related

result = calculate_related_articles(new_article_keywords, existing_articles)

for article_id, score in result:
    print(f"記事ID: {article_id}, 共通キーワード数: {score}")
