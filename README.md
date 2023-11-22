# Siba

Siba (coming from [_Sibawayh_](https://en.wikipedia.org/wiki/Sibawayh)) is a Django translation tool that uses `json` files instead of `gettext (po, mo)`.

**Features**:

- Support for nested keys
- Reads current locale from Django translation module
- Simple parameter injection to values
- Support for caching locales (loading into memory) to improve performance if needed
- Pluralization: none, one, some, many
- Multiple prefixes (you can have separate translation files for different contexts)
- Lazy loading translations


**What it doesn't do**:


- Right now there is no support to use this library in Django templates. Rest framework should be supported well.


## Requirements

Tested with Python 3.9, but 3.6+ should be supported as well. Django >= 4.2.

## Usage

You can create files with format `{prefix}.{locale}.json` under a directory of your choice so Siba scans them.
For example `application.en.json` should contain `en` locale data for prefix `application` (default). You can change default prefix and directory of locales in settings (read below).

Example json content:

```json
{
  "phrase": {
    "welcomeMessage": "Welcome to application, {username}"
  }
}
```

You can now read this translation using:

```python
from siba.translation import translate, translate_lazy

translate("phrase.welcomeMessage")
translate_lazy("phrase.welcomeMessage")
```

You can directly pass a locale as well:

```python
from siba.translation import translate, translate_lazy

translate("phrase.welcomeMessage", locale="de")
translate_lazy("phrase.welcomeMessage", locale="de")
```

Or change the prefix (reads from a different file):

```python
from siba.translation import translate

# looks in messages.de.json file
translate("phrase.welcomeMessage", prefix="messages", locale="de")  
```

If you don't pass a locale it goes for active translation in Django.
So you don't have to worry if you already change active translation in your middlewares.

```python
from siba.translation import translate
from django.utils import translation

translation.activate("de")
translate("phrase.welcomeMessage")  # looks for de locale
```

And you can inject parameter values

```python
from siba.translation import translate

translate("phrase.welcomeMessage", parameters={"username": "siba"})
```

### Pluralization

Siba supports pluralization. To use it you need at least these two keys defined in your json object for a parent key you want to pluralize:
`one`, `many`.

Through the settings you can enable support for `some`, and it supports `none` by default too.

Example:

```json
{
  "catCounter": {
    "none": "You have no cats! Start to pet one.",
    "one": "You only have a single cat! Get more pets.",
    "some": "Glad to see you have some cats.",
    "many": "I've never seen so many cats bein pets of a single person!"
  }
}
```

Using key argument `p_count` you can determine which translation should be used.

```python
from siba.translation import translate

translate("catCounter")  # You only have a single cat! Get more pets.
translate("catCounter", p_count=0)  # You have no cats! Start to pet one.
translate("catCounter", p_count=1)  # You only have a single cat! Get more pets.
translate("catCounter", p_count=3)  # Glad to see you have some cats.

# Dynamical example:
cats = []
translate("catCounter", p_count=len(cats))
```

## Settings 

You can change the settings by using code below in your `settings.py`.
```python
from siba import set_setting


set_setting(key, value)
```

Setting keys are:

- `error_on_unknown_key`: expects `(bool)`, determines if error should rise when a translation key is missing. 
- `error_on_missing_locale_file`: expects `(bool)`, determines if error should rise when a locale file is missing. 
- `key_split_delimiter`: expects `(str)`, delimiter for keys. 
- `locales_path`: expects `(str)`, directory to find locale files in .
- `cache_locales`: expects `(bool)`, determines if locale data should be cached (loaded into memory). 
- `prefixes`: expects `(list[str])`, list of supported locale file prefixes. 
- `default_prefix`: expects `(str)`, default prefix (currently set to `application`). 
- `locales`: expects `(list[str])`, list of supported locales in the application. 
- `default_locale`: expects `(str)`, the default locale of the application (currently set to `en`).
- `missing_parameter_handler`: expects (`function(key:str)`), callable function to call when a parameter is missing. By default the parameter name is returned.
- `pluralization`: expects `(dict)`, with keys below:
  - `some_enabled`: expects `(bool)`, determines if "some" should be supported
  - `some_limit`: expects `(int)`, determines value which plural will be known as "some" if count is between this number or 1.  

