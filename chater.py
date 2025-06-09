import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def openai_chat(messages, model="gpt-4o-mini"):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not found in environment.")
        return None
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print("OpenAI API error:", e)
        return None

def chat_loop():
    messages = [
        {"role": "system", "content": (
            "You are a helpful assistant. Always reply in a casual, conversational tone. "
            "Keep it short and friendly—never go over 100 words. Be direct and easy to understand."
        )}
    ]
    print("Chat (type 'exit' to quit):")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        # Add explicit user instruction if you want
        # user_message = f"{user_input} (Please keep your answer under 100 words and make it conversational.)"
        # messages.append({"role": "user", "content": user_message})
        messages.append({"role": "user", "content": user_input})
        print(f'messages: {messages}')
        response = openai_chat(messages)
        if response:
            print("Assistant:", response)
            messages.append({"role": "assistant", "content": response})
        else:
            print("No response from assistant.")


if __name__ == "__main__":
    chat_loop()
