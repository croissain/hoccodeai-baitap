from openai import OpenAI
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import requests

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

OpenAI.api_key = os.getenv("LOCAL_API_KEY")

client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("LOCAL_API_KEY"))


def extract_content_by_beautifulsoup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "meta", "link"]):
            tag.decompose()

        text = " ".join(soup.stripped_strings)
        return text
    except Exception as e:
        return f"Error: {str(e)}"


def summarize_text(text):
    try:
        prompt = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Please summarize the following text in 150 words or less.",
            },
            {"role": "user", "content": text},
        ]
        response = client.chat.completions.create(
            messages=prompt,
            model=os.getenv("MODEL"),
            stream=True,
            temperature=0,
            max_tokens=500,
            top_p=1,
        )
        bot_reply = ""

        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                bot_reply += content
        return bot_reply
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    print("Welcome to the Chatbot website summarize! (Type '0' to exit)\n")
    while True:
        website_url = input("Link: ")
        content = extract_content_by_beautifulsoup(website_url)
        summary = summarize_text(content)
        print(summary)
        print()
        user_input = input("You: ")

        if user_input.lower() == "0":
            break


if __name__ == "__main__":
    main()
