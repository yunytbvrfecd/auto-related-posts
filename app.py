from flask import Flask, render_template, request, redirect, url_for
import uuid
import boto3
from Dynamoview import article_id
from extract_keywords import extract_keywords

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('form.html')  # ← HTMLフォームに切り替えるとよいかも？

@app.route('/postarticle', methods=['POST'])
def postarticle():
    article_text = request.form['articletxt']
    title = request.form['title']

    if not article_text.strip():
        return "記事内容が空です。入力してください。"

    if len(title) > 30:
        return "タイトルが長すぎます（最大30文字）。"

    if not article_text.strip():
        return "記事内容が空です。入力してください。"

    if len(article_text) > 5000:
        return "記事が長すぎます（最大5000文字）。"

    article_id = str(uuid.uuid4())
    keywords = extract_keywords(article_text)

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('test-articles')

    try:
        table.put_item(
            Item={
                'article_id': article_id,
                'title': title,
                'body': article_text,
                'keywords': keywords
            }
        )
        return '''
        <html>
            <meta http-equiv="refresh" content="2;url=/" />
            <body style="text-align:center;">
                <h2>記事が保存されました！</h2>
                <p>2秒後にフォームに戻ります...</p>
            </body>
        </html>
    '''
    except Exception as e:
        return f"保存中にエラーが発生しました: {e}"

@app.route('/article_list')
def show_article_list():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('test-articles')
    response = table.scan()
    items = response['Items']
    return render_template('article_list.html',articles=items)

@app.route('/article/<article_id>')
def article_detail(article_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('test-articles')
    try:
        response = table.get_item(Key={'article_id': article_id})
        item = response.get('Item')
        if not item:
            return "記事が見つかりませんでした。"
        return render_template('article_detail.html', article=item)
    except Exception as e:
        return f"取得エラー: {e}"

if __name__ == '__main__':
    app.run(debug=True)
