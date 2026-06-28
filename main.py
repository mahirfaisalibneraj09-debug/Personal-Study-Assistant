import sys
import csv
import time
import subprocess
import spacy
import os
import pyautogui
import re
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import webbrowser
import urllib.parse
from pytube import Search
import pyttsx3
import logging

# ==========================================
# SYSTEM SETUP & PATCHES
# ==========================================
logging.getLogger("pytube").setLevel(logging.CRITICAL)
nlp = spacy.load("en_core_web_sm")
vscode_path = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe")
words_to_remove = ["open youtube and play", "play", "please", "please play"]
app_paths = {
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "notepad": r"C:\Windows\System32\notepad.exe",
    "calculator": "calc.exe"
}

# Subprocess patch for Windows sounddevice
if sys.platform == "win32":
    original_popen_init = subprocess.Popen.__init__
    def patched_popen_init(self, *args, **kwargs):
        if kwargs.get('stdin') is None:
            kwargs['stdin'] = subprocess.DEVNULL
        if kwargs.get('stdout') is None:
            kwargs['stdout'] = subprocess.PIPE
        if kwargs.get('stderr') is None:
            kwargs['stderr'] = subprocess.PIPE
        original_popen_init(self, *args, **kwargs)
    subprocess.Popen.__init__ = patched_popen_init

# ==========================================
# CORE FUNCTIONS
# ==========================================
def ask_question(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def set_volume(sound):
    sound_decrease = ["decrease", "lower", "quieter", "down"]
    sound_increase = ["increase", "higher", "louder", "up"]
    for word in sound_increase:
        if word in sound:
            return 0.25
    for word in sound_decrease:
        if word in sound:
            return -0.25
    return 0

def opening_app(app):
    for app_name in app_paths:
        if app_name in app.lower():
            try:
                os.startfile(app_paths[app_name])
                print(f"Opening {app_name}...")
                return True
            except FileNotFoundError:
                print(f"Error: Could not find the file for {app_name}")
                return False
    return False

def command_to_search(m):
    doc = nlp(m)
    m_01 = m.lower()
    if any(word in m_01 for word in words_to_remove):
        for word in words_to_remove:
            if word in m_01:
                m_01 = m_01.replace(word, "").strip()
    elif doc.ents:
        m_01 = doc.ents[0].text
    return m_01

def play_on_yt(r):
    s = Search(r)
    i = 0
    print("\nHere are your recommendations: ")
    while i < 5:
        video = s.results[i]
        print(f"{i+1}. {video.title}")
        i += 1
        
    ask_question("Which one will you prefer to play?")
    try:
        number = int(input("Enter number (1-5): "))
        first_video = s.results[number-1]
    except (ValueError, IndexError):
        print("Invalid choice, defaulting to the first video.")
        first_video = s.results[0]
        
    watch_url = first_video.watch_url
    print(f"Playing video: {first_video.title}")
    webbrowser.open(watch_url)

def speech():
    r = sr.Recognizer()
    sample_rate = 48000  
    duration = 5       

    try:
        default_device = sd.default.device[0]  
    except Exception:
        default_device = None  
    print("\n[🎙️ Listening for 5 seconds...]")
    audio_data = sd.rec(
        int(duration * sample_rate), 
        samplerate=sample_rate, 
        channels=1, 
        dtype='int16', 
        device=default_device
    )
    sd.wait() 

    audio_bytes = audio_data.tobytes()
    audio = sr.AudioData(audio_bytes, sample_rate, 2) 

    try:
        r.energy_threshold = 300 
        r.dynamic_energy_threshold = True
        text_01 = r.recognize_google(audio).lower()
        return text_01
    except (sr.RequestError, sr.UnknownValueError):
        print("[Silence or unintelligible]")
        return ""

def pit_stop():
    filename = 'course_tracking.csv'
    rows = []
    current_task = None
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
            
    for row in rows:
        if row['lecture_status'] != 'Done' or row['homework_status'] != 'Done':
            current_task = row
            break
            
    if not current_task:
        ask_question("You have completed all modules in the database. Great job.")
        return

    if current_task['lecture_status'] != 'Done':
        ask_question("how long do you want to study? ")

        time_01=int(input("how long do you want to study? "))
        ask_question(f"Opening lecture for {current_task['course']} {current_task['title']}. See you in one hour.")
        webbrowser.open(current_task['url'])
        time.sleep(time_01)
        
        pyautogui.press('space') 
        pyautogui.hotkey('alt', 'tab') 
        
        ask_question("Time is up. Are you done with the video?")
        ans = speech()
        
        if ans and "yes" in ans.lower():
            current_task['lecture_status'] = 'Done'
            ask_question("Great. Do you want another 1-hour block for the homework?")
            ans_2 = speech()
            if ans_2 and "yes" in ans_2.lower():
                ask_question("Starting homework block.")
            else:
                ask_question("You did great today boss,, See you next time.")
        else:
            ask_question("You did great today boss,, See you next time.")

    elif current_task['homework_status'] != 'Done':
        ask_question("Starting homework session. Opening CS50 and your playlist.")
        ask_question("how long do you want to study? ")
        time_01=int(input("how long do you want to study? "))
        webbrowser.open("https://www.youtube.com/watch?v=VJxppgsHjF8&list=RDVJxppgsHjF8&start_radio=1")
        webbrowser.open("https://cs50.harvard.edu/x/2026/")
        time.sleep(time_01)
        
        pyautogui.press('space')
        pyautogui.hotkey('alt', 'tab')
        
        ask_question("Time is up. Are you done with the homework?")
        ans = speech()
        
        if ans and ("already done" in ans.lower() or "yes" in ans.lower()):
            current_task['homework_status'] = 'Done'
            print("You earned a deserved break Mahir.")
            ask_question("You earned a deserved break Mahir.")
        else:
            ask_question("You did great job today boss,, See you next time.")

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# ==========================================
# MAIN LOOP
# ==========================================

def main():
    ask_question("The program has started")
    text_01 = ""
    r = sr.Recognizer()
    r.energy_threshold = 300 
    r.dynamic_energy_threshold = True
    opener=["hey", "hello", "start", "jarvis"]
    ender=["stop", "end", "close", "finish", "done"]
    # WAKE WORD LOOP
    while True:
        while not any(word in text_01.lower() for word in opener):  
            sample_rate = 48000  
            duration = 5       
            try:
                default_device = sd.default.device[0]  
            except Exception:
                default_device = None  

            audio_data = sd.rec(
                int(duration * sample_rate), 
                samplerate=sample_rate, 
                channels=1, 
                dtype='int16', 
                device=default_device
            )
            sd.wait() 
            
            audio_bytes = audio_data.tobytes()
            audio = sr.AudioData(audio_bytes, sample_rate, 2) 
            try:
                text_01 = r.recognize_google(audio).lower()
                if any(word in text_01 for word in opener):
                    text_01=""
                    print("Trigger word detected!")
                    ask_question("Hey, My name is Jarvis... How can I help you?")
                    speech_01 = speech()
                    if not speech_01:
                        continue
                        
                    print(f"Your message was: {speech_01}")
                    pit_word=["pit stop", "pitstop", "study session", "study"]
                    if any(word in speech_01.lower() for word in pit_word):
                        pit_stop()
                        break
                    elif "volume" in speech_01:
                        try:
                            volume_change = set_volume(speech_01)
                            if volume_change == .25:
                                for i in range(5):
                                    pyautogui.press('volumeup')
                            elif volume_change == -.25:
                                for i in range(5):
                                    pyautogui.press('volumedown')
                            else:
                                ask_question("what are u saying, man? we cant do it.")
                            break
                        except Exception:
                            print("wrong command")
                            ask_question("wrong command")
                    elif "open" in speech_01 and "youtube" not in speech_01 and "play" not in speech_01:
                        success = opening_app(speech_01)
                        if not success:
                            print("app not found")
                            
                    elif "shut down" in speech_01 or "stop" in speech_01 and "pit" not in speech_01:
                        ask_question("Shutting down. See you later.")
                        break 
                    elif "practice" in speech_01:
                        ask_question("how long do you want to practise? ")
                        time_01=int(input("how long do you want to practise? "))
                        webbrowser.open("https://www.youtube.com/watch?v=VJxppgsHjF8&list=RDVJxppgsHjF8&start_radio=1")
                        webbrowser.open("https://www.keybr.com/")
                        time.sleep(time_01)
                        break
                    else:
                        command_01 = command_to_search(speech_01)
                        if command_01.startswith("Caught either UnknownValueError"):
                            ask_question("Sorry we can't proceed")
                            break
                        play_on_yt(command_01)
                        break
                elif any(word in text_01.lower() for word in ender):
                    ask_question("We are done for now. Goodbye boss,, see you later")
                    return
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"Network error: {e}")
if __name__ == "__main__":
    main()
