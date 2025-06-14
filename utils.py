import os
import datetime


date = datetime.datetime.now().strftime("%Y-%m-%d")

def folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def save_conversation(messages):
    folder = "conversations"
    folder_exists(folder)
    file_path = os.path.join(folder, f"conversation_{date}.txt")
    with open(file_path, "a") as f:
        f.write("[Conversation Started at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]\n")
        for message in messages:
            f.write(f"{message['role']}: \n")
            f.write(f"{message['content']}\n")
        f.write("[Conversation Ended at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]\n")
        f.write("\n")