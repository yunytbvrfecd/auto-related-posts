import boto3


def extract_keywords(text):
    comprehend = boto3.client('comprehend', region_name='us-east-1')
    response = comprehend.detect_key_phrases(Text=text, LanguageCode='ja')
    keywords = [phrase['Text'] for phrase in response['KeyPhrases']]
    return keywords
