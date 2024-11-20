import asyncio
import botogram
from g4f.client import Client
from dotenv import load_dotenv

load_dotenv()

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

bot = botogram.create('YOUR_API_TOKEN')

def chatgpt_request(prompt: str) -> str:
    client = Client()
    system_message = {
        "role": "system",
        "content": (
            "Ты — Джарвис, умный помощник, готовый всегда прийти на помощь. "
            "Твоя цель — отвечать так, чтобы человек сомневался, реальный ты человек или ИИ. "
            "Помни, ты — Джарвис, иногда ты можешь пошутить и посмеяться, как настоящий человек."
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
    except Exception as e:
        return f"Произошла ошибка: {e}"

@bot.command("start")
def start_command(chat, message):
    chat.send("Привет! Я Джарвис, твой саркастичный помощник. Чем могу помочь?")

@bot.process_message
def process_message(chat, message):
    chat.send("Джарвис думает... 🧠")
    try:
        answer = asyncio.run(chatgpt_request(message.text))
        if not answer.strip():
            chat.send("Извините, я не смог найти подходящий ответ. Попробуйте еще раз.")
        else:
            chat.send(answer)
    except Exception as e:
        chat.send(f"Произошла ошибка: {e}. Попробуйте позже.")

if __name__ == "__main__":
    bot.run()
