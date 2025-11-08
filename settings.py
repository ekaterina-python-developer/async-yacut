import os
import string
from re import escape


USER_LINK_LIMIT = 16
VALID_SYMBOLS = string.ascii_letters + string.digits
SHORT_PATTERN = f'^[{escape(VALID_SYMBOLS)}]*$'
EMPTY_BODY = 'Отсутствует тело запроса'
INVALID_SYMBOLS = (f'Введены недопустимые символы.'
                   f'Разрешенные символы: {VALID_SYMBOLS}')
NO_URL_ERROR = '"url" является обязательным полем!'
BAD_SHORT = 'Указано недопустимое имя для короткой ссылки'
SHORT_EXIST = 'Предложенный вариант короткой ссылки уже существует.'
SHORT_NOT_FOUND = 'Указанный id не найден'
GENERATION_FAIL = 'Не удалось сгенерировать короткую ссылку'
MAX_ORIGINAL_LENGTH = 1024
MIN_ORIGINAL_LENGTH = 1
SHORT_LENGTH = 6
MAX_ATTEMPTS = 50




class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DISK_TOKEN = os.getenv('DISK_TOKEN')
    