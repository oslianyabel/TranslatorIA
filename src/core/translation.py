from googletrans import Translator
from deep_translator import GoogleTranslator, MyMemoryTranslator
from src.core.common import Audio
from src.core.common.common import EU_languages, iso_code_2_dict
from src.core.common.errors import InvalidInputError

translators = ["GoogleTranslator", "MyMemoryTranslator"]

class Text_Translation:
    """ Base class for text translation models """
    def __init__(self):
        """
        Initialize the translation model
        """
        pass

    def aviable_languages(self) -> list:
        """ 
        Get the aviable languages for the translator
        
        Returns:
            list: A list of str containing the aviable languages. 
        """
        raise NotImplementedError()
    
    # def detect_languge() -> str:
    #     pass

    def translate_text(self, input_text: str, target_lang: str, source_lang: str):
        """
        Translates the input text to the target language.
        
        Args:
            input_text (str): text in the source language.
            target_lang (str): target language for the translation.
            source_lang (str): source language of the input_text.
        """
        raise NotImplementedError()

class Multimodel_translator(Text_Translation):
    """ Translation models based on deep_translator, right now features:  ["GoogleTranslator", "MyMemoryTranslator"] """
    translators = {"GoogleTranslator"   : GoogleTranslator,
                   "MyMemoryTranslator" : MyMemoryTranslator,
                #    "LibreTranslator"    : LibreTranslator # has multiple mirrors which can be used for the API endpoint. Some require an API key to be used.
                   }

    def __init__(self, translator: str="GoogleTranslator"):
        """
        Initialize the translation model

        Args:
            translator (str): translator, must be one of the following:  "GoogleTranslator", "MyMemoryTranslator".
        """
        super().__init__()
        in_dict = self.translators.get(translator)
        if in_dict is None:
            self.translator = GoogleTranslator()
            print("Invalid translator value, default to GoogleTranslator")
        else: 
            # if translator == "LibreTranslator":
            #     self.translator = in_dict(base_url=self.libre_translator_free_url[1])
            # else: 
            self.translator = in_dict()
    
    def aviable_languages(self) -> list:
        """ 
        Get the aviable languages for the translator.
        
        Returns:
            list: A list of str containing the aviable languages. 
        """
        return iso_code_2_dict # TODO intersection between google languages and iso_code_2_dict

    def translate_text(self, input_text: str, target_lang: str, source_lang: str):
        """
        Translates the input text to the target language.
        
        Args:
            input_text (str): text in the source language.
            target_lang (str): target language for the translation.
            source_lang (str): source language of the input_text.
        """
        valid_langs = self.translator.get_supported_languages(as_dict=True)
        
        # if target_lang not in list(valid_langs.keys()):
        if target_lang not in list(valid_langs.values()):
            raise InvalidInputError(f"the target language {target_lang} is not aviable for the current translator. \nAviable languages: {list(valid_langs.values())}")
        # TODO Check if source language and target language are different
        self.translator.target = target_lang
        self.translator.source = source_lang

        translated_text = self.translator.translate(text=input_text)
        return translated_text
    
class Text_Translation_google:
    """ Translation model based on googletrans """
    def __init__(self):
        """
        Initialize the translation model
        """
        self.translator = Translator(service_urls=[
                        'translate.google.com',
                        ])

    def translate_text(self, input_text: str, target_lang: str, source_lang: str='auto'):
        """
        Translates the input text to the target language.
        
        Args:
            input_text (str): text in the source language.
            target_lang (str): target language for the translation.
            source_lang (str): source language of the input_text.
        """
       
        # TODO check if the target language is a valid one. Check if source language and target language are different
        # Translate the text to the target language 
        translated_text = self.translator.translate(input_text, dest=target_lang,src=source_lang)
        # print(translated_text) # TODO remove print
        return translated_text.text

    def aviable_languages(self) -> list:
        """ 
        Get the aviable languages for the translator.
        
        Returns:
            list: A list of str containing the aviable languages. 
        """
        return iso_code_2_dict # TODO intersection between google languages and iso_code_2_dict

