import pyttsx3

def text_to_speech(text, output_file=None, rate=150, volume=1.0, voice='Samantha'):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)      # Speed of speech
    engine.setProperty('volume', volume)  # Volume (0.0 to 1.0)
    if voice:
        voices = engine.getProperty('voices')
        for v in voices:
            if voice.lower() in v.name.lower():
                engine.setProperty('voice', v.id)
                break

    if output_file:
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        print(f"Saved speech to {output_file}")
    else:
        engine.say(text)
        engine.runAndWait()

if __name__ == '__main__':
    # Example usage
    text = "Hello! This is an offline text to speech demo."
    text_to_speech(text, output_file=None)  # Set to a filename.wav for file output
    
    # engine = pyttsx3.init()
    # voices = engine.getProperty('voices')
    # for idx, voice in enumerate(voices):
    #     print(f"Voice #{idx}: {voice.name}, ID: {voice.id}, Lang: {voice.languages}")
