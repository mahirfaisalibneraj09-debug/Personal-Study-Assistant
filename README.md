# Jarvis: Multimodal Voice Assistant & Study Manager 🎙️

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![CS50P](https://img.shields.io/badge/CS50-Python-red.svg)](https://cs50.harvard.edu/python/)

**Jarvis** is a comprehensive, voice-activated desktop assistant built as a final project for CS50P. It goes beyond simple text-to-speech by integrating natural language processing, system-level audio patching, graphical interface automation, and persistent state management to create a seamless, hands-free workflow environment.

## 🚀 Key Features

* **Continuous Wake-Word Detection:** Listens silently in the background and activates instantly when recognizing trigger words (e.g., "Hey", "Jarvis").
* **Smart Media Control:** Uses spaCy for Natural Language Processing (NLP) to parse commands, strip out conversational filler, and directly search, recommend, and play YouTube videos.
* **System & Application Management:** Opens local applications (Brave, VS Code, Notepad, Calculator) and dynamically controls system volume through simulated keystrokes.
* **"Pit Stop" Automated Study Manager:** A built-in productivity tracker that reads a `course_tracking.csv` database, identifies incomplete lectures or homework, opens the relevant URLs and background music, initiates a timed focus block, and writes updated progress back to the database.

## 🧠 Technical Architecture

This project glues together several complex libraries and handles edge cases for a smooth user experience:
* **Audio Processing:** Utilizes `speech_recognition` and `sounddevice` with NumPy for robust audio capturing. 
* **System-Level Patching:** Includes a custom `subprocess.Popen` patch to resolve known console handle poisoning issues specific to Windows when using `sounddevice`.
* **State Management:** Implements CSV file I/O to track course progress persistently across sessions without requiring a heavy SQL database.
* **NLP & Intent Parsing:** Uses `en_core_web_sm` from spaCy to isolate core entities from spoken commands, allowing for natural, conversational requests.

## ⚙️ Installation & Setup

1. **Clone the repository:**
2. Install the required dependencies:

Bash
pip install -r requirements.txt
Download the spaCy English language model:

Bash
python -m spacy download en_core_web_sm
3.Prepare the database:
Ensure you have a course_tracking.csv file in the root directory with the following headers: course, title, url, lecture_status, homework_status.

🎤 Usage
Run the main script to start the assistant:

Bash
python main.py
Example Voice Commands:

"Hey Jarvis" (Wakes up the assistant)

"Open Brave"

"Increase the volume"

"Play some lo-fi study music on YouTube"

"Start study session" (Triggers the Pit Stop module)

"Practice" (Opens typing practice and background music)

"Shut down"

👤 Author
Mahir Faisal Ibne Raj
   ```bash
   git clone [https://github.com/yourusername/jarvis-assistant.git](https://github.com/yourusername/jarvis-assistant.git)
   cd jarvis-assistant
