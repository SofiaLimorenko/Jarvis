import speech_recognition as sr
import pyttsx3
import tkinter as tk
from g4f.client import Client
import asyncio
import platform
import requests
from bs4 import BeautifulSoup
import os

recognizer = sr.Recognizer()
engine = pyttsx3.init()
size = '500x600'

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def parser(prompt):
    def search_google(query):
        url = f"https://www.google.com/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            if "url?q=" in a['href']:
                link = a['href'].split("url?q=")[1].split("&")[0]
                links.append(link)
        return links

    def extract_data_from_site(url):
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        data = []
        for element in soup.find_all(['h1', 'h2', 'h3', 'p']):
            data.append(element.get_text(strip=True))
        return data
    def save_data_to_downloads_as_txt(data, filename="data.txt"):
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        filepath = os.path.join(downloads_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            for item in data:
                file.write("\n".join(item['data']))
                file.write("\n\n" + "-" * 80 + "\n\n")

        return filepath

    query = prompt
    links = search_google(query)
    all_data = []
    for link in links:
        try:
            data = extract_data_from_site(link)
            all_data.append({"url": link, "data": data})
        except Exception as e:
            continue
    filename = "data.txt"
    file_path = save_data_to_downloads_as_txt(all_data, filename)
    os.startfile(file_path)
    return file_path

def chatgpt_request(prompt: str) -> str:
    client = Client()
    system_message = {
        "role": "system",
        "content": (
            "You are Jarvis, a smart assistant always ready to help. "
            "Your goal is to answer in a way that makes the person doubt whether you're a real human or an AI. "
            "Remember, you're Jarvis, and sometimes you can joke and laugh like a real person. "
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
        return "An error occurred. Please try again."

def recognize_speech() -> str:
    with sr.Microphone() as source:
        audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
    try:
        return recognizer.recognize_google(audio, language='en-US')
    except:
        return "Failed to recognize speech."

def speak(text: str):
    engine.setProperty('voice', engine.getProperty('voices')[0].id)
    engine.setProperty('rate', 240)
    engine.say(text)
    engine.runAndWait()

def start_chatgpt():
    while True:
        user_input = recognize_speech()
        if not user_input:
            speak("I couldn't hear you. Please repeat.")
            continue
        if 'stop' in user_input.lower():
            speak("Goodbye!")
            break
        response = chatgpt_request(user_input)
        if response:
            speak(response)
        else:
            speak("An error occurred while getting the response.")

def setup_gui():
    def open_navigation_window():
        navigation_window.deiconify()
        root.withdraw()

    def open_google_window():
        google_window.deiconify()
        navigation_window.withdraw()

    def open_ai_window():
        ai_window.deiconify()
        navigation_window.withdraw()

    def open_ai_voice_window():
        ai_voice_window.deiconify()
        ai_window.withdraw()

    def back_to_main():
        navigation_window.withdraw()
        root.deiconify()

    def start_voice_chat():
        start_chatgpt()

    def back_to_navigation():
        for window in [google_window, ai_window, ai_voice_window]:
            window.withdraw()
        navigation_window.deiconify()

    root = tk.Tk()
    root.title('J.A.R.V.I.S.')
    root.geometry(size)
    root.resizable(False, False)

    try:
        logo_image = tk.PhotoImage(file='./logo.png').subsample(10, 10)
        logo_label = tk.Label(root, image=logo_image)
        logo_label.pack(pady=20)
    except Exception:
        tk.Label(root, text="J.A.R.V.I.S.", font=("Arial Black", 20), fg="black").pack(pady=20)

    tk.Button(root, text='Start', command=open_navigation_window, width=20, height=2).pack(pady=20)

    navigation_window = tk.Toplevel(root)
    navigation_window.title("J.A.R.V.I.S.")
    navigation_window.geometry(size)
    navigation_window.resizable(False, False)
    navigation_window.withdraw()

    tk.Label(navigation_window, text="Choose an option:", font=("Arial", 14)).pack(pady=20)
    tk.Button(navigation_window, text='Google', command=open_google_window, width=20, height=2).pack(pady=10)
    tk.Button(navigation_window, text='AI', command=open_ai_window, width=20, height=2).pack(pady=10)
    tk.Button(navigation_window, text='<-', command=back_to_main, width=20, height=2).pack(pady=10)

    def send_response():
        user_input = google_input.get().strip()
        if user_input:
            google_output.config(state='normal')
            google_output.insert("end", f"User: {user_input}\n")
            google_output.insert("end", f"Response: {parser(user_input)}\n")
            google_output.config(state='disabled')
            google_input.delete(0, "end")



    google_window = tk.Toplevel(root)
    google_window.title("J.A.R.V.I.S.")
    google_window.geometry(size)
    google_window.resizable(False, False)
    google_window.withdraw()

    tk.Label(google_window, text="Google Input", font=("Arial", 14)).pack(pady=10)
    google_input = tk.Entry(google_window, width=50)
    google_input.pack(pady=10)

    tk.Label(google_window, text="Google Output", font=("Arial", 14)).pack(pady=10)
    google_output = tk.Text(google_window, width=60, height=15)
    google_output.pack(pady=10)
    google_output.config(state='disabled')


    tk.Button(google_window, text="Send", command=send_response).pack(pady=10)
    tk.Button(google_window, text="<-", command=back_to_navigation, width=20, height=2).pack(pady=20)



    ai_window = tk.Toplevel(root)
    ai_window.title("J.A.R.V.I.S.")
    ai_window.geometry(size)
    ai_window.resizable(False, False)
    ai_window.withdraw()

    tk.Label(ai_window, text="Chat with AI", font=("Arial", 14)).pack(pady=10)

    chat_frame = tk.Frame(ai_window)
    chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

    chat_output = tk.Text(chat_frame, height=20, width=60, state='disabled', bg="#f0f0f0")
    chat_output.pack(pady=10)

    chat_input = tk.Entry(chat_frame, width=50)
    chat_input.pack(pady=5)

    def send_ai_message():
        message = chat_input.get().strip()
        if message:
            chat_output.config(state='normal')
            chat_output.insert("end", f"You: {message}\n")
            chat_output.insert("end", f'AI: {chatgpt_request(message)}\n')
            chat_output.config(state='disabled')
            chat_input.delete(0, "end")

    tk.Button(ai_window, text="Send", command=send_ai_message).pack(pady=10)
    tk.Button(ai_window,text='Voice',command=open_ai_voice_window).pack(pady=10)
    tk.Button(ai_window, text="<-", command=back_to_navigation, width=20, height=2).pack(pady=20)


    ai_voice_window = tk.Toplevel(ai_window)
    ai_voice_window.title('J.A.R.V.I.S.')
    ai_voice_window.geometry(size)
    try:
        logo_image1 = tk.PhotoImage(file='./voice.png').subsample(4, 4)
        logo_label1 = tk.Label(ai_voice_window, image=logo_image1)
        logo_label1.pack(pady=20)
    except Exception:
        tk.Label(ai_voice_window, text="J.A.R.V.I.S.", font=("Arial Black", 20), fg="black").pack(pady=20)
    ai_voice_window.resizable(False, False)
    ai_voice_window.withdraw()

    tk.Label(ai_voice_window, text="Tell Jarvis...", font=("Arial", 14)).pack(pady=10)
    tk.Button(ai_voice_window,text='Start',command=start_voice_chat,width=20,height=2).pack(pady=20)
    tk.Button(ai_voice_window,text='<-',command=back_to_navigation,width=20,height=2).pack(pady=20)



    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()

setup_gui()


if __name__ == "__main__":
    setup_gui()