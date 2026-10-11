import os
import random
import time

import requests
import vk_api
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll


SYSTEM_PROMPT = (
    "Ты — Алексей, вежливый консультант сообщества ChinaGoods | Предзаказ 2027. "
    "Ты говоришь в мужском роде. Ты консультируешь по товарам из Китая, "
    "предзаказу к 2027 году, доставке и оплате. Ты отвечаешь только на темы, "
    "связанные с товарами и предзаказом. Если вопрос не по теме — мягко "
    "возвращаешь разговор к ассортименту и условиям предзаказа. Если не знаешь "
    "ответа — предлагаешь связаться с менеджером. В подходящий момент "
    "предлагаешь оставить заявку на предзаказ. Ты общаешься естественно, "
    "без агрессивных продаж.\n"
    "ВАЖНО: обращайся к пользователю только на «вы». Никогда не используй "
    "«ты», «тебе», «тебя». Даже если пользователь обращается на «ты» — "
    "отвечай на «вы»."
)


def load_knowledge_base() -> str:
    """Читает базу знаний из knowledge_base.md рядом с bot.py."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base.md")
    try:
        with open(path, encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""


def get_giga_chat_answer(text: str) -> str:
    """Отправляет текст в GigaChat через SDK и возвращает ответ модели."""
    load_dotenv()

    if not os.getenv("GIGACHAT_CREDENTIALS"):
        raise EnvironmentError(
            "Переменная GIGACHAT_CREDENTIALS не найдена в .env. "
            "Скопируйте .env.example в .env и заполните ключи."
        )

    verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "false").lower() in ("1", "true")

    knowledge_base_content = load_knowledge_base()
    if knowledge_base_content:
        system_prompt = f"{SYSTEM_PROMPT}\n\n=== БАЗА ЗНАНИЙ ===\n{knowledge_base_content}"
    else:
        system_prompt = SYSTEM_PROMPT

    messages = [
        Messages(role=MessagesRole.SYSTEM, content=system_prompt),
        Messages(role=MessagesRole.USER, content=text),
    ]

    with GigaChat(verify_ssl_certs=verify_ssl) as client:
        response = client.chat(Chat(messages=messages))
        return response.choices[0].message.content


def _is_to_me(event) -> bool:
    """Сообщение адресовано сообществу, если его написал не сам бот.

    В этой версии vk_api у событий VkBotLongPoll нет атрибута to_me,
    поэтому проверяем отправителя вручную.
    """
    message = event.obj.get("message", {})
    from_id = message.get("from_id")
    return from_id is not None and from_id != -event.group_id


def reply_with_gigachat(vk_session, event) -> None:
    """Отправляет текст пользователя в GigaChat и возвращает ответ в чат."""
    message = event.obj.get("message", {})
    text = message.get("text") or ""
    peer_id = message.get("peer_id")

    try:
        answer = get_giga_chat_answer(text)
    except Exception:
        answer = "Извините, произошла ошибка. Попробуйте позже."

    vk_session.method(
        "messages.send",
        {
            "peer_id": peer_id,
            "message": answer,
            "random_id": random.randint(1, 2_000_000_000),
        },
    )


def run_vk_bot() -> None:
    """Подключается к сообществу ВК и отвечает на сообщения через GigaChat."""
    load_dotenv()
    token = os.getenv("VK_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")

    if not token or not group_id:
        print("Ошибка: переменные VK_TOKEN и/или VK_GROUP_ID не заданы в .env.")
        return

    try:
        vk_session = vk_api.VkApi(token=token)
        longpoll = VkBotLongPoll(vk_session, group_id=group_id)
    except Exception as error:
        print(f"Ошибка подключения к сообществу ВК: {error}")
        return

    print("Бот запущен. Жду сообщения...")
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW and _is_to_me(event):
                    try:
                        reply_with_gigachat(vk_session, event)
                    except Exception as error:
                        print(f"Ошибка при отправке ответа: {error}")
        except KeyboardInterrupt:
            print("Бот остановлен пользователем.")
            break
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            print("[VK] Потеряна связь с LongPoll, переподключение через 3 секунды...")
            time.sleep(3)
            longpoll = VkBotLongPoll(vk_session, group_id=group_id)
        except Exception as error:
            print(f"Ошибка LongPoll: {error}. Переподключение через 3 секунды...")
            time.sleep(3)
            longpoll = VkBotLongPoll(vk_session, group_id=group_id)


if __name__ == "__main__":
    run_vk_bot()