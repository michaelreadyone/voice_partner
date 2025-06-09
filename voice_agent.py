import os
import openai
import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper
import pyttsx3
import tempfile

# Settings
SAMPLE_RATE = 16000
DURATION = 5  # seconds per recording
MODEL_NAME = 'base'  # Whisper model

openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Whisper
whisper_model = whisper.load_model(MODEL_NAME)

# Initialize TTS
tts_engine = pyttsx3.init()

def record_audio(duration=DURATION, sample_rate=SAMPLE_RATE):
    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    audio = np.squeeze(audio)
    return audio

def save_wav(audio, sample_rate):
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    sf.write(temp_wav.name, audio, sample_rate)
    return temp_wav.name

def transcribe(audio_path):
    print("Transcribing...")
    result = whisper_model.transcribe(audio_path)
    return result['text']

def chat_with_gpt(prompt, history=None):
    print("Sending to OpenAI...")
    messages = history if history else []
    messages.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    reply = response['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": reply})
    return reply, messages

def speak(text):
    print("Speaking...")
    tts_engine.say(text)
    tts_engine.runAndWait()

def main():
    print("Voice Agent Ready. Press Ctrl+C to exit.")
    history = []
    while True:
        try:
            audio = record_audio()
            wav_path = save_wav(audio, SAMPLE_RATE)
            user_text = transcribe(wav_path)
            print(f"You: {user_text}")
            if user_text.strip() == '':
                continue
            reply, history = chat_with_gpt(user_text, history)
            print(f"Agent: {reply}")
            speak(reply)
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main() 