import os
import uuid

import boto3
import pyotp
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import check_password_hash

from extract_keywords import extract_keywords

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('test-articles')


class User(UserMixin):
    def __init__(self, id):
        self.id = id


app = Flask(__name__)
app.secret_key = os.urandom(24)

load_dotenv()  # パスを暗号化したため、envを読み込む。
app.secret_key = os.getenv("SECRET_KEY")
secret = os.getenv("TOTP_SECRET")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/')
def hello():
    response = table.scan()
    items = response['Items']
    return render_template('article_list.html', articles=items)


@app.route('/form')
@login_required
def form():
    return render_template('form.html')


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
    items = response.get('Items', [])
    return render_template('article_list.html', articles=items, query=None)


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


# 記事をIDで取得する関数
def get_article_by_id(article_id):
    response = table.get_item(Key={'article_id': article_id})
    return response.get('Item')


# 記事を全件取得する関数（最大1MBまで）
def get_all_articles():
    response = table.scan()
    return response.get('Items', [])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        stored_username = os.getenv("ADMIN_USERNAME")
        stored_password_hash = os.getenv("ADMIN_PASSWORD")
        if username == stored_username and check_password_hash(stored_password_hash, password):
            session['pending_user'] = username  # 認証前セッションマーク
            return redirect(url_for('verify_totp'))
        else:
            return 'ログインに失敗。'
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
    return redirect(url_for('show_article_list'))


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()

    if not query:
        return redirect(url_for('show_article_list'))

    response = table.scan()
    all_articles = response.get('Items', [])

    # タイトル、キーワードに検索語を含む記事を抽出（部分一致）
    matching_articles = []
    for article in all_articles:
        title = article.get('title', '')
        keywords = article.get('keywords', [])
        if query in title or any(query in kw for kw in keywords):
            matching_articles.append(article)

    return render_template('article_list.html', articles=matching_articles, query=query)


@app.route('/verify', methods=['GET', 'POST'])
def verify_totp():
    if 'pending_user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        code = request.form['totp_code']
        totp = pyotp.TOTP(os.getenv("TOTP_SECRET"))

        if totp.verify(code):
            user = User(id=session.pop('pending_user'))
            login_user(user)
            return redirect(url_for('form'))
        else:
            return render_template('verify.html', error="TOTPコードが間違っています。")

    # GETリクエストのときは認証フォームを表示
    return render_template('verify.html')


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=5000, debug = True)
