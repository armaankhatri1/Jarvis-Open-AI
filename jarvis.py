import sounddevice as sd
import numpy as np
import os
import speech_recognition as sr
import openai
import pyttsx3
from scipy.io.wavfile import write  # This is used to save the audio to a WAV file

# Initialize OpenAI API and text-to-speech engine
engine = pyttsx3.init()
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    raise ValueError("OpenAI API key is not set. Please set the 'OPENAI_API_KEY' environment variable.")

# Queue for audio data
audio_data_queue = []

# Capture audio with sounddevice
def capture_audio(duration=5, fs=16000):
    print("Listening for command...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    return np.squeeze(recording)  # Convert 2D array to 1D

# Use speech_recognition to process the audio
def recognize_speech_from_audio(audio_data):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_data) as source:
        audio = recognizer.record(source)
    try:
        # Recognize speech using Google Web API
        text = recognizer.recognize_google(audio)
        print(f"Recognized: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    return None

# Function to send command to OpenAI and get a response
# Function to send command to OpenAI and get a response using the new ChatCompletion method
def get_openai_response(command):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Updated model name
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful AI assistant."},
                {"role": "user", "content": command}
            ],
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error communicating with OpenAI: {e}")
        return None


# Function to speak the response
def speak_response(response):
    if response:
        engine.say(response)
        engine.runAndWait()

# Main function to listen, process, and respond
def jarvis():
    audio_data = capture_audio()  # Capture audio for 5 seconds
    if audio_data is not None:
        # Save the audio data to a WAV file using scipy.io.wavfile.write
        audio_file = "command.wav"
        write(audio_file, 16000, audio_data)  # Save audio to file
        
        # Recognize speech from the captured audio
        command = recognize_speech_from_audio(audio_file)
        if command:
            response = get_openai_response(command)
            speak_response(response)
    else:
        print("No command detected.")

# Run Jarvis
if __name__ == "__main__":
    jarvis()
