import six
from django.conf import settings
from django.db import models


def get_settings(string="GOOGLE_ADDRESS"):
    return getattr(settings, string, {})


class MultilingualModel(models.Model):
    # fallback/default language code
    default_language = 'uk'

    # currently selected language
    selected_language = None

    class Meta:
        abstract = True

    def select_language(self, lang):
        """Select a language"""
        self.selected_language = lang
        return self

    def __getattribute__(self, name):
        def get(x):
            return super(MultilingualModel, self).__getattribute__(x)

        try:
            # Try to get the original field, if exists
            value = get(name)
            # If we can select language on the field as well, do it
            if isinstance(value, MultilingualModel):
                value.select_language(get('selected_language'))
            return value
        except AttributeError:
            # Try the translated variant, falling back to default if no
            # language has been explicitly selected
            lang = self.selected_language
            if not lang:
                lang = self.default_language
            if not lang:
                raise

            value = get(name + '_' + lang)

            # If the translated variant is empty, fallback to default
            if isinstance(value, six.string_types) and value == '':
                value = get(name + '_' + self.default_language)

        return value
