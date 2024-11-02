from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import requests
import feedparser
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app)

# API 키 설정
SOLAR_API_KEY = os.getenv("UPSTAGE_API_KEY", "up_******")  # 여기에 실제 API 키 입력
BASE_URL = "https://api.upstage.ai/v1/solar"
HEADERS = {
    "Authorization": f"Bearer {SOLAR_API_KEY}",
    "Content-Type": "application/json",
}

rss_feeds = {
    "전체": [
        'https://www.yna.co.kr/rss/all.xml',
        'https://news.kbs.co.kr/news/rss/rss.xml',
        'https://www.hani.co.kr/rss/',
        'https://rss.joins.com/joins_news_list.xml',
        'https://www.donga.com/news/rss/headline.xml',
        'https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml',
        'https://rss.hankyung.com/feed/economy.xml',
        'https://www.mk.co.kr/rss/40300001/',
        'https://www.sedaily.com/rss/Main.xml',
        'https://www.etnews.com/section02.xml',
    ],
    "정치": [
        'https://www.yna.co.kr/rss/politics.xml',
        'https://www.hankyung.com/feed/politics',
    ],
    "연예": [
        'https://www.yna.co.kr/rss/entertainment.xml',
        'https://www.hankyung.com/feed/entertainment',
    ],
    "경제": [
        'https://www.yna.co.kr/rss/economy.xml',
        'https://www.hankyung.com/feed/economy',
    ],
    "스포츠": [
        'https://www.yna.co.kr/rss/sports.xml',
        'https://www.hankyung.com/feed/sports',
    ],
    "과학기술": [
        'https://www.yna.co.kr/rss/science.xml',
        'https://www.etnews.com/section02.xml',
    ],
    "세계": [
        'https://www.yna.co.kr/rss/world.xml',
        'https://www.hankyung.com/feed/world',
    ],
    "건강": [
        'https://www.yna.co.kr/rss/health.xml',
        'https://www.hankyung.com/feed/health',
    ]
}

@app.route('/')
def home():
    return render_template('pr.html')  # pr.html 파일을 반환

@app.route('/api/profile', methods=['POST'])
def receive_profile():
    try:
        profile = request.json
        print("Received Profile:", profile)

        # 선택된 카테고리 가져오기 (하나만 선택됨)
        selected_preferences = profile.get("preferences", "")
        category = selected_preferences if selected_preferences else "전체"

        print("Selected Category:", category)

        # 선택된 카테고리에 해당하는 RSS 피드 가져오기
        feeds = rss_feeds.get(category, rss_feeds["전체"])  # 카테고리에 따라 RSS 피드 선택
        articles = []

        for feed in feeds:
            d = feedparser.parse(feed)
            for entry in d.entries:
                articles.append(entry.summary if 'summary' in entry else "")

        # 기사를 요약
        summary = summarize_articles(articles)
        if summary:
            return jsonify({"message": "Profile received successfully!", "summary": summary})  # 요약 포함하여 응답
        else:
            return jsonify({"message": "Error summarizing articles."}), 500

    except Exception as e:
        print(f"Error in receive_profile: {e}")
        return jsonify({"message": "An error occurred while processing the profile."}), 500

@app.route('/summary')
def summary_page():
    return render_template('summary.html')  # summary.html 파일을 반환

# 함수: 여러 기사를 간략한 구문 형태로 요약하는 함수
def summarize_articles(articles_text):
    try:
        combined_text = " ".join(articles_text)  # 여러 기사 내용을 하나로 합침
        data = {
            "model": "solar-1-mini-chat",
            "messages": [
                {"role": "system", "content": "You are an assistant that summarizes multiple news articles in Korean, providing concise phrases."},
                {"role": "user", "content": f"뉴스 기사를 10 단어로 요약해서 순번을 붙여서 5개 출력해줘: {combined_text}"},
            ],
        }

        response = requests.post(f"{BASE_URL}/chat/completions", headers=HEADERS, json=data)
        if response.status_code == 200:
            result = response.json()
            summary_text = result['choices'][0]['message']['content']
            return summary_text
        else:
            print(f"Error in summarize_articles: {response.status_code}, Response: {response.text}")  # 오류 메시지 출력
            return None
    except Exception as e:
        print(f"Error in summarize_articles: {e}")
        return None

# 함수: 요약된 내용을 한국어로 번역
def translate_to_korean(text):
    try:
        translation = GoogleTranslator(source='auto', target='ko').translate(text)
        return translation
    except Exception as e:
        print(f"Error in translate_to_korean: {e}")
        return text  # 실패 시 원래 텍스트를 반환

if __name__ == '__main__':
    app.run(debug=True)







