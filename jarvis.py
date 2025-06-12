import os
import speech_recognition as sr
import pyttsx3
import webbrowser
import keyboard
import requests
import time
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk, ImageSequence
import ctypes
import pyautogui
import threading
import datetime
import smtplib
import imaplib
import email
from email.message import EmailMessage
from credentials import GEMINI_API_KEY, EMAIL_ADDRESS, EMAIL_PASSWORD


GIF_PATH = r"C:\Users\DELL\Documents\Tushar\AI-GIF.gif"

# === SPEECH SETUP ===
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 175)

# === GUI SETUP ===
window = tk.Tk()
window.title("Jarvis - AI Assistant")
window.attributes("-fullscreen", True)

gif = Image.open(GIF_PATH)
frames = [ImageTk.PhotoImage(frame.copy().convert('RGBA')) for frame in ImageSequence.Iterator(gif)]
frame_count = len(frames)

bg_label = tk.Label(window)
bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

def animate_gif(index):
    frame = frames[index]
    bg_label.config(image=frame)
    window.after(100, animate_gif, (index + 1) % frame_count)

animate_gif(0)

chat_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Consolas", 14), bg="black", fg="white", insertbackground="white")
chat_area.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.35)
chat_area.config(state='disabled')

def update_chat(message, sender="Jarvis"):
    chat_area.config(state='normal')
    chat_area.insert(tk.END, f"{sender}: {message}\n")
    chat_area.yview(tk.END)
    chat_area.config(state='disabled')

def speak(text):
    update_chat(text)
    engine.say(text)
    engine.runAndWait()


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Auto-noise adjustment
        print("Listening...")
        update_chat("🎙️ Listening...", "System")
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)  # Shortened wait times
            command = recognizer.recognize_google(audio)
            update_chat(command, "Tushar")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn’t catch that.")
            return ""
        except sr.WaitTimeoutError:
            speak("No voice detected.")
            return ""
        except sr.RequestError:
            speak("Google services not responding.")
            return ""


def telltime():
    now = datetime.datetime.now()
    hour = now.strftime("%I")
    minute = now.strftime("%M")
    period = now.strftime("%p")
    speak(f"The time is {int(hour)} hours and {int(minute)} minutes {period}")

def find_and_open_file(keyword, drive_letter="C"):
    speak(f"Searching for {keyword} in {drive_letter} drive...")
    for root, dirs, files in os.walk(f"{drive_letter}:/"):
        for file in files:
            if keyword.lower() in file.lower():
                full_path = os.path.join(root, file)
                os.startfile(full_path)
                speak(f"Opening {file}")
                return
    speak("File not found.")

def send_email(receiver, content):
    try:
        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = "Voice Assistant Message"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = receiver

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        speak("Email has been sent.")
    except Exception as e:
        speak("Sorry, I couldn't send the email.")
        print("Email Error:", e)

def read_emails():
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')
        mail_ids = messages[0].split()

        if not mail_ids:
            speak("No new emails.")
            return

        for num in mail_ids[:5]:
            status, msg_data = mail.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["subject"]
                    sender = msg["from"]
                    speak(f"Email from {sender} says: {subject}")
        mail.logout()
    except Exception as e:
        speak("Couldn't read emails.")
        print("Email read error:", e)

def ask_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    params = {"key": GEMINI_API_KEY}
    try:
        response = requests.post(url, headers=headers, json=data, params=params)
        response.raise_for_status()
        gemini_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        speak(gemini_text)
    except Exception as e:
        speak("Sorry, I had trouble reaching Gemini.")
        print("Gemini error:", e)

def control_pc(command):
    if "volume up" in command:
        for _ in range(5): pyautogui.press("volumeup")
        speak("Increased volume.")
    elif "volume down" in command:
        for _ in range(5): pyautogui.press("volumedown")
        speak("Decreased volume.")
    elif "mute" in command:
        pyautogui.press("volumemute")
        speak("Muted.")
    elif "brightness up" in command:
        pyautogui.press("brightnessup")
        speak("Brightness increased.")
    elif "brightness down" in command:
        pyautogui.press("brightnessdown")
        speak("Brightness decreased.")
    elif "lock" in command:
        speak("Locking your computer.")
        ctypes.windll.user32.LockWorkStation()
    elif "shutdown" in command:
        speak("Shutting down the system.")
        os.system("shutdown /s /t 1")
    elif "restart" in command:
        speak("Restarting the system.")
        os.system("shutdown /r /t 1")
    elif "time" in command:
        telltime()
    else:
        return False
    return True

def search_google(query):
    speak(f"Searching Google for {query}")
    webbrowser.open(f"https://www.google.com/search?q={query}")

def open_app(app_name):
    speak(f"Opening {app_name}")
    keyboard.press('win')
    time.sleep(0.5)
    keyboard.release('win')
    time.sleep(0.5)
    keyboard.write(app_name)
    time.sleep(1)
    keyboard.press_and_release('enter')

def close_app():
    speak("Closing the application.")
    keyboard.press_and_release('alt+f4')

def respond_to_command(command):
    if control_pc(command):
        return True
    elif 'search google' in command:
        query = command.replace('search google', '').strip()
        search_google(query)
    elif "open" in command and "drive" in command:
        words = command.split()
        keyword = words[2]
        drive_letter = words[-2].upper() if words[-1].lower() == "drive" else "C"
        find_and_open_file(keyword, drive_letter)
    elif "send an email to" in command:
        try:
            parts = command.split("saying")
            recipient = parts[0].replace("send an email to", "").strip()
            message = parts[1].strip()
            send_email("recipient_email@example.com", message)  # Map actual name to email if needed
        except:
            speak("Couldn't understand the email content.")
    elif "read my emails" in command or "read new emails" in command:
        read_emails()
    elif 'open' in command:
        app_name = command.replace('open', '').strip()
        open_app(app_name)
    elif 'close' in command:
        close_app()
    elif 'bye' in command or 'goodbye' in command:
        speak("Goodbye Tushar! See you soon.")
        return False
    else:
        ask_gemini(command)
    return True

def run_jarvis():
    speak("Hello,How can I assist you today?")
    while True:
        command = listen()
        if command == "":
            continue
        if not respond_to_command(command):
            break

threading.Thread(target=run_jarvis, daemon=True).start()

def exit_fullscreen(event=None):
    window.attributes("-fullscreen", False)

window.bind("<Escape>", exit_fullscreen)
window.mainloop()
