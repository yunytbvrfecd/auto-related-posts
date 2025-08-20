# Flask ポートフォリオ（学習用）

AWS の練習を兼ねて作った Flask の Web アプリです。  
記事を投稿できる仕組みを用意し、DynamoDB に保存しています。  
また、Amazon Comprehend で文章からキーワードを取り出し、関連記事を表示するようにしました。  
ログイン機能には二段階認証も加えています。

---

## 主な機能

- ユーザー登録とログイン（パスワードはハッシュ化）
- 二段階認証（Google Authenticator 互換 / `pyotp`）
- 記事の投稿と閲覧
- Amazon Comprehend によるキーフレーズ抽出
- 抽出したキーワードを使った関連記事の表示（簡易版）

---

## 構成図

![architecture](docs/architecture.png)

- Web アプリ: Flask  
- 実行環境: gunicorn  
- 逆プロキシ: nginx  
- サーバ: AWS EC2  
- データベース: DynamoDB  
- 文章解析: Amazon Comprehend  

---

## 動かし方（ローカル）

bash
python -m venv .venv
source .venv/bin/activate  # Windows は .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env  # 値を設定してコピー
flask run

---

## デプロイ方法

- EC2 を作成
- 仮想環境を用意し、必要なパッケージをインストール
- gunicorn で Flask を起動
- systemd に登録して常駐化
- nginx を設定して外部からアクセス可能に
- SSL は学習用なので自己署名で対応

---

## セキュリティ面の工夫

パスワードを平文で保存せず、ハッシュ化して保存
二段階認証を追加
秘密情報は .env で管理

---

## 学んだこと・工夫した点

AWSを理解するため、実際にAWSを用いた作品を作ることにしたが、そのためにはGithub、CMDの扱い方等、今までの仕事では利用してこなかった部分が多く必要になった。
そのため、一つ一つをインターネットで調べつつ形に仕上げることとなったが、今まで用いなかったツールの基本的な使用方法を学ぶことが出来た。
DynamoDBとComprehendを実際に組み合わせ、AWS のマネージドサービスを体験できた。
Flask-Loginに加えてpyotpを導入し、二段階認証を実装したことでセキュリティを意識した。
systemdとnginxを使い、サーバを常時稼働させる仕組みを整えた。   

---

## 注意点

このアプリは学習用です。商用利用は想定していません。
