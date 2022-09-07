import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv
import exceptions

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


RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляем сообщение в чат."""
    bot.send_message(TELEGRAM_CHAT_ID, message)


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
        raise exceptions.AnswerNot200(response.status_code, params)
    return response.json()


def check_response(response):
    """Проверка ответа API на корректность."""
    if not isinstance(response, dict):
        raise exceptions.AnswerNotDict('Ответ API не словарь.')
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise exceptions.Homeworksnotlist
    if homeworks:
        return homeworks


def parse_status(homework):
    """Получение информации о конкретной домашней работе."""
    if 'homework_name' not in homework:
        raise exceptions.DictIsNotCorrect
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    if homework_status not in HOMEWORK_STATUSES:
        raise exceptions.StatusIsNotCorrect
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяем доступность переменных окружения."""
    return_value = all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])
    if not return_value:
        raise exceptions.NotAllTokens
    return return_value


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time() - 12000000)
    cash = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response['current_date']
            homeworks = check_response(response)
            if homeworks:
                homework = homeworks[0]
                message = parse_status(homework)
                if cash != message:
                    cash = message
                    send_message(bot, message)
                    logger.info('Сообщение о статусе ДЗ отправлено в чат')
        except exceptions.AnswerNot200 as error:
            logger.error(f'{error} Эндпоинт {ENDPOINT} недоступен.')
        except exceptions.AnswerNotDict:
            logger.error('Ответ API не словарь.')
        except exceptions.Homeworksnotlist:
            logger.error('Не получили список домашних работ.')
        except exceptions.DictIsNotCorrect:
            logger.error('Неверный ответ сервера')
        except exceptions.StatusIsNotCorrect:
            logging.error('Недокументированный статус домашней работы')
        except exceptions.NotAllTokens:
            logger.critical('Введены не все токены.')
        except exceptions.ErrorMessage:
            logger.error(
                f'Ошибка при отправке сообщения в чат {TELEGRAM_CHAT_ID}.'
            )
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
