import boto3
import requests

def extract_keywords(text):
    clean_text = re.sub(r'\r\n?|\n', '\n', text)
    
    comprehend = boto3.client('comprehend', region_name='ap-northeast-1')
    response = comprehend.detect_key_phrases(Text=clean_text, LanguageCode='ja')
    
    keywords = [phrase['Text'] for phrase in response['KeyPhrases']]
    return keywords

#Stopword辞書を読み込み
def load_stopwords():
    url = "https://raw.githubusercontent.com/stopwords-iso/stopwords-ja/master/stopwords-ja.txt"
    response = requests.get(url)
    stopwords = set(response.text.splitlines())

    #カスタムの除外語も加える
    custom_exclude = {'こと', '方法', '情報', '内容', '記事', '仕組み'}
    stopwords |= custom_exclude

    return stopwords


#Comprehendからキーフレーズを抽出し、ストップワード除去
def extract_filtered_keywords(text):
    client = boto3.client('comprehend', region_name='us-east-1')
    response = client.detect_key_phrases(Text=text, LanguageCode='ja')

    raw_keywords = {phrase['Text'] for phrase in response['KeyPhrases']}

    stopwords = load_stopwords()
    filtered_keywords = [kw for kw in raw_keywords if kw not in stopwords and len(kw) > 1]

    return filtered_keywords
