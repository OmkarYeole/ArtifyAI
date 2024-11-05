import torch
from transformers import pipeline
import librosa
import os
import soundfile as sf
from pydub import AudioSegment
import tempfile
import subprocess
from pydub.exceptions import CouldntDecodeError
import numpy as np

def convert_bytes_to_array(audio_bytes):
    try:
        # Save the byte stream to a temporary WebM file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name

        # Convert directly to WAV or MP3 using ffmpeg
        wav_file_path = temp_file_path.replace(".webm", ".wav")
        subprocess.run(['ffmpeg', '-i', temp_file_path, wav_file_path], check=True)

        if not os.path.exists(wav_file_path):
            raise FileNotFoundError(f"Conversion to {wav_file_path} failed.")

        # Load the converted WAV file
        audio_array, sample_rate = sf.read(wav_file_path)
        return audio_array, sample_rate

    except CouldntDecodeError as e:
        print("Could not decode the file:", e)
        raise e
    except Exception as e:
        print("Error processing file:", e)
        raise e


def transcribe_audio(audio_bytes):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    pipe = pipeline(
        task="automatic-speech-recognition",
        model="openai/whisper-small",
        chunk_length_s=30,
        device=device,
        generate_kwargs = {"language":"<|en|>","task": "transcribe"}
    )   

    try:
        audio_array, sample_rate = convert_bytes_to_array(audio_bytes)
        
        prediction = pipe(audio_array, batch_size=1)["text"]
        return prediction
    
    except Exception as e:
        print(f"Error in transcribe_audio: {e}")
        raise