from web_base.settings import BASE_DIR, STATICFILES_DIRS
from accounts.models import UserBase, TranslationInfo_User, Saved_voices_user
import os
import pickle
import random
from pydub import AudioSegment
from src.core.common.common import EU_languages, EU_languages_en_es, iso_code_2_dict
from src.core.main import Video, TranslationPack, Process_Video, SpeakerSettings, PhraseSettings
from src.core.text_to_speech import VoiceClone_XTTS
from src.core.common import errors
from django.conf import settings
from django.utils.translation import gettext as _

def s2t_and_tts_lang_i18n(processor: Process_Video=None, i18n:str='en'):
    def _get_lang_tuple_list(languages_list):
        ret = []
        for l in languages_list:
            if i18n == 'en':
                ret.append((l, l))
            elif i18n =='es':
                ret.append((l, EU_languages_en_es[l]))
        return ret

    if processor == None:
        processor = Process_Video()
    source = processor.get_s2t_languages()
    ret_s = _get_lang_tuple_list(source)

    tts = processor.get_tts_languages()
    ret_tts = _get_lang_tuple_list(tts)

    clone = processor.get_cloning_languages()
    ret_clone = _get_lang_tuple_list(clone)

    # sorted_list = sorted(list_of_tuples, key=lambda x: x[1])
    ret_s.sort(key=lambda x: x[1])
    ret_tts.sort(key=lambda x: x[1])
    ret_clone.sort(key=lambda x: x[1])
    return ret_s, ret_tts, ret_clone

def translation_to_dict(translations: list, i18n:str='en'):
    trans_dict_list = []
    for tr in translations:
        tr: TranslationInfo_User
        sl = tr.translation_info.source_language_sel
        tl = tr.translation_info.translated_language_sel
        if i18n == 'en':
            tsl = (sl, sl)
            ttl = (tl, tl)
        elif i18n =='es':
            tsl = (sl, EU_languages_en_es.get(sl, None))
            ttl = (tl, EU_languages_en_es.get(tl, None))
        trans_dict_list.append({
            'pk': tr.pk,
            'transl_name' : tr.transl_name,
            'source_language_sel' : tsl,
            'translated_language_sel' : ttl,
            'date_modified' : tr.date_modified,
        })
    return trans_dict_list

def voices_list_by_lang(processor: Process_Video, user: UserBase, lang_tuple_list: list):
    """ lang_tuple_list = [( lang1, _(lang1) ), ... , ( _lang_n, _(lang_n) )]"""

    if processor == None:
        processor = Process_Video()
        
    voices_dict = {}

    voices_user = Saved_voices_user.objects.filter(user=user, to_show=True)
    custom_voices = []
    if voices_user:
        # print('ies',voices_user)
        custom_voices = [item.voice_name for item in voices_user]
        # for item in voices_user:
        #     custom_voices.append(item.voice_name)
    clone_languages = processor.get_cloning_languages()
    # print('nop',voices_user)
    for l, il in lang_tuple_list:      
        try:
            dest_lang_code = processor.tts_model.supported_languages(None, as_dict=True)[l]
            voices_f = processor.tts_model.preset_voices(None,language=dest_lang_code, gender='female', as_dict=False)
            voices_m = processor.tts_model.preset_voices(None,language=dest_lang_code, gender='male', as_dict=False)
        except Exception as er:
            print(er)
            if l in clone_languages:
                voices_dict [l] = {'voices_f': [], 'voices_m': [], 'voices_clone': custom_voices}
            else: 
                voices_dict [l] = {'voices_f': [], 'voices_m': [], 'voices_clone': []}
            continue
        
        if l in clone_languages:
            voices_dict [l] = {'voices_f': voices_f, 'voices_m': voices_m, 'voices_clone': custom_voices}
        else: 
            voices_dict [l] = {'voices_f': voices_f, 'voices_m': voices_m, 'voices_clone': []}
    return voices_dict

def voices_list_from_lang(processor: Process_Video, user: UserBase):

    voices_user = Saved_voices_user.objects.filter(user=user, to_show=True)
    custom_voices = []
    if voices_user:
        custom_voices = [item.voice_name for item in voices_user]
    clone_languages = processor.get_cloning_languages()

    try:
        dest_lang_code = processor.tts_model.supported_languages(None, as_dict=True)[processor.dest_language]
        voices_f = processor.tts_model.preset_voices(None, language=dest_lang_code, gender='female', as_dict=False)
        voices_m = processor.tts_model.preset_voices(None, language=dest_lang_code, gender='male', as_dict=False)
    except Exception as er:
        print(er)
        return [], [], custom_voices
    
    if processor.dest_language in clone_languages:
        return voices_f, voices_m, custom_voices
    else: 
        return voices_f, voices_m, []
    
def out_random_voice_sett(processor: Process_Video, user: UserBase):
    voices_f, voices_m, custom_voices = voices_list_from_lang(processor, user)

    processor.speakers_settings = []
    speakers = set()
    for id in processor.translated_phrases:
        spk = processor.translated_phrases[id].speaker
        speakers.add(spk)
    speakers = sorted(list(speakers))

    if len(custom_voices) > 0:
        for id in speakers:
            voice = random.choice(custom_voices)
            audio_sample = __get_cloned_voice_sample(user, voice)
            processor.speakers_settings.append(VoiceClone_XTTS(id, voice, audio_sample))
    else:
        for id in speakers:
            if len(voices_f) > 0 and len(voices_m) > 0:
                voice_f = random.choice(voices_f)
                voice_m = random.choice(voices_m)
                x = random.randint(0,100)
                if x % 2 == 0:
                    processor.speakers_settings.append(SpeakerSettings(id, 'female', voice_f))
                else:
                    processor.speakers_settings.append(SpeakerSettings(id, 'male', voice_m))
            elif len(voices_f) > 0 :
                voice_f = random.choice(voices_f)
                processor.speakers_settings.append(SpeakerSettings(id, 'female', voice_f))
            elif len(voices_m) > 0:
                voice_m = random.choice(voices_m)
                processor.speakers_settings.append(SpeakerSettings(id, 'male', voice_m))
        
    print('radom speakers_settings generated',processor.speakers_settings)
    assert(len(processor.speakers_settings) == len(speakers))

def set_new_phr_times(processor: Process_Video, new_times: list):
    for id in processor.translated_phrases:
        start_time_ms = new_times[id][0] # (s_hours, s_min, s_sec)
        end_time_ms = new_times[id][1]   # (e_hours, e_min, e_sec)
        start_time_ms = start_time_ms[0]*3600 + start_time_ms[1]*60 + start_time_ms[2]  # sec
        end_time_ms = end_time_ms[0]*3600 + end_time_ms[1]*60 + end_time_ms[2]          # sec
        start_time_ms = start_time_ms * 1000
        end_time_ms = end_time_ms * 1000
        processor.translated_phrases[id].start = start_time_ms
        processor.translated_phrases[id].end = end_time_ms

def set_new_volumes(processor: Process_Video, new_vols: list):
    for i, sett in enumerate(processor.phrases_settings):
        sett.volume = new_vols[i]

def set_new_speeds(processor: Process_Video, new_spds: list):
    for i, sett in enumerate(processor.phrases_settings):
        sett.speed = new_spds[i]

file_session_path = os.path.join(BASE_DIR, "static", "user_transl_session.bin")

def file_session_for_transl(user:UserBase, transl_user:TranslationInfo_User):
    ret = dict()
    try:
        with open(file_session_path, 'rb') as session_file:
            session = pickle.load(session_file)
            ret = session[(user.pk, transl_user.pk)]
    except:
        ret = dict()
    return ret

def get_file_session(user:UserBase, transl_user:TranslationInfo_User, info_to_get:str, default=None):
    ret = default
    try:
        with open(file_session_path, 'rb') as session_file:
            session = pickle.load(session_file)
            ret = session[(user.pk, transl_user.pk)][info_to_get]
    except:
        ret = default
    return ret

def save_to_file_session(user:UserBase, transl_user:TranslationInfo_User, info_to_save:dict):
    dictionary = {}
    with open(file_session_path, 'rb') as session_file:
        try:
            session = pickle.load(session_file)
            dictionary = session
        except: pass

    dict_for_user:dict = dictionary.get((user.pk, transl_user.pk), dict())
    dict_for_user.update(info_to_save)
    dictionary[(user.pk, transl_user.pk)] = dict_for_user

    with open(file_session_path, 'wb') as session_file:
        pickle.dump(dictionary, session_file)

def del_in_file_session(user:UserBase, transl_user:TranslationInfo_User, info_to_del:str):
    dictionary = {}
    with open(file_session_path, 'rb') as session_file:
        try:
            session = pickle.load(session_file)
            dictionary = session
        except: pass
    ret = dictionary[(user.pk, transl_user.pk)].pop(info_to_del,None)

    with open(file_session_path, 'wb') as session_file:
        pickle.dump(dictionary, session_file)
    return ret

COLORS = [ '#0000FF', # Blue
           '#D2691E', # Chocolate
           '#DC143C', # Crimson
           '#483D8B', # DarkSlateBlue
           '#228B22', # ForestGreen
           '#9370DB', # MediumPurple
           '#800000', # Maroon
           '#4B0082', # Indigo
           '#32CD32', # LimeGreen
           '#C71585', # MediumVioletRed
           '#000080', # Navy
           '#DEB887', # BurlyWood
           '#B0E0E6', # PowderBlue
           '#7FFFD4', # Aquamarine
           '#FFB6C1', # LightPink
           ]

def __get_cloned_voice_sample(user: UserBase, voice_name: str):
    voices_user = Saved_voices_user.objects.filter(user=user, voice_name=voice_name, to_show=True)
    if voices_user:
        # print('ies',voices_user)

        for item in voices_user:
            custom_voice = item.voice_sample

    return custom_voice

# def del_voice(user, voice_sett):
#     print('del_voice')
#     for vs in voice_sett:
#         print(__get_cloned_voice_sample(user,vs.name))
#     return False


def speakers_list(processor: Process_Video, user:UserBase):
    phrases = processor.translated_phrases
    voice_sett = processor.speakers_settings
    if voice_sett == None or len(voice_sett) == 0:
        out_random_voice_sett(processor, user)
        voice_sett = processor.speakers_settings
    # print('voice_sett', voice_sett)
    result = []
    gotten = []
    for id in phrases:
        spk = phrases[id].speaker + 1
        if spk in gotten:
            continue
        if voice_sett != None:
            result.append((spk, f"spk{spk}_volumeNumber",f"spk{spk}_volumeBar", f"spk{spk}_speedNumber",f"spk{spk}_speedBar",
                           voice_sett[spk-1].voice_gender, voice_sett[spk-1].name))
        else:
            result.append((spk, f"spk{spk}_volumeNumber",f"spk{spk}_volumeBar", f"spk{spk}_speedNumber",f"spk{spk}_speedBar",
                           None, None))

        gotten.append(spk)
    # print("speakers",result)
    return result

def phr_dict_to_list(processor: Process_Video, phrases: dict, transl=False, video=False): # TODO deprecated
    
    result = []
    for id in phrases:
        color = COLORS[phrases[id].speaker % len(COLORS)]
        if transl and video:
            result.append((id+1, phrases[id], color, phrases[id].speaker+1, f"phr_{id+1}_EditTModal",
                           float(round(processor.phrases_settings[id].speed, 1)), processor.phrases_settings[id].volume,
                           f"phr_{id+1}_Modal", f"phr{id+1}_volumeNumber",f"spk{id+1}_volumeBar",
                           f"phr{id+1}_speedNumber",f"spk{id+1}_speedBar"))
        elif transl:
            result.append((id+1, phrases[id], color, phrases[id].speaker+1, f"phr_{id+1}_EditTModal",None,None,None,None,None,None,None))
        else:
            result.append((id+1, phrases[id], color, phrases[id].speaker+1, f"phr_{id+1}_EditModal"))
    return result

def phr_2_dict_to_list(processor: Process_Video):
    source_phrases = processor.source_phrases
    transl_phrases = processor.translated_phrases
    video = processor.translated_video != None
    result = []
    if source_phrases != None and transl_phrases != None and (len(source_phrases.items()) == len(transl_phrases.items())):
        for id in source_phrases:
            color = COLORS[source_phrases[id].speaker % len(COLORS)]
            phr_dict = {}
            phr_dict['max_time_ms'] = 0 # TODO
            phr_dict['id'] = id+1
            phr_dict['color'] = color
            phr_dict['speaker'] = source_phrases[id].speaker+1
            
            phr_dict['source_text'] = source_phrases[id].text
            phr_dict['source_start'] = source_phrases[id].start # TODO change to hour:min:sec
            phr_dict['source_end'] = source_phrases[id].end
            phr_dict['source_editModal'] = f"phr_{id+1}_EditModal"
            
            phr_dict['transl_text'] = transl_phrases[id].text
            phr_dict['transl_start'] = transl_phrases[id].start # TODO change to hour:min:sec
            phr_dict['transl_end'] = transl_phrases[id].end
            phr_dict['transl_editModal'] = f"phr_{id+1}_EditTModal"
            if video:
                phr_dict['speed'] = float(round(processor.phrases_settings[id].speed, 1))
                phr_dict['volume'] = processor.phrases_settings[id].volume
                phr_dict['phrModal'] = f"phr_{id+1}_Modal"
                phr_dict['phr_vol_name'] = f"phr{id+1}_volumeNumber"
                phr_dict['phr_vol_name2'] = f"phr{id+1}_volumeBar"
                phr_dict['phr_spd_name'] = f"phr{id+1}_speedNumber"
                phr_dict['phr_spd_name2'] = f"phr{id+1}_speedBar"
            
            result.append(phr_dict)
    elif source_phrases != None:     
        for id in source_phrases:
            color = COLORS[source_phrases[id].speaker % len(COLORS)]
            phr_dict = {}
            phr_dict['max_time_ms'] = 0 # TODO
            phr_dict['id'] = id+1
            phr_dict['color'] = color
            phr_dict['speaker'] = source_phrases[id].speaker+1
            
            phr_dict['source_text'] = source_phrases[id].text
            phr_dict['source_start'] = source_phrases[id].start # TODO change to hour:min:sec
            phr_dict['source_end'] = source_phrases[id].end
            phr_dict['source_editModal'] = f"phr_{id+1}_EditModal"  

            phr_dict['transl_text'] = False    
            result.append(phr_dict)

    return result
    
