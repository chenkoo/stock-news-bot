import os
import openai
import feedparser
import telegram
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
keywords = [kw.strip().lower() for kw in os.getenv("KEYWORDS", "").split(",")]

bot = telegram.Bot(token=telegram_token)

def fetch_news():
    feeds = [
        "https://www.reuters.com/rssFeed/businessNews",
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL,TSLA,NVDA&region=US&lang=en-US"
    ]
    all_items = []
    for url in feeds:
        feed = feedparser.parse(url)
        all_items.extend(feed.entries)
    return all_items

def filter_news_by_keywords(items, keywords):
    return [item for item in items if any(kw in item.title.lower() for kw in keywords)]

def summarize(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一个财经新闻摘要助手。"},
            {"role": "user", "content": f"请用中文简要总结这段财经新闻，重点是可能影响股价的部分：\n\n{text}"}
        ]
    )
    return response['choices'][0]['message']['content']

def main():
    news_items = fetch_news()
    filtered = filter_news_by_keywords(news_items, keywords)

    for item in filtered[:5]:
        title = item.title
        link = item.link
        summary = summarize(title)
        message = f"📰 *{title}*\n\n{summary}\n[查看原文]({link})"
        bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

if __name__ == "__main__":
    main()
