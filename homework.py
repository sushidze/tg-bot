import time
import logging
import sys

import telegram
from dotenv import load_dotenv
import os
import requests

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 6
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляем сообщение в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(
            f'В чат {TELEGRAM_CHAT_ID} отправлено сообщение {message}.'
        )
    except telegram.TelegramError:
        logging.error(
            f'Ошибка при отправке сообщения в чат {TELEGRAM_CHAT_ID}.'
        )


def get_api_answer(current_timestamp):
    """Запрос к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params
    )
    if response.status_code != 200:
        raise requests.ConnectionError(response.status_code)
    return response.json()


def check_response(response):
    """Проверка ответа API на корректность."""
    if type(response) is not dict:
        logger.error('Ответ API не словарь.')
        raise TypeError('Ответ API не словарь.')
    homeworks = response['homeworks']
    if type(homeworks) is not list:
        logger.error('Не получили список домашних работ.')
        raise TypeError('Не получили список домашних работ.')
    return homeworks


def parse_status(homework):
    """Получение информации о конкретной домашней работе."""
    try:
        homework_name = homework['homework_name']
    except KeyError:
        logging.error('Неверный ответ сервера')
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    if homework_status not in HOMEWORK_STATUSES:
        message = 'Недокументированный статус домашней работы'
        raise KeyError(message)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяем доступность переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())
        cash = ''
        while True:
            try:
                response = get_api_answer(current_timestamp)
                current_timestamp = response['current_date']
                time.sleep(RETRY_TIME)

            except requests.ConnectionError as error:
                logging.error(f'{error} Эндпоинт {ENDPOINT} недоступен.')
            else:
                homework = check_response(response)[0]
                message = parse_status(homework)
                if cash != message:
                    cash = message
                    send_message(bot, message)
                    logging.info('Сообщение о статусе ДЗ отправлено в чат')
    else:
        logging.critical(f'Введены не все токены.')


if __name__ == '__main__':
    main()
