""" Several text-to-speech (TTS) models"""

from src.core.common.errors import InvalidInputError
from src.core.common.common import iso_code_3_dict, iso_code_2_dict, SpeakerSettings
from pydub import AudioSegment
from gtts import gTTS
from google.cloud import texttospeech
from ttsmms import TTS as mmstts, download
import TTS.api as coquitts
# from IPython.display import PyAudio
# from scipy.io.wavfile import write as write_wav
# from bark.api import generate_audio
# from encodec.utils import convert_audio
# import torchaudio
import torch

from transformers import AutoProcessor, AutoModel
from pathlib import Path
import os
import random
import string
import scipy
import nltk

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMP_PATH = os.path.join(BASE_DIR,"src","app","static","audio") # src/app/static/audio

class TTS_Base:
    """Text-to-speech models base class """
    def __init__(self, use_GPU: bool=False):
        """
        Initialize the text-to-speech model
        """
        pass
    def generate_speech(self, input_text: str, language: str, save_audio_path: str, *args):
        """
        Execute the text-to-speech generation.
        
        Args:
            input_text (str): source text for the speech.
            language (str): text language, for better speech generation.
            save_audio_path (str): the resulting speech will be saved on that path. Must include the file name and extension (.wav | .mp3).
        """
        raise NotImplementedError()
    def supported_languages(self, as_dict: bool=False):
        """
        Show the supported_languages for the current model.

        Args:
            as_dict (bool): if True, the result is a dictionary with the languages and the codes. If False, the result is a list with the codes.
        """
        raise NotImplementedError()
    def voices_choices(self) -> bool:
        return False

class TTS_google(TTS_Base):
    """Text-to-speech model based on google tts """
    def __init__(self):
        super().__init__()
    
    def generate_speech(self, input_text: str, language: str, save_audio_path: str, slow: bool=False):
        """
        Execute the text-to-speech generation.
        
        Args:
            input_text (str): source text for the speech.
            language (str): text language, for better speech generation.
            save_audio_path (str): the resulting speech will be saved on that path. Must include the file name and extension (.wav | .mp3).
            slow (bool): if True reads text more slowly.
        """
        tts = gTTS(text=input_text, lang=language, slow=slow)
        tts.save(save_audio_path)
    
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

class TTS_google_cloud(TTS_Base):
    """Text-to-speech model based on google cloud tts """
    def __init__(self, use_GPU: bool=False):
        """
        Initialize the text-to-speech model
        """
        # Instantiates a client
        self.client = texttospeech.TextToSpeechClient()

    def generate_speech(self, input_text: str, language: str, save_audio_path: str, voice_sett: SpeakerSettings):
        """
        Execute the text-to-speech generation.
        
        Args:
            input_text (str): source text for the speech.
            language (str): text language, for better speech generation.
            save_audio_path (str): the resulting speech will be saved on that path. Must include the file name and extension (.wav | .mp3).
            slow (bool): if True reads text more slowly.
        """
        valid_langs = self.supported_languages(as_dict=True)
        if language not in list(valid_langs.values()) and language not in valid_langs:
            raise InvalidInputError(f"the language {language} is not aviable for google cloud text-to-speech. \nAviable languages: {valid_langs}")
        if language in valid_langs and language in voice_sett.name:
            language = valid_langs[language]

        split = voice_sett.name.split('-')
        four_code = f"{split[0]}-{split[1]}"

        text_input = texttospeech.SynthesisInput(text=input_text)
        gender = texttospeech.SsmlVoiceGender.FEMALE if voice_sett.voice_gender == "female" else texttospeech.SsmlVoiceGender.MALE
        voice_params = texttospeech.VoiceSelectionParams(language_code=four_code, ssml_gender=gender, name=voice_sett.name)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

        response = self.client.synthesize_speech(
            input=text_input, voice=voice_params, audio_config=audio_config
        )

        # The response's audio_content is binary.
        with open(save_audio_path, "wb") as out:
            out.write(response.audio_content)
            print('Audio content written to file',save_audio_path)
    
    def supported_languages(self, as_dict: bool=False):
        """
        Show the supported_languages for the current model.

        Args:
            as_dict (bool): if True, the result is a dictionary with the languages and the codes. If False, the result is a list with the codes.
        """
        subset = [  "Bulgarian", "Catalan", "Czech", "Danish", "Dutch", "English", 
                    "Finnish", "French", "German", "Greek", "Hungarian", 
                    "Italian", "Latvian", "Lithuanian", "Polish", "Portuguese", 
                    "Romanian", "Slovak",  "Spanish","Swedish"]
        
        subset_of_iso_code_2_dict = {}
        for item in iso_code_2_dict:
            if item in subset:
                subset_of_iso_code_2_dict[item] = iso_code_2_dict[item]


        if as_dict:
            return subset_of_iso_code_2_dict
        else:
            return list(subset_of_iso_code_2_dict.values())
    
    def voices_choices(self) -> bool:
        return True
    
    def _generate_voices_dict(self):

        # Performs the list voices request
        voices = self.client.list_voices()

        valid_lang_codes = list(self.supported_languages(as_dict=True).values())
        # valid_lang_codes = ['en']
        voices_dict = {}
        for lang_code in valid_lang_codes:
            voices_dict[lang_code] = {'female':[],'male':[]}
        # voices_dict['en'] = {'female':[],'male':[]}

        for voice in voices.voices:
            """{
                "languageCodes": [
                    string
                ],
                "name": string,
                "ssmlGender": enum (SsmlVoiceGender),
                "naturalSampleRateHertz": integer
                }
            """
            
            name = voice.name
            ssml_gender:str = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
            ssml_gender = ssml_gender.lower()
            rate = voice.natural_sample_rate_hertz
            for lang_code in voice.language_codes:
                main_lang = lang_code.split('-')[0]
                if main_lang in valid_lang_codes:
                    voices_dict[main_lang][ssml_gender].append(f"{name}")
                    # print(f"Name: {name}")
                    # print(f"SSML Voice Gender: {ssml_gender}")
                    # print(f"Natural Sample Rate Hertz: {rate}\n")
        print(voices_dict)

    def preset_voices(self, language="all", gender="all", as_dict:bool=True):
        """ dictionary as { language_code: {
                                            'female':[...],
                                            'male': [...]
                                            },
                            ...
                            }
        """
        dictionary = {'bg': {'female': ['bg-BG-Standard-A'], 'male': []}, 
                      'ca': {'female': ['ca-ES-Standard-A'], 'male':[]},
                      'cs': {'female': ['cs-CZ-Standard-A', 'cs-CZ-Wavenet-A'], 'male': []}, 
                      'da': {'female': ['da-DK-Neural2-D', 'da-DK-Standard-A', 'da-DK-Standard-D', 'da-DK-Standard-E', 'da-DK-Wavenet-A', 'da-DK-Wavenet-D', 'da-DK-Wavenet-E'], 'male': ['da-DK-Standard-C', 'da-DK-Wavenet-C']}, 
                      'nl': {'female': ['nl-BE-Standard-A', 'nl-BE-Wavenet-A', 'nl-NL-Standard-A', 'nl-NL-Standard-D', 'nl-NL-Standard-E', 'nl-NL-Wavenet-A', 'nl-NL-Wavenet-D', 'nl-NL-Wavenet-E'], 'male': ['nl-BE-Standard-B', 'nl-BE-Wavenet-B', 'nl-NL-Standard-B', 'nl-NL-Standard-C', 'nl-NL-Wavenet-B', 'nl-NL-Wavenet-C']}, 
                      'en': {'female': ['en-AU-Neural2-A', 'en-AU-Neural2-C', 'en-AU-News-E', 'en-AU-News-F', 'en-AU-Standard-A', 'en-AU-Standard-C', 'en-AU-Wavenet-A', 'en-AU-Wavenet-C', 'en-GB-Neural2-A', 'en-GB-Neural2-C', 'en-GB-Neural2-F', 'en-GB-News-G', 'en-GB-News-H', 'en-GB-News-I', 'en-GB-Standard-A', 'en-GB-Standard-C', 'en-GB-Standard-F', 'en-GB-Wavenet-A', 'en-GB-Wavenet-C', 'en-GB-Wavenet-F', 'en-IN-Neural2-A', 'en-IN-Neural2-D', 'en-IN-Standard-A', 'en-IN-Standard-D', 'en-IN-Wavenet-A', 'en-IN-Wavenet-D', 'en-US-Neural2-C', 'en-US-Neural2-E', 'en-US-Neural2-F', 'en-US-Neural2-G', 'en-US-Neural2-H', 'en-US-News-K', 'en-US-News-L', 'en-US-Standard-C', 'en-US-Standard-E', 'en-US-Standard-F', 'en-US-Standard-G', 'en-US-Standard-H', 'en-US-Wavenet-C', 'en-US-Wavenet-E', 'en-US-Wavenet-F', 'en-US-Wavenet-G', 'en-US-Wavenet-H'], 'male': ['en-AU-Neural2-B', 'en-AU-Neural2-D', 'en-AU-News-G', 'en-AU-Polyglot-1', 'en-AU-Standard-B', 'en-AU-Standard-D', 'en-AU-Wavenet-B', 'en-AU-Wavenet-D', 'en-GB-Neural2-B', 'en-GB-Neural2-D', 'en-GB-News-J', 'en-GB-News-K', 'en-GB-News-L', 'en-GB-News-M', 'en-GB-Standard-B', 'en-GB-Standard-D', 'en-GB-Wavenet-B', 'en-GB-Wavenet-D', 'en-IN-Neural2-B', 'en-IN-Neural2-C', 'en-IN-Standard-B', 'en-IN-Standard-C', 'en-IN-Wavenet-B', 'en-IN-Wavenet-C', 'en-US-Neural2-A', 'en-US-Neural2-D', 'en-US-Neural2-I', 'en-US-Neural2-J', 'en-US-News-M', 'en-US-News-N', 'en-US-Polyglot-1', 'en-US-Standard-A', 'en-US-Standard-B', 'en-US-Standard-D', 'en-US-Standard-I', 'en-US-Standard-J', 'en-US-Wavenet-A', 'en-US-Wavenet-B', 'en-US-Wavenet-D', 'en-US-Wavenet-I', 'en-US-Wavenet-J']}, 
                      'fi': {'female': ['fi-FI-Standard-A', 'fi-FI-Wavenet-A'], 'male': []}, 
                      'fr': {'female': ['fr-CA-Neural2-A', 'fr-CA-Neural2-C', 'fr-CA-Standard-A', 'fr-CA-Standard-C', 'fr-CA-Wavenet-A', 'fr-CA-Wavenet-C', 'fr-FR-Neural2-A', 'fr-FR-Neural2-C', 'fr-FR-Neural2-E', 'fr-FR-Standard-A', 'fr-FR-Standard-C', 'fr-FR-Standard-E', 'fr-FR-Wavenet-A', 'fr-FR-Wavenet-C', 'fr-FR-Wavenet-E'], 'male': ['fr-CA-Neural2-B', 'fr-CA-Neural2-D', 'fr-CA-Standard-B', 'fr-CA-Standard-D', 'fr-CA-Wavenet-B', 'fr-CA-Wavenet-D', 'fr-FR-Neural2-B', 'fr-FR-Neural2-D', 'fr-FR-Polyglot-1', 'fr-FR-Standard-B', 'fr-FR-Standard-D', 'fr-FR-Wavenet-B', 'fr-FR-Wavenet-D']}, 
                      'de': {'female': ['de-DE-Neural2-A', 'de-DE-Neural2-C', 'de-DE-Neural2-F', 'de-DE-Standard-A', 'de-DE-Standard-C', 'de-DE-Standard-F', 'de-DE-Wavenet-A', 'de-DE-Wavenet-C', 'de-DE-Wavenet-F'], 'male': ['de-DE-Neural2-B', 'de-DE-Neural2-D', 'de-DE-Polyglot-1', 'de-DE-Standard-B', 'de-DE-Standard-D', 'de-DE-Standard-E', 'de-DE-Wavenet-B', 'de-DE-Wavenet-D', 'de-DE-Wavenet-E']}, 
                      'el': {'female': ['el-GR-Standard-A', 'el-GR-Wavenet-A'], 'male': []}, 
                      'hu': {'female': ['hu-HU-Standard-A', 'hu-HU-Wavenet-A'], 'male': []}, 
                      'it': {'female': ['it-IT-Neural2-A', 'it-IT-Standard-A', 'it-IT-Standard-B', 'it-IT-Wavenet-A', 'it-IT-Wavenet-B'], 'male': ['it-IT-Neural2-C', 'it-IT-Standard-C', 'it-IT-Standard-D', 'it-IT-Wavenet-C', 'it-IT-Wavenet-D']}, 
                      'lv': {'female': [], 'male': ['lv-LV-Standard-A']}, 
                      'lt': {'female': [], 'male': ['lt-LT-Standard-A']}, 
                      'pl': {'female': ['pl-PL-Standard-A', 'pl-PL-Standard-D', 'pl-PL-Standard-E', 'pl-PL-Wavenet-A', 'pl-PL-Wavenet-D', 'pl-PL-Wavenet-E'], 'male': ['pl-PL-Standard-B', 'pl-PL-Standard-C', 'pl-PL-Wavenet-B', 'pl-PL-Wavenet-C']}, 
                      'pt': {'female': ['pt-BR-Neural2-A', 'pt-BR-Neural2-C', 'pt-BR-Standard-A', 'pt-BR-Standard-C', 'pt-BR-Wavenet-A', 'pt-BR-Wavenet-C', 'pt-PT-Standard-A', 'pt-PT-Standard-D', 'pt-PT-Wavenet-A', 'pt-PT-Wavenet-D'], 'male': ['pt-BR-Neural2-B', 'pt-BR-Standard-B', 'pt-BR-Wavenet-B', 'pt-PT-Standard-B', 'pt-PT-Standard-C', 'pt-PT-Wavenet-B', 'pt-PT-Wavenet-C']}, 
                      'ro': {'female': ['ro-RO-Standard-A', 'ro-RO-Wavenet-A'], 'male': []}, 
                      'sk': {'female': ['sk-SK-Standard-A', 'sk-SK-Wavenet-A'], 'male': []}, 
                      'es': {'female': ['es-ES-Neural2-A', 'es-ES-Neural2-C', 'es-ES-Neural2-D', 'es-ES-Neural2-E', 'es-ES-Standard-A', 'es-ES-Standard-C', 'es-ES-Standard-D', 'es-ES-Wavenet-C', 'es-ES-Wavenet-D', 'es-US-Neural2-A', 'es-US-News-F', 'es-US-News-G', 'es-US-Standard-A', 'es-US-Wavenet-A'], 'male': ['es-ES-Neural2-B', 'es-ES-Neural2-F', 'es-ES-Polyglot-1', 'es-ES-Standard-B', 'es-ES-Wavenet-B', 'es-US-Neural2-B', 'es-US-Neural2-C', 'es-US-News-D', 'es-US-News-E', 'es-US-Polyglot-1', 'es-US-Standard-B', 'es-US-Standard-C', 'es-US-Wavenet-B', 'es-US-Wavenet-C']}, 
                      'sv': {'female': ['sv-SE-Standard-A', 'sv-SE-Standard-B', 'sv-SE-Standard-C', 'sv-SE-Wavenet-A', 'sv-SE-Wavenet-B', 'sv-SE-Wavenet-D'], 'male': ['sv-SE-Standard-D', 'sv-SE-Standard-E', 'sv-SE-Wavenet-C', 'sv-SE-Wavenet-E']}
                      }

        if language == "all" and gender=="all" and as_dict:
            return dictionary
        if language == "all" and gender=="all":
            result = []
            for l in dictionary:
                for gen in dictionary[l]:
                    result += dictionary[l][gen]
            return result
        if language == "all":
            result = {}
            for l in dictionary:
                result[l] = dictionary[l][gender]
            if as_dict: return result
            else: 
                l = []
                for lan in result:
                    l += result[lan]
                return l
        if gender=="all":
            result = {}
            result = dictionary[language]
            if as_dict: return result
            else:
                l = []
                for g in result:
                    l += result[g]
                return l
        
        return dictionary[language][gender]

# myobj = TTS_google()
# myobj.generate_speech(transl1,'en',"vegetta1.wav")
# myobj.generate_speech(transl2,'en',"vegetta2.wav")

class TTS_MMS(TTS_Base):
    """Text-to-speech model based on facebook MMS """
    def __init__(self, use_GPU: bool=False):
        super().__init__()

        self.gpu = use_GPU
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.models_path = os.path.join(BASE_DIR,"data","MMS") # TODO make it an absolute path
    
    def generate_speech(self, input_text: str, language: str, save_audio_path: str):
        """
        Execute the text-to-speech generation.
        
        Args:
            input_text (str): source text for the speech.
            language (str): text language, must be on iso standar of 3 letters.
            save_audio_path (str): the resulting speech will be saved on that path. Must include the file name and extension (.wav ).
            slow (bool): if True reads text more slowly.
        """

        valid_langs = self.supported_languages(as_dict=True)
        
        if language not in list(valid_langs.values()) and language not in valid_langs:
            raise InvalidInputError(f"the language {language} is not aviable for MMS text-to-speech. \nAviable languages: {valid_langs}")
        if language in valid_langs:
            language = valid_langs[language]
        try:

            # check if the model for that language is downloaded, in that case, generate the audio and save it
            tts = mmstts(os.path.join(self.models_path, language))

            tts.synthesis(input_text, wav_path=save_audio_path)

        except AssertionError as er:
            print(f"Error : {er}. Downloading the model first.")
            dir_path = download(language, self.models_path) # lang_code, dir for save model
            tts = mmstts(os.path.join(self.models_path, language))
            
            tts.synthesis(input_text, wav_path=save_audio_path)
              
    def supported_languages(self, as_dict: bool=False):
        """
        Show the supported_languages for the current model.

        Args:
            as_dict (bool): if True, the result is a dictionary with the languages and the codes. If False, the result is a list with the codes.
        """
        if as_dict:
            return iso_code_3_dict
        else:
            return list(iso_code_3_dict.values())
    def voices_choices(self) -> bool:
        return False

class TTS_Bark(TTS_Base):
    """
    Text-to-speech model based on Bark. 
    
    Text-prompted Generative Audio Model - With the ability to clone voices.
    """
    
    def __init__(self, use_GPU: bool=False):
        """
        Initialize the text-to-speech model
        """
        self.gpu = use_GPU
        if self.gpu:
            # os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:20"
            # torch.cuda.empty_cache()
            self.processor = AutoProcessor.from_pretrained("suno/bark-small") # suno/bark
            self.model = AutoModel.from_pretrained("suno/bark-small") #suno/bark
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
            self.model = self.model.to(self.device)
        else:
            self.processor = AutoProcessor.from_pretrained("suno/bark-small") # suno/bark
            self.model = AutoModel.from_pretrained("suno/bark-small") #suno/bark
        
    def generate_speech(self, input_text: str, language: str, save_audio_path: str, voice_sett: SpeakerSettings):
        """
        Execute the text-to-speech generation.
        
        Args:
            input_text (str): source text for the speech.
            language (str): text language, for better speech generation.
            save_audio_path (str): the resulting speech will be saved on that path. Must include the file name and extension (.wav | .mp3).
        """
        valid_langs = self.supported_languages(as_dict=True)
        if language not in list(valid_langs.values()) and language not in valid_langs:
            raise InvalidInputError(f"the language {language} is not aviable for Bark text-to-speech. \nAviable languages: {valid_langs}")
        if language in valid_langs:
            language = valid_langs[language]

        sentences = nltk.sent_tokenize(input_text)
        print(sentences)
        if len(sentences) >= 4:
            # print("HERE0")
            temp =[None,None]
            half = len(sentences)//2
            temp[0] = sentences[:half]
            temp[1] = sentences[half:]
            sentences = ["",""]
            for s in temp[0]:
                sentences[0] = sentences[0] + s + " "
            sentences[0]+='.'
            for s in temp[1]:
                sentences[1] = sentences[1] + s + " "
            sentences[1]+='.'
        else: 
            # print("HERE1")
            for i, sent in enumerate(sentences):
                # print("HERE2")
                # print(sent)
                sent:str
                if not sent.endswith('.'): 
                    # print("HERE3")
                    sentences[i] = sent+'.'
                    # print('now:',sent)
        pieces = []
        for i, sent in enumerate(sentences):
            print(sent)
            path = os.path.dirname(save_audio_path)
            name = os.path.splitext(os.path.basename(save_audio_path))[0]
            temp_file = os.path.join(path,f"{name}_bark_{i}.wav")
            pieces.append(temp_file)

            inputs = self.processor(sent, voice_preset=voice_sett.name)
            speech_values = self.model.generate(**inputs, num_beams=4,temperature=0.5, do_sample=True)
        
            sampling_rate = self.model.generation_config.sample_rate
            scipy.io.wavfile.write(temp_file, rate=sampling_rate, data=speech_values.cpu().numpy().squeeze())

        result_audio = None
        for path in pieces:
            temp = AudioSegment.from_wav(path)
            if result_audio == None:  result_audio = temp
            else: result_audio += temp

            os.remove(path)
        result_audio.export(save_audio_path, format="wav")

    def supported_languages(self, as_dict: bool=False):
        """
        Show the supported_languages for the current model.

        Args:
            as_dict (bool): if True, the result is a dictionary with the languages and the codes. If False, the result is a list with the codes.
        """
        supported = { 
                    # "Dutch":"nl",
                    "English":"en",
                    # "Finnish":"fi",
                    "French":"fr",
                    "German":"de",
                    # "Greek":"el",
                    # "Hungarian":"hu", 
                    "Portuguese":"pt",
                    # "Romanian":"ro", 
                    "Spanish":"es",
                    # "Swedish":"sv",
                    "Italian":"it"}
        
        if as_dict:
            return supported
        else:
            return list(supported.values())
    
    def preset_voices(self, language="all", gender="all", as_dict:bool=True):
        """ dictionary as { language_code: {
                                            'female':[...],
                                            'male': [...]
                                            },
                            ...
                            }
        """
        dictionary = {"en":{'female':["v2/en_speaker_9"],'male':["v2/en_speaker_0","v2/en_speaker_1","v2/en_speaker_2","v2/en_speaker_3","v2/en_speaker_4","v2/en_speaker_5","v2/en_speaker_6","v2/en_speaker_7","v2/en_speaker_8"]},
                       "fr":{'female':["v2/fr_speaker_1","v2/fr_speaker_2","v2/fr_speaker_5"],'male':["v2/fr_speaker_0","v2/fr_speaker_3","v2/fr_speaker_4","v2/fr_speaker_6","v2/fr_speaker_7","v2/fr_speaker_8","v2/fr_speaker_9"]},
                       "de":{'female':["v2/de_speaker_3","v2/de_speaker_8"],'male':["v2/de_speaker_0","v2/de_speaker_1","v2/de_speaker_2","v2/de_speaker_4","v2/de_speaker_5","v2/de_speaker_6","v2/de_speaker_7","v2/de_speaker_9"]},
                       "pt":{'female':[],'male':["v2/pt_speaker_0","v2/pt_speaker_1","v2/pt_speaker_2","v2/pt_speaker_3","v2/pt_speaker_4","v2/pt_speaker_5","v2/pt_speaker_6","v2/pt_speaker_7","v2/pt_speaker_8","v2/pt_speaker_9"]},
                       "es":{'female':["v2/es_speaker_8","v2/es_speaker_9"],'male':["v2/es_speaker_0","v2/es_speaker_1","v2/es_speaker_2","v2/es_speaker_3","v2/es_speaker_4","v2/es_speaker_5","v2/es_speaker_6","v2/es_speaker_7"]},
                       "it":{'female':["v2/it_speaker_2","v2/it_speaker_7"],'male':["v2/it_speaker_0","v2/it_speaker_1","v2/it_speaker_3","v2/it_speaker_4","v2/it_speaker_5","v2/it_speaker_6","v2/it_speaker_8","v2/it_speaker_9"]},}

        if language == "all" and gender=="all" and as_dict:
            return dictionary
        if language == "all" and gender=="all":
            result = []
            for l in dictionary:
                for gen in dictionary[l]:
                    result += dictionary[l][gen]
            return result
        if language == "all":
            result = {}
            for l in dictionary:
                result[l] = dictionary[l][gender]
            if as_dict: return result
            else: 
                l = []
                for lan in result:
                    l += result[lan]
                return l
        if gender=="all":
            result = {}
            result = dictionary[language]
            if as_dict: return result
            else:
                l = []
                for g in result:
                    l += result[g]
                return l
        
        return dictionary[language][gender]

    def voices_choices(self) -> bool:
        return True

class CloneTTS_Base:
    """Voice clone models base class """
    def __init__(self, use_GPU: bool=False):
        """
        Initialize the text-to-speech/voice-clone model
        """
        pass
    def generate_speech(self, input_text: str, language: str, save_audio_path: str, *args):
        """
        Execute the text-to-speech generation with a cloned voice.
        
        Args:
            input_text (str): source text for the speech.
            language (str): text language, for better speech generation.
            save_audio_path (str): the resulting speech will be saved on that path. Must include the file name and extension (.wav | .mp3).
        """
        raise NotImplementedError()
    def supported_languages(self, as_dict: bool=False):
        """
        Show the supported_languages for the current model.

        Args:
            as_dict (bool): if True, the result is a dictionary with the languages and the codes. If False, the result is a list with the codes.
        """
        raise NotImplementedError()

class VoiceClone_XTTS(SpeakerSettings):
    def __init__(self, spk_id: int, voice_name: str, sample_audio: AudioSegment) -> None:
        self.speaker = spk_id
        self.voice_gender = "clone"
        self.name = voice_name
        self.cloned = True
        self.sample_audio = sample_audio

    def __str__(self) -> str:
        return f"Coqui TTS's XTTS Voice: {self.name}"
    def __repr__(self) -> str:
        return self.__str__()

class CloneTTS_XTTT(CloneTTS_Base):
    """Voice clone model based on Coqui TTS's XTTS """
    # https://github.com/coqui-ai/TTS
    # https://huggingface.co/coqui/XTTS-v1
    # https://huggingface.co/spaces/coqui/xtts
    # https://tts.readthedocs.io/en/dev/models/xtts.html
    # https://docs.coqui.ai/en/dev/models/xtts.html
    # tts_models/multilingual/multi-dataset/xtts_v1.1
    # tts_models/multilingual/multi-dataset/xtts_v2
    def __init__(self, use_GPU: bool=False):
        """
        Initialize the text-to-speech/voice-clone model
        """
        self.xtts = coquitts.TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_GPU)

    def _gen_split_text(self, input_text: str, language: str, save_audio_path: str, voice_clone: VoiceClone_XTTS):
        sentences = nltk.sent_tokenize(input_text)
        for i, sent in enumerate(sentences):
            # print(sent)
            sent:str
            sent = sent.strip()
            if sent.endswith('.'): 
                sentences[i] = sent[-1]
                # print('now:',sent)

        temp_name = (''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)])) #+'.wav'
        temp_file = os.path.join(TEMP_PATH, temp_name+'.wav')
        voice_clone.sample_audio.export(temp_file, format="wav")
        pieces = []
        for i, sent in enumerate(sentences):
            print(sent)
            temp_file_s = os.path.join(TEMP_PATH,f"{temp_name}_xtts_{i}.wav")
            pieces.append(temp_file_s)


            self.xtts.tts_to_file(text=sent, 
                                file_path=temp_file_s,
                                speaker_wav=temp_file,
                                language=language)
        result_audio = None
        for path in pieces:
            temp = AudioSegment.from_wav(path)
            if result_audio == None:  result_audio = temp
            else: result_audio += temp

        result_audio.export(save_audio_path, format="wav")
        os.remove(temp_file)

    def generate_speech(self, input_text: str, language: str, save_audio_path: str, voice_clone: VoiceClone_XTTS):
        """
        Execute the text-to-speech generation with a cloned voice.
        
        Args:
            input_text (str): source text for the speech.
            language (str): text language, for better speech generation.
            save_audio_path (str): the resulting speech will be saved on that path. Must include the file name and extension (.wav | .mp3).
        """
        
        valid_langs = self.supported_languages(as_dict=True)
        if language not in list(valid_langs.values()) and language not in valid_langs:
            raise InvalidInputError(f"the language {language} is not aviable for coqui XTTS. \nAviable languages: {valid_langs}")
        if language in valid_langs:
            language = valid_langs[language]
        if language == "Catalan" or language == "ca":
            language = "es"

        voices_list = []
        temp_name = (''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)])) 
        if isinstance(voice_clone.sample_audio, list):
            for i, sample in enumerate(voice_clone.sample_audio):
                sample: AudioSegment
                temp_file = os.path.join(TEMP_PATH, temp_name + f'_{i}.wav')
                sample.export(temp_file, format="wav")
                voices_list.append(temp_file)
        else:
            temp_file = os.path.join(TEMP_PATH, temp_name+'.wav')
            voice_clone.sample_audio.export(temp_file, format="wav")
            voices_list.append(temp_file)

        self.xtts.tts_to_file(text=input_text, 
                              file_path=save_audio_path,
                              speaker_wav=voices_list,
                              language=language)
        for temp in voices_list:
            os.remove(temp)
    
    def supported_languages(self, as_dict: bool=False):
        """
        Show the supported_languages for the current model.

        Args:
            as_dict (bool): if True, the result is a dictionary with the languages and the codes. If False, the result is a list with the codes.
        """
        subset = [  "Catalan", "Czech", "Dutch", "English", "French", "German",
                    "Italian", "Polish", "Portuguese", "Spanish", "Hungarian"]
        
        subset_of_iso_code_2_dict = {}
        for item in iso_code_2_dict:
            if item in subset:
                subset_of_iso_code_2_dict[item] = iso_code_2_dict[item]


        if as_dict:
            return subset_of_iso_code_2_dict
        else:
            return list(subset_of_iso_code_2_dict.values())
    
class VitsTTS_cat(TTS_Base):
    # tts_models/ca/custom/vits
    def __init__(self, use_GPU: bool=False):
        """
        Initialize the text-to-speech catalan model
        """
        super().__init__()
        self.use_GPU = use_GPU

    def generate_speech(self, input_text: str, language: str, save_audio_path: str, voice_id: int):
        """
        Execute the text-to-speech generation.
        
        Args:
            input_text (str): source text for the speech.
            language (str): text language, for better speech generation.
            save_audio_path (str): the resulting speech will be saved on that path. Must include the file name and extension (.wav | .mp3).
        """
        
        valid_langs = self.supported_languages(as_dict=True)
        if language not in list(valid_langs.values()) and language not in valid_langs:
            raise InvalidInputError(f"the language {language} is not aviable for coqui Vits/ca. \nAviable languages: {valid_langs}")
        if language in valid_langs:
            language = valid_langs[language]

        self.vits = coquitts.TTS("tts_models/ca/custom/vits",voice_id=voice_id, gpu=self.use_GPU)

        # self.vits.tts_to_file(text=input_text, 
        #                     file_path=save_audio_path,
        #                     language=language)
        self.vits.synthesize(input_text, save_audio_path)
        
    def supported_languages(self, as_dict: bool=False):
        """
        Show the supported_languages for the current model.

        Args:
            as_dict (bool): if True, the result is a dictionary with the languages and the codes. If False, the result is a list with the codes.
        """
        subset = ["Catalan"]
        
        subset_of_iso_code_2_dict = {}
        for item in iso_code_2_dict:
            if item in subset:
                subset_of_iso_code_2_dict[item] = iso_code_2_dict[item]


        if as_dict:
            return subset_of_iso_code_2_dict
        else:
            return list(subset_of_iso_code_2_dict.values())
