import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
from src.core.common import Audio, Video, preprocess, Phrase, SpeakerSettings
from src.core import speech_to_text as s2t
from src.core import translation
from src.core import text_to_speech as mytts
from src.core import join_audio_video as genvid
from src.core.common import audio_time_stretch as ats_
from src.core import main

def full_test():
    vid_aud_list = preprocess.load_videos_from("../vidub dataset/")

    transcription_list = []
    # audio = Audio('src\core\speech_original.wav')

    # transcript = s2t.S2T_Speech_Recognition()
    transcript = s2t.S2T_Whisper("medium")
    # transcript.get_text(audio,"en-GB")
    source_lang = ['en','en','ja','ja','ja','ja','ja','es','es','es','es','es','es']
    dest_lang = ['es','es','es','en','en','en','es','en','en','en','en','en','en']
    for i, tupl in enumerate(vid_aud_list):
        # print(tupl)
        # print(tupl[1])
        text = transcript.get_text(source_audio=tupl[1], language=source_lang[i], show_all=False)
        transcription_list.append(text)
        print("\n",tupl[1],"\n\t",text)
    # transcription_list = ["Harry Cavill has been replaced in some pretty unfair terms, but despite all this, he did say yes in a positive way. Harry Cavill has "+
    #                       "had a rough-goer's Superman where he's out of the role for five years until returning for a cameo and black Adam. But he was planning on "+
    #                       "coming back for a black Adam and Superman movie, things just didn't work out where the movie lost $80 million dollars to the box office. "+
    #                       "James Gunn came into run DC, where after seeing the failures of the last few movies he decided to reboot the universe and fire Henry Cavill. "+
    #                       "Harry Cavill still wasn't done in Superman where he filmed a small cameo for the flash alongside the most mentally stable actor in the world as "+
    #                       "a Miller. Because of the plan to reboot the DC, the cameo has been cut saying it wouldn't make sense for future movies. One character who is staying in the "+
    #                       "flash in a big role is Sasha Cavill who will be super girl. But one thing DC did do for Henry Cavill was call him up and ask him to was okay to cast super girl."+
    #                       " The Cavill responded to saying absolutely yes, he wanted fans to have a character love even if it wasn't him. It's neat to Sasha about the character "+
    #                       "offered her advice on how to do the role. But while he knows he's not coming back to Superman, he wishes her and other actors to play Superman the best. Henry Cavill isn't Superman anymore but he has the heart of Clark Kent with an uncharged role as a cracker learn something.",
                          
    #                       "Why your channel is not growing fast? Shit. But... Um... Yeah, I'm not uploading as much. I was thinking even if I should make a new channel or something. "+
    #                       "Because people come to my channel and they're like, why does it need you? I'm not having more. But again, it's not that important. It doesn't matter. I don't "+
    #                       "feel like I need to prove myself to anyone at this point.",

    #                       "YouTubeはMUSGIVER2020!やあーーーー!はい!1日、2月、2日、かよび夜ししがらYouTubeはMUSGIVERンでるのって来部配信されますはい、普通はめっちゃ寒審ですね、社長、よろしくお楽しみです来部配信でご覧にならない方もご実は赤い部でご覧になってみてください以上、ヘスヘラミングでしたバイバイ!おい、かん!",
                          
    #                       "正直 Battle vocationシノ Givenどうやばいんな今後俺をフレンマーさんみない今日みんな僕から教しい",

    #                       "うまーこのシュープがハイほぼ30分でほんそそこらの見せよりおいしい本格を取り出しらめアンツアピントリシャーシュ上手に作っちゃいますから中"+
    #                       "ビグライで2を置いて30分どうですか?頃頃です僕の生まみがすぎますか?かばい!2人分の回収を作っていきますアルコールを飛ばすともにこれは正直のカードを"+
    #                       "取ってくんですねこうせい3倍カードのバンイレンの何がね?おーさしに入り替える6フリーですこのようにポリチャーシューを取り出したら感じるのだろ",

    #                       "お腹を一番目食いっすいなあかうま食いっすいな今日もさぁ活動不出電子に入って40秒から50秒細かくてとしてるとな1人じゃかぐていいないんです "+
    #                       "よ皆さんもこれから思い知ろうとなりますよこのタレを覚えてください20秒くらいな必ずこういう水でしょがとなのかよく知るからいただきますどうしようと "+
    #                       "なってもはい気を入りきんぎくんも少し入れいいね",

    #                       "でたすでさけのめるってほんと使い上おめっかよ落ちばにかけてもうまいですよ僕が昔当たれさ超人キレッサーなじょ最人しましたムギンサラだ全部"+
    #                       "マスティンですマイチのサラが性格が変わりのせいが本当にでいい感じに良かったらされてますパレッサーをパレッスヒルトンになりますんでキールトーなす "+
    #                       "ごら本当にうますぎてねムギンドレッシングで食べるムギンサラだ感想でございます",

    #                       "voy a intentar ser lo más... ...sutil posible. Trump... ...Murio. Y el 6 día pasa morir tú! Baza morir! Me han enseñado huevos a plastados destrozados."+
    #                       " Estaban ahí sufriendo uno tras otro miñeña. Baza morir 6 días te quedan de vida. No le tengo miedo pa. Deberías, muchas chadeberías tenerle miedo. "+
    #                       "Deberías tenerle miedo. Pero tranquila, tu papi está aquí y va a intentar ayudarte.",

    #                       "Me estoy llevado también oro pero no sé por qué, se ha desimagido que por que lo llevo a la sangre, no? Spanioles. Vale.",

    #                       " Ya... Cuando se ve tan rico, pero como decía mi abuelo. Ya... No importa cómo cocine, sino cuanto el derrido saguante. "+
    #                       "Adolí, no importa cómo cocine, sino cuanto el derrido saguante. Adolurí. ¿Por qué? Cuando un sorta como cocine, sino cuanto"+
    #                       " el derrido saguante. A lo entendí, eso es el humor de Néstimo. ¿Ahora habrá un momento a comentarios? Yo no voy a tirarse "+
    #                       "como otro refero, te gano porque te respeto. Así nos vemos. Yo... No. Es un minuto. ¿Qué hay ya te pudo? No, ni, ni, ni, ni. "+
    #                       "¡Hee! Suo delicio. Pudo delicio. ¿Qué va a ver? Ay, a dirarte como otro refero. Se gano porque te respeto. Así nos vemos. Yo... No. Es un minuto. ¿Qué hay ya te pudo? No, ni, ni, ni, ni, ni.",

    #                       "Y si se es una de las yosas mas importantes del antiguo Egipto. Y Y Y Y Y Evinito. Es la hija de Jébin Núds, que son la tierra "+
    #                       "y el cielo y es la ríosa de muchísimas cosas. La realeza, la magia, beesielo. Muchas cosas. ¡Em muy buena! Está casada con nos iris,"+
    #                       " SCHEST, el Rey de Egipto. Ella es la rina. ¿Qué pasa? O sí dice LIA con otra. Y el mar millimeter de la otra, que es 7, la encierra "+
    #                       "en un saco fago y letira un río. ¡Chau! Pado, y si es muy preocupada al final, encuentras el saco fago y se lo lleva a casa. Y así por"+
    #                       " arte de magia, solo pues salvándles, se quedan embarazada de oro. Pero se hacen cuenta de nuevo a Osiris. Y le descuartiz. ¡Aaaaaa! "+
    #                       "Y si se encuentras los trozos, los cose y le resucita. Después de muchos jaleos, Vilsa cabasiendo. El faraol eis libre de Jejuntau, una amiga que es Melos Códillo. ¡FIN!",
                          
    #                       "Lo romano, es tanto, pero supongo que no han sido de los griegos. Y los griegos, aquí se lo plagiaron. Porque se hauró que hay que entrar. "+
    #                       "Pues de la divisación minóica, que son los pavos que vivían en la isla de creta por el año 2000 antes de creer. Y todo lo que sabemos de "+
    #                       "ellos es gracias a la arqueología. A la gracia sonar. Que lo que... Siempre está en la amea. De hecho, eso de minóico se lo inventó un "+
    #                       "arqueólogo hace ciráños, porque en contra referencias a la leyenda del abrinto de minos en una de sus ruidos. El ojo a podés esta gente es que "+
    #                       "tenían unos paraciones que se enteraba la olla. Y unas trámicas tovapas pintadas que son las destúen, un clas de plástico aboniendo. Tres tienta "+
    #                       "mil años. De hecho, seguro que te es una este grabado de minos humanos, hay saltando un toro dochado. Pues el fresco este las anices tiene unos 3.500 "+
    #                       "años de antigua. Y está tu bien hecho, ¿eh? Que que es tirado, tiene. Vale, en el hecho lo muy bonito, pero si tan prospero en el jeep, porque se fueron a mi hermoso. "+
    #                       "¡Mos hay dos teorías! Primero, catástrofe es naturales, los reventaron al máximo y que hay movernos. Y la otra es que los griegos, los alos, mis ténicos, "+
    #                       "aparecieron por ahí. Y los derrotaron haciendo ese copy-paste, todo lo que tenía. ¡Ah! ¡No, no, no, no! ¡Y es que otra cosa no! Pero los humanos copyando. ¡Oh! ¡Samos unos crants!",
                          
    #                       "¿Sabes cuántos hijos tenía Loki? No, te lo voy a contar. Loki tuvo varios hijos con sus dos mujeres y uno con un caballo. Poco tu nervioso. Vamos allá. "+
    #                       "Con la giganta angreboda, tuvo tres hijos probablemente los más conocidos. Fengrir, un loco gigante cuyo destino sería devorar a Odin en El Ragnarok. "+
    #                       "Jormung Ander, una serpiente marina que rodeaba el mundo entero, y Jela, la diosa de los muertos. Todos, buena gente. Luego, con la diosa siguin tuvo otros dos hijos, "+
    #                       "Narfi y Bali. Y los pobres no tuvieron mucha suerte en la vida, la verdad. Tras provocar la muerte de Valdur, los dios se perciguieron a Loki hasta que conseguiron capturarle. "+
    #                       "Y entonces, convirtieron a Bali en un lobo que en mata y desperaza a su hermano. Y luego usaron las tripas para tal a Loki a una piedra. Tá muy mal esto. Y por último, "+
    #                       "Loki es la madre del famoso caballo de Odin. Es la hipunidad. Todo esto, tras convertirse en Diego a para seducir a un caballo imporente llamado Esvadil Farin. "+
    #                       "Vale a familia."    ]

    trans = translation.Multimodel_translator("GoogleTranslator")
    # print(trans.aviable_languages())

    for i, txt  in enumerate(transcription_list):
        result = trans.translate_text(input_text=txt,source_lang=source_lang[i],target_lang=dest_lang[i])
        print("original: ",txt,"\n  translation to",dest_lang[i],": ",result,"\n")

def solo_test(video_path,source_lang,dest_lang):
    # preprocess.video_file_to_Video_Audio()
    processor = main.Process_Video()
    processor.set_video(video_path,source_lang)
    processor.voices_from_video = True
    s_phrases = processor.get_speech_to_text(source_lang,'base')
    print(s_phrases)
    t_phrases = processor.get_text_translation(dest_lang)
    print(t_phrases)
    new_video = processor.generate_video_main('default',True)
    print(new_video)

def phrases_parser(str_phrases: list) -> list:
    result = []
    for line in str_phrases:
        line:str
        parts = line.split("  ")
        id = parts[0]
        text = parts[1]
        start = parts[2]
        end = parts[3]
        speakers = parts[4]

        id = int(id.split(" ")[1][:-1])
        start = int(start.split(" ")[1])
        end = int(end.split(" ")[1])
        speakers = speakers.split(" ")[2]
        # print(id,text,start,end,speakers,sep="\n")

        result.append({"id":id, "text":text, "start":start, "end":end, "speakers":speakers})
    return result

def test_audio_generation(language="English"):
    with open('transl_phrases.txt',"r", encoding='utf-8') as phr:
        phrases = phr.read().splitlines()

    phrases = phrases_parser(phrases)

    syntetizer= mytts.TTS_MMS()
    audio_slices_ordered = AudioSegment.silent(duration=phrases[0]['start'])
    for i, phrase in enumerate(phrases):
        phrase:dict
        save_audio_path = os.path.join("src\core\\temp",f"test_en_{phrase['start']}-{phrase['end']}_.wav")
        
        syntetizer.generate_speech(input_text=phrase['text'], language=language, save_audio_path=save_audio_path)
        generated_audio = AudioSegment.from_wav(save_audio_path)
        wanted_duration = phrase['end'] - phrase['start']
        # if abs(len(audio_slice) - wanted_duration) >= 500:
        audio_slice = Audio.adjust_audio_speed(generated_audio, wanted_duration_ms=wanted_duration)
        if abs(len(audio_slice) - wanted_duration) >= 500:
            print("not properly adjusted audio.","\n   Original duration:",len(generated_audio),"\n   Adjusted duration:",
                    len(audio_slice),"\n   Wanted duration: ", wanted_duration)
        
        audio_slices_ordered = audio_slices_ordered + audio_slice

        if i < len(phrases)-1:
            silence_duration = phrases[i+1]['start'] - phrase['end']
            print("add a silence of size ", silence_duration)
            silence = AudioSegment.silent(duration=silence_duration)
            audio_slices_ordered = audio_slices_ordered + silence
        print(f"Ending phrase {phrase['id']}. phrase end time: {phrase['end']} ms. Generated audio current len: {len(audio_slices_ordered)} ms")

    save_audio_path = os.path.join("src\core\\temp",f"test.wav")
    audio_slices_ordered.export(save_audio_path, format="wav")
    print("new audio size = ",len(audio_slices_ordered))
    translated_audio = Audio(save_audio_path, language)
    
    # vid_generator = gen_vid.Video_Audio_joiner(self.source_video,self.translated_audio)
    
    # new_video_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])
    # new_video_path = os.path.join(self.gen_video_path, new_video_name+'.mp4')
    # vid_generator.join(new_video_path)
    # self.translated_video = Video(new_video_path)

    return save_audio_path

MAX_LENGHT_PHRASE = 20 * 1000 # 20 seconds
SIMIL_THR = 1000

def test_aud_split_whisper_only(source_audio:str):
    pass

def test_aud_split_pydub_whisper(source_audio:str,language):

    sound = AudioSegment.from_wav(source_audio)        
    audio_chunks = split_on_silence(sound, min_silence_len=700, silence_thresh=-40, keep_silence=True)
        
    silence_segments = []
    s = 0
    for chunk in audio_chunks:
        silence_segments.append((s,s+len(chunk)))
        s = s+len(chunk)

    # print("silences split, number of segments: ",len(silence_segments))

    # for seg in silence_segments:
    #     print(seg,"size: ",seg[1]-seg[0])

    model = s2t.S2T_Whisper('tiny')
    lang_code = model.supported_languages(as_dict=True).get(language, None)
    if lang_code == None:
        raise Exception(f"Invalid language: {language}")
        
    whisper_tiny = model.get_text(Audio(source_audio,language),lang_code,True)
    whisper_tiny = whisper_tiny['segments']
    # print("tiny segments: ",len(whisper_tiny))

    # get the start and the end of each whisper segment
    wht_segment_size = []
    for i in range(len(whisper_tiny)):
        wht_segment_size.append((whisper_tiny[i]["start"],whisper_tiny[i]["end"]))
    # set the time in miliseconds
    for i in range(len(wht_segment_size)):
        wht_segment_size[i] = (wht_segment_size[i][0]*1000,wht_segment_size[i][1]*1000)
        
    # print(wht_segment_size)

    milestones = []
    sil_beg = 0
    for s, e in wht_segment_size:
        for i in range(sil_beg, len(silence_segments)):
            if abs(e - silence_segments[i][1]) <= SIMIL_THR:
                milestones.append([silence_segments[sil_beg][0], silence_segments[i][1]])
                sil_beg = i+1
                break

    # print("milestones: ",len(milestones))
    # if len(milestones) > 0:
    #     print(milestones)

    if len(milestones) == 0:
        sil_beg = 0
        for s, e in wht_segment_size:
            for i in range(sil_beg, len(silence_segments)-1):
                if e > silence_segments[i][1] and e < silence_segments[i+1][1]:
                    milestones.append([silence_segments[sil_beg][0], silence_segments[i][1]])
                    sil_beg = i+1
                    break

    # print("milestones 2: ",len(milestones))
    # if len(milestones) > 0:
    #     print(milestones)                

    result_phrases = []
    result_splits = []

    save_audio_directory = "src/core/temp/"
    model = s2t.S2T_Whisper("medium")
    for m_list in milestones:
        output_file = os.path.join(save_audio_directory, f"test_chunk_{m_list[0]}-{m_list[1]}.wav")
        chunk:AudioSegment = sound[m_list[0]:m_list[1]]
        chunk.export(output_file, format="wav")

        text_decent = model.get_text(Audio(output_file,language),lang_code,True)

        if m_list[1] - m_list[0] <= MAX_LENGHT_PHRASE:
            # print("Good size! ")
            result_phrases.append(Phrase(len(result_phrases), m_list[0], m_list[1], None, text_decent['text']))
            result_splits.append((m_list[0],m_list[1]))
            # print("----------",result_phrases[len(result_phrases)-1])

        else:
            # print("Trying to reduce: ")
            #try to re_reduce
            decent_segments = text_decent['segments'] 
            whd_segment_size = []
            for i in range(len(decent_segments)):
                whd_segment_size.append((decent_segments[i]["start"],decent_segments[i]["end"]))
            # set the time in miliseconds
            for i in range(len(whd_segment_size)):
                whd_segment_size[i] = (whd_segment_size[i][0]*1000,whd_segment_size[i][1]*1000)
        
            for i in range(len(decent_segments)):
                s, e = whd_segment_size[i]
                result_phrases.append(Phrase(len(result_phrases), m_list[0]+s, m_list[0]+e, None, decent_segments[i]['text']))
                result_splits.append((m_list[0]+s, m_list[0]+e))
                # print("----------",result_phrases[len(result_phrases)-1])


        #remove chunk
        os.remove(output_file)
    
    split_audio = Audio(source_audio,language)
    split_audio.set_split(result_splits)

    return split_audio, result_phrases

def test_trans_aud_gen(audio:Audio,phrases_list,source_language,target_language,tts_model):
    
    translator = translation.Multimodel_translator("GoogleTranslator")
    dest_lang_code = translator.aviable_languages().get(target_language,None)
    if dest_lang_code == None:
        raise Exception(f"Invalid language: {target_language}")
    source_lang_code = translator.aviable_languages().get(source_language,None)
    if source_lang_code == None:
        raise Exception(f"Invalid language: {source_language}")
    
    translated_phrases = []
    
    for phrase in phrases_list:
        phrase:Phrase
        transl = translator.translate_text(input_text = phrase.get_text(), target_lang=dest_lang_code, source_lang=source_lang_code)
        translated_phrases.append(Phrase(phrase.index,phrase.start,phrase.end,phrase.speaker,transl))
    
    ############# audio generation #############
    models = {"MMS":mytts.TTS_MMS, "google":mytts.TTS_google}
    syntetizer:mytts.TTS_Base = models.get(tts_model,None)()
    if syntetizer == None:
        raise Exception(f"Invalid model: {tts_model}. Use one of the following: {list(models.keys())}")
    
    audio_slices = []
    current_audio_size = 0
    for i, phrase in enumerate(translated_phrases):
        phrase:Phrase
        save_audio_path = os.path.join("src/core/temp",f"test_es-en_{phrase.get_start_time()}-{phrase.get_end_time()}.wav")
        if tts_model == "google":
            target_language = "en"
        syntetizer.generate_speech(input_text=phrase.get_text(), language=target_language, save_audio_path=save_audio_path)
        
        audio_slice = AudioSegment.from_wav(save_audio_path)
        # audio_slice.export(save_audio_path, format="wav")
        wanted_duration = phrase.get_end_time() - phrase.get_start_time()
        current_duration = len(audio_slice)
        speed = round( current_duration / wanted_duration , 4)

        if speed > 1.15: speed = 1.15
        elif speed < 0.8: speed = 0.83
        
        # audio_slice = Audio.adjust_audio_speed(save_audio_path, speed=speed)
        ats.audio_time_stretch(save_audio_path,save_audio_path,speed)
        audio_slice = AudioSegment.from_wav(save_audio_path)

        audio_slice += 10

        print("wanted_duration ",wanted_duration,". gotten duration ",len(audio_slice))
        audio_slices.append(audio_slice) # phrase.get_start_time(),phrase.get_end_time(),
        current_audio_size += len(audio_slice)
        #remove chunk
        os.remove(save_audio_path)
    
    generated_audio = None

    if audio.get_audio_duration_ms() - current_audio_size > 2000:
        ## Add silences
        difference = audio.get_audio_duration_ms() - current_audio_size
        print("current_audio_size: ",current_audio_size, "original duration: ",audio.get_audio_duration_ms()," difference: ",difference)
        silences_to_add = len(audio_slices)+1
        silence_dur = int(difference / silences_to_add)
        print("Everysilence will last: ",silence_dur," with ",silences_to_add, " silences.")
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

    save_audio_path = os.path.join("src/core/temp",f"test_es-en_.wav")
    generated_audio.export(save_audio_path, format="wav")

def test_automatic_voices_extraction():
    video_path = "/home/an/Documents/VSCode/TranlatorIA/src/app/static/videos/Spanish_English_source.mp4"
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join("/home/an/Documents/VSCode/TranlatorIA/src/app/static/audio", video_name+'.wav')
    print(audio_path)
    source_video, source_audio = preprocess.video_file_to_Video_Audio(video_file=video_path, path_to_save_audio=audio_path, language='Spanish')

    source_audio, phrases = audio_split_and_S2T(source_audio, False, 'base')
    # phrases = { 0: Phrase(0, 401, 17892, 0, "Hay otra pregunta que no sé si tú tengas alguna opinión con respecto a esto, pero ¿qué opinas del futuro los programadores con respecto a la inteligencia artificial? Es un tema súper popular en este momento, no sé si tienes alguna opinión."),
    #             1: Phrase(1, 18063, 41366, 1, "Sí, bueno, yo he experimentado con esa misma herramienta de chat GPT que puede escribir. O digo, bueno. Sí, es. Eso es, escribe código mejor que yo, yo digo miércoles. Pero, pero bueno, creo que siempre ha sido cierto que en si estás en una carrera de tecnología, es que tienes que adaptarte al cambio, porque siempre"),
    #             2: Phrase(2, 41366, 64259, 1, "Por ejemplo, ahora mismo estamos aprendiendo lenguajes populares como Java o Angular, pero en 10 años esas tecnologías pueden ser los soletas. Y hace 10 años no usábamos estos lenguajes para crear aplicaciones. Así que creo que siempre hay que como que poderse adaptarse. Es un aspecto de nuestra carrera."), 
    #             3: Phrase(3, 64259, 80748, 1, "Y si es el caso que la inteligencia artificial va a evolucionar a un nivel que va a empezar a reemplazar trabajos, pues tenemos que adaptarnos a ese cambio y empezar a aprender sobre la inteligencia artificial quizás."),
    #             4: Phrase(4, 80748, 88004, 1, "Y ser las personas que crean estas herramientas en vez de las personas que se están reemplazando con estas herramientas.")}
    print(phrases)
    print("-------------------")
    voices_by_spks:dict = automatic_voices_extraction(phrases, source_audio, 'auto voice')
    print(voices_by_spks)

test_automatic_voices_extraction()
# solo_test("/home/an/Documents/VSCode/TranlatorIA/src/app/static/videos/Spanish_English_source.mp4",
#           "Spanish", "English")
# print("-------------------")
# solo_test("/home/an/Documents/VSCode/TranlatorIA/src/app/static/videos/Spanish_French_source.mp4",
#           "Spanish", "English")

# ats.audio_time_stretch("src/core/temp/Spanish_English_source.wav","src/core/temp/stretch.wav",2)


# audio_split, phrases = test_aud_split_pydub_whisper("src/core/temp/Spanish_English_source.wav","Spanish")
# print("###### RESULT ######")
# print(phrases)
# test_trans_aud_gen(audio_split, phrases,"Spanish","English","MMS") #"google"

# full_test()
# solo_test("src\core\\temp\La SUTILEZA de VEGETTA777.wav",'es','en')
# solo_test("src\\app\\static\\videos\\English_Spanish_source.mp4",'en','es')

# p = main.Process_Video()
# p.set_video("../vidub dataset/spanish (España)/La SUTILEZA de VEGETTA777.mp4")
# text = p.get_speech_to_text("Spanish")
# print(text)
# transl = p.get_translation("English")
# print(transl)
# new_video = p.get_translated_video()
# print(new_video)
# test_audio_generation()

# video = Video("/media/an/Transcend/Video_Translation/TranslatorIA_clone/TranlatorIA/src/app/static/videos/5jFtZRov6MhZTMjF.mp4",'5jFtZRov6MhZTMjF')
# gen_vid.watermark_by_text(video,"water1.mp4")
# gen_vid.watermark_by_image(video,'/media/an/Transcend/Video_Translation/TranslatorIA_clone/TranlatorIA/src/app/static/assets/img/Watermark.png')


       
# tts = mytts.TTS_google_cloud()
# tts.generate_speech("A 17-year-old boy, who is perfect, angular features, high cheekbones, strong jawline, blue-grain eyes, untide bronze colored hair, with light color closed base jacket in a modern setting.","English",'gctts.mp3')
# print(tts.preset_voices() )
# tts._generate_voices_dict()

# save_audio_path = os.path.join("src/core/temp",f"test_google_cloud.wav")

# tts.generate_speech(input_text="A 17-year-old boy, who is perfect, angular features, high cheekbones, strong jawline, blue-grain eyes, untide bronze colored hair, with light color closed base jacket in a modern setting.", 
                    # language="English", save_audio_path=save_audio_path,voice_sett=SpeakerSettings(0,'male','en-US-Standard-C'))

# audio_slice = AudioSegment.from_wav(save_audio_path)

# video = AudioSegment.from_file("I guess I'm a dead channel now.mp4", 'mp4')
# video.export("pew_sample.wav", format="wav")

# audio = AudioSegment.from_wav("voice_sample.wav")
# ms=1000
# ten_sec =  audio[38*ms:41500] + AudioSegment.silent(500) + audio[47*ms:52*ms] # audio[11*ms:15] +
# # # audio[11*ms:15*ms].export("voice_sample_11-15.wav", format="wav")
# # # audio[38*ms:41500].export("voice_sample_38-42.wav", format="wav")
# # # audio[47*ms:52*ms].export("voice_sample_47-52.wav", format="wav")
# ten_sec.export("voice_sample_10_sec.wav", format="wav")

# audio = AudioSegment.fro e_result1.wav",voice)
# clone_synt.generate_speech("I guess I'm a dead channel now. But I don't feel like I need to prove myself to anyone.",
#                            "English","clone_result2.wav",voice)