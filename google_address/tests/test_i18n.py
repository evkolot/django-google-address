from django.test import TestCase
from django.test.utils import override_settings

from google_address.models import Address


@override_settings(
    GOOGLE_ADDRESS={'API_LANGUAGE': 'uk', 'API_KEY': 'AIzaSyBHiZluBD8Mrf4NESx4Zy8PFz5mRnUySlw', 'I18N': ['ru']}
)
class AddressModelWithI18NTestCase(TestCase):
    def test_api_call(self):
        """Assert Address calls google API and get address"""
        a = Address(raw="Киев")
        a.save()

        a = Address.objects.get(pk=a.pk)
        self.assertTrue(a.raw == "Киев")
        self.assertTrue(a.address_line == "місто Київ, Україна")
        self.assertTrue(a.__str__() == "місто Київ, Україна")
        self.assertTrue(a.lat)
        self.assertTrue(a.lng)

        a_comp = a.address_components.cities().first()
        self.assertTrue(a_comp.i18n.long_name_ru == "Киев")
        self.assertTrue(a_comp.i18n.select_language('ru').long_name == "Киев")
        self.assertTrue(a_comp.i18n.long_name_uk == "Київ")
        self.assertTrue(a_comp.i18n.select_language('uk').long_name == "Київ")
