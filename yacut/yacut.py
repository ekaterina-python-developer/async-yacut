from flask import flash, redirect, render_template, request
from . import app, db
from .error_handlers import ShortLinkGenerationError
from .forms import LinkForm, FileUploadForm
from .models import URLMap

from .yandex_disk import upload_multiple_files
import asyncio


@app.route('/', methods=('GET', 'POST'))
def index_view():
    """Главная страница для создания коротких ссылок."""
    form = LinkForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)
    try:
        return render_template(
            'index.html',
            form=form,
            link=URLMap.create(
                original=form.original_link.data,
                short=form.custom_id.data,
            ).short_link()
        )
    except (ValueError, ShortLinkGenerationError) as error:
        flash(str(error))
        return render_template('index.html', form=form)


@app.route('/<string:short>', methods=('GET',))
def redirect_short_link(short):
    """Перенаправляет с короткой ссылки на оригинальную."""
    url_map = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map.original)


@app.route('/files', methods=('GET', 'POST'))
def files():
    """Страница загрузки файлов на Яндекс.Диск."""
    form = FileUploadForm()
    links = []
    if request.method == 'GET' or not form.validate_on_submit():
        return render_template('files.html', form=form, links=links)
    files_list = request.files.getlist('files')
    try:
        upload_results = asyncio.run(upload_multiple_files(files_list))
    except Exception as error:
        flash(f'Ошибка загрузки: {error}', 'danger')
        return render_template('files.html', form=form, links=links)
    for upload_result in upload_results:
        view_url = upload_result.get('view_url')
        file_name = upload_result.get('file_name')
        if not view_url or not file_name:
            continue
        url_map = URLMap(
            original=view_url,
            short=URLMap.get_unique_short()
        )
        url_map.is_file = True
        url_map.file_name = file_name
        try:
            db.session.add(url_map)
            db.session.commit()
            links.append(url_map)
        except Exception as error:
            db.session.rollback()
            flash(f'Ошибка сохранения файла {file_name}: {error}', 'danger')
    if links:
        flash('Файлы успешно загружены!', 'success')
    return render_template('files.html', form=form, links=links)