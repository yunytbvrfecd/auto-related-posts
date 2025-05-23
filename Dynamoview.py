import boto3

# DynamoDBクライアント作成
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('test-articles')

# 全件取得（scan）
try:
    response = table.scan()
    items = response['Items']

    for item in items:
        article_id = item.get('article_id')
        title = item.get('title')
        body = item.get('body')
        keywords = item.get('keywords')

        print(f"記事ID: {article_id}")
        print(f"タイトル: {title}")
        print(f"本文: {body}")
        print(f"キーワード: {keywords}")
        print("=" * 40)

except Exception as e:
    print(f"エラーが発生しました: {e}")
