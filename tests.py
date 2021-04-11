from googletrans import Translator
from typing import List

def tr(language: str, message: str) -> List[str]:
    """ Translates a message into another language.
    :param language: The language to translate the message to.
    :param message: The message to translate.
    :return: A translated message. """

    print(language, message)
    trans = Translator(service_urls=['translate.googleapis.com'])

    try:
        translation = trans.translate(message, dest=language)
        print(translation)
    except ValueError as e:
        print('Value Error:', e)

    else:
        print('AH')
        return translation.src, translation.dest, translation.text

message = tr(language="en", message="Das ist wirklich")
# print(message)

# pip uninstall googletrans
# git clone https://github.com/alainrouillon/py-googletrans.git
# cd ./py-googletrans
# git checkout origin/feature/enhance-use-of-direct-api
# python setup.py install