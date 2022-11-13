from wtforms.widgets import html_params

try:
    from wtforms.fields.core import _unset_value as unset_value
except ImportError:
    from wtforms.utils import unset_value

from flask_admin._backwards import Markup
from flask_admin._compat import string_types, urljoin
import ast
from PIL import Image
from wtforms.widgets import html_params
from flask_admin._backwards import Markup
from wtforms.utils import unset_value
from flask_admin.form.upload import ImageUploadField
from flask_admin._compat import string_types, urljoin

try:
    from PIL import Image
except ImportError:
    Image = None
    ImageOps = None

__all__ = ['FileUploadInput', 'FileUploadField',
           'ImageUploadInput', 'ImageUploadField',
           'namegen_filename', 'thumbgen_filename']

class customImageUploadInput(object):
    empty_template = "<input %(file)s multiple>"

    data_template = ('<div class="image-thumbnail">'
                     '%(images)s'
                     '</div>'
                     '<input %(file)s multiple>')

    def __call__(self, field, **kwargs):

        kwargs.setdefault("id", field.id)
        kwargs.setdefault("name", field.name)

        args = {
            "file": html_params(type="file", **kwargs),
            'marker': '_%s-delete' % field.name
        }

        if field.data and isinstance(field.data, string_types):
            string = self.get_attributes(field)
            args['images'] = "&emsp;".join(["<img src='{}' />".format(src, filename) for src, filename in string])
            template = self.data_template

        else:
            template = self.empty_template

        return Markup(template % args)

    def get_attributes(self, field):

        for x in ast.literal_eval(field.data):

            picture = x

            if field.url_relative_path:
                picture = urljoin(field.url_relative_path, picture)

            yield picture, field.data

class customImageUploadField(ImageUploadField):

    widget = customImageUploadInput()

    def process(self, formdata, data=unset_value):

        self.formdata = formdata
        return super(customImageUploadField, self).process(formdata, data)

    def process_formdata(self, valuelist):

        self.data = list()

        for x in valuelist:
            if self._is_uploaded_file(x):
                self.data.append(x)

    def populate_obj(self, obj, name):
        
        field = getattr(obj, name, None)

        if field:

            filenames = ast.literal_eval(field)

            for y in filenames[:]:
                if y + "-delete" in self.formdata:
                    self._delete_file(y)
                    filenames.remove(y)
        else:
            filenames = list()

        for data in self.data:
            if self._is_uploaded_file(data):

                self.image = Image.open(data)

                x = self.generate_name(obj, data)
                x = self._save_file(data, x)

                data.x = x

                filenames.append(x)

        setattr(obj, name, str(filenames))