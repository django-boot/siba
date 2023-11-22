from unittest.mock import Mock

from django.test import TestCase
from django.utils import translation

from siba import set_setting
from siba.locale import preload_locales, get_cached_locales, clear_cached_locales, read_locale
from siba.parser import Parsable
from siba.translation import translate, translate_lazy


class TestLocaleFile(TestCase):

    def setUp(self) -> None:
        set_setting("locales", ["en", "fa"])
        set_setting("cache_locales", False)

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

    def test_missing_locale_file_silently(self):
        set_setting("error_on_missing_locale_file", False)
        translation.activate("it")
        with self.assertRaises(KeyError):
            translate("phrase.hello")

    def test_locale_cache_lazy(self):
        set_setting("cache_locales", True)

        mock = Mock()
        mock.load.return_value = {}
        f = lambda: mock
        read_locale("application", "en", loader_class=f)
        mock.load.assert_called_once()

        mock = Mock()
        mock.load.return_value = {}
        f = lambda: mock
        read_locale("application", "en", loader_class=f)
        mock.load.assert_not_called()

    def test_locale_cache_preload(self):
        mock = Mock()
        mock.load.return_value = {}
        f = lambda: mock
        read_locale("application", "en", loader_class=f)
        mock.load.assert_called_once()

        set_setting("locales", ["en", "fa"])
        set_setting("cache_locales", True)
        preload_locales()
        locales = get_cached_locales()
        self.assertIsNotNone(locales)
        self.assertIn("application-en", locales)
        self.assertIn("application-fa", locales)
        self.assertIn("phrase.hello", locales["application-en"])
        self.assertIn("phrase.hello", locales["application-fa"])

        mock = Mock()
        read_locale("application", "en", mock)
        mock.assert_not_called()

        clear_cached_locales()

    def test_formatting(self):
        en_locales = read_locale("application", "en")
        self.assertIn("phrase.hello", en_locales)
        self.assertIn("phrase.welcomeMessage", en_locales)
        self.assertIn("catCounter", en_locales)
        self.assertNotIn("catCounter.none", en_locales)
        self.assertNotIn("catCounter.one", en_locales)
        self.assertNotIn("catCounter.some", en_locales)
        self.assertNotIn("catCounter.many", en_locales)

        self.assertTrue(isinstance(en_locales["catCounter"], Parsable))

    def test_invalid_type(self):
        with self.assertRaises(ValueError) as assertion:
            read_locale("application", "fr")
            self.assertEqual(
                str(assertion.exception),
                "Translation data should either be str or dictionary. Got <class 'list'>"
            )


class TestTranslations(TestCase):

    def setUp(self) -> None:
        set_setting("locales", ["en", "fa"])
        set_setting("cache_locales", False)
        set_setting("error_on_unknown_key", True)

    def test_missing_key_silently(self):
        set_setting("error_on_unknown_key", False)
        translate("missingKey")

    def test_existing_value(self):
        translation.activate("en")
        self.assertEqual(translate("phrase.hello"), "Hello")
        self.assertEqual(translate("phrase.welcomeMessage"), "Welcome dear username.")
        self.assertEqual(translate("catCounter"), "You only have a single cat! Get more pets.")

    def test_parameter_injection(self):
        translation.activate("en")
        value = translate("phrase.welcomeMessage", variables={"username": "siba"})
        self.assertEqual(value, "Welcome dear siba.")

    def test_missing_parameter_handler(self):
        translation.activate("en")
        set_setting("missing_parameter_handler", lambda x: "test")
        self.assertEqual(translate("phrase.welcomeMessage"), "Welcome dear test.")

    def test_lazy(self):
        translation.activate("en")
        self.assertEqual(translate_lazy("phrase.hello"), "Hello")

    def test_default_locale(self):
        translation.deactivate_all()
        self.assertEqual(translate("phrase.hello"), "Hello")

    def test_pluralization(self):
        translation.activate("en")
        self.assertEqual(translate("catCounter"), "You only have a single cat! Get more pets.")
        self.assertEqual(translate("catCounter", p_count=0), "You have no cats! Start to pet one.")
        self.assertEqual(translate("catCounter", p_count=1), "You only have a single cat! Get more pets.")
        self.assertEqual(translate("catCounter", p_count=3), "Glad to see you have some cats.")
        self.assertEqual(
            translate("catCounter", p_count=7), "I've never seen so many cats bein pets of a single person!"
        )

        set_setting("pluralization", {
            "some_enabled": True,
            "some_limit": 8
        })
        self.assertEqual(translate("catCounter", p_count=7), "Glad to see you have some cats.")

