from flask_wtf import FlaskForm
from wtforms import SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp, URL

from flask_wtf.file import FileField, FileRequired, FileAllowed

from constants import (MAX_ORIGINAL_LENGTH, MIN_ORIGINAL_LENGTH,
                       SHORT_PATTERN, USER_LINK_LIMIT)


class LinkForm(FlaskForm):
    """Форма для создания коротких ссылок."""

    original_link = URLField(
        'Длинная ссылка',
        validators=(
            DataRequired(message='Обязательное поле'),
            URL(message='Некорректный URL'),
            Length(MIN_ORIGINAL_LENGTH, MAX_ORIGINAL_LENGTH)
        )
    )
    custom_id = URLField(
        'Добавьте свой вариант короткой ссылки',
        validators=(
            Optional(),
            Length(
                max=USER_LINK_LIMIT,
                message='Слишком длинная ссылка'
            ),
            Regexp(SHORT_PATTERN, message='Разрешены только латиница и цифры'),
        )
    )
    submit = SubmitField('Создать ссылку')


class FileUploadForm(FlaskForm):
    """Форма для загрузки файлов на Яндекс.Диск."""

    files = FileField(
        'Выберите файлы для загрузки',
        validators=(
            FileRequired(
                message='Выберите хотя бы один файл'),
            FileAllowed(
                ('jpg',
                 'jpeg',
                 'png',
                 'gif',
                 'pdf',
                 'doc',
                 'docx',
                 'txt'),
                message='Недопустимый тип файла')),
        render_kw={
            'multiple': True})
    submit = SubmitField('Загрузить файлы')
