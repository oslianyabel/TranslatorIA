from src.core.common import Video, Audio, Phrase, errors
from src.core.speech_to_text import S2T_Whisper
from src.core.text_to_speech import VoiceClone_XTTS
import os
import re
from pathlib import Path
import operator
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pyannote.audio import Pipeline
import torch
# from pyAudioAnalysis import audioTrainTest as aT
# from pyAudioAnalysis import audioSegmentation as aS
# import numpy as np
import whisper
# import json


MAX_LENGHT_PHRASE = 30 * 1000 # 30 seconds
SIMIL_THR = 1000
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Phrases_separator:
    """ Funtions to separate/split an audio by phrases or silences. """
    def split_pydub_whisper(audio: Audio):
        sound = AudioSegment.from_wav(audio.get_filename())   

        ###### pydub split_on_silence ######    
        audio_chunks = split_on_silence(sound, min_silence_len=700, silence_thresh=-40, keep_silence=True)
            
        silence_segments = []
        s = 0
        for chunk in audio_chunks:
            silence_segments.append((s, s + len(chunk)))
            s = s + len(chunk) 

        ###### whisper tiny segments ######
        transcript = S2T_Whisper('tiny')

        lang_code = transcript.supported_languages(as_dict=True).get(audio.get_language(),None)
        if lang_code == None:
            raise errors.InvalidInputError(f"Invalid language: {audio.get_language()}")
                    
        whisper_tiny = transcript.get_text(audio, lang_code, True)
        whisper_tiny = whisper_tiny['segments']
        
        wh_t_segments = Phrases_separator.whisper_seg_to_mili(whisper_tiny)

        # search milestones for S2T
        # print("silence_segments",silence_segments)
        # print("wh_t_segments",wh_t_segments)
        milestones = []
        sil_beg = 0
        for s, e in wh_t_segments:
            for i in range(sil_beg, len(silence_segments)):
                if abs(e - silence_segments[i][1]) <= SIMIL_THR:
                    milestones.append([silence_segments[sil_beg][0], silence_segments[i][1]])
                    sil_beg = i + 1
                    break
        if len(milestones) == 0:
            sil_beg = 0
            for s, e in wh_t_segments:
                for i in range(sil_beg, len(silence_segments)-1):
                    if e > silence_segments[i][1] and e < silence_segments[i+1][1]:
                        milestones.append([silence_segments[sil_beg][0], silence_segments[i][1]])
                        sil_beg = i+1
                        break
        # print("milestones 1 ",milestones)
        i = 0
        while i < len(milestones):
            seg = milestones[i]

            if seg[1] - seg[0] < MAX_LENGHT_PHRASE/2 and i < len(milestones)-1:
                # join with the next if the next is also small
                if milestones[i+1][1] - milestones[i+1][0] < MAX_LENGHT_PHRASE/2:
                    # print(seg[1] - seg[0], "join with the next if the next is also small",milestones[i+1][1] - milestones[i+1][0])
                    milestones[i] = [seg[0], milestones[i+1][1]]
                    milestones.remove(milestones[i+1])
                else: i+=1
            else: i+=1

        # print("milestones 2 ",milestones)
        return milestones 


    def split_by_silences(audio: Audio, save_audio_directory=None): # pydub version 1
        """ """
        sound = AudioSegment.from_wav(audio.get_filename())
        
        audio_chunks = split_on_silence(sound, min_silence_len=700, silence_thresh=-40, keep_silence=True)
        
        chunks = []
        audio_name = os.path.splitext(os.path.basename(audio.get_filename()))[0]
        if save_audio_directory == None:
            save_audio_directory = os.path.join(BASE_DIR,"src","app","static","audio")
            print(save_audio_directory)

        for i, chunk in enumerate(audio_chunks):
            output_file = os.path.join(save_audio_directory, audio_name+f"_chunk_{i}.wav")
            print("Exporting file", output_file)
            chunk.export(output_file, format="wav")
            chunks.append(Audio(output_file))
        audio.set_split(splits=chunks)
        return audio

    def whisper_split_by_silences(audio: Audio, source_language:str, whisper_model='tiny'):
        """ """
        model: whisper.Whisper = whisper.load_model(whisper_model)
        transcription = model.transcribe(
                        audio=audio.get_filename(),
                        language=source_language,
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
        # with open(f"docs/whisper_{audio_name}.json", "w+") as file:
        #     json.dump(transcription, file)
        segments = transcription["segments"]
        
        segments_size = Phrases_separator.whisper_seg_to_dict(segments)

        # chunks = []
        # audio_name = os.path.splitext(os.path.basename(audio.get_filename()))[0]
        # if save_audio_directory == None:
        #     save_audio_directory = os.path.dirname(audio.get_filename())
        #     print(save_audio_directory)

        # for i, t in enumerate(segments_size):
        #     output_file = os.path.join(save_audio_directory, audio_name+f"_chunk_{i}.wav")
        #     print("Exporting file", output_file)
        #     split = sound[t[0] : t[1]]
        #     split.export(output_file, format="wav")
        #     chunks.append(Audio(output_file))
        # audio.set_split(splits=chunks)
        return segments_size

    def whisper_seg_to_mili(segments: list):
        n_segments = len(segments)

        # get the start and the of each whisper segment
        segment_size = []
        for i in range(n_segments):
            # if i < n_segments-1:
            #     segment_size.append((segments[i]["start"], segments[i+1]["start"]))
            # else: 
            #     segment_size.append((segments[i]["start"], segments[i]["end"]))
            # TODO check if whisper removes silences or the sort
            segment_size.append((segments[i]["start"],segments[i]["end"]))
        
        # set the time in miliseconds
        for i in range(len(segment_size)):
            segment_size[i] = (segment_size[i][0]*1000,segment_size[i][1]*1000)
        
        return segment_size

class Speaker_diarization:
    """ Funtions to separate/split an audio by speaker. It answers who spoke when. """

    def pyannote_diarization(audio: Audio, use_GPU):
        """

        """
        def __millisec(timeStr):
            spl = timeStr.split(":")
            s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
            return s
        
        DEMO_FILE = {'uri': 'blabal', 'audio': audio.get_filename()}

        if use_GPU:
            pipeline = Pipeline.from_pretrained( "pyannote/speaker-diarization-3.1",use_auth_token="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")
            # torch.cuda.empty_cache()            
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            print("Use GPU requested on pyannote. Current cuda device:", device)
            pipeline.to(torch.device("cuda")) # switch to gpu
            dz = pipeline(DEMO_FILE)
        else:
            pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization',use_auth_token="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")
            dz = pipeline(DEMO_FILE)  
        dz = pipeline(DEMO_FILE)  
        dz = str(dz).splitlines()
        dzList = []

        for l in dz:
            start, end =  tuple(re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=l))
            start = __millisec(start) 
            end = __millisec(end)  
            key = int(l.split("_")[1])
            dzList.append((start, end, key))

        return dzList

def remove_overlaping(segments_list:list) -> list:
    # [(start, end, key), ...]
    # sort tuple list asc by strat, and if equal by end: 
    sorted_segments = sorted(segments_list, key = operator.itemgetter(0, 1))

    # https://stackoverflow.com/a/52866263
    events = []
    for start, stop, symbol in sorted_segments:
        events.append((start, True, stop, symbol))
        events.append((stop, False, start, symbol))

    def event_key(event):
        # to sort by:
            # endpoint
            # if equal: 
                # key_is_start == True first
                # if equal:
                    # the other limit of the interval
        key_endpoint, key_is_start, key_other, _ = event
        key_order = 0 if key_is_start else 1
        return key_endpoint, key_order, key_other
    
    # [(0, True, 75, 'b'), (75, False, 0, 'b'), (0, True, 100, 'a'), (100, False, 0, 'a'), 
    #  (95, True, 150, 'c'), (150, False, 95, 'c'), (120, True, 130, 'd'), (130, False, 120, 'd')]
    events.sort(key=event_key)
    # [(0, True, 75, 'b'), (0, True, 100, 'a'), (75, False, 0, 'b'), (95, True, 150, 'c'), 
    # (100, False, 0, 'a'), (120, True, 130, 'd'), (130, False, 120, 'd'), (150, False, 95, 'c')]
    current_set = set()
    ranges = []
    current_start = -1

    for endpoint, is_start, other, symbol in events:
        # print(endpoint, is_start, other, symbol, ' --- > ')
        if is_start:
            if current_start != -1 and endpoint != current_start and \
                    endpoint > current_start and current_set:
                ranges.append((current_start, endpoint, current_set.copy()))
                
            current_start = endpoint
            current_set.add(symbol)
        else:
            if current_start != -1 and endpoint > current_start and current_set:
                ranges.append((current_start, endpoint, current_set.copy()))
                
            current_set.remove(symbol)
            current_start = endpoint

    return ranges

def join_intervals(non_overlap_segments: list):
    """ 
    From non overlap ordered segments like: [ (start1, end1, speakers_set1), (start2, end2, speakers_set2), ... ] 

    Get a list that for every consecutive segments where the speaker is the same, join the intervals
    """
    r_list = []
    t_speaker:set = set()
    t_start = None
    t_end = None
    for i in range (len(non_overlap_segments)):
        if len(t_speaker)==0:
            t_start = non_overlap_segments[i][0]
            t_end = non_overlap_segments[i][1]
            t_speaker = non_overlap_segments[i][2]
        else:
            if len(t_speaker) == len(t_speaker.intersection(non_overlap_segments[i][2])):
                t_end = non_overlap_segments [i][1]
            elif len(t_speaker.intersection(non_overlap_segments[i][2])) >= 1:
                t_speaker = t_speaker.intersection(non_overlap_segments[i][2])
                t_end = non_overlap_segments[i][1]
            elif len(t_speaker.intersection(non_overlap_segments[i][2])) == 0:
                r_list.append((t_start,t_end,t_speaker.pop()))
                
                t_start = non_overlap_segments[i][0]
                t_end = non_overlap_segments[i][1]
                t_speaker = non_overlap_segments[i][2]
    r_list.append((t_start,t_end,t_speaker.pop()))
    return r_list

def audio_split_and_S2T(audio: Audio, use_GPU: bool, whisper_model: str="medium"):
    phrases_dict = dict()
    n_phrases = 0
    audiosplit = list()

    full_audio = AudioSegment.from_wav(audio.get_filename())
    audio_name = os.path.splitext(os.path.basename(audio.get_filename()))[0]
    save_audio_directory = os.path.join(BASE_DIR,"src","app","static","audio")

    ##################### LAYER 1 split on speakers #####################
    segments_list = Speaker_diarization.pyannote_diarization(audio, use_GPU=use_GPU)
    # segments_list = [(401, 8575, 0), (9343, 17892, 0), (18063, 56322, 1), (23131, 26134, 0), (57465, 60366, 1), (61151, 74633, 1), (75418, 88131, 1)]
    print("pyannote diarization result : ", segments_list)
    non_overlap_segments_list = remove_overlaping(segments_list)
    print("segments split with overlapping removed", non_overlap_segments_list)
    speakers_segments = join_intervals(non_overlap_segments_list)

    ############## LAYER 2 split on phrases including S2T ###############
    print("transcript with whisper model: ",whisper_model)
    transcript = S2T_Whisper(model_selected=whisper_model, use_GPU=use_GPU)
    lang_code = transcript.supported_languages(as_dict=True).get(audio.get_language(),None)
    if lang_code == None:
        raise errors.InvalidInputError(f"Invalid language: {audio.get_language()}")
        

    for i, segm in enumerate(speakers_segments):
        # extract as a full audio, remove later
        spk_seg_file = os.path.join(save_audio_directory, f"segment_{i}_{audio_name}.wav")
        spk_segment_audio:AudioSegment = full_audio[segm[0] : segm[1]]
        spk_segment_audio.export(spk_seg_file, format="wav")
        spk_seg_audio = Audio(spk_seg_file, audio.get_language())

        segment_milestones = Phrases_separator.split_pydub_whisper(spk_seg_audio)
        segment_splits = [] #[(start, end, id), ...] for each phrase

        for m in segment_milestones:
            m_start = m[0]
            m_end = m[1]
            # HERE perform S2T
            
            m_file = os.path.join(save_audio_directory, f"milest_{m_start}-{m_end}_{audio_name}.wav")
            m_chunk:AudioSegment = spk_segment_audio[m_start : m_end]
            m_chunk.export(m_file, format="wav")
            
            s2t_result = transcript.get_text(Audio(m_file, audio.get_language()), lang_code, True)
            # print("whisper result for phrase",n_phrases,"->",s2t_result)
            # print("segment size = ", m_end - m_start)
            if m_end - m_start <= MAX_LENGHT_PHRASE:
                # print("Good size! ")
                phrases_dict[n_phrases] = Phrase(index=n_phrases, start=segm[0]+m_start, end=segm[0]+m_end, speaker=segm[2], text=s2t_result['text'])
                segment_splits.append((segm[0]+m_start, segm[0]+m_end, n_phrases))
                # print("----------",phrases_dict[n_phrases])
                n_phrases += 1
            # if milestone is too big, re-reduce into smaller segments
            else:
                # print("Trying to reduce: ")
                S2T_segments = s2t_result['segments'] 
                wh_d_segments = Phrases_separator.whisper_seg_to_mili(S2T_segments)

                for i in range(len(S2T_segments)):
                    s, e = wh_d_segments[i]

                    phrases_dict[n_phrases] = Phrase(index=n_phrases, start=segm[0]+m_start+s, end=segm[0]+m_start+e, speaker=segm[2], text=S2T_segments[i]['text'])
                    segment_splits.append((segm[0]+m_start+s, segm[0]+m_start+e, n_phrases))
                    # print("----------",phrases_dict[n_phrases])
                    n_phrases += 1


            #remove chunk
            os.remove(m_file)

        #remove speaker segment 
        os.remove(spk_seg_file)
        audiosplit.append([segm[2],segment_splits])

    audio.set_split(audiosplit)
    return audio, phrases_dict

def automatic_voices_extraction(phrases_dict: dict, audio: Audio, voice_name_prefix: str, n_audios_for_clone: int=2):
    def get_sections_by_spk(phrases: dict):
        result = dict() # {'spk_id': [(phr_id1, duration1), (phr_id2, duration2), ... ]}
        for phr_id, phr in list(phrases_dict.items()):
            # phr:Phrase = phrases_dict[phr_id]
            dur = phr.end - phr.start
            if not (result.get(phr.speaker,False)):
                result[phr.speaker] = [(phr_id, dur)]
            else:
                result[phr.speaker].append((phr_id, dur))
        print("Phrases by speakers: ", result)
        return result
    
    def select_n_samples_by_spk(sections_by_spk:dict, n: int, min_dur: int):
        result = dict() # {'spk_id1': [phr1, ..., phrn], 'spk_id2': [phr1, [phr2, phr3], ..., phrn]}
        for spk, phrases_list in list(sections_by_spk.items()):
            sorted_list = sorted(phrases_list, key=lambda x: x[1], reverse=True)
            print("sorted phrases list for speaker ",spk,":",sorted_list,"\n number of samples: ",n)
            # Case 1: the first n phrases are >= min_dur ===>>> remove the n+1 and onwards
            if len(sorted_list) >= n and sorted_list[n-1][1] >= min_dur:
                result[spk] = [phr for phr, dur in sorted_list[:n]]
                continue
            # Case 2: more than n phrases, but not longer than min_dur ===>>> concat until all of them are longer than min_dur or until you run out of phrases
            if len(sorted_list) > n and sorted_list[n-1][1] < min_dur:
                good_phrases = []
                i = 0
                while len(good_phrases) < n and len(sorted_list) < i:
                    phr, dur = sorted_list[i]
                    if dur >= min_dur:
                        # still on the first good ones
                        good_phrases.append(phr)
                        i+=1
                    else:
                        concat = [phr]
                        acc = dur
                        i+=1
                        while acc < min_dur and len(sorted_list) < i:
                            phr, dur = sorted_list[i]
                            concat.append(phr)
                            acc += dur
                            i+=1
                        if acc >= min_dur or len(good_phrases) == 0:
                            good_phrases.append(concat)
                result[spk] = good_phrases
                continue
            # Case 3: less than n phrases, but all the elements are >= min_dur
            if len(sorted_list) <= n and sorted_list[-1][1] >= min_dur:
                result[spk] = [phr for phr, dur in sorted_list] 
                continue
            # Case 4: less than n phrases, but not all the elements are >= min_dur
            if len(sorted_list) < n:
                good_phrases = []
                i = 0
                while len(sorted_list) < i:
                    phr, dur = sorted_list[i]
                    if dur >= min_dur:
                        # still on the first good ones
                        good_phrases.append(phr)
                        i+=1
                    else:
                        concat = [phr]
                        acc = dur
                        i+=1
                        while acc < min_dur and len(sorted_list) < i:
                            phr, dur = sorted_list[i]
                            concat.append(phr)
                            acc += dur
                            i+=1
                        if acc >= min_dur or len(good_phrases) == 0:
                            good_phrases.append(concat)
                        good_phrases.append(concat)
                result[spk] = good_phrases
                continue
             
            raise Exception("Shouldn't get here")
        return result

    sections_by_spk = get_sections_by_spk(phrases_dict)
    samples_id_by_spk = select_n_samples_by_spk(sections_by_spk, n_audios_for_clone, 3000)
    full_audio = AudioSegment.from_wav(audio.get_filename())
    audio_name = os.path.splitext(os.path.basename(audio.get_filename()))[0]
    save_audio_directory = os.path.join(BASE_DIR,"src","app","static","audio")
    voices_by_spks = dict() # dict of SpeakerSettings, in each speaker_id is the settings for it's voice
    
    for spk in samples_id_by_spk:
        samples_ids = samples_id_by_spk[spk]
        sample_audios = []
        for i in range(len(samples_ids)):
            if isinstance(samples_ids[i], list):
                phr_ids = samples_ids[i]
            else:
                phr_ids = [samples_ids[i]]
            temp = AudioSegment.silent(duration=1)
            for j, id in enumerate(phr_ids):
                phr = phrases_dict[id]
                assert(phr.speaker==spk)
                spk_segment_audio:AudioSegment = full_audio[phr.start : phr.end]
                if j == len(phr_ids)-1:
                    temp = temp + spk_segment_audio
                else:
                    temp = temp + spk_segment_audio + AudioSegment.silent(duration=200)
            # if len(temp) > 15 * 1000: # TODO
            #     temp = temp[:15000]
            sample_audios.append(temp)
            # TODO remove
            # file = os.path.join(save_audio_directory, f"{audio_name}_speaker-{spk}-{i}_voice sample.wav")
            # temp.export(file, format="wav")
            print(f"Phrases {phr_ids} used for clone voice for speaker {spk}, and it lasts {len(temp)}")
            
        spk_sett = VoiceClone_XTTS( spk_id=spk, 
                                    voice_name=f"{voice_name_prefix}-{spk}",
                                    sample_audio=sample_audios)
        voices_by_spks[spk] = spk_sett

    # TODO clear background noise, or detect amount of background noise
    
    # voices_by_spks = dict() # dict of SpeakerSettings, in each speaker_id is the settings for it's voice
    # short_phrases = dict() 
    # spks_ids = []
    # full_audio = AudioSegment.from_wav(audio.get_filename())
    # audio_name = os.path.splitext(os.path.basename(audio.get_filename()))[0]
    # save_audio_directory = os.path.join(BASE_DIR,"src","app","static","audio")
            

    # for phr_id in phrases_dict:
    #     phr:Phrase = phrases_dict[phr_id]
    #     dur = phr.end - phr.start
    #     # print(dur)
    #     spks_ids.append(phr.speaker)
    #     if not (voices_by_spks.get(phr.speaker,False)):
    #         # this user has not been processed
    #         if dur < 3000:
    #             # If the audio length is less than 3 seconds add to 'short_phrases'
    #             if (short_phrases.get(phr.speaker,False)):
    #                 short_phrases[phr.speaker].append(phr)
    #             short_phrases[phr.speaker] = [phr]
    #             continue

    #         spk_segment_audio:AudioSegment = full_audio[phr.start : phr.end]
    #         file = os.path.join(save_audio_directory, f"{audio_name}_speaker-{phr.speaker}_voice sample.wav")
    #         spk_segment_audio.export(file, format="wav")
    #         print(f"Phrase {phr.index} audio segment is for speaker {phr.speaker}, and it lasts {len(spk_segment_audio)}")
    #         if len(spk_segment_audio) > 15 * 1000:
    #             spk_segment_audio = spk_segment_audio[:15000]
    #         spk_sett = VoiceClone_XTTS(spk_id=phr.speaker, 
    #                                    voice_name=f"{voice_name_prefix}-{phr.speaker}",
    #                                    sample_audio=spk_segment_audio)
    #         voices_by_spks[phr.speaker] = spk_sett

    # spks_ids = sorted(list(set(spks_ids)))
    
    # for id in spks_ids:
    #     if not (voices_by_spks.get(id,False)):
    #         # this person does not have any voice longer than 3 seconds
    #         spk_phrases = short_phrases[id]
    #         if len(spk_phrases) == 1:
    #             phr:Phrase = spk_phrases[0]
    #             assert(phr.speaker==id)
    #             spk_segment_audio:AudioSegment = full_audio[phr.start : phr.end]
    #             print(f"Phrase {phr.index} audio segment is for speaker {phr.speaker}, and it lasts {len(spk_segment_audio)}")

    #             spk_sett = VoiceClone_XTTS( spk_id=phr.speaker, 
    #                                         voice_name=f"{voice_name_prefix}-{phr.speaker}",
    #                                         sample_audio=spk_segment_audio)
    #             voices_by_spks[phr.speaker] = spk_sett
    #         else:
    #             i = 0
    #             temp = AudioSegment.silent(duration=1)
    #             while i < len(spk_phrases) and len(temp < 10000):
    #                 phr:Phrase = spk_phrases[i]
    #                 assert(phr.speaker==id)
    #                 spk_segment_audio:AudioSegment = full_audio[phr.start : phr.end]
    #                 print(f"Concat: phrase {phr.index} audio segment is for speaker {phr.speaker}, and it lasts {len(spk_segment_audio)}")
    #                 temp = temp + spk_segment_audio + AudioSegment.silent(duration=100)
                    
    #                 i+=1
    #             spk_sett = VoiceClone_XTTS( spk_id=id, 
    #                                         voice_name=f"{voice_name_prefix}-{id}",
    #                                         sample_audio=temp)
    #             voices_by_spks[id] = spk_sett

    return voices_by_spks