from django.test import TestCase
from django.utils import translation
from siba.translation import translate


class TestLocaleFile(TestCase):

    def test_existing_locale_file(self):
        translation.activate("en")
        text = translate("phrase.hello")
        self.assertEqual(text, "Hello")

        translation.activate("fa")
        text = translate("phrase.hello")
        self.assertIsNotNone(text)
        self.assertNotEqual(text, "Hello")

    def test_missing_locale_file(self):
        translation.activate("it")
        with self.assertRaises(FileNotFoundError):
            translate("phrase.hello")

