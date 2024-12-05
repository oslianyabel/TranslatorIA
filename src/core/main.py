from src.core.common import Audio, Video, PhraseSettings, SpeakerSettings, Phrase, preprocess, errors
from src.core.common.common import EU_languages, iso_code_2_dict
from src.core import speech_to_text as s2t
from src.core.audio_video_separation import audio_split_and_S2T, automatic_voices_extraction
from src.core import text_to_speech as mytts
from src.core import translation
from src.core import join_audio_video as gen_vid
from pydub import AudioSegment
from pathlib import Path
import os
import random
import pickle
import string
import copy

BASE_DIR = Path(__file__).resolve().parent.parent.parent
GPU_USAGE = True
def dict_deepcopy(to_copy :dict) -> dict:
    copy = dict()
    for key in to_copy:
        item = to_copy[key]
        copy[key] = item.deepcopy()
    return copy

class TranslationPack:
    def __init__(self) -> None:
        self.source_video:Video = None 
        self.source_audio:Audio = None 
        self.source_language_sel:str = None
        self.source_phrases:dict = None
        self.original_source_phrases:dict = None

        self.translated_video:Video = None 
        self.translated_audio:Audio = None 
        self.translated_language_sel:str = None
        self.translated_phrases:dict = None
        self.original_translated_phrases:dict = None

        self.phrases_settings:list = None # list of PhraseSettings of translated_phrases
        self.speakers_settings:list = None # list of SpeakerSettings 
    
        self.changes_not_applied = {'changes_in_source_text': False, 
                                    'changes_in_transl_text': False,
                                    'changes_in_phrases_settings': False,
                                    'changes_in_speaker_settings': False}

        self.voices_from_video = False

        self.s2t_model:s2t.S2T_Base = None # Speech-to-text model
        self.transl_model:translation.Text_Translation = None # Translator model
        self.tts_model:mytts.TTS_Base = None # Text-to-speech model
    
    def __str__(self) -> str:
        return f"{self.source_video}, in {self.source_language_sel}.\n{self.source_phrases}\n\n"+\
                f"{self.translated_video}, in {self.translated_language_sel}.\n{self.translated_phrases}\n\n"+\
                f"{self.phrases_settings}\n{self.speakers_settings}"
    
    def source_language(self) -> str:
        return self.source_language_sel

    def translated_language(self) -> str:
        return self.translated_language_sel
    
class Process_Video:
    s2t_ordered = ['whisper']
    s2t_models = {"whisper":s2t.S2T_Whisper}
    transl_ordered = ['multimodel','google']
    transl_models = {"multimodel":translation.Multimodel_translator, "google":translation.Text_Translation_google}
    tts_ordered = ['google_cloud','MMS','bark','google']
    tts_models = {"MMS":mytts.TTS_MMS, "google":mytts.TTS_google, "bark":mytts.TTS_Bark, 'google_cloud':mytts.TTS_google_cloud}

    def __init__(self, pack: TranslationPack = None) -> None:
        self.source_video = None
        self.source_audio = None
        self.source_language = None
        self.source_phrases = None
        self.original_source_phrases = None
        self.dest_language = None
        self.translated_phrases = None
        self.original_translated_phrases = None
        self.translated_audio = None
        self.translated_video = None

        self.phrases_settings = None 
        self.speakers_settings = None 
        self.changes_not_applied = None
        self.voices_from_video = None

        if pack != None:
            self.__from_translation_pack(pack)

        self.s2t_model:s2t.S2T_Base = self.s2t_models[self.s2t_ordered[0]]
        self.transl_model:translation.Text_Translation = self.transl_models[self.transl_ordered[0]]
        self.tts_model:mytts.TTS_Base = self.tts_models[self.tts_ordered[0]]
        self.cloning_model = mytts.CloneTTS_XTTT

        self.audio_path = os.path.join("src","app","static","audio")
        self.gen_video_path = os.path.join("src","app","static","videos")
  
    def __from_translation_pack(self, pack: TranslationPack):
        self.source_video = pack.source_video
        self.source_audio = pack.source_audio
        self.source_language = pack.source_language_sel

        if pack.source_phrases != None:            
            self.source_phrases = dict_deepcopy(pack.source_phrases)
        if pack.original_source_phrases != None:            
            self.original_source_phrases = dict_deepcopy(pack.original_source_phrases)
        
        self.translated_video = pack.translated_video
        self.translated_audio = pack.translated_audio
        self.dest_language = pack.translated_language_sel
        if pack.translated_phrases != None:            
            self.translated_phrases = dict_deepcopy(pack.translated_phrases)
        if pack.original_translated_phrases != None:            
            self.original_translated_phrases = dict_deepcopy(pack.original_translated_phrases)
        
        if pack.phrases_settings != None:
            self.phrases_settings = pack.phrases_settings.copy()
        if pack.speakers_settings != None:
            self.speakers_settings = pack.speakers_settings.copy()
        try:
            self.changes_not_applied = dict_deepcopy(pack.changes_not_applied)
        except: 
            self.changes_not_applied = {'changes_in_source_text': False, 
                                        'changes_in_transl_text': False,
                                        'changes_in_phrases_settings': False,
                                        'changes_in_speaker_settings': False}
        try:
            self.voices_from_video = pack.voices_from_video
        except:
            self.voices_from_video = False
        
    def get_translation_pack(self) -> TranslationPack:
        result = TranslationPack()

        result.source_video = self.source_video
        result.source_audio = self.source_audio
        result.source_language_sel = self.source_language
        if self.source_phrases != None:            
            result.source_phrases = dict_deepcopy(self.source_phrases)
        if self.original_source_phrases != None:            
            result.original_source_phrases = dict_deepcopy(self.original_source_phrases)
        
        result.translated_video = self.translated_video
        result.translated_audio = self.translated_audio
        result.translated_language_sel = self.dest_language
        if self.translated_phrases != None:            
            result.translated_phrases = dict_deepcopy(self.translated_phrases)
        if self.original_translated_phrases != None:            
            result.original_translated_phrases = dict_deepcopy(self.original_translated_phrases)
        
        if self.phrases_settings != None:
            result.phrases_settings = self.phrases_settings.copy()
        if self.speakers_settings != None:
            result.speakers_settings = self.speakers_settings.copy()

        result.changes_not_applied = self.changes_not_applied
        result.voices_from_video = self.voices_from_video
            
        result.s2t_model = self.s2t_model
        result.transl_model = self.transl_model
        result.tts_model = self.tts_model

        return result
 
    def get_system_languages(self) -> list:
        return EU_languages
    
    def get_s2t_languages(self) -> list:
        return list(self.s2t_model.supported_languages(None,True).keys())
    
    def get_tts_languages(self) -> list:
        return list(self.tts_model.supported_languages(None,True).keys())
    
    def get_cloning_languages(self) -> list:
        return list(self.cloning_model.supported_languages(None,True).keys())

    def set_video(self, video_path :str, language: str = "Unknown"):
        
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(BASE_DIR, self.audio_path, video_name+'.wav')
        if language in self.get_system_languages():
            self.source_language = language
        elif language != "Unknown":
            raise errors.InvalidInputError(f"Invalid language: {language}. Use one of the following: {self.get_system_languages()}")
        self.source_video, self.source_audio = preprocess.video_file_to_Video_Audio(video_file=video_path, path_to_save_audio=audio_path, language=language)
    
    def get_speech_to_text(self, language :str, whisper_model :str='medium'):
        
        if self.source_video == None or self.source_audio == None:
            raise errors.MissingPreviousInfoError("No source video or audio, cannot extract text")

        if language in self.get_system_languages():
            self.source_language = language
        else:
            raise errors.InvalidInputError(f"Invalid language: {language}. Use one of the following: {self.get_system_languages()}")
        
        self.source_video.set_language(self.source_language)
        self.source_audio.set_language(self.source_language)

        self.source_audio, phrases = audio_split_and_S2T(self.source_audio, GPU_USAGE, whisper_model)
        phrases:dict
        self.souce_split = self.source_audio.get_split()
        self.source_phrases = dict_deepcopy(phrases)
        self.original_source_phrases = dict_deepcopy(phrases)

        if self.voices_from_video:
            self.auto_voice_extraction()

        #     self.voices_from_video = False
        # # clean future work:
        self.translated_phrases = None
        self.original_translated_phrases = None
        self.translated_audio = None
        self.translated_video = None
        self.phrases_settings = None 

        return self.source_phrases

    def get_text_translation(self, dest_lang :str):
        if self.source_video == None or self.source_audio == None or self.source_language == None or self.source_phrases == None:
            raise errors.MissingPreviousInfoError("Cannot translate before getting original text")

        if dest_lang in self.get_system_languages():
            self.dest_language = dest_lang
        else:
            raise errors.InvalidInputError(f"Invalid language: {dest_lang}. Use one of the following: {self.get_system_languages()}")
        
        translator:translation.Text_Translation = self.transl_model() #translation.Multimodel_translator("GoogleTranslator")

        dest_lang_code = translator.aviable_languages().get(self.dest_language,None)
        if dest_lang_code == None:
            raise errors.InvalidInputError(f"Invalid language: {dest_lang} for translation")
        source_lang_code = translator.aviable_languages().get(self.source_language,None)
        if source_lang_code == None:
            raise errors.InvalidInputError(f"Invalid language: {self.source_language} for translation")

        self.translated_phrases = dict()
        self.original_translated_phrases = dict()
        self.phrases_settings = []

        for id in self.source_phrases:
            phrase:Phrase = self.source_phrases[id]
            transl = translator.translate_text(input_text = phrase.get_text(), target_lang=dest_lang_code, source_lang=source_lang_code)
            self.translated_phrases[id] = Phrase(phrase.index, phrase.start, phrase.end, phrase.speaker, transl )
            self.original_translated_phrases[id] = Phrase(phrase.index, phrase.start, phrase.end, phrase.speaker, transl)
            self.phrases_settings.append(PhraseSettings())
        speakers = set()
        for id in self.translated_phrases:
            spk = self.translated_phrases[id].speaker
            speakers.add(spk)

        speakers = list(speakers)
        
        if self.speakers_settings == None:
            self.random_voice_sett(dest_lang_code)
        elif len(self.speakers_settings) == 1 and self.speakers_settings[0].speaker == -1:
            newss = []
            for i in range(len(speakers)):
                ss:SpeakerSettings = copy.deepcopy(self.speakers_settings[0])
                ss.speaker = i
                newss.append(ss)
            self.speakers_settings = newss.copy()
            # print(self.speakers_settings) 

        # # clean future work:
        self.translated_audio = None
        self.translated_video = None

        return self.translated_phrases

    def random_voice_sett(self, lang_code, syntetizer: mytts.TTS_Base=None):
        if syntetizer == None: 
            syntetizer = self.tts_model()
        # if not syntetizer.voices_choices():
        #     return
        self.speakers_settings = []
        speakers = set()
        for id in self.translated_phrases:
            spk = self.translated_phrases[id].speaker
            speakers.add(spk)

        speakers = sorted(list(speakers)) # don't think is necessary
        
        for id in speakers:
            all_f = syntetizer.preset_voices(lang_code,'female',False)
            all_m = syntetizer.preset_voices(lang_code,'male',False)
            if len(all_f) > 0 and len(all_m) > 0:
                voice_f = random.choice(all_f)
                voice_m = random.choice(all_m)
                x = random.randint(0,100)
                if x % 2 == 0:
                    self.speakers_settings.append(SpeakerSettings(id, 'female', voice_f))
                else:
                    self.speakers_settings.append(SpeakerSettings(id, 'male', voice_m))
            elif len(all_f) > 0 :
                voice_f = random.choice(all_f)
                self.speakers_settings.append(SpeakerSettings(id, 'female', voice_f))
            elif len(all_m) > 0:
                voice_m = random.choice(all_m)
                self.speakers_settings.append(SpeakerSettings(id, 'male', voice_m))
        
        print('self.speakers_settings',self.speakers_settings)
        assert(len(self.speakers_settings) == len(speakers))

    def edit_source_phrase(self, phrase_id: int, new_text: str):
        if self.source_phrases == None:
            raise errors.MissingPreviousInfoError("Cannot edit non-existent phrases")

        phrase:Phrase = self.source_phrases[phrase_id]
        phrase.set_text(new_text)
        self.source_phrases[phrase_id] = phrase.deepcopy()
        # print("self.source_phrases[phrase_id] == self.original_source_phrases[phrase_id]",self.source_phrases[phrase_id].text == self.original_source_phrases[phrase_id].text)
        # print(self.source_phrases[phrase_id].text)
        # print(self.original_source_phrases[phrase_id].text)
        return self.source_phrases
    
    def edit_transl_phrase(self, phrase_id: int, new_text: str):
        if self.translated_phrases == None:
            raise errors.MissingPreviousInfoError("Cannot edit non-existent phrases")

        phrase:Phrase = self.translated_phrases[phrase_id]
        phrase.set_text(new_text)
        self.translated_phrases[phrase_id] = phrase.deepcopy()
        # print("self.translated_phrases[phrase_id] == self.original_translated_phrases[phrase_id]",self.translated_phrases[phrase_id].text == self.original_translated_phrases[phrase_id].text)
        # print(self.translated_phrases[phrase_id].text)
        # print(self.original_translated_phrases[phrase_id].text)
        return self.translated_phrases
    
    def restore_source_phrase(self, phrase_id: int):
        if self.source_phrases == None or self.original_source_phrases == None:
            raise errors.MissingPreviousInfoError("Cannot restore non-existent phrases")

        # print("self.source_phrases[phrase_id] == self.original_source_phrases[phrase_id]",self.source_phrases[phrase_id].text == self.original_source_phrases[phrase_id].text)
        self.source_phrases[phrase_id] = self.original_source_phrases[phrase_id].deepcopy()
        # print(self.source_phrases[phrase_id].text)
        # print(self.original_source_phrases[phrase_id].text)
        return self.source_phrases
        
    def restore_transl_phrase(self, phrase_id: int):
        if self.translated_phrases == None or self.original_translated_phrases == None:
            raise errors.MissingPreviousInfoError("Cannot restore non-existent phrases")

        # print("self.translated_phrases[phrase_id] == self.original_translated_phrases[phrase_id]",self.translated_phrases[phrase_id].text == self.original_translated_phrases[phrase_id].text)
        self.translated_phrases[phrase_id] = self.original_translated_phrases[phrase_id].deepcopy()
        # print(self.translated_phrases[phrase_id].text)
        # print(self.original_translated_phrases[phrase_id].text)
        return self.translated_phrases

    def restore_original_times(self):
        if self.dest_language == None or self.translated_phrases == None:
            print(self.dest_language)
            print(self.translated_phrases)
            raise errors.MissingPreviousInfoError("Cannot restore original times without translated phrases.")
        for id in self.translated_phrases:
            self.translated_phrases[id].start = self.source_phrases[id].start
            self.translated_phrases[id].end = self.source_phrases[id].end

    def __tts_models_from_language(self, language: str):
        models_for_language = []
        for modl_str in self.tts_ordered:
            modl = self.tts_models[modl_str]
            if language in list(mytts.modl.supported_languages(None,True).keys()):
                models_for_language.append(modl)
        return models_for_language
    
    def auto_voice_extraction(self):
        self.speakers_settings = []
        voices_by_spks:dict = automatic_voices_extraction(self.source_phrases, self.source_audio, 'auto voice')
        print('voices_by_spks',voices_by_spks)
        for i in range(len(list(voices_by_spks.keys()))):
            self.speakers_settings.append(voices_by_spks[i])
        self.voices_from_video = True
        return self.speakers_settings
    
    def __tts_manager(self, path :str, name :str, adjust_speed_by_original=True, by_phr_speed=False):
        syntetizer = None
        cloned_syntetizer = None
        audio_slices = []
        current_audio_size = 0

        lang_code = iso_code_2_dict.get(self.dest_language, None)
        if lang_code == None:
            raise errors.InvalidInputError(f"Invalid language {self.dest_language}")
        if self.speakers_settings == None:
                self.random_voice_sett(lang_code, self.tts_model())
        
        for id in self.translated_phrases:
            phrase:Phrase = self.translated_phrases[id]

            save_audio_path = os.path.join(BASE_DIR,path,f"{name}_{iso_code_2_dict[self.dest_language]}_{phrase.get_start_time()}-{phrase.get_end_time()}.wav")
            voice_id:SpeakerSettings = self.speakers_settings[phrase.get_speaker_id()]

            # if phrase text is empty generate a silence of the appropiate duration and go to next phrase
            if phrase.get_text() == "":
                audio_slice = AudioSegment.silent(duration=phrase.get_end_time() - phrase.get_start_time)
                audio_slices.append(audio_slice) 
                current_audio_size += len(audio_slice)
                continue

            if voice_id.cloned:
                if cloned_syntetizer == None: 
                    cloned_syntetizer:mytts.CloneTTS_Base = self.cloning_model(GPU_USAGE) 
                cloned_syntetizer.generate_speech(input_text=phrase.get_text(), language=self.dest_language, save_audio_path=save_audio_path, voice_clone=voice_id)
            else: 
                if syntetizer == None: 
                    syntetizer:mytts.TTS_Base = self.tts_model(GPU_USAGE)
                if syntetizer.voices_choices():
                    syntetizer.generate_speech(input_text=phrase.get_text(), language=self.dest_language, save_audio_path=save_audio_path, voice_sett=voice_id)
                else:
                    syntetizer.generate_speech(input_text=phrase.get_text(), language=self.dest_language, save_audio_path=save_audio_path)
            print(save_audio_path)
            # Adjust speed of audio_slice
            if by_phr_speed:
                audio_slice = Audio.adjust_audio(generated_audio_path=save_audio_path, phrase_settings=self.phrases_settings[id])
            else:
                if adjust_speed_by_original:
                    curr_audio_slice = AudioSegment.from_wav(save_audio_path)
                    current_duration = len(curr_audio_slice)
                    print(f'{id} current_duration',current_duration)
                    speed = current_duration / (self.source_phrases[id].get_end_time() - self.source_phrases[id].get_start_time())
                    print(f'{id} speed',speed)
                    if speed > 1.4: speed = 1.4
                    if speed < 0.7: speed = 0.7

                    self.phrases_settings[id].speed = speed
                    audio_slice = Audio.adjust_audio(generated_audio_path=save_audio_path, phrase_settings=self.phrases_settings[id])
                else:
                    curr_audio_slice = AudioSegment.from_wav(save_audio_path)
                    current_duration = len(curr_audio_slice)
                    print(f'{id} current_duration',current_duration)
                    speed = current_duration / (phrase.get_end_time() - phrase.get_start_time())
                    print(f'{id} speed',speed)
                    if speed > 1.4: speed = 1.4
                    if speed < 0.7: speed = 0.7
                    
                    self.phrases_settings[id].speed = speed
                    audio_slice = Audio.adjust_audio(generated_audio_path=save_audio_path, phrase_settings=self.phrases_settings[id])
            
            audio_slices.append(audio_slice) 
            current_audio_size += len(audio_slice)
            #remove chunk
            # os.remove(save_audio_path)
        
        return audio_slices, current_audio_size

    def __join_audio_slices(self, audio_slices:list, phrases:dict, current_audio_size:int, keep_orig_audio_in_sil=False, by_phr_speed=False):
        def add_silence(sourceAudio, from_ms, to_ms, keep_orig_audio_in_sil, sourcePhr):
            if keep_orig_audio_in_sil:
                if len(sourceAudio) >= to_ms:
                    print(f'adding silence from original audio, from {from_ms} to {to_ms}')
                    return sourceAudio[from_ms:to_ms]
            
            return AudioSegment.silent(duration=(to_ms-from_ms))
            
        def was_silence(sourceAudio, from_ms, to_ms, sourcePhr):
            i = 0
            phrase:Phrase = sourcePhr[0]
            while i < len(sourcePhr)-1 and phrase.get_end_time() < from_ms:
                i += 1
                phrase:Phrase = sourcePhr[i]

            if i >= len(sourcePhr)-1: # TODO
                return AudioSegment.silent(duration=(to_ms-from_ms))
            
            if phrase.get_start_time() > to_ms:
                return sourceAudio[from_ms:to_ms]
                
            if phrase.get_start_time() > from_ms:# and phrase.get_end_time() > to_ms:
                return sourceAudio[from_ms:phrase.get_start_time()]  + AudioSegment.silent(duration=(to_ms-phrase.get_start_time()))

            return AudioSegment.silent(duration=(to_ms-from_ms))
        keep_orig_audio_in_sil = False # TODO remove
        sourceAudio = AudioSegment.from_wav(self.source_audio.get_filename())
        # generated_audio = None
        # if not by_phr_speed:
        #     beg_sil = phrases[0].get_start_time()
        #     print('beg_sil',beg_sil)
        #     if beg_sil > 0:
        #         generated_audio = add_silence(sourceAudio, 0, beg_sil, keep_orig_audio_in_sil, self.source_phrases)
        #         generated_audio = generated_audio + audio_slices[0]
        #         current_audio_size += beg_sil 
        #     else: generated_audio = audio_slices[0]

        #     i = 1
        #     last_end = phrases[0].get_end_time()
        #     while i < len(phrases):
        #         difference = phrases[i].get_start_time() - last_end
        #         silence = add_silence(sourceAudio, last_end, phrases[i].get_start_time(), keep_orig_audio_in_sil, self.source_phrases)
        #         generated_audio = generated_audio + silence + audio_slices[i]
        #         current_audio_size += difference
        #         last_end = phrases[i].get_end_time()
        #         i += 1

        #     end_sil = self.source_audio.get_audio_duration_ms() - phrases[len(phrases)-1].get_end_time()
        #     if end_sil > 0:
        #         silence = add_silence(sourceAudio, self.source_audio.get_audio_duration_ms(), phrases[len(phrases)-1].get_end_time(), keep_orig_audio_in_sil, self.source_phrases)
        #         generated_audio = generated_audio + silence
        #         current_audio_size += end_sil
        #     return generated_audio, current_audio_size
        
        beg_sil = phrases[0].get_start_time()
        if beg_sil > 0:
            generated_audio = add_silence(sourceAudio, 0, beg_sil, keep_orig_audio_in_sil, self.source_phrases)
            generated_audio = generated_audio + audio_slices[0]
            current_audio_size += beg_sil 
        else: generated_audio = audio_slices[0]
        
        i = 1
        while i < len(phrases):
            last_actual_end = len(generated_audio)
            last_supposed_end = phrases[i-1].get_end_time()
            curr_beg = phrases[i].get_start_time()

            # The phrase i-1 ended before the phrase 1 needed to to begin
            if last_actual_end < curr_beg: 
                
                # time of silence between phrase i-1 and phrase i 
                difference = phrases[i].get_start_time() - last_actual_end 
                silence = add_silence(sourceAudio, last_actual_end, phrases[i].get_start_time(), keep_orig_audio_in_sil, self.source_phrases)
                generated_audio = generated_audio + silence + audio_slices[i]
                current_audio_size += difference
            else:
                # The phrase i-1 ended after the phrase 1 needed to to begin
                generated_audio = generated_audio + audio_slices[i]
            i += 1
        last_actual_end = len(generated_audio)
        original_audio_duration = self.source_audio.get_audio_duration_ms()
        if last_actual_end < original_audio_duration:
            end_sil = original_audio_duration - last_actual_end
            print(f'adding silence at the final, with a duration of {end_sil}. From {last_actual_end} to {original_audio_duration}.')
            silence = add_silence(sourceAudio, last_actual_end, original_audio_duration-1, keep_orig_audio_in_sil, self.source_phrases)
            generated_audio = generated_audio + silence
            current_audio_size += end_sil
        
        return generated_audio, current_audio_size

    def generate_video_main(self, mode='default', keep_orig_audio_in_sil=False, watermark=False):
        """
            modes = ['default','restore_origin','default_random','restore_origin_random','by_phr_sett']
        """
        if self.dest_language == None or self.translated_phrases == None:
            print(self.dest_language)
            print(self.translated_phrases)
            if self.dest_language == None:
                self.translated_phrases = None
            raise errors.MissingPreviousInfoError("Cannot generate video without the text for it.")
        
        # GENERATE AUDIO
        path = os.path.join('src', (os.path.split(self.source_audio.get_filename())[0]).split('src/',1)[1] )
        name = os.path.splitext(os.path.basename(self.source_audio.get_filename()))[0] # name = filename # no .wav  
        if mode == 'default':
            """ Generate translated video in default mode. 
                Adjust speed and silences by transl_phrases time stamps
                Choose current or default (if none current) volume
                Choose current or random (if none current) voice settings               
            """            
            audio_slices, current_audio_size = self.__tts_manager(path, name, adjust_speed_by_original=False)
            generated_audio, current_audio_size = self.__join_audio_slices(audio_slices, self.translated_phrases, current_audio_size, keep_orig_audio_in_sil, False)
            print(f"current audio size: {current_audio_size}. original audio size: {self.source_audio.get_audio_duration_ms()}")
        elif mode == 'restore_origin':
            """ Generate translated video in restore_origin mode. 
                Adjust speed and silences by source_phrases time stamps
                Choose current or default (if none current) volume
                Choose current or random (if none current) voice settings                
            """ 
            audio_slices, current_audio_size = self.__tts_manager(path, name, adjust_speed_by_original=True)
            generated_audio, current_audio_size = self.__join_audio_slices(audio_slices, self.source_phrases, current_audio_size, keep_orig_audio_in_sil, False)
            print(f"current audio size: {current_audio_size}. original audio size: {self.source_audio.get_audio_duration_ms()}")
        elif mode == 'default_random':
            """ Generate translated video in default_random mode. 
                Adjust speed and silences by transl_phrases time stamps
                Choose current or default (if none current) volume
                Random voice settings                
            """ 
            self.random_voice_sett(iso_code_2_dict[self.dest_language]) # TODO
            audio_slices, current_audio_size = self.__tts_manager(path, name, adjust_speed_by_original=False)
            for sl in audio_slices:
                print(len(sl))
            generated_audio, current_audio_size = self.__join_audio_slices(audio_slices, self.translated_phrases, current_audio_size, keep_orig_audio_in_sil, False)
            print(f"current audio size: {current_audio_size}. original audio size: {self.source_audio.get_audio_duration_ms()}")
        elif mode == 'restore_origin_random':
            """ Generate translated video in restore_origin_random mode. 
                Adjust speed and silences by source_phrases time stamps
                Choose current or default (if none current) volume
                Random voice settings                
            """ 
            self.random_voice_sett(iso_code_2_dict[self.dest_language]) # TODO
            audio_slices, current_audio_size = self.__tts_manager(path, name, adjust_speed_by_original=True)
            generated_audio, current_audio_size = self.__join_audio_slices(audio_slices, self.source_phrases, current_audio_size, keep_orig_audio_in_sil, False)
            print(f"current audio size: {current_audio_size}. original audio size: {self.source_audio.get_audio_duration_ms()}")
        elif mode == 'by_phr_speed':
            """ Generate translated video in by_phr_speed mode. 
                Adjust speed and silences by phrase_speed choice
                Choose current or default (if none current) volume
                Choose current or random (if none current) voice settings       
            """  
            audio_slices, current_audio_size = self.__tts_manager(path, name, adjust_speed_by_original=False, by_phr_speed=True)
            generated_audio, current_audio_size = self.__join_audio_slices(audio_slices, self.translated_phrases, current_audio_size, keep_orig_audio_in_sil, True)
            print(f"current audio size: {current_audio_size}. original audio size: {self.source_audio.get_audio_duration_ms()}")
        
        save_audio_path = os.path.join(BASE_DIR, path, name+'_'+iso_code_2_dict[self.dest_language]+'.wav')
        generated_audio.export(save_audio_path, format="wav")
        self.translated_audio = Audio(save_audio_path, self.dest_language)
        # GENERATE VIDEO
        return self._generate_video(watermark=watermark)

    def get_translated_video(self, auto_adjust=True, watermark=False):
        
        if self.dest_language == None or self.translated_phrases == None:
            print('translation language: ',self.dest_language)
            print('translation text: ',self.translated_phrases)
            raise errors.MissingPreviousInfoError("Cannot generate video without the text for it.")

        # models = {"MMS":mytts.TTS_MMS, "google":mytts.TTS_google, "bark":mytts.TTS_Bark}

        # path = os.path.join('src',self.source_audio.get_filename().split('src/',1)[1]) # path = 'src/app/.../filename.wav'  
        path = os.path.join('src', (os.path.split(self.source_audio.get_filename())[0]).split('src/',1)[1] )
        name = os.path.splitext(os.path.basename(self.source_audio.get_filename()))[0] # name = filename # no .wav   
        
        audio_slices, current_audio_size = self.__tts_manager(path, name, auto_adjust)

        generated_audio = None

        beg_sil = self.translated_phrases[0].get_start_time()
        end_sil = self.source_audio.get_audio_duration_ms() - self.translated_phrases[len(self.translated_phrases)-1].get_end_time()
        # print('beg_sil',beg_sil,'\tend_sil',end_sil)
        # print("wanted duration",self.source_audio.get_audio_duration_ms(), '\tcurrent_audio_size', current_audio_size)

        if self.source_audio.get_audio_duration_ms() - current_audio_size > 2000:
            if beg_sil + end_sil > 100 and self.source_audio.get_audio_duration_ms() - current_audio_size > beg_sil + end_sil:
                
                beg_silence = AudioSegment.silent(duration=beg_sil)
                end_silence = AudioSegment.silent(duration=end_sil)
                generated_audio = beg_silence

                current_audio_size = current_audio_size + beg_sil + end_sil
                difference = self.source_audio.get_audio_duration_ms() - current_audio_size
                # print('new current_audio_size', current_audio_size, '\tdifference', difference)
                # print("current_audio_size: ",current_audio_size, "original duration: ",audio.get_audio_duration_ms()," difference: ",difference)
                silences_to_add = len(audio_slices) + 1
                silence_dur = int(difference / silences_to_add)
                # print("Every silence will last: ",silence_dur," with ",silences_to_add, " silences.")
                silence = AudioSegment.silent(duration=silence_dur)
                for slice in audio_slices:
                    generated_audio = generated_audio + slice + silence
                generated_audio = generated_audio + end_silence
            else:
                ## Add silences
                difference = self.source_audio.get_audio_duration_ms() - current_audio_size
                # print("current_audio_size: ",current_audio_size, "original duration: ",audio.get_audio_duration_ms()," difference: ",difference)
                silences_to_add = len(audio_slices) + 1
                silence_dur = int(difference / silences_to_add)
                # print("Every silence will last: ",silence_dur," with ",silences_to_add, " silences.")
                silence = AudioSegment.silent(duration=silence_dur)
                generated_audio = silence
                for slice in audio_slices:
                    generated_audio = generated_audio + slice + silence 
        else:
            for slice in audio_slices:
                if generated_audio == None:
                    generated_audio = slice
                else:
                    generated_audio = generated_audio + slice

        save_audio_path = os.path.join(BASE_DIR,path, name+iso_code_2_dict[self.dest_language]+'.wav')
        generated_audio.export(save_audio_path, format="wav")
        self.translated_audio = Audio(save_audio_path, self.dest_language)
        # self.translated_audio.set_split(audio_split) 

        # GENERATE VIDEO
        return self._generate_video(watermark=watermark)

    def _generate_video(self, watermark=False) -> str:

        if self.source_video == None or self.translated_audio == None:
            raise errors.MissingPreviousInfoError("To generate video is necesary the original video and the translated audio")

        vid_generator = gen_vid.Video_Audio_joiner(self.source_video, self.translated_audio)

        new_video_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])
        new_video_path = os.path.join(self.gen_video_path, new_video_name+'.mp4')
        # print(new_video_path)
        vid_generator.join(new_video_path)
        self.translated_video = Video(new_video_path, new_video_name, self.dest_language)

        if watermark:
            gen_vid.watermark_by_image(self.translated_video, os.path.join(BASE_DIR,"src","app","static","assets","img","Watermark.png"))

        return new_video_name+'.mp4'
        
    def recreate_video_from_spk_sett(self, settings_by_speaker: list, watermark=False):
        settings = ["volume","speed"]
        
        if self.dest_language == None or self.translated_phrases == None:
            raise errors.MissingPreviousInfoError("Cannot generate video without the text for it.")

        for id in self.translated_phrases:
            phrase:Phrase = self.translated_phrases[id]
            # speakers_settings[phrase.speaker]['speed'],speakers_settings[phrase.speaker]['volume']
            self.phrases_settings[id].volume = settings_by_speaker[phrase.speaker]['volume']
            self.phrases_settings[id].speed = settings_by_speaker[phrase.speaker]['speed']

        # audio_slices, _ = self.__tts_manager(path, name, False)
        
        # generated_audio = None

        # for slice in audio_slices:
        #     if generated_audio == None:
        #         generated_audio = slice
        #     else:
        #         generated_audio = generated_audio + slice

        # save_audio_path = os.path.join(BASE_DIR, path,name+iso_code_2_dict[self.dest_language]+'.wav')
        # generated_audio.export(save_audio_path, format="wav")
        # self.translated_audio = Audio(save_audio_path, self.dest_language)
        # # self.translated_audio.set_split(audio_split)

        # # GENERATE VIDEO
        # return self._generate_video(watermark=watermark)
        return self.generate_video_main(mode='default', watermark=watermark)

    def recreate_video_from_phr_sett(self, phrase_id: int, phrases_setting: PhraseSettings, watermark=False):
        settings = ["volume","speed"]
        
        if self.dest_language == None or self.translated_phrases == None:
            raise errors.MissingPreviousInfoError("Cannot generate video without the text for it.")

        # path = os.path.join('src',self.source_audio.get_filename().split('src/',1)[1]) # path = 'src/app/.../filename.wav'  
        path = os.path.join('src', (os.path.split(self.source_audio.get_filename())[0]).split('src/',1)[1] )
        name = os.path.splitext(os.path.basename(self.source_audio.get_filename()))[0] # name = filename # no .wav 
        
        self.phrases_settings[phrase_id] = phrases_setting

        # audio_slices, _ = self.__tts_manager(path, name, False)
        
        # generated_audio = None

        # for slice in audio_slices:
        #     if generated_audio == None:
        #         generated_audio = slice
        #     else:
        #         generated_audio = generated_audio + slice

        # save_audio_path = os.path.join(BASE_DIR,path,name+iso_code_2_dict[self.dest_language]+'.wav')
        # generated_audio.export(save_audio_path, format="wav")
        # self.translated_audio = Audio(save_audio_path, self.dest_language)
        # # self.translated_audio.set_split(audio_split)

        # # GENERATE VIDEO
        # return self._generate_video(watermark=watermark)
        return self.generate_video_main(mode='default', watermark=watermark)

    def can_s2t(self):
        if self.source_video == None or self.source_audio == None:
            return False
        return True
    def can_translate(self):
        if self.source_video == None or self.source_audio == None or self.source_language == None or self.source_phrases == None:
            return False
        return True
    def can_edit_source(self):
        if self.source_phrases == None:
                return False
        return True
    def can_edit_transl(self):
        if self.translated_phrases == None:
                return False
        return True
    def can_restore_source(self):
        if self.source_phrases == None or self.original_source_phrases == None:
                return False
        return True
    def can_restore_transl(self):
        if self.translated_phrases == None or self.original_translated_phrases == None:
                return False
        return True
    def can_restore_times(self):
        if self.source_phrases == None or self.dest_language == None or self.translated_phrases == None:
            return False
        return True
    def can_generate_video(self):
        if self.dest_language == None or self.translated_phrases == None or self.source_audio == None or self.dest_language == None:
            return False
        return True