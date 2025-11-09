from flask import jsonify, request
from http import HTTPStatus

from yacut import app
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap
from constants import EMPTY_BODY, NO_URL_ERROR, SHORT_NOT_FOUND


@app.route('/api/id/', methods=('POST',))
def new_short():
    """Создание новой короткой ссылки."""
    request_data = request.get_json(silent=True)

    if request_data is None:
        raise InvalidAPIUsage(EMPTY_BODY)
    if 'url' not in request_data:
        raise InvalidAPIUsage(NO_URL_ERROR)

    try:
        url_map = URLMap.create(
            original=request_data['url'],
            short=request_data.get('custom_id')
        )
    except (RuntimeError, ValueError) as error:
        raise InvalidAPIUsage(str(error)) from error

    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short>/', methods=('GET',))
def api_redirect_short_link(short):
    """Возвращает информацию о короткой ссылке по её идентификатору."""
    url_map = URLMap.get(short)
    if url_map is None:
        raise InvalidAPIUsage(SHORT_NOT_FOUND, HTTPStatus.NOT_FOUND)
    return jsonify(url_map.to_dict(True))
