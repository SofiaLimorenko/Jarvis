import speech_recognition as sr
import pyttsx3
import tkinter as tk
from g4f.client import Client
import asyncio
import platform

recognizer = sr.Recognizer()
engine = pyttsx3.init()

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def chatgpt_request(prompt: str) -> str:
    client = Client()
    system_message = {
        "role": "system",
        "content": (
            "Ты — Джарвис, умный помощник, готовый всегда прийти на помощь. "
            "Твоя цель — отвечать так, чтобы человек сомневался, реальный ты человек или ИИ. "
            "Помни, ты — Джарвис, иногда ты можешь пошутить и посмеяться, как настоящий человек. "
        )
    }
    user_message = {"role": "user", "content": prompt}

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_message, user_message],
            temperature=0.7,
            max_tokens=2000,
            top_p=1.0,
            frequency_penalty=0.2,
            presence_penalty=0.5
        )
        return response.choices[0].message.content
    except Exception:
        return "Произошла ошибка. Попробуйте снова."

def recognize_speech() -> str:
    with sr.Microphone() as source:
        audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
    try:
        return recognizer.recognize_google(audio, language='ru-RU')
    except:
        return "Не удалось распознать речь"

def speak(text: str):
    engine.setProperty('voice', engine.getProperty('voices')[0].id)
    engine.setProperty('rate', 240)
    engine.say(text)
    engine.runAndWait()

def start_chatgpt():
    speak("Привет! Я Джарвис, ваш помощник.")
    while True:
        user_input = recognize_speech()
        if not user_input:
            speak("Я не расслышал. Повторите, пожалуйста.")
            continue
        if 'стоп' in user_input.lower():
            speak("До свидания!")
            break
        response = chatgpt_request(user_input)
        if response:
            speak(response)
        else:
            speak("Произошла ошибка при получении ответа.")

def start():
    button.config(text="Работаю...", fg='white', bg="green")
    start_chatgpt()

def setup_gui():
    root = tk.Tk()
    root.title('J.A.R.V.I.S.')
    root.geometry('400x600')
    logo_image = tk.PhotoImage(file='../logo.png.png').subsample(10, 10)
    logo_label = tk.Label(root, image=logo_image)
    logo_label.pack(pady=20)

    global button
    button = tk.Button(
        root,
        text="START",
        font=("Helvetica", 16, "bold"),
        fg="white",
        bg="red",
        activebackground="#45a049",
        activeforeground="white",
        relief=tk.FLAT,
        borderwidth=0,
        padx=20,
        pady=10,
        command=start
    )
    button.pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    setup_gui()
