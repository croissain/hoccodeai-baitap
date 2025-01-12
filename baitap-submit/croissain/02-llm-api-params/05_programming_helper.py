from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

OpenAI.api_key = os.getenv("LOCAL_API_KEY")


def get_completion(prompt):
    try:
        client = OpenAI(
            base_url=os.getenv("BASE_URL"), api_key=os.getenv("LOCAL_API_KEY")
        )
        response = client.chat.completions.create(
            messages=prompt,
            model=os.getenv("MODEL"),
            stream=True,
            temperature=0,
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
    print("Welcome to the Chatbot console! (Type '0' to exit)\n")
    history = []
    while True:
        user_input = input("You: ")
        if user_input.lower() == "0":
            break
        history.append({"role": "user", "content": user_input})

        print("Bot: ", end="", flush=True)

        response = get_completion(history)

        print()  # New line after complete response
        history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
