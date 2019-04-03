import threading

from google_address.api import GoogleAddressApi
from google_address.models import Address, AddressComponent
from .helpers import get_settings


def update_address(instance):
    response = GoogleAddressApi().query(instance.raw)
    i18n_response = {}
    languages = get_settings().get("I18N", None)

    if len(response["results"]) > 0:
        result = response["results"][0]
        if languages:
            for language in languages:
                language_response = GoogleAddressApi(language=language).query(instance.raw)
                if len(response["results"]) > 0:
                    i18n_response[language] = language_response["results"][0]["address_components"]
    else:
        return False

    instance.address_components.clear()
    for i, api_component in enumerate(result["address_components"]):
        i18n_component_data = {lang: data[i] for lang, data in i18n_response.items()}
        component = AddressComponent.get_or_create_component(api_component, i18n_component_data)
        instance.address_components.add(component)

    try:
        if result["geometry"]:
            Address.objects.filter(pk=instance.pk).update(lat=result["geometry"]["location"]["lat"],
                                                          lng=result["geometry"]["location"]["lng"])
    except:  # pragma: no cover
        pass

    # Using update to avoid post_save signal
    instance.address_line = instance.get_address()
    Address.objects.filter(pk=instance.pk).update(address_line=instance.address_line,
                                                  city_state=instance.get_city_state())


class UpdateThread(threading.Thread):
    def __init__(self, instance):
        self.instance = instance
        threading.Thread.__init__(self)

    def run(self):
        return update_address(self.instance)
