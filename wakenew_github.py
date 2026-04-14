import struct
import subprocess
import time
import queue
from datetime import datetime
import os
import webbrowser

import numpy as np
import sounddevice as sd
import pvporcupine
from faster_whisper import WhisperModel
from openai import OpenAI
from colorama import Fore, Style, init

init(autoreset=True)

# ===============================
# 🔐 CONFIG
# ===============================
PICOVOICE_ACCESS_KEY = "keyyy"
GROQ_API_KEY = "keyyy"
WAKE_WORD = "computer"

# ===============================
# 🧠 GROQ CLIENT
# ===============================
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = (
    "You are Robo, a robot voice assistant. "
    "Reply in 1 or 2 short conversational sentences only. "
    "Be clear, natural, and concise."
)

conversation_history = []

# ===============================
# 🎨 SYSTEM STATE
# ===============================
def set_state(state):
    colors = {
        "IDLE": Fore.BLUE,
        "WAKE_DETECTED": Fore.CYAN,
        "LISTENING": Fore.GREEN,
        "TRANSCRIBING": Fore.YELLOW,
        "ROUTING": Fore.MAGENTA,
        "THINKING": Fore.LIGHTMAGENTA_EX,
        "SPEAKING": Fore.RED,
    }
    print(colors.get(state, Fore.WHITE) + f"[{state}]" + Style.RESET_ALL)

# ===============================
# 🔊 TTS
# ===============================
def speak(text: str):
    text = text.strip()
    if not text:
        return

    set_state("SPEAKING")
    print("🔊", text)

    safe = text.replace('"', '').replace("\n", " ")

    subprocess.run(
        [
            "powershell",
            "-Command",
            "Add-Type -AssemblyName System.Speech; "
            f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{safe}")',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

# ===============================
# 🎤 WHISPER
# ===============================
print("Loading Whisper model...")
whisper = WhisperModel("base", compute_type="int8")

audio_queue = queue.Queue()

def callback(indata, frames, time_info, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

def record_command(seconds=4.0):
    while not audio_queue.empty():
        audio_queue.get_nowait()

    set_state("LISTENING")

    with sd.InputStream(samplerate=16000, channels=1, dtype="float32", callback=callback):
        sd.sleep(int(seconds * 1000))

    chunks = []
    while not audio_queue.empty():
        chunks.append(audio_queue.get_nowait())

    if not chunks:
        return "", 0.0

    audio = np.concatenate(chunks, axis=0).flatten().astype(np.float32)

    set_state("TRANSCRIBING")

    # ✅ Only transcription time is measured here
    transcribe_start = time.time()
    segments, _ = whisper.transcribe(
        audio,
        beam_size=1,
        language="en",
        vad_filter=True,
        condition_on_previous_text=False,
    )
    text = ""
    for seg in segments:
        text += seg.text.strip() + " "
    transcribe_time = time.time() - transcribe_start

    return text.strip(), transcribe_time

# ===============================
# 🧠 LOCAL COMMANDS
# ===============================
def handle_local_command(command: str):
    text = command.lower().strip()

    # TIME / DATE
    if "time" in text:
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."

    if "date" in text or "today" in text:
        return f"Today's date is {datetime.now().strftime('%d %B %Y')}."

    # WEB
    if "open google" in text:
        webbrowser.open("https://www.google.com")
        return "Opening Google."

    if "open youtube" in text:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."

    if "search" in text:
        query = text.replace("search for", "").replace("search", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching for {query}"

    # APPS
    if "open chrome" in text:
        subprocess.run("start chrome", shell=True)
        return "Opening Chrome."

    if "open notepad" in text:
        subprocess.run("notepad", shell=True)
        return "Opening Notepad."

    if "open calculator" in text:
        subprocess.run("calc", shell=True)
        return "Opening Calculator."

    if "open cmd" in text or "command prompt" in text:
        subprocess.run("start cmd", shell=True)
        return "Opening Command Prompt."

    if "open vscode" in text:
        subprocess.run("code", shell=True)
        return "Opening VS Code."

    # FOLDERS
    if "open downloads" in text:
        os.startfile(os.path.expanduser("~/Downloads"))
        return "Opening Downloads."

    if "open documents" in text:
        os.startfile(os.path.expanduser("~/Documents"))
        return "Opening Documents."

    if "open desktop" in text:
        os.startfile(os.path.expanduser("~/Desktop"))
        return "Opening Desktop."

    if "open project folder" in text:
        os.startfile(r"E:\vscode\Python\voice_ai_whisper")
        return "Opening project folder."

    # DRIVES
    if "open drive c" in text:
        os.startfile("C:\\")
        return "Opening C drive."

    if "open drive d" in text:
        os.startfile("D:\\")
        return "Opening D drive."

    # SYSTEM CONTROL
    if "shutdown" in text:
        subprocess.run("shutdown /s /t 5", shell=True)
        return "Shutting down."

    if "restart" in text:
        subprocess.run("shutdown /r /t 5", shell=True)
        return "Restarting."

    # IDENTITY
    if "who are you" in text:
        return "I am Robo, your voice assistant."

    if "what can you do" in text:
        return "I can open apps, search the web, manage files, and answer questions."

    # 🔥 DYNAMIC APP OPEN
    if text.startswith("open "):
    	app = text.replace("open ", "").strip()

    	# Fix common app names
    	if app in ["vs code", "visual studio code"]:
        	app = "code"

    	if app == "chrome":
        	app = "chrome"

    	try:
        	subprocess.Popen(f"start {app}", shell=True)
        	return f"Opening {app}."
    	except Exception:
        	return f"I couldn't open {app}."

# ===============================
# 🧠 GROQ WITH ERROR HANDLING
# ===============================
def ask_groq(text):
    global conversation_history

    conversation_history.append({"role": "user", "content": text})
    conversation_history = conversation_history[-6:]

    set_state("THINKING")

    try:
        response = client.responses.create(
            model="openai/gpt-oss-20b",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_history,
            ],
        )

        reply = response.output_text.strip()

    except Exception:
        return "Sorry, I couldn't process that right now."

    conversation_history.append({"role": "assistant", "content": reply})
    conversation_history = conversation_history[-6:]

    return reply

# ===============================
# 📊 LATENCY
# ===============================
def print_latency_report(transcribe_time, route_time, llm_time):
    total_delay = transcribe_time + route_time + llm_time
    print(Fore.CYAN + "\n========== LATENCY ==========")
    print(f"Transcribe : {transcribe_time:.2f}s")
    print(f"Route      : {route_time:.4f}s")
    print(f"LLM        : {llm_time:.2f}s")
    #print(f"TTS        : {tts_time:.2f}s")
    print(f"─────────────────────────")
    print(f"Total delay: {total_delay:.2f}s  ← wait time after you spoke")
    print("=============================\n")

# ===============================
# 🚀 MAIN
# ===============================
def main():
    speak("Robo is online.")

    porcupine = pvporcupine.create(
        access_key=PICOVOICE_ACCESS_KEY,
        keywords=[WAKE_WORD],
    )

    with sd.RawInputStream(
        samplerate=porcupine.sample_rate,
        blocksize=porcupine.frame_length,
        dtype="int16",
        channels=1,
    ) as stream:

        set_state("IDLE")
        print("Listening...")

        while True:
            pcm = stream.read(porcupine.frame_length)[0]
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm)

            if result >= 0:
                set_state("WAKE_DETECTED")
                speak("Yes, how can I help?")

                command, transcribe_time = record_command()

                if not command:
                    speak("I didn't catch that.")
                    continue

                print("Command:", command)

                if command.lower() in {"exit", "quit", "stop"}:
                    speak("Shutting down.")
                    break

                set_state("ROUTING")
                route_start = time.time()
                local_reply = handle_local_command(command)
                route_time = time.time() - route_start

                llm_time = 0.0

                if local_reply:
                    reply = local_reply
                    print("Route: LOCAL")
                else:
                    print("Route: LLM")
                    llm_start = time.time()
                    reply = ask_groq(command)
                    llm_time = time.time() - llm_start

                print("Assistant:", reply)

                tts_start = time.time()
                speak(reply)
                tts_time = time.time() - tts_start

                print_latency_report(transcribe_time, route_time, llm_time)

                set_state("IDLE")

    porcupine.delete()

if __name__ == "__main__":
    main()