from openai import OpenAI

client = OpenAI(
    base_url="http://172.16.0.2:1234/v1",
    api_key='your-api-key'
)

def chat_with_bot():
    print("\nWelcome to the Chatbot console! (Type '0' to exit)\n")
    list_messages = []
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == '0':
            break

        list_messages.append({"role": "user", "content": user_input})

        # Enable streaming response
        response = client.chat.completions.create(
            messages=list_messages,
            model="llama-3.2-1b-instruct",
            stream=True,  # Enable streaming
            temperature=0,
        )

        print("Bot: ", end="", flush=True)
        bot_reply = ""
        
        # Process the streaming response
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                bot_reply += content
                
        print()  # New line after complete response
        list_messages.append({"role": "assistant", "content": bot_reply})

if __name__ == "__main__":
    chat_with_bot()
