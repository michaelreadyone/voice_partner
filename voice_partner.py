import datetime
import sounddevice as sd
import numpy as np
import whisper
import soundfile as sf
import tempfile
import pyttsx3
import os
import openai
from dotenv import load_dotenv
import torch
from TTS.api import TTS as CoquiTTS

from utils import save_conversation

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
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


def speech_digest_once(
    model_size="base",
    energy_threshold=0.01,
    pause_duration=1.2,
    frame_duration=0.2,
    sample_rate=16000,
    verbose=True
):
    """
    Records speech from the microphone and stops when the user is silent for 'pause_duration' seconds.
    Returns the transcribed text (or None if nothing was said).
    """
    def rms(audio):
        return np.sqrt(np.mean(audio**2))

    if verbose:
        print("Loading Whisper model...")
    model = whisper.load_model(model_size)
    if verbose:
        print(
            f"Listening for speech. Speak and then pause for >{pause_duration}s to finish...")

    buffer = []
    silence_counter = 0
    spoken = False

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32') as stream:
            while True:
                audio_chunk, _ = stream.read(int(sample_rate * frame_duration))
                audio_chunk = np.squeeze(audio_chunk)
                buffer.append(audio_chunk)
                energy = rms(audio_chunk)

                # If any non-silent frame detected, mark as spoken
                if energy >= energy_threshold:
                    silence_counter = 0
                    spoken = True
                else:
                    silence_counter += frame_duration

                # Stop if we have heard speech and then a long enough pause
                if spoken and silence_counter >= pause_duration:
                    break
            # Only process if something was spoken
            if spoken:
                audio_data = np.concatenate(buffer)
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    temp_name = f.name
                sf.write(temp_name, audio_data, sample_rate)
                result = model.transcribe(temp_name, fp16=False)
                text = result['text'].strip()
                # if verbose:
                #     print("\n[Transcription]:", text)
                os.remove(temp_name)  # Clean up temp file!
                return text
            else:
                if verbose:
                    print("No speech detected.")
                return None
    except KeyboardInterrupt:
        if verbose:
            print("\nInterrupted.")
        return None


# def text_to_speech(text, output_file=None, rate=150, volume=1.0):
#     # voice = "Tingting"
#     # voice = "Samantha"
#     voice = None
#     engine = pyttsx3.init()
#     engine.setProperty('rate', rate)      # Speed of speech
#     engine.setProperty('volume', volume)  # Volume (0.0 to 1.0)
#     if voice:
#         voices = engine.getProperty('voices')
#         for v in voices:
#             if voice.lower() in v.name.lower():
#                 engine.setProperty('voice', v.id)
#                 break

#     if output_file:
#         engine.save_to_file(text, output_file)
#         engine.runAndWait()
#         print(f"Saved speech to {output_file}")
#     else:
#         engine.say(text)
#         engine.runAndWait()
        


def text_to_speech(text, engine_name="pyttsx3", output_file=None, rate=150, volume=1.0):
    """
    Speak text using either pyttsx3 (local TTS engine) or Coqui TTS.
    
    Args:
      text (str): Text to be spoken.
      engine_name (str): "pyttsx3" or "coqui".
      output_file (str or None): Optional filepath to save audio (Coqui only).
      rate (int): Speaking rate for pyttsx3.
      volume (float): Volume level (0.0 to 1.0) for pyttsx3.
    """
    if engine_name.lower() == "pyttsx3":
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
        if output_file:
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            print(f"Saved speech to {output_file}")
        else:
            engine.say(text)
            engine.runAndWait()

    elif engine_name.lower() == "coqui":
        use_gpu = torch.cuda.is_available()
        tts = CoquiTTS(model_name="tts_models/en/ljspeech/fast_pitch", gpu=use_gpu)
        
        if output_file:
            tts.tts_to_file(text=text, file_path=output_file)
            print(f"Saved speech to {output_file}")
        else:
            wav = tts.tts(text)
            sr = tts.synthesizer.output_sample_rate
            sd.play(wav, samplerate=sr)
            sd.wait()

    else:
        raise ValueError(f"Unsupported engine: {engine_name}")



def chat_loop():
    messages = [
        {"role": "system", "content": (
            "You are a helpful assistant. Always reply in a casual, conversational tone. "
            "Keep it short and friendly—never go over 100 words. Be direct and easy to understand."
        )}
    ]
    print("Chat (type 'exit' to quit):")
    while True:
        # user_input = input("You: ")
        print()
        user_input = speech_digest_once()
        print("[You]:")
        print(user_input)
        if user_input.lower() == "exit":
            break
        messages.append({"role": "user", "content": user_input})
        # print(f'messages: {messages}')
        response = openai_chat(messages)
        if response:
            print("[Assistant]:")
            print(response)
            text_to_speech(response, engine_name="pyttsx3")
            messages.append({"role": "assistant", "content": response})
        else:
            print("No response from assistant.")
        if "goodbye" in user_input.lower() or "good bye" in user_input.lower():
            # save conversation to local txt with today's date
            save_conversation(messages)
            # date = datetime.datetime.now().strftime("%Y-%m-%d")
            # with open(f"conversation_{date}.txt", "a") as f:
            #     f.write("[Conversation Started at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]\n")
            #     for message in messages:
            #         f.write(f"{message['role']}: \n")
            #         f.write(f"{message['content']}\n")
            #     f.write("[Conversation Ended at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]\n")
            #     f.write("\n")
            
            break


if __name__ == "__main__":
    chat_loop()
