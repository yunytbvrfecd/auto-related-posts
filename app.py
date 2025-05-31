import uuid
import boto3
import os

from flask import Flask, render_template, request, redirect, url_for
from extract_keywords import extract_keywords
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('test-articles')

class User(UserMixin):
    def __init__(self, id):
        self.id = id

app = Flask(__name__)
app.secret_key = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)




@app.route('/')
def hello():
    return render_template('form.html')  # ← HTMLフォームに切り替えるとよいかも？

@app.route('/postarticle', methods=['POST'])
@login_required
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
    response = table.scan()
    items = response['Items']
    return render_template('article_list.html',articles=items)

def find_related_articles(current_article, all_articles):
    current_keywords = set(current_article['keywords'])
    related = []

    for article in all_articles:
        if article['article_id'] == current_article['article_id']:
            continue  # 自分自身は除外

        score = len(current_keywords & set(article['keywords']))
        if score >= 2:
            related.append((article, score))

    # スコア順に並べて上位5件まで返す
    related.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in related[:5]]


@app.route('/article/<article_id>')
def show_article(article_id):
    try:
        article = get_article_by_id(article_id)
        if not article:
            return "記事が見つかりませんでした。"

        all_articles = get_all_articles()
        related_articles = find_related_articles(article, all_articles)

        return render_template(
            'article_detail.html',  # ← こちらに統一
            article=article,
            related_articles=related_articles
        )
    except Exception as e:
        return f"取得エラー: {e}"

#記事をIDで取得する関数
def get_article_by_id(article_id):
    response = table.get_item(Key={'article_id': article_id})
    return response.get('Item')

#記事を全件取得する関数（最大1MBまで）
def get_all_articles():
    response = table.scan()
    return response.get('Items', [])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'PASSWORD':
            user = User(id=username)
            login_user(user)
            return redirect(url_for('form'))
        else:
            return '駄目っぽい'
    else:
        return '''
        <form method="POST">
            <input type=text name=username placeholder="Username">
            <input type=password name=password placeholder="Password">
            <input type=submit value=Login>
        </form>
        '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('/article_list'))

if __name__ == '__main__':
    app.run(debug=True)
