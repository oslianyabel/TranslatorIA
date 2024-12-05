LANGUAGES = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'ny': 'chichewa',
    'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'french',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'german',
    'el': 'greek',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'he': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'korean',
    'ku': 'kurdish (kurmanji)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'or': 'odia',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'gd': 'scots gaelic',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'ug': 'uyghur',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu'}

language_list =[ "Dutch", "Catalan","English", "Finnish", "French", "German", "Greek", 
                "Hungarian", "Portuguese", "Romanian", "Spanish","Swedish"]

EU_languages = [ "Bulgarian", "Catalan", "Croatian", "Czech", "Danish", "Dutch", "English", 
                "Estonian", "Finnish", "French", "German", "Greek", "Hungarian", 
                "Irish", "Italian", "Latvian", "Lithuanian", "Maltese", "Polish",
                "Portuguese", "Romanian", "Slovak", "Slovene", "Spanish","Swedish"]

EU_languages_en_es={"Bulgarian":"Búlgaro",
                    "Catalan":"Catalan",
                    "Croatian": "Croata",
                    "Czech": "Checo",
                    "Danish": "Danés",
                    "Dutch": "Holandés",
                    "English": "Inglés",
                    "Estonian": "Estonio",
                    "Finnish":"Finlandés",
                    "French": "Francés",
                    "German": "Alemán",
                    "Greek": "Griego",
                    "Hungarian":"Húngaro", 
                    "Irish": "Irlandés",
                    "Italian":"Italiano",
                    "Latvian": "Letón",
                    "Lithuanian":"Lituano",
                    "Maltese": "Maltés",
                    "Polish": "Polaco",
                    "Portuguese":"Portugués",
                    "Romanian": "Rumano", 
                    "Slovak": "Eslovaco",
                    "Slovene":"Esloveno",
                    "Spanish": "Español",
                    "Swedish": "Sueco"}

iso_code_2_dict = {"Bulgarian":"bg",
                    "Catalan":"ca",
                    "Croatian": "hr",
                    "Czech": "cs",
                    "Danish": "da",
                    "Dutch":"nl",
                    "English":"en",
                    "Estonian": "et",
                    "Finnish":"fi",
                    "French":"fr",
                    "German":"de",
                    "Greek":"el",
                    "Hungarian":"hu", 
                    "Irish": "ga",
                    "Italian":"it",
                    "Latvian":"lv",
                    "Lithuanian":"lt",
                    "Maltese":"mt",
                    "Polish":"pl",
                    "Portuguese":"pt",
                    "Romanian":"ro", 
                    "Slovak":"sk",
                    "Slovene":"sl",
                    "Spanish":"es",
                    "Swedish":"sv"}

iso_code_3_dict = {"Bulgarian":"bul",
                  "Catalan":"cat",
                  "Dutch":"nld",
                  "English":"eng",
                  "Finnish":"fin",
                  "French":"fra",
                  "German":"deu",
                  "Greek":"ell",
                  "Hungarian":"hun",
                  "Latvian":"lav",
                  "Polish":"pol",
                  "Portuguese":"por",
                  "Romanian":"ron",
                  "Spanish":"spa",
                  "Swedish":"swe",
                  }

from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pathlib import Path
import os
from src.core.common import audio_time_stretch as ats

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # TranlatorIA/src
CORE_PARENT_DIR = BASE_DIR.parent  # TranlatorIA

class PhraseSettings:
    def __init__(self, volume=0, speed=1.0) -> None:
        self.volume = volume
        self.speed = speed
        
    def __str__(self) -> str:
        return f"volume: {self.volume}, speed: {self.speed}"
    def __repr__(self) -> str:
        return self.__str__()

class SpeakerSettings:
    def __init__(self, spk_id: int, gender: str, voice_name: str, cloned = False) -> None:
        self.speaker = spk_id
        self.voice_gender = gender
        self.name = voice_name
        self.cloned = cloned 

    def __str__(self) -> str:
        return f"{self.speaker} : {self.voice_gender} - {self.name}"
    def __repr__(self) -> str:
        return self.__str__()

class Audio:
    """
    Class representing an audio.

    Attributes:
        file_path (str): The file path of the audio.
        language (str): The language of the audio.
    """
    def __init__(self, file_path: str, language: str = "Unknown"):
        """
        The constructor for the Audio class.

        Args:
            file_path (str): The file path of the audio.
            language (str): The language of the audio.
        """
        self.original_file_path = file_path
        print(self.original_file_path)
        self.language = language
        self.splits = [(0, self.get_audio_duration_ms())]
        # print("audio duration : ",self.splits)
        self.is_split = False

    def __str__(self) -> str:
        return f"Audio: {self.get_filename()}. language: {self.get_language()}"
    
    def __repr__(self) -> str:
        return self.__str__()

    def get_filename(self) -> str:
        """
        Get the file path of the audio.

        Returns:
            str: The file path of the audio.
        """
        return os.path.join(CORE_PARENT_DIR, self.original_file_path)

    def set_filename(self, file_path: str):
        """
        Set the file path of the audio.

        Args:
            file_path (str): The new file path of the audio.
        """
        self.original_file_path = file_path

    def get_language(self) -> str:
        """
        Get the language of the audio.

        Returns:
            str: The language of the audio.
        """
        return self.language

    def set_language(self, language: str):
        """
        Set the language of the audio.

        Args:
            language (str): The new language of the audio.
        """
        self.language = language

    def get_audio_duration_ms(self):
        # print(self.get_filename())
        audio = AudioSegment.from_file(self.get_filename())
        duration_ms = len(audio)
        return duration_ms
    
    def get_split(self) -> list:
        """
        Get the list of sub_audios intervals. If is_split == False, returns a list with the original audio file.

        Returns:
            list: sub_audios from the split.
        """
        
        return self.splits

    def set_split(self, splits: list):
        """
        Set the list of sub_audios intervals.

        Args:
            splits (list): sub_audios from the split.
        """
        self.splits = splits
        self.is_split = True

    @staticmethod 
    def adjust_audio_speed(input_audio: str, output_audio:str=None, speed: float=1.0):
        if output_audio == None:
            output_audio = input_audio
        if speed > 1.4: speed = 1.4
        if speed < 0.7: speed = 0.7
        ats.audio_time_stretch(input_audio, output_audio, speed)
    
    @staticmethod 
    def adjust_audio_volume(audio_path: str, volume: int=0):
        audio = AudioSegment.from_wav(audio_path)
        audio = audio + volume
        audio.export(audio_path, format="wav")
    
    @staticmethod 
    def auto_adjust_audio(phrase, generated_audio_path):
        # text = phrase.text

        original_start = phrase.get_start_time()
        original_end = phrase.get_end_time()
        original_duration = original_end - original_start
        
        audio_slice = AudioSegment.from_wav(generated_audio_path)
        current_duration = len(audio_slice)

        speed = current_duration / original_duration
        if speed > 1.4: speed = 1.4
        if speed < 0.7: speed = 0.7

        path = os.path.dirname(generated_audio_path)
        name = os.path.splitext(os.path.basename(generated_audio_path))[0]
        new_audio_path = os.path.join(path,f"{name}_adjusted.wav")

        Audio.adjust_audio_speed(generated_audio_path, new_audio_path, speed=speed)
        audio_slice = AudioSegment.from_wav(new_audio_path)
        #remove chunk
        os.remove(new_audio_path)

        # audio_slice:AudioSegment = audio_slice + 10
        # audio_slice.export(new_audio_path, format="wav")

        # phrase_settings.speed = speed
        # phrase_settings.volume = 0

        return audio_slice, PhraseSettings(volume=0,speed=speed)

    @staticmethod 
    def adjust_audio(generated_audio_path, phrase_settings: PhraseSettings):        
        audio_slice = AudioSegment.from_wav(generated_audio_path)

        path = os.path.dirname(generated_audio_path)
        name = os.path.splitext(os.path.basename(generated_audio_path))[0]
        new_audio_path = os.path.join(path,f"{name}_adjusted.wav")
        audio_slice.export(new_audio_path, format="wav")
        
        if phrase_settings.speed > 1.4: phrase_settings.speed = 1.4
        if phrase_settings.speed < 0.7: phrase_settings.speed = 0.7
        
        Audio.adjust_audio_speed(generated_audio_path, new_audio_path, speed=phrase_settings.speed)
        
        audio_slice = AudioSegment.from_wav(new_audio_path)
        if phrase_settings.volume > 0:
            audio_slice = audio_slice + phrase_settings.volume
        elif phrase_settings.volume < 0: 
            audio_slice = audio_slice - phrase_settings.volume
        
        #remove chunk
        os.remove(new_audio_path)

        return audio_slice


class Video:
    """
    Class representing a video.

    Attributes:
        file_path (str): The file path of the video.
        language (str): The language of the video.
    """

    def __init__(self, file_path: str, video_name_ext:str, language: str = "Unknown"):
        """
        The constructor for the Video class.

        Args:
            file (str): The file path of the video.
            language (str): The language of the video.
        """
        self.file_path = file_path
        self.language = language
        self.video_name = video_name_ext
    
    def __str__(self) -> str:
        return f"Video: {self.get_filename()}. language: {self.get_language()}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def get_filename(self) -> str:
        """
        Get the file path of the video.

        Returns:
            str: The file path of the video.
        """
        return os.path.join(CORE_PARENT_DIR, self.file_path)

    def set_filename(self, file_path: str):
        """
        Set the file path of the video.

        Args:
            file (str): The new file path of the video.
        """
        self.file_path = file_path

    def get_language(self) -> str:
        """
        Get the language of the video.

        Returns:
            str: The language of the video.
        """
        return self.language

    def set_language(self, language: str):
        """
        Set the language of the video.

        Args:
            language (str): The new language of the video.
        """
        self.language = language
    
    def get_duration(self) -> int:
        """
        Get the duration in milliseconds of the video.

        Returns:
            int: The duration of the video.
        """
        clip = VideoFileClip(self.file_path)
        duration = clip.duration
        clip.close()
        return duration * 1000

class Phrase:
    """
    Class representing a single phrase/sentence. 

    Attributes:
        index (int): The position of the current phrase in the whole text. An integer >= 0. Used for ordering.
        start (int): The time (in milliseconds) when the phrase began to be spoken.
        end (int): The time (in milliseconds) when the phrase ended.
        speaker (set): Identify which speaker this phrase belongs to.
        text (str): The content, presumibly in Unicode.
    """ # TODO check the work for unicode characters.

    def __init__(self, index: int, start: int, end: int, speaker:set, text: str):
        self.index = index
        self.start = start
        self.end = end
        self.speaker = speaker
        self.text = text

    def __str__(self) -> str:
        return f"\nPhrase {self.index}: {self.text}  starts: {self.start} ms.  ends: {self.end} ms.  spoken by: {self.speaker}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def deepcopy(self):
        return Phrase(self.index,self.start,self.end,self.speaker,self.text)
    
    def get_start_time(self) -> int:
        """
        Get the time (in milliseconds) when the phrase began to be spoken.

        Returns:
            int: The start time of the phrase in milliseconds.
        """
        return self.start
    
    def set_start_time(self, start_time: int):
        """
        Set time (in milliseconds) when the phrase began to be spoken.

        Args:
            start_time (int): The start time of the phrase in milliseconds.
        """
        self.start = start_time
    
    def get_end_time(self) -> int:
        """
        Get the time (in milliseconds) when the phrase ended.

        Returns:
            int: The end time of the phrase in milliseconds.
        """
        return self.end
    
    def set_end_time(self, end_time: int):
        """
        Set time (in milliseconds) when the phrase ended.

        Args:
            end_time (int): The end time of the phrase in milliseconds.
        """
        self.end = end_time
    
    def get_speaker_id(self):
        """
        Get the ID of the speaker of the phrase.

        Returns:
            (): The speaker identifier.
        """
        return self.speaker
    
    def set_speaker_id(self, speaker_id):
        """
        Set the ID of the speaker of the phrase.

        Args:
            speaker_id (): The speaker identifier.
        """
        self.speaker = speaker_id
    
    def get_text(self) -> str:
        """
        Get the phrase content/text.

        Returns:
            str: The phrase text.
        """
        return self.text
    
    def set_text(self, text):
        """
        Set the phrase content/text.

        Args:
            str: The phrase text.
        """
        self.text = text


class Audio_Gen_Settings:
    """
    Class representing a single phrase/sentence 's settings. 

    Attributes:
        phrase (Phrase): .
        start (int): The time (in milliseconds) when the phrase began to be spoken.
        end (int): The time (in milliseconds) when the phrase ended.
        speaker (set): Identify which speaker this phrase belongs to.
        text (str): The content, presumibly in Unicode.
    """ 
    def __init__(self, language: str, translated_phrase: Phrase, phrase_settings: PhraseSettings, speaker_settings: SpeakerSettings):
        self.language = language
        self.text = translated_phrase.text
        self.original_start = translated_phrase.get_start_time()
        self.original_end = translated_phrase.get_end_time()
        self.original_duration = self.original_end - self.original_start
        self.speaker_id = translated_phrase.speaker
        assert(self.speaker_id == speaker_settings.speaker)

        self.generated_audio_path = None
        self.current_speed = phrase_settings.speed
        self.current_volume = 0
    
    def info_to_generate_audio(self):
        return self.text, self.language, self.speaker_id
    
    def change_generated_audio(self, new_audio_path: str):
        self.generated_audio_path = new_audio_path
    
    

    


        

class Text:
    """
    Base class representing a text.
    
    It may includes more information such as phrases/sentences separation, 
    durations of the linked audio or video, and the language of the text.
    """
    full_text = ""
    phrases = []
    language = "Unknown"

    def __str__(self) -> str:
        return f"Text: {self.get_full_text()}.\n  language: {self.get_language()}"
    
    def __repr__(self) -> str:
        return self.__str__()

    def get_language(self) -> str:
        """
        Get the language of the text.

        Returns:
            str: The language of the text.
        """
        return self.language

    def set_language(self, language: str):
        """
        Set the language of the text.

        Args:
            language (str): The new language of the text.
        """
        self.language = language

    def add_phrase(self, index: int, start: int, end: int, speaker_id, text: str):
        """
        Add a phrase to the list.

        Args:
            index (int): The position of the current phrase in the whole text. An integer >= 0. Used for ordering.
            start (int): The time (in milliseconds) when the phrase began to be spoken.
            end (int): The time (in milliseconds) when the phrase ended.
            speaker_id (): Identify which speaker this phrase belongs to.
            text (str): The content, presumibly in Unicode.
        """
        # TODO Make the full check on the phrase
        self.phrases.append(Phrase(index, start, end, speaker_id, text))
        # TODO Sort self.phrases by index
    
    def get_phrase(self, indexof:int) -> Phrase:
        """
        Get the indexof-th phrase of the text.

        Returns:
            str: The indexof-th phrase of the text.
        """
        # TODO add more get parameters and check whether the index is a valid one
        return self.phrases[indexof]
    
    def get_full_text(self) -> str:
        """
        Get the full text.

        Returns:
            str: The full text.
        """
        return self.full_text

class SText(Text):
    """
    Class representing the source text extracted from the whole original video.
    """
    def __init__(self, full_text: str, video_duration: int, language: str = "Unknown", phrases: list=None):
        """
        The constructor for the SText class.

        Args:
            full_text (str): All the text non separated.
            video_duration (int): The duration (in milliseconds) of the original video.
            language (str): The language of the original video.
            phrases (str) (optional): A list with the pieces of the text in format of a Phrase instance.
        """
        self.full_text = full_text
        if phrases == None:
            # TODO Make the full check on the phrase
            self.phrases = [Phrase(0, 0, video_duration, 0, self.full_text)]
        else:
            self.phrases = phrases
            if full_text == "" or full_text == None:
                concat_text = ""
                for phr in self.phrases:
                    phr: Phrase
                    concat_text += f" {phr.get_text()} "
                self.full_text = concat_text
            
        self.video_duration = video_duration
        self.language = language
        
    # def get_video_duration_ms(self) -> int:
    #     """
    #     Get the duration (in milliseconds) of the original video.

    #     Returns:
    #         int: The duration (in milliseconds) of the original video.
    #     """
    #     return self.video_duration

    # def set_video_duration_ms(self, duration_ms: int):
    #     """
    #     Set the duration (in milliseconds) of the original video.

    #     Args:
    #         duration_ms (int): The duration (in milliseconds) of the original video.
    #     """
    #     self.video_duration = duration_ms

class TText(Text):
    """
    Class representing the translated text.
    """
    def __init__(self, full_text: str, language: str = "Unknown", phrases: list=None):
        """
        The constructor for the TText class.

        Args:
            full_text (str): All the text non separated.
            language (str): The language of the translation.
            phrases (str) (optional): A list with the pieces of the text in format of a Phrase instance.  The time intervals for these phrases represent the time intervals of the phrase in the original audio/video.
        """
        self.full_text = full_text
        if phrases == None:
            # TODO Make the full check on the phrase
            self.phrases = []
        else:
            self.phrases = phrases
            if full_text == "" or full_text == None:
                concat_text = ""
                for phr in self.phrases:
                    phr: Phrase
                    concat_text += f" {phr.get_text()} "
                self.full_text = concat_text
        self.language = language
        
