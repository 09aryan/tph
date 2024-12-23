from flask import Flask, request, jsonify, Response
import os
from openai import OpenAI
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not FIRECRAWL_API_KEY or not OPENAI_API_KEY:
    raise RuntimeError("Missing FIRECRAWL_API_KEY or OPENAI_API_KEY in .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Flask app setup
app = Flask(__name__)
SCRAPED_CONTENT_FILE = "website_content.txt"

# Helper function: Summarize content using gpt-3.5-turbo
def summarize_content(content, client):
    """Summarize long content to fit within token limits."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Summarize the following content:\n\n{content}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR] Failed to summarize content: {str(e)}"

@app.route('/scrape', methods=['POST'])
def scrape():
    """Scrape a single URL using Firecrawl API."""
    try:
        data = request.json
        url = data.get("url")
        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Firecrawl API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}"
        }
        payload = {
            "url": url,
            "formats": ["markdown", "html"]
        }

        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers=headers,
            json=payload
        )
        response_data = response.json()

        # Handle Firecrawl API errors
        if response.status_code != 200 or not response_data.get("success", False):
            error_message = response_data.get("error", "Unknown error")
            return jsonify({"error": f"Firecrawl API error: {error_message}"}), 500

        # Extract content
        content = response_data.get("data", {}).get("markdown", "")
        if not content:
            return jsonify({"error": "No content returned by Firecrawl"}), 500

        # Save content to a file
        with open(SCRAPED_CONTENT_FILE, "w", encoding="utf-8") as f:
            f.write(content)

        return jsonify({"message": "Website scraped successfully", "content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ask', methods=['POST'])
def ask():
    """Ask a question based on the scraped website content."""
    try:
        data = request.json
        question = data.get("question")
        if not question:
            return jsonify({"error": "Question is required"}), 400

        # Ensure the scraped content file exists
        if not os.path.exists(SCRAPED_CONTENT_FILE):
            return jsonify({"error": "Scraped content not found. Please scrape a website first."}), 404

        # Read the scraped content
        with open(SCRAPED_CONTENT_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # If content is too large, summarize it
        max_chars = 5000  # Adjust this based on your token limit
        if len(content) > max_chars:
            content = summarize_content(content, client)

        # Streaming option (uncomment if needed)
        def generate():
            try:
                stream = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an assistant trained to answer questions based on website content."},
                        {"role": "user", "content": f"The following is content from a website:\n\n{content}\n\nAnswer the question: {question}"}
                    ],
                    stream=True,
                )
                for chunk in stream:
                    # Access the content directly
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield f"data: {delta}\n\n"
            except Exception as e:
                yield f"data: [ERROR] {str(e)}\n\n"

        # Uncomment the following line to enable streaming
        # return Response(generate(), content_type="text/event-stream")

        # Non-streaming response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant trained to answer questions based on website content."},
                {"role": "user", "content": f"The following is content from a website:\n\n{content}\n\nAnswer the question: {question}"}
            ]
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({"question": question, "answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
