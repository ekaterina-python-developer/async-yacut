from flask import flash, redirect, render_template, request
from . import app, db
from .error_handlers import ShortLinkGenerationError
from .forms import LinkForm, FileUploadForm
from .models import URLMap

from .yandex_disk import upload_multiple_files
import asyncio

@app.route('/', methods=('GET', 'POST'))
def index_view():
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
    url_map = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map.original)

@app.route('/files', methods=['GET', 'POST'])
def files():
    form = FileUploadForm()
    links = []

    if form.validate_on_submit():
        files = request.files.getlist('files')
        try:
            upload_results = asyncio.run(upload_multiple_files(files))
            for item in upload_results:
                url_map = URLMap(
                    original=item['view_url'],
                    short=URLMap.get_unique_short()
                )
                url_map.is_file = True
                url_map.file_name = item['file_name']
                db.session.add(url_map)
                db.session.commit()
                links.append(url_map)
            flash('Файлы успешно загружены!', 'success')
        except Exception as e:
            flash(f'Ошибка загрузки: {e}', 'danger')

    return render_template('files.html', form=form, links=links)