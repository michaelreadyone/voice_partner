import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
for idx, voice in enumerate(voices):
    print(f"Voice #{idx}: {voice.name}, ID: {voice.id}, Lang: {voice.languages}")
