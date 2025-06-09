import sounddevice as sd
import numpy as np
import whisper
import soundfile as sf
import tempfile
import time

def speech_digest_once(
    model_size="base",
    energy_threshold=0.01,
    pause_duration=3.0,
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
        print(f"Listening for speech. Speak and then pause for >{pause_duration}s to finish...")

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
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
                    sf.write(f.name, audio_data, sample_rate)
                    result = model.transcribe(f.name)
                    text = result['text'].strip()
                    if verbose:
                        print("\n[Transcription]:", text)
                    return text
            else:
                if verbose:
                    print("No speech detected.")
                return None
    except KeyboardInterrupt:
        if verbose:
            print("\nInterrupted.")
        return None

# Example usage:
