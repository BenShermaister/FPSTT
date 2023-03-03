import tkinter as tk
import customtkinter as ctk
import soundfile as sf
import pyaudio
import wave
import time
import threading
import numpy as np

# pip install git+https://github.com/openai/whisper.git
import whisper

# Select from the following models: "tiny", "base", "small", "medium", "large"
model = whisper.load_model("base")

stop_recording = False
thread_obj = None
ready_to_transcribe = False

def record():
    print("Recording...")
    global stop_recording
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 500
    filename = "output.wav"
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    stream = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input=True)
    frames = []  # Initialize array to store frames
    # Store data in chunks for 3 seconds
    max_rec = int(fs / chunk * seconds)
    r = range(0, max_rec)
    stop_time = -1
    for i in r:
        data = stream.read(chunk)
        frames.append(data)
        if(i == stop_time):
            stop_time = -1
            break
        if(stop_recording):
            # stop the recording 0.3s aftter clicking the button
            stop_time = i + 30
            stop_recording = False
    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()
    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    stop_recording = False
    


def voice_rec():
    global stop_recording, thread_obj
    if thread_obj != None:
        stop_recording = True
        #find the thread and stop it
        thread_obj.join()
        transcribe()
        thread_obj = None
        recordButton.configure(text="Record")
    else:
        thread_obj = threading.Thread(target=record)
        thread_obj.start()
        stop_recording = False
        recordButton.configure(text="Stop record & transcribe")
        

def transcribe():
    audio = "output.wav"
    # You can provide the language to the model if it is a bit to "exotic" to predict
    options = {"fp16": False, "language": "Hebrew", "task": "transcribe"}
    results = model.transcribe(audio, **options)
    print(results["text"])
    #clear old text
    textbox.delete(1.0, tk.END)
    textbox.tag_configure('tag-right', justify='right')
    textbox.insert(tk.END, results["text"], 'tag-right')
    



# create the root
root = tk.Tk()
root.geometry("300x300")
root.title("Voice to text")
ctk.set_appearance_mode("dark")



recordButton = ctk.CTkButton(
    height=40,
    width=120,
    #text_font=("Roboto Medium", 20),
    master=root,
    text_color="white",
    fg_color=("white", "gray38"),
    command=voice_rec,
    text="Record"
)
recordButton.place(x=90, y=70)





textbox = tk.Text(root, height=10, width=35)
textbox.place(x=8, y=120)
#main header text
headerText = ctk.CTkLabel(master=root, text="Voice to text DEMO", text_color="black", font=("Arial", 25))
headerText.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
    # run root
root.mainloop()