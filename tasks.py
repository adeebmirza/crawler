from celery_app import app
from datetime import datetime
from celery_app import app
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
import requests
from io import BytesIO
from PIL import Image
import json
import logging
from firecrawl import FirecrawlApp
from tavily import TavilyClient
import praw
import os
import google.generativeai as genai
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
import requests
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

from bson import ObjectId
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class QuestionRequest(BaseModel):
    question: str
    image_url: str | None = None

# --- 🔐 API Keys ---
TAVILY_API_KEY= ""
FIRECRAWL_API_KEY= ""
GEMINI_API_KEY= ""

#--- Reddit Setup---

client_id="BaxjxvCTqjk817rNQa1VHw"
client_secret="yu1cCkZnsUow7Kq--KE800Tw0nVJqGA"
password="adeebM1#"
username="MainLettuce419"
user_agent="python:adeeb.scraper:v1.0 (by /u/u/MainLettuce419)"


# --- 🔍 Tavily Setup ---
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# --- 🔥 Firecrawl Setup ---
firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

# --- 🧠 Reddit Setup ---
reddit = praw.Reddit(
    client_id="BaxjxvCTqjk817rNQa1VHw",
    client_secret="u1cCkZnsUow7Kq--KE800Tw0nVJqGA",
    password="adeebM1#",
    username="MainLettuce419",
    user_agent="python:adeeb.scraper:v1.0 (by /u/u/MainLettuce419)"
)

# --- 💬 Gemini Setup ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

client = MongoClient("mongodb://localhost:27017")
db = client["reddit_db"]
posts_collection = db["Post"]

@app.task(name='process_message')
def process_message(message_body):
    """
    Process incoming SQS messages in either format:
    1. {"post_id": "...", "text": "...", "image_urls": ["..."]}
    2. {"post_id": "...", "text": "..."}
    """
    try:
        # Parse message if it's a JSON string
        if isinstance(message_body, str):
            try:
                message_data = json.loads(message_body)
            except json.JSONDecodeError:
                logger.error("Invalid JSON format.")
                return {"error": "Invalid JSON format"}
        elif isinstance(message_body, dict):
            message_data = message_body
        else:
            logger.error("Unsupported message format.")
            return {"error": "Unsupported message format"}

        # Extract required fields
        post_id = message_data.get("post_id")
        text = message_data.get("text")
        image_urls = message_data.get("image_urls", [])
        image_url = image_urls[0] if image_urls else None

        if not post_id or not text:
            logger.warning("Missing 'post_id' or 'text' in message.")
            return {"error": "Missing 'post_id' or 'text'"}

        # Call the downstream task
        return ask_gemini(post_id=post_id, text=text, image=image_url)


    except Exception as e:
        logger.exception("Unexpected error during message processing.")
        return {"error": str(e)}




def scrape_reddit(url: str) -> str:
    submission = reddit.submission(url=url)
    submission.comments.replace_more(limit=0)
    comments = "\n\n".join([f"{c.author}: {c.body}" for c in submission.comments[:5]])
    return f"""
🔺 REDDIT POST: {url}
🔹 Title: {submission.title}
🔹 Author: {submission.author}
🔹 Score: {submission.score}

📌 Text:
{submission.selftext}

💬 Top Comments:
{comments}
"""

def scrape_firecrawl(url: str) -> str:
    response = firecrawl.scrape_url(url, formats=["markdown"])
    return f"🌐 WEBSITE: {url}\n\n" + response.markdown


def ask_gemini(post_id: str, text: str, image: str = None):
    from datetime import datetime, timezone

    # Step 1: Classify question
    category_prompt = f"""
    You are a helpful assistant. Given the user's question below, classify it into one of the following categories:
    ["Technology", "Health", "Science", "Finance", "Education", "General", "Life"]
    Respond with only the category name.
    Question: {text}
    """
    try:
        category_response = model.generate_content(category_prompt)
        top_category = category_response.text.strip()
    except Exception as e:
        print(f"❌ Gemini category classification failed: {e}")
        top_category = "General"  # fallback category

    urls = []
    combined_content = ""
    image_description = ""

    if image:
        # IMAGE + QUESTION → Gemini image analysis only, no Tavily search
        response = requests.get(image)
        image_bytes = response.content
        img = Image.open(BytesIO(image_bytes))

        # Analyze image - get one sentence description
        image_prompt = f"""
        Analyze the image based on the user's question and give me one sentence.

        User Question: {text}
        """

        try:
            response = model.generate_content([img, image_prompt])
            image_description = response.text.strip()

            search_result = tavily.search(query=image_description, search_depth="advanced", max_results=5)

            combined_content = ""
            urls = []

            for result in search_result.get("results", []):
                url = result["url"]
                urls.append(url)

                try:
                    if "reddit.com" in url:
                        content = scrape_reddit(url)
                    else:
                        content = scrape_firecrawl(url)

                    combined_content += f"\n\n===== 🔗 {url} =====\n{content}\n"
                except Exception as e:
                    combined_content += f"\n\n⚠️ Error scraping {url}: {str(e)}"

            final_prompt = f"""
            You are an expert assistant. Based on the user's question and the web content below, provide a helpful answer under 200 words.
            🔸 Question: {image_description}
            🔹 Web Context:
            {combined_content}
            """

            try:
                response = model.generate_content(final_prompt)
                answer = response.text.strip()
            except Exception as e:
                print(f"❌ Gemini generate_content failed: {e}")
                answer = "Sorry, I couldn't generate an answer at this time."

        except Exception as e:
            print(f"❌ Gemini generate_content failed: {e}")
            answer = "Sorry, I couldn't generate an answer at this time."

    else:
        # ONLY QUESTION → web search mode
        try:
            search_result = tavily.search(query=text, search_depth="advanced", max_results=5)
        except Exception as e:
            print(f"❌ Tavily search failed: {e}")
            search_result = {"results": []}

        for result in search_result.get("results", []):
            url = result["url"]
            urls.append(url)
            try:
                if "reddit.com" in url:
                    content = scrape_reddit(url)
                else:
                    content = scrape_firecrawl(url)
                combined_content += f"\n\n===== 🔗 {url} =====\n{content}\n"
            except Exception as e:
                print(f"content {combined_content} ")
                combined_content += f"\n\n⚠️ Error scraping {url}: {str(e)}"


        final_prompt = f"""
        You are an expert assistant. Based on the user's question and the web content below, provide a helpful answer under 200 words.
        🔸 Question: {text}
        🔹 Web Context:
        {combined_content}
        """
        try:
            response = model.generate_content(final_prompt)
            answer = response.text.strip()
        except Exception as e:
            print(f"❌ Gemini generate_content failed: {e}")
            answer = "Sorry, I couldn't generate an answer at this time."

    # Step 3: Store and return
    # Store answer as a string
    result_doc = {
        "question": text,
        "answer": answer,  # Store as a string
        "category": top_category,
        "source": urls,  # Using 'source' to match the database model field name
        "timestamp": datetime.now(timezone.utc)
    }

    if post_id:
        try:
            print(f"Anweriis is : {answer}")
            print(f"Category is : {top_category}")
            print(f"Urls are : {urls}")
            posts_collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": {
                    "answer": answer,
                    "category": top_category,
                    "sources": urls
                }}
            )
        except Exception as e:
            print(f"❌ Failed to update post {post_id}: {e}")

    return result_doc