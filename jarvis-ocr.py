import torch
import cv2
import pyttsx3
import speech_recognition as sr

# Initialize voice engine
engine = pyttsx3.init()
engine.say("Tura: Good Afternoon Tushar! I am Tura, your personal assistant. How may I help you today?")
engine.runAndWait()

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)  # Loads with AutoShape

# Voice recognition setup
recognizer = sr.Recognizer()
mic = sr.Microphone()

def speak(text):
    print("Tura:", text)
    engine.say(text)
    engine.runAndWait()

def detect_object():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("❌ Unable to access the webcam.")
        return

    speak("Please hold the object steadily...")
    ret, frame = cap.read()

    if not ret:
        speak("❌ Failed to capture the frame from the webcam.")
        cap.release()
        return

    # Run YOLOv5 detection
    results = model(frame)

    # Show results visually (optional)
    results.print()
    results.show()

    detected = results.pred[0]  # Tensor: [x1, y1, x2, y2, conf, class]
    labels = results.names

    if detected is not None and len(detected) > 0:
        classes = detected[:, -1].tolist()
        objects = [labels[int(cls)] for cls in classes]
        unique_objects = list(set(objects))
        speak("I detected: " + ", ".join(unique_objects))
    else:
        speak("I couldn't detect any object in your hand.")

    cap.release()
    cv2.destroyAllWindows()

# Main assistant loop
while True:
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening... Please say a command like 'what is in my hand' or 'exit' to quit.")

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            query = recognizer.recognize_google(audio)
            print("You said:", query)

            if "what is in my hand" in query.lower():
                detect_object()
            elif "exit" in query.lower() or "stop" in query.lower():
                speak("Goodbye Tushar. Have a great day!")
                break
            else:
                speak("Sorry, I don't understand that yet. Please try again.")

        except sr.UnknownValueError:
            speak("Sorry Tushar, I could not understand what you said. Please try again clearly.")
        except sr.WaitTimeoutError:
            speak("Timeout: You didn’t say anything. Please try again.")
        except sr.RequestError:
            speak("Network error, please check your internet connection.")
