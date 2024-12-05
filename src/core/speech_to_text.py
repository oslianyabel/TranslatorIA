""" Several speech-to-text (S2T) models"""

from src.core.common import Audio, Phrase, errors
from src.core.common.common import iso_code_2_dict

# import speech_recognition as sr
import whisper
import os
import torch
from pydub import AudioSegment

class S2T_Base:
    """Speech-to-text models base class """
    def __init__(self):
        """
        Initialize the speech-to-text model
        """
        pass

    def get_text(self, source_audio: Audio, language: str, show_all: bool=False):
        """
        Execute the speech-to-text transcription on the audio.
        
        Args:
            source_audio (Audio): a valid Audio object.
            language (str): source_audio language, for correct recognition.
            show_all (bool): if True, all the detais of the transcription will be returned. If False, only the text will be returned.
        """
        raise NotImplementedError()
    
    def supported_languages(self, as_dict: bool=False):
        """
        Show the supported_languages for the current model.

        Args:
            as_dict (bool): if True, the result is a dictionary with the languages and the codes. If False, the result is a list with the codes.
        """
        raise NotImplementedError()

# class S2T_Speech_Recognition(S2T_Base):
#     """Speech-to-text model based on the library SpeechRecognition """
    
#     def __init__(self):
#         super().__init__()
#         self.transcriptor = sr.Recognizer()

#     def get_text(self, source_audio: Audio, language: str, show_all: bool=False):
#         """
#         Execute the speech-to-text transcription on the audio.
        
#         Args:
#             source_audio (Audio): a valid Audio object.
#             language (str): source_audio language, for correct recognition.
#             show_all (bool): if True, all the detais of the transcription will be returned. If False, only the text will be returned.
#         """
#         try:
#             with sr.AudioFile(source_audio.get_filename()) as source:
#                 audio = self.transcriptor.listen(source)
#                 # TODO research other recognizers in sr
#                 transcription = self.transcriptor.recognize_google(audio_data=audio, language=language, show_all=show_all, pfilter=0)
#         except Exception as e:
#             print(f"Error during speech-to-text: {e}")
#         return transcription

#     def supported_languages(self, as_dict: bool=False):
#         """
#         Show the supported_languages for the current recognizer.

#         Args:
#             as_dict (bool): if True, the result is a dictionary with the languages and the codes. If False, the result is a list with the codes.
#         """
#         googe_cloud_supported_lang = {
#             "Afrikaans (South Africa)": "af-ZA",
#             "Arabic (Algeria)":   "ar-DZ",
#             "Arabic (Bahrain)":  "ar-BH",
#             "Arabic (Egypt)":   "ar-EG",
#             "Arabic (Iraq)":"ar-IQ",
#             "Arabic (Israel)": "ar-IL",
#             "Arabic (Jordan)": "ar-JO",
#             "Arabic (Kuwait)":"ar-KW",
#             "Arabic (Lebanon)":"ar-LB",
#             "Arabic (Mauritania)":"ar-MR",
#             "Arabic (Morocco)"     :   "ar-MA",
#             "Arabic (Oman)"    :   "ar-OM",
#             "Arabic (Palestinian Territory)"   :   "ar-PS",
#             "Arabic (Qatar)"   :   "ar-QA",
#             "Arabic (Saudi Arabia)"    :   "ar-SA",
#             "Arabic (Tunisia)" :   "ar-TN",
#             "Arabic (UAE)":    "ar-AE",
#             "Basque (Spain)": "eu-ES",
#             "Bulgarian": "bg-BG",
#             "Catalan (Spain)": "ca-ES",
#             "Chinese Mandarin (China (Simp.))": "cmn-Hans-CN",
#             "Chinese Mandarin (Hong Kong SAR (Trad.))": "cmn-Hans-HK",
#             "Chinese Mandarin (Taiwan (Trad.))": "cmn-Hant-TW",
#             "Chinese Cantonese (Hong Kong)": "yue-Hant-HK",
#             "Croatian": "hr_HR",
#             "Czech":  "cs-CZ",
#             "Danish":  "da-DK",
#             "English (Australia)": "en-AU",
#             "English (Canada)": "en-CA",
#             "English (India)": "en-IN",
#             "English (Ireland)": "en-IE",
#             "English (New Zealand)": "en-NZ",
#             "English (Philippines)": "en-PH",
#             "English (South Africa)": "en-ZA",
#             "English (United Kingdom)": "en-GB",
#             "English (United States)": "en-US",
#             "Farsi (Iran)": "fa-IR",
#             "French": "fr-FR",                                                                
#             "Filipino (Philippines)": "fil-PH",
#             "Galician (Spain)": "gl-ES",
#             "German":  "de-DE",
#             "Greek":  "el-GR",
#             "Finnish":  "fi-FI",
#             "Hebrew" : "he-IL",
#             "Hindi (India)": "hi-IN",
#             "Hungarian":  "hu-HU",
#             "Indonesian":  "id-ID",
#             "Icelandic":  "is-IS",
#             "Italian (Italy)": "it-IT",
#             "Italian (Switzerland)": "it-CH",
#             "Japanese": "ja-JP",
#             "Korean":  "ko-KR",
#             "Lithuanian":  "lt-LT",
#             "Malaysian":  "ms-MY",
#             "Dutch (Netherlands)": "nl-NL",
#             "Norwegian":  "nb-NO",
#             "Polish":  "pl-PL",
#             "Portuguese (Brazil)": "pt-BR",
#             "Portuguese (Portugal)": "pt-PT",
#             "Romanian":  "ro-RO",
#             "Russian":  "ru-RU",
#             "Serbian":  "sr-RS",
#             "Slovak":  "sk-SK",
#             "Slovenian":  "sl-SI",
#             "Spanish (Argentina)": "es-AR",
#             "Spanish (Bolivia)": "es-BO",
#             "Spanish (Chile)": "es-CL",
#             "Spanish (Colombia)": "es-CO",
#             "Spanish (Costa Rica)": "es-CR",
#             "Spanish (Dominican Republic)": "es-DO",
#             "Spanish (Ecuador)": "es-EC",
#             "Spanish (El Salvador)": "es-SV",
#             "Spanish (Guatemala)": "es-GT",
#             "Spanish (Honduras)": "es-HN",
#             "Spanish (México)": "es-MX",
#             "Spanish (Nicaragua)": "es-NI",
#             "Spanish (Panamá)": "es-PA",
#             "Spanish (Paraguay)": "es-PY",
#             "Spanish (Perú)": "es-PE",
#             "Spanish (Puerto Rico)": "es-PR",
#             "Spanish (Spain)": "es-ES",
#             "Spanish (Uruguay)": "es-UY",
#             "Spanish (United States)": "es-US",
#             "Spanish (Venezuela)": "es-VE",
#             "Swedish": "sv-SE",
#             "Thai (Thailand)": "th-TH",
#             "Turkish (Turkey)": "tr-TR",
#             "Ukrainian (Ukraine)": "uk-UA",
#             "Vietnamese (Viet Nam)": "vi-VN",
#             "Zulu (South Africa)": "zu-ZA",
#             }
#         if as_dict:
#             return googe_cloud_supported_lang
#         else:
#             return list(googe_cloud_supported_lang.values())

class S2T_Whisper(S2T_Base):
    """Speech-to-text model based on Whisper """
    MODELS = "tiny", "base", "small", "medium", "large-v1", "large-v2"
    # https://github.com/openai/whisper
    # TODO check out https://huggingface.co/openai/whisper-large

    def __init__(self, model_selected: str ="small", use_GPU: bool=False):
        """
        Initialize the speech-to-text model.

        Args:
            model_selected (str): whisper model, must be one of the following: "tiny", "base", "small", "medium", "large-v1", "large-v2".
            use_GPU (bool): if True will create the model with GPU if aviable. if False will create the model with CPU.
        """
        self.gpu = use_GPU
        if self.gpu:
            torch.cuda.init()
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print("Use GPU requested on Whisper. Current cuda device:", self.device)
        
            self._load_model_decresing(model_selected)
        else:
            self.model: whisper.Whisper = whisper.load_model(model_selected)

    def _load_model_decresing(self, model_selected):
        models = ["tiny", "base", "small", "medium", "large-v1", "large-v2"]
        model = model_selected
        not_load = True
        while not_load:      
            if models.index(model) == 0: # model == models[0]:
                not_load = False   
                print("Attempting to load Whisper",model)  
                self.model: whisper.Whisper = whisper.load_model(model).to(self.device)
            else:
                try:
                    print("Attempting to load Whisper",model)  
                    self.model: whisper.Whisper = whisper.load_model(model).to(self.device)
                    not_load = False   
                except Exception as er:
                    print(er)
                    ind = models.index(model)
                    model = models[ind - 1]

    def get_text(self, source_audio: Audio, language: str, show_all: bool=False):
        """
        Execute the speech-to-text transcription on the audio.
        
        Args:
            audio (Audio): a valid Audio object.
            language (str): source_audio language, for correct recognition.
            show_all (bool): if True, all the detais of the transcription will be returned. If False, only the text will be returned.
        """
        if self.gpu:
            try:
                with torch.cuda.device(self.device):
                    transcription = self.model.transcribe(
                                audio=source_audio.get_filename(),
                                language=language,
                                task='transcribe',
                                fp16=False
                                # temperature=temperature,
                                # compression_ratio_threshold=compression_ratio_threshold,
                                # logprob_threshold=logprob_threshold,
                                # no_speech_threshold=no_speech_threshold,
                                # condition_on_previous_text=condition_on_previous_text,
                                # initial_prompt=initial_prompt,
                                # **whisper_extra_args,
                            )
            except Exception as e:
                print(f"Error during speech-to-text: {e}")
                return None
        else:
            try:
                transcription = self.model.transcribe(
                            audio=source_audio.get_filename(),
                            language=language,
                            task='transcribe',
                            fp16=False
                            # temperature=temperature,
                            # compression_ratio_threshold=compression_ratio_threshold,
                            # logprob_threshold=logprob_threshold,
                            # no_speech_threshold=no_speech_threshold,
                            # condition_on_previous_text=condition_on_previous_text,
                            # initial_prompt=initial_prompt,
                            # **whisper_extra_args,
                        )
                
            except Exception as e:
                print(f"Error during speech-to-text: {e}")
                return None
        if show_all:
            return transcription
        else:
            return transcription['text']

    def supported_languages(self, as_dict: bool=False):
        """
        Show the supported_languages for the current model.

        Args:
            as_dict (bool): if True, the result is a dictionary with the languages and the codes. If False, the result is a list with the codes.
        """
        if as_dict:
            return iso_code_2_dict
        else:
            return list(iso_code_2_dict.values())

