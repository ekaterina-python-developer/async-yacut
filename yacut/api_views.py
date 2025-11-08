from flask import jsonify, request
from http import HTTPStatus

from yacut import app
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap
from settings import EMPTY_BODY, NO_URL_ERROR, SHORT_NOT_FOUND


@app.route('/api/id/', methods=('POST',))
def new_short():
    """Создание новой короткой ссылки"""
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage(EMPTY_BODY)
    if 'url' not in data:
        raise InvalidAPIUsage(NO_URL_ERROR)
    try:
        return jsonify(
            URLMap.create(
                original=data['url'],
                short=data.get('custom_id')
            ).to_dict()
        ), HTTPStatus.CREATED
    except (RuntimeError, ValueError) as error:
        raise InvalidAPIUsage(str(error))


@app.route('/api/id/<string:short>/', methods=('GET',))
def api_redirect_short_link(short):
    url_map = URLMap.get(short)
    if url_map is None:
        raise InvalidAPIUsage(SHORT_NOT_FOUND, HTTPStatus.NOT_FOUND)
    return jsonify(url_map.to_dict(True)), HTTPStatus.OK
