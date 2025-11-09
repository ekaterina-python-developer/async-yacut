from http import HTTPStatus 
from flask import jsonify, render_template 
from . import app 


class APIException(Exception):
    """Базовое исключение для всех API ошибок."""


class InvalidAPIUsage(APIException): 
    """Кастомное исключение для API ошибок.""" 
    
    status_code = HTTPStatus.BAD_REQUEST 

    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST): 
        super().__init__() 
        self.message = message 
        self.status_code = status_code 

    def to_dict(self): 
        """Возвращает ошибку в виде словаря.""" 
        return {'message': self.message} 


class ShortLinkGenerationError(APIException): 
    """Ошибка генерации уникального короткого идентификатора."""


class YandexDiskAPIError(APIException):
    """Базовое исключение для ошибок API Яндекс.Диска"""


class UploadURLGetError(YandexDiskAPIError):
    """Ошибка получения URL для загрузки"""


class UploadHrefError(YandexDiskAPIError):
    """Ошибка получения upload_href"""

@app.errorhandler(HTTPStatus.NOT_FOUND) 
def page_not_found(error): 
    """Обрабатывает ошибку 404.""" 
    return render_template('404.html'), HTTPStatus.NOT_FOUND 

@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_error(error):
    """Обрабатывает ошибку 500."""
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR

@app.errorhandler(APIException) 
def handle_api_exception(error): 
    """Обрабатывает все API-исключения."""
    if isinstance(error, InvalidAPIUsage):
        return jsonify(error.to_dict()), error.status_code 
    return jsonify({'message': 'Internal server error'}), HTTPStatus.INTERNAL_SERVER_ERROR