import boto3

# DynamoDBクライアントを作成
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# 仮のテーブル名
table_name = 'test-articles'
table = dynamodb.Table(table_name)

# テーブルの中身をスキャン（全件取得）
try:
    response = table.scan()
    items = response['Items']

    for item in items:
        print(item)

except Exception as e:
    print(f"エラーが発生しました: {e}")
