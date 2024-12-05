from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from web_base.settings import BASE_DIR, STATICFILES_DIRS
from accounts.models import UserBase, TranslationInfo_User, Saved_voices_user
from home.models import File
from video_translation.forms import AudioForm
from video_translation import functions as vt_f
import os
import shutil
import random
import string
from pydub import AudioSegment
from src.core.main import Video, TranslationPack, Process_Video, SpeakerSettings, PhraseSettings
from src.core.text_to_speech import VoiceClone_XTTS
from src.core.common import errors
from django.http import FileResponse, HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.translation import to_locale, get_language

def activate_language(request, language_code):
    next_url = request.GET.get("next", request.META.get('HTTP_REFERER', '/'))
    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=404)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code)
    return response

@login_required(login_url="/accounts/login/")
def voice_clone(request):
    def handle_uploaded_file(f,extension):  
        random_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)]) + extension
        full_path = os.path.join(BASE_DIR, 'static', 'clone audio', random_name)
        with open(full_path, 'wb+') as destination:  
            for chunk in f.chunks():  
                destination.write(chunk)
        return random_name, full_path
        
    context = {'redirect_to': request.path}
    
    if request.method == 'POST' and request.POST.get('existingPath', False) and request.POST.get('nextSlice', False):
        # print(request.POST)
        file = request.FILES['file'].read()
        fileName = request.POST['filename']
        existingPath = request.POST['existingPath']
        end = request.POST['end']
        nextSlice = request.POST['nextSlice']

        if file=="" or fileName=="" or existingPath=="" or end=="" or nextSlice=="":
            res = JsonResponse({'data':'Invalid Request'})
            return res        
        else:
            if existingPath == 'null':
                path = 'media/' + fileName
                with open(path, 'wb+') as destination: 
                    destination.write(file)
                FileFolder = File()
                FileFolder.existingPath = fileName
                FileFolder.eof = end
                FileFolder.name = fileName
                FileFolder.save()
                if int(end):
                    res = JsonResponse({'data':'Uploaded Successfully','existingPath': fileName})
                else:
                    res = JsonResponse({'existingPath': fileName})
                return res
            else:
                path = 'media/' + existingPath
                model_id = File.objects.get(existingPath=existingPath)
                if model_id.name == fileName:
                    if not model_id.eof:
                        with open(path, 'ab+') as destination: 
                            destination.write(file)
                        if int(end):
                            model_id.eof = int(end)
                            model_id.save()
                            res = JsonResponse({'data':'Uploaded Successfully','existingPath':model_id.existingPath})
                        else:
                            res = JsonResponse({'existingPath':model_id.existingPath})    
                        return res
                    else:
                        res = JsonResponse({'data':'EOF found. Invalid request'})
                        return res
                else:
                    res = JsonResponse({'data':'No such file exists in the existingPath'})
                    return res
    if request.method == 'POST' and request.FILES.get('file', False) and request.POST.get('voice_name', False):
        # print(request.POST, request.FILES, request.FILES['file'].name)
        
        file = AudioForm(request.POST, request.FILES)  
        media = os.path.join(settings.BASE_DIR,'media')
        orig_filename = str(request.FILES['file'])
        try:
            os.remove(os.path.join(media, orig_filename))
        except Exception as er:
            print(er)

        if file.is_valid():
            context['posted'] = False 
            # print(file.cleaned_data['languages'])
            file_name_without_ext, file_ext = os.path.splitext(request.FILES['file'].name)
            filename, fullpath = handle_uploaded_file(request.FILES['file'],file_ext)  
            file_name_without_ext, file_ext = os.path.splitext(fullpath)

            if file_ext != '.wav':
                temp = AudioSegment.from_mp3(fullpath)
                temp.export(file_name_without_ext+'.wav', format="wav")
            
            voice = AudioSegment.from_wav(file_name_without_ext+'.wav')
            if len(voice) > 15 * 1000:
                voice = voice[:15000]

            user: UserBase = request.user
            # voice_clone = VoiceClone_XTTS(file.voice_name,sample_audio=voice)

            cloned_voice = Saved_voices_user()
            cloned_voice.user = user
            cloned_voice.voice_name = file.cleaned_data['voice_name']
            # cloned_voice.language = file.cleaned_data['languages']
            cloned_voice.voice_sample = voice
            cloned_voice.save()
            os.remove(fullpath)

            # context ['form'] = file 
            context = {}
            context['posted'] = True
            file = AudioForm() 
            context ['form'] = file 
            return render(request,template_name='Input.html',context=context) # TODO redirect("home")
        else:
            print(file.errors)
            context['posted'] = False
            context ['form'] = file
            return render(request,template_name='Input.html',context=context)
    else:  
        context['posted'] = True 
        file = AudioForm() 
        context ['form'] = file 
    return render(request,template_name='Input.html',context=context)

@login_required(login_url="/accounts/login/")
def translation(request, pk=None):
    def save_trans(processor: Process_Video, transl_user: TranslationInfo_User):
        """Given a Process_Video, save the info within it to transl_user.translation_info (TranslationPack). Then update transl_user in datbase """
        user: UserBase = request.user
        request.session['translation_pk'] = transl_user.pk
        
        trans_pack = processor.get_translation_pack()
        transl_user.translation_info = trans_pack
        if transl_user.using_storage:
            transl_user.update_storage()

        transl_user.save()
        
    def to_loading(processor, transl_user, context, towards_loading):
        if towards_loading:
            # print(request.session)
            if not request.session.get('loading', False):
                # render loading screen
                print('loading True')
                request.session['loading'] = True
                context['loading'] = True
                save_trans(processor, transl_user) 
                return True
            else: return False
        else:
            if request.session.get('loading', False):
                # normal behavior, load stuff while loading screen and show it afterwards
                print('loading False')
                request.session['loading'] = False
            context['loading'] = False            
            return False

    system_messages = messages.get_messages(request)
    for message in system_messages:
        # This iteration is necessary
        pass
    # print('pk = ',pk)
    user: UserBase = request.user
    # transl_pack = None
    if pk == None: # TODO or other thing 
        if request.session.has_key('translation_pk') and request.session['translation_pk'] != None:
            pk = request.session['translation_pk']
            transl_user = TranslationInfo_User.objects.get(pk=pk)
            print('not new')
        else: # TODO unchecked
            transl_user = TranslationInfo_User()
            transl_user.user = user
            transl_user.translation_info = TranslationPack()
            if request.session.get('transl_name', '!Not in request') != '!Not in request':
                transl_user.transl_name = request.session['transl_name']
            if request.session.get('source_lang', '!Not in request') != '!Not in request':
                transl_user.translation_info.source_language_sel = request.session['source_lang']
            if request.session.get('dest_lang', '!Not in request') != '!Not in request':
                transl_user.translation_info.translated_language_sel = request.session['dest_lang']
            if request.session.get('voice_gender', '!Not in request') != '!Not in request' and request.session.get('voice', '!Not in request') != '!Not in request':
                request_voice_gender = request.session['voice_gender']
                request_voice_name = request.session['voice']
                if request_voice_gender == 'auto' and request_voice_name == 'auto':
                    transl_user.translation_info.voices_from_video = True
                elif request_voice_gender == 'clone':
                    transl_user.translation_info.voices_from_video = False
                    voice_user = Saved_voices_user.objects.filter(user=user, voice_name=request_voice_name, to_show=True)
                    if len(voice_user) != 0:
                        voice_user = voice_user[0]
                        transl_user.translation_info.speakers_settings = [VoiceClone_XTTS(spk_id=-1, voice_name=request_voice_name, sample_audio=voice_user.voice_sample)]
                    else:
                        transl_user.translation_info.speakers_settings = None
                else:
                    transl_user.translation_info.voices_from_video = False
                    transl_user.translation_info.speakers_settings = [SpeakerSettings(spk_id=-1, gender=request_voice_gender, voice_name=request_voice_name, cloned=False)]
            transl_user.save()
            print('new', transl_user.transl_name)
    else:
        transl_user = TranslationInfo_User.objects.get(pk=pk)
        print('pk-', pk, transl_user.transl_name)

    # print('using_storage: ',transl_user.using_storage)
    processor = Process_Video(transl_user.translation_info)
    watermark = user.is_free
    vid_dir = 'videos' if not transl_user.using_storage else 'user_saved'
    # not sure about this one 
    processor.gen_video_path = os.path.join(BASE_DIR, "static", vid_dir)

    # text_generated = (processor.source_video != None) and (processor.source_language != None) and (processor.source_phrases != None)
    # transl_generated = (processor.dest_language != None) and (processor.translated_phrases != None)
    # video_generated = (processor.translated_phrases != None) and (processor.translated_video != None) and (processor.phrases_settings != None) #and (processor.speakers_settings != None)
    source_lang = 'English' if processor.source_language == None else processor.source_language
    dest_lang = 'Spanish' if processor.dest_language == None else processor.dest_language

    intern_languages = vt_f.s2t_and_tts_lang_i18n(processor, to_locale(get_language()))

    context = { 'redirect_to': request.path, 
                'pk':transl_user.pk,
                'source_languages': intern_languages[0],
                'tts_languages': intern_languages[1],
                'default_lang_source': source_lang,
                'default_lang_dest': dest_lang,
                'using_storage': transl_user.using_storage,
                'transl_name': transl_user.transl_name,
                'changes_not_applied': processor.changes_not_applied,
                'loading': False
                }
    
    # print('using_storage: ',transl_user.using_storage)

    # to_loading = False
    if processor.source_video == None:
        context['source_text'] = 'default-auto'
        context['source_text_color'] = None
        context['dest_text'] = 'default-auto'
        context['dest_text_color'] = None
        context['phrases_dict'] = None
        context['gen_video'] = 'None'
        restart = True
        # to_loading = True
    else: 
        # print('source video',processor.source_video)
        restart = False
    
    # if (processor.source_video != None and processor.source_language != None and processor.source_phrases == None ) or \
    #     (processor.source_phrases != None and processor.dest_language != None and processor.translated_phrases == None) or \
    #     (processor.translated_phrases != None and processor.translated_video == None):
    #     # if gonna do at least s2t or translate or gen_video
    #     if not request.method == 'POST':
    #         to_loading = True

    # if (processor.translated_phrases != None and processor.speakers_settings == None):
    #     vt_f.out_random_voice_sett(processor, user)

    # if transl_user.using_storage:
    #     context['transl_name'] = transl_user.transl_name
    
    if (restart or (request.session.has_key('got_video') and not request.session['got_video'])) and request.session.has_key('video_path'):
        video_name, video_path = request.session['video_path']
        context['video_path'] = os.path.join(vid_dir, video_name)
        request.session['got_video'] = True
        processor.set_video(video_path)
        print('new video')
    else: 
        context['video_path'] = os.path.join(vid_dir, processor.source_video.video_name)
        request.session['got_video'] = True
        
    if processor.source_phrases == None or processor.source_video == None or processor.source_language == None:
        context['source_text'] = 'default-auto'
        source_text = ''
    else:
        # (processor.source_video != None) and (processor.source_language != None) and (processor.source_phrases != None)
        source_text = processor.source_phrases
        # context['default_lang_source'] = source_lang
        context['source_text'] = source_text
        # context['source_text_color'] = vt_f.phr_dict_to_list(processor, source_text)
        context['phrases_dict'] = vt_f.phr_2_dict_to_list(processor)
    
    if processor.dest_language == None or processor.translated_phrases == None:
        context['dest_text'] = 'default-auto'
        dest_text = ''
    else:
        # (processor.dest_language != None) and (processor.translated_phrases != None)
        dest_text = processor.translated_phrases
        context['default_lang_dest'] = processor.dest_language
        context['dest_text'] = dest_text
        # context['dest_text_color'] = vt_f.phr_dict_to_list(processor, dest_text, True, False)
        context['phrases_dict'] = vt_f.phr_2_dict_to_list(processor)
        context['speaker_list'] = vt_f.speakers_list(processor, user)
        voices = vt_f.voices_list_from_lang(processor, user)
        context['voices_f'] = voices[0]
        context['voices_m'] = voices[1]
        context['voices_clone'] = voices[2]    
     
    if processor.translated_phrases == None or processor.translated_video == None or processor.phrases_settings == None:
        context['gen_video'] = 'None'
        gen_video_path = ''
    else:
        # (processor.translated_phrases != None) and (processor.translated_video != None) and (processor.phrases_settings != None) and (processor.speakers_settings != None)
        gen_video_path = os.path.join(vid_dir, processor.translated_video.video_name+'.mp4')
        context['gen_video'] = gen_video_path
        # context['dest_text_color'] = vt_f.phr_dict_to_list(processor, dest_text,True,True)
        context['phrases_dict'] = vt_f.phr_2_dict_to_list(processor)
        

    # print('restart', restart, "  request.session['loading']",request.session.get('loading', False))
    # long_process = (request.method == 'POST' and (request.POST.get('gen_text') or request.POST.get('generate_video') \
    #     or request.POST.get('apply_sett_phr'), request.POST.get('spk_sett_1'), request.POST.get('spk_sett_2')))
    # if request.session.get('loading', False):
    #     # render loading screen
    #     print('loading True')
    #     request.session['loading'] = True
    #     context['loading'] = True
    #     save_trans(processor, transl_user) 
    #     return render(request,template_name='translation.html',context=context)
    # else:
    #     # normal behavior, load stuff while loading screen and show it afterwards
        # print('loading False')
        # request.session['loading'] = False
        # context['loading'] = False
    
    if processor.source_phrases != None and processor.translated_phrases != None and (len(processor.source_phrases.items()) != len(processor.translated_phrases.items())):
        if len(processor.translated_phrases) < len(processor.source_phrases):
            processor.translated_phrases = None
            processor.dest_language = None
            processor.translated_audio = None
            processor.translated_video = None
    print(request.method, request.POST, request.GET)

    # empty post
    if request.method == 'POST' and request.POST.get('empty_post',False) != False:
        save_trans(processor, transl_user) 
        context = update_context(context,processor,user,vid_dir)
        # print(context)
        # print(transl_user.using_storage)
        print('empty post')
        to_loading(processor, transl_user, context, towards_loading=False)
        return render(request,template_name='translation.html',context=context)
    
    # get text from speech
    if (request.method == 'POST' and request.POST.get('gen_text',False) != False) or (processor.source_video != None and processor.source_language != None and processor.source_phrases == None ):
        print("speech to text")
        print(request.method == 'POST' and request.POST.get('gen_text',False) != False)
        print(request.POST)
        print(processor.source_video != None and processor.source_language != None and processor.source_phrases == None)
        
        if request.method == 'POST' and request.POST.get('gen_text',False) != False:
            source_lang = request.POST['source_lang']
            processor.source_language = source_lang
        else:
            source_lang = processor.source_language
        if processor.can_s2t() and not request.GET.get('ajax',False):
            print('bef',context['loading'])
            if to_loading(processor, transl_user, context, towards_loading=True):
                print('after',context['loading'])
                processor.source_phrases = None
                save_trans(processor, transl_user) 
                return render(request,template_name='translation.html',context=context)
            print('after',context['loading'])
        else: 
            print(processor.source_video, processor.source_audio)
        try:
            # print(source_lang)
            # source_text = processor.get_speech_to_text(source_lang, "tiny") # TODO
            source_text = processor.get_speech_to_text(source_lang, "medium")
            # print('source_text', source_text)
        except errors.MissingPreviousInfoError as err:
            print(err)
            messages.error(request, _("Error while generating text from source video"))
            save_trans(processor, transl_user) 
            context = update_context(context,processor,user,vid_dir)
            to_loading(processor, transl_user, context, towards_loading=False)
            return render(request,template_name='translation.html',context=context)

        save_trans(processor, transl_user) 
        context = update_context(context, processor, user, vid_dir)
        to_loading(processor, transl_user, context, towards_loading=False)
        if request.method == 'POST' and request.POST.get('gen_text',False) != False:
            print('Text extracted from video by gen_text button')
            return render(request,template_name='translation.html',context=context)
   
    # translate to dest_lang
    if (request.method == 'POST' and request.POST.get('transl_text',False) != False) or (processor.source_phrases != None and processor.dest_language != None and processor.translated_phrases == None):
        print("translate to dest_lang")
        print(request.method == 'POST' and request.POST.get('transl_text',False) != False)
        print(request.POST)
        print(processor.source_phrases != None and processor.dest_language != None and processor.translated_phrases == None)
        
        if request.method == 'POST' and request.POST.get('transl_text',False) != False:
            dest_lang = request.POST['dest_lang']
            processor.dest_language = dest_lang
            vt_f.save_to_file_session(user, transl_user,{'transl_by_btn':True})
        else:
            dest_lang = processor.dest_language
        if processor.can_translate():
            if request.GET.get('ajax',False) == False:
                print('bef',context['loading'])
                if to_loading(processor, transl_user, context, towards_loading=True):
                    processor.translated_phrases = None
                    print('after yes',context['loading'])
                    save_trans(processor, transl_user) 
                    return render(request,template_name='translation.html',context=context)
            print('after not',context['loading'])
        else:
            print("couldn't translate",processor.source_video, processor.source_audio, processor.source_phrases, processor.source_language)
            save_trans(processor, transl_user) 
            context = update_context(context,processor,user,vid_dir)
            return render(request,template_name='translation.html',context=context)
        print(vt_f.file_session_for_transl(user,transl_user))
        transl_by_btn = vt_f.get_file_session(user, transl_user, 'transl_by_btn', False)
        if transl_by_btn != False: vt_f.del_in_file_session(user, transl_user, 'transl_by_btn')
        print('transl_by_btn',transl_by_btn)
        
        try:
            dest_text = processor.get_text_translation(dest_lang)
            if processor.speakers_settings == None:
                vt_f.out_random_voice_sett(processor, user)
        except Exception as err:
            print(err)
            messages.error(request, _("Error while translating text"))
            save_trans(processor, transl_user) 
            context = update_context(context,processor,user,vid_dir)
            to_loading(processor, transl_user, context, towards_loading=False)
            return render(request,template_name='translation.html',context=context)
        
        processor.changes_not_applied['changes_in_source_text'] = False
        save_trans(processor, transl_user) 
        context = update_context(context,processor,user,vid_dir)
        to_loading(processor, transl_user, context, towards_loading=False)
        if (request.method == 'POST' and request.POST.get('transl_text',False) != False) or transl_by_btn:
            print('Text translated by transl_text button')
            return render(request,template_name='translation.html',context=context)

    ###### edit text in a phrase ###### 

    # edit text in a source phrase
    if request.method == 'POST' and request.POST.get('edit_source_text',False) != False:
        phr_id = -1
        phr_new_text = None
        for item in request.POST:
            if 'phr_' in item and '_EditModal' in item:
                # item is the name of the textarea
                spl = item.split('_')
                phr_id = int(spl[1]) - 1
                phr_new_text = request.POST.get(item,None)
                break
        if phr_id < 0 or phr_new_text == None:
            print(phr_id, phr_new_text)
            messages.error(request, _("Error while editing source text"))
            save_trans(processor, transl_user)
            context = update_context(context,processor,user,vid_dir)
            # print(context)
            return render(request,template_name='translation.html',context=context)

        source_text = processor.edit_source_phrase(phrase_id=phr_id, new_text=phr_new_text)
        
        processor.changes_not_applied['changes_in_source_text'] = True

        context = update_context(context,processor,user,vid_dir)
        # print(context['source_text']) # TODO
        # context['source_text'] = source_text
        # context['source_text_color'] = vt_f.phr_dict_to_list(processor, source_text)
        # context['phrases_dict'] = vt_f.phr_2_dict_to_list(processor)
        
        save_trans(processor, transl_user)    
        return render(request,template_name='translation.html',context=context)

    # edit text in a dest phrase
    if request.method == 'POST' and request.POST.get('edit_transl_text',False) != False:
        phr_id = -1
        phr_new_text = None
        for item in request.POST:
            if 'phr_' in item and '_EditTModal' in item:
                # item is the name of the textarea
                spl = item.split('_')
                phr_id = int(spl[1]) - 1
                phr_new_text = request.POST.get(item,None)
                break
        if phr_id < 0 or phr_new_text == None:
            print(phr_id, phr_new_text)
            messages.error(request, _("Error while editing translated text"))
            save_trans(processor, transl_user)
            context = update_context(context,processor,user,vid_dir)
            return render(request,template_name='translation.html',context=context)
        
        dest_text = processor.edit_transl_phrase(phrase_id=phr_id, new_text=phr_new_text)
        
        processor.changes_not_applied['changes_in_transl_text'] = True

        context = update_context(context,processor,user,vid_dir)
        # context['dest_text'] = dest_text  
        # context['dest_text_color'] = vt_f.phr_dict_to_list(processor, dest_text, True,True)        
        # context['phrases_dict'] = vt_f.phr_2_dict_to_list(processor)

        save_trans(processor, transl_user) 
        return render(request,template_name='translation.html',context=context)
    
    # restore text in a source phrase
    if request.method == 'POST' and request.POST.get('restore_source_text',False) != False:
        phr_id = -1
        for item in request.POST:
            if 'phr_' in item and '_EditModal' in item:
                # item is the name of the textarea
                spl = item.split('_')
                phr_id = int(spl[1]) - 1
                break
        if phr_id < 0:
            print(request.POST)
            messages.error(request, _("Error while restoring source text"))
            save_trans(processor, transl_user)
            context = update_context(context,processor,user,vid_dir)
            # print(context)
            return render(request,template_name='translation.html',context=context)
        
        source_text = processor.restore_source_phrase(phrase_id=phr_id)

        processor.changes_not_applied['changes_in_source_text'] = True
        
        context = update_context(context,processor,user,vid_dir)
        # context['source_text'] = source_text
        # context['source_text_color'] = vt_f.phr_dict_to_list(processor, source_text)
        # context['phrases_dict'] = vt_f.phr_2_dict_to_list(processor)

        save_trans(processor, transl_user)
        return render(request,template_name='translation.html',context=context)

    # restore text in a dest phrase
    if request.method == 'POST' and request.POST.get('restore_transl_text',False) != False:
        phr_id = -1
        for item in request.POST:
            if 'phr_' in item and '_EditTModal' in item:
                # item is the name of the textarea
                spl = item.split('_')
                phr_id = int(spl[1]) - 1
                break
        if phr_id < 0:
            print(request.POST)
            messages.error(request, _("Error while restoring translated text"))
            save_trans(processor, transl_user)
            context = update_context(context,processor,user,vid_dir)
            return render(request,template_name='translation.html',context=context)
        
        dest_text = processor.restore_transl_phrase(phrase_id=phr_id)

        processor.changes_not_applied['changes_in_transl_text'] = True

        context = update_context(context,processor,user,vid_dir)
        # context['dest_text'] = dest_text  
        # context['dest_text_color'] = vt_f.phr_dict_to_list(processor, dest_text, True,True)
        # context['phrases_dict'] = vt_f.phr_2_dict_to_list(processor)
        
        save_trans(processor, transl_user)
        return render(request,template_name='translation.html',context=context)
    # print(request.method, request.session.get('apply_sett_phr'))
    # apply the settings by phrases 
    if (request.method == 'POST' and (request.POST.get('apply_sett_phr',False) != False or \
                                      request.POST.get('apply_gen_sett_phr',False) != False))  \
                                    or vt_f.get_file_session(user,transl_user,'apply_sett_phr',False):
        print("apply the settings by phrases")
        print((request.POST.get('apply_sett_phr',False) != False or request.POST.get('apply_gen_sett_phr',False) != False))
        print(vt_f.get_file_session(user,transl_user,'apply_sett_phr',False))
        translated_video = processor.translated_video != None
        print('settings by phrases', vt_f.get_file_session(user,transl_user,'apply_sett_phr'))
        if not translated_video:
            messages.error(request, _("Error while applying phrases settings. Generate video first"))
            save_trans(processor, transl_user)
            context = update_context(context,processor,user,vid_dir)
            # print(context)
            return render(request,template_name='translation.html',context=context)
        print(request.POST)
        # print(context['phrases_dict'])
        if not vt_f.get_file_session(user,transl_user,'apply_sett_phr',False):
            time_speed = request.POST.get("time-speed_switch", None)
            if time_speed == "on": # by speed
                mode="by_phr_speed"
                speeds = []
                volumes = []
                for phr_dict in context['phrases_dict']:
                    volume = f"{phr_dict['phr_vol_name']}"
                    speed = f"{phr_dict['phr_spd_name']}"

                    volume = request.POST.get(volume,False)
                    speed = request.POST.get(speed,False)
                    print(volume,speed)
                    if volume != False:
                        volume = int(volume)
                    if  speed != False:
                        speed = float(speed)
                    volumes.append(volume)
                    speeds.append(speed)
                vt_f.set_new_volumes(processor,volumes)
                vt_f.set_new_speeds(processor,speeds)
            else: # by time
                mode="default"
                phrases_new_times = []
                volumes = []
                for phr_dict in context['phrases_dict']:
                    s_hours = f"{ phr_dict['id'] }-st-time-hours"
                    s_min = f"{ phr_dict['id'] }-st-time-min"
                    s_sec = f"{ phr_dict['id'] }-st-time-sec"
                    e_hours = f"{ phr_dict['id'] }-end-time-hours"
                    e_min = f"{ phr_dict['id'] }-end-time-min"
                    e_sec = f"{ phr_dict['id'] }-end-time-sec"
                    volume = phr_dict['phr_vol_name']
                    
                    volume = request.POST.getlist(volume)[0]
                    s_hours = request.POST.get(s_hours,False)
                    s_min = request.POST.get(s_min,False)
                    s_sec = request.POST.get(s_sec,False)
                    e_hours = request.POST.get(e_hours,False)
                    e_min = request.POST.get(e_min,False)
                    e_sec = request.POST.get(e_sec,False)

                    if volume != False:
                        volume = int(volume)
                    if s_hours != False:
                        s_hours = int(s_hours)
                    if s_min != False:
                        s_min = int(s_min)
                    if s_sec != False:
                        s_sec = int(s_sec)
                    if e_hours != False:
                        e_hours = int(e_hours)
                    if e_min != False:
                        e_min = int(e_min)
                    if e_sec != False:
                        e_sec = int(e_sec)
                    phrases_new_times.append([(s_hours, s_min, s_sec),(e_hours, e_min, e_sec)])
                    volumes.append(volume)
                vt_f.set_new_phr_times(processor,phrases_new_times)
                vt_f.set_new_volumes(processor,volumes)
        else:
            mode = vt_f.get_file_session(user,transl_user,'apply_sett_phr')
            print(mode, '-', vt_f.get_file_session(user,transl_user,'apply_sett_phr'))
        # print(processor.translated_phrases)
        # print(processor.phrases_settings)
        # raise Exception()
        
        if request.POST.get('apply_gen_sett_phr',False) != False or vt_f.get_file_session(user,transl_user,'apply_sett_phr',False) != False:
            if vt_f.get_file_session(user,transl_user,'apply_sett_phr',False) != False:
                # del request.session['apply_sett_phr']
                # m = request.session.pop('your key')
                vt_f.del_in_file_session(user,transl_user,'apply_sett_phr')

            if processor.can_generate_video() and not request.GET.get('ajax',False):
                keep_orig_sil = request.POST.get("keep_orig_sil-switch", None)
                if keep_orig_sil == "on":
                    vt_f.save_to_file_session(user,transl_user,{'keep_orig_sil':True})
                else: vt_f.save_to_file_session(user,transl_user,{'keep_orig_sil':False})

                print('bef',context['loading'])
                if to_loading(processor, transl_user, context, towards_loading=True):
                    vt_f.save_to_file_session(user,transl_user,{'apply_sett_phr':mode})
                    print(mode, '-', vt_f.get_file_session(user,transl_user,'apply_sett_phr'))
                    print('after',context['loading'])
                    return render(request,template_name='translation.html',context=context)
                print('no ret after',context['loading'])
            # request.session['apply_sett_phr'] = False
            # request.session.modified = True
            # request.session.save()
            print(mode, '--',vt_f.get_file_session(user,transl_user,'apply_sett_phr',False))
            if translated_video:
                older = os.path.join(STATICFILES_DIRS[0],gen_video_path)

            try:
                keep_orig_sil = vt_f.get_file_session(user,transl_user,'keep_orig_sil',None)
                gen_video_path = os.path.join(vid_dir, processor.generate_video_main(mode=mode, keep_orig_audio_in_sil=keep_orig_sil,watermark=watermark))
            except Exception as err:
                print(err)
                messages.error(request, _("Error while applying phrases settings"))
                save_trans(processor, transl_user) 
                context = update_context(context,processor,user,vid_dir)
                to_loading(processor, transl_user, context, towards_loading=False)
                print('except', vt_f.get_file_session(user,transl_user,'apply_sett_phr'))
                return render(request,template_name='translation.html',context=context)
            
            if translated_video:
                try:
                    os.remove(older)
                except Exception as err:
                    print(err)
        
            processor.changes_not_applied['changes_in_transl_text'] = False
            save_trans(processor, transl_user) 
            context = update_context(context,processor,user,vid_dir)
            to_loading(processor, transl_user, context, towards_loading=False)
            print(request.session['loading'], vt_f.get_file_session(user,transl_user,'apply_sett_phr',False))
            return render(request,template_name='translation.html',context=context)
        
        save_trans(processor, transl_user)
        context = update_context(context,processor,user,vid_dir)
        # to_loading(processor, transl_user, context, towards_loading=False)
        return render(request,template_name='translation.html',context=context)
    
    # apply volume and speed changes by speaker
    if request.method == 'POST' and request.POST.get('spk_sett_1',False) != False: 
        translated_video = processor.translated_video != None
        if not translated_video:
            messages.error(request, _("Error while applying speakers settings. Generate video first"))
            save_trans(processor, transl_user)
            context = update_context(context,processor,user,vid_dir)
            return render(request,template_name='translation.html',context=context)
        
        spk_settings = []
        for tup in context['speaker_list']:
            spk = tup[0]
            vol_name = f'spk{int(spk)}_volumeNumber'
            spd_name = f'spk{int(spk)}_speedNumber'

            volume = request.POST.get(vol_name,False)
            if volume != False:
                volume = int(volume)

            speed = request.POST.get(spd_name,False)
            if speed != False:
                speed = float(speed)
            spk_settings.append({"volume":volume,"speed":speed}) 

        # print(spk_settings)
        if translated_video:
            older = os.path.join(STATICFILES_DIRS[0],gen_video_path)

        try:
            gen_video_path = os.path.join(vid_dir, processor.recreate_video_from_spk_sett(spk_settings,watermark=watermark))
        except Exception as err:
            print(err)
            messages.error(request, _("Error while applying speakers settings"))
            save_trans(processor, transl_user) 
            context = update_context(context,processor,user,vid_dir)
            return render(request,template_name='translation.html',context=context)
        
        if translated_video:
            try:
                os.remove(older)
            except Exception as err:
                print(err)
        processor.changes_not_applied['changes_in_transl_text'] = False
        save_trans(processor, transl_user)
        context = update_context(context,processor,user,vid_dir)
        return render(request,template_name='translation.html',context=context)

    # # apply voices changes by speaker
    # if request.method == 'POST' and request.POST.get('spk_sett_2',False) != False:
    #     translated_video = processor.translated_video != None
    #     if not translated_video:            
    #         messages.error(request, _("Error while applying voices settings. Generate video first"))
    #         save_trans(processor, transl_user)
    #         context = update_context(context,processor,user,vid_dir)
    #         # print(context)
    #         return render(request,template_name='translation.html',context=context)
        
    #     voice_sett_by_spk = get_voices_from_POST(request.POST, context['speaker_list'])
    #     if voice_sett_by_spk == False:
    #         print("Failure", list(request.POST))
    #         messages.error(request, _("Error while applying voices settings. No gender or voice selected"))
    #         save_trans(processor, transl_user) 
    #         context = update_context(context,processor,user,vid_dir)
    #         return render(request,template_name='translation.html',context=context)
    #     voice_settings(processor, user, voice_sett_by_spk)
    #     # print(voice_sett_by_spk)
    #     if translated_video:
    #         older = os.path.join(STATICFILES_DIRS[0],gen_video_path)
    #     try:
    #         gen_video_path = os.path.join(vid_dir, processor.generate_video_main(mode='default',watermark=watermark))
    #     except Exception as err:
    #         print(err)
    #         messages.error(request, _("Error while applying voices settings"))
    #         save_trans(processor, transl_user) 
    #         context = update_context(context,processor,user,vid_dir)
    #         # print(context)
    #         return render(request,template_name='translation.html',context=context)
        
    #     if translated_video:
    #         try:
    #             os.remove(older)
    #         except Exception as err:
    #             print(err)
    #     processor.changes_not_applied['changes_in_transl_text'] = False
    #     save_trans(processor, transl_user)
    #     context = update_context(context,processor,user,vid_dir)
    #     # print(context)
    #     return render(request,template_name='translation.html',context=context)

    # download video
    if request.method == 'POST' and request.POST.get('download_video',False) != False:
        try:
            video:Video = processor.translated_video
        except Exception as err:
            print(err)
            messages.error(request, _("Error while downloading video"))             
            save_trans(processor, transl_user) 
            context = update_context(context,processor,user,vid_dir)
            # print(context)
            return render(request,template_name='translation.html',context=context)
        
        filename = video.get_filename()
        source_lang_code = vt_f.iso_code_2_dict[processor.source_language]
        dest_lang_code = vt_f.iso_code_2_dict[processor.dest_language]
        new_name = transl_user.transl_name + "_" + source_lang_code  + "-" + dest_lang_code + ".mp4"
        user.add_time_used(video.get_duration())
        response = FileResponse(open(filename, 'rb'), as_attachment=True, filename=new_name)
        # print('to download')
        return response
    
    # save translation info
    if request.method == 'POST' and request.POST.get('save_translation',False) != False:
        if user.is_free:
            print("the use is free, can't save data")
            messages.error(request, _("The user is free, can't save data"))       
            save_trans(processor, transl_user) 
            context = update_context(context,processor,user,vid_dir)
            # print(context)
            return render(request,template_name='translation.html',context=context)
        
        name = request.POST.get('transl_name','Unknown')
        # print('new name',name)
        transl_user.transl_name = name
        transl_user.save()
        context['transl_name'] = transl_user.transl_name
        save_trans(processor, transl_user)
        if transl_user.using_storage:            
            context = update_context(context,processor,user,vid_dir)
            # print(context)
            return render(request,template_name='translation.html',context=context)


        to_move = []
        source_video = transl_user.translation_info.source_video#.get_filename()
        source_audio = transl_user.translation_info.source_audio#.get_filename()
        transl_video = transl_user.translation_info.translated_video#.get_filename()
        transl_audio = transl_user.translation_info.translated_audio#.get_filename()

        if source_video != None: to_move.append(source_video)
        if source_audio != None: to_move.append(source_audio)
        if transl_video != None: to_move.append(transl_video)
        if transl_audio != None: to_move.append(transl_audio)

        destination_folder = os.path.join(BASE_DIR, 'static', 'user_saved') 
        new_ocupied_space = 0
        for file in to_move:
            file_path = file.get_filename()
            file_stats = os.stat(file_path)
            new_ocupied_space += file_stats.st_size / (1024 * 1024)

        if transl_user.user.storage_MB_used + new_ocupied_space > transl_user.user.max_storage_capacity_MB:
            print("The user storage space has been used up")
            messages.error(request, _("The user storage space has been used up"))   
            save_trans(processor, transl_user) 
            context = update_context(context,processor,user,vid_dir)
            # print(context)
            return render(request,template_name='translation.html',context=context)
    
        for file in to_move:
            file_path = file.get_filename()
            # print(file_path,"->")
            shutil.move(file_path, destination_folder)
            file_name = os.path.basename(file_path)
            file.set_filename(os.path.join(destination_folder,file_name))
            # print(file.get_filename(),"\n")

        transl_user.storage_weight_MB += new_ocupied_space
        transl_user.user.storage_MB_used += new_ocupied_space
        transl_user.using_storage = True
        transl_user.save()
        # processor.__from_translation_pack(transl_user.tr)
        # print('saved to another folder')
        vid_dir = 'user_saved'
        video_name, video_path = request.session['video_path']
        context['video_path'] = os.path.join(vid_dir, video_name)
        
        save_trans(processor, transl_user) 
        context = update_context(context,processor,user,vid_dir)
        # print(context)
        return render(request,template_name='translation.html',context=context)
        
    # generate video 
    if (request.method == 'POST' and request.POST.get('generate_video',False) != False) or (processor.translated_phrases != None and processor.translated_video == None):
        translated_video = processor.translated_video != None
        print("generate video")
        print(request.method == 'POST' and request.POST.get('generate_video',False) != False)
        print(request.POST)
        print(processor.translated_phrases != None and processor.translated_video == None)
        # print(vt_f.get_file_session(user,transl_user,'apply_sett_phr',False))
        if request.method == 'POST' and request.POST.get('generate_video',False) != False:
            random_voice = request.POST.get("random_voice", None)
            auto_adjust = request.POST.get("auto_adjust", None)
            auto_detect_voice = request.POST.get("auto-detect-voices_switch", None)
            if auto_adjust == 'on':
                processor.restore_original_times()
            if random_voice == 'on' or auto_detect_voice =='on':
                if random_voice == 'on':
                    vt_f.out_random_voice_sett(processor, user)
                else:
                    processor.voices_from_video = True
                    processor.auto_voice_extraction()
            else:
                voice_sett_by_spk = get_voices_from_POST(request.POST, context['speaker_list'])
                if voice_sett_by_spk == False:
                    print("Failure", list(request.POST))
                    messages.error(request, _("Error while generating video. No gender or voice selected"))
                    save_trans(processor, transl_user) 
                    context = update_context(context,processor,user,vid_dir)
                    return render(request,template_name='translation.html',context=context)
                # print(voice_sett_by_spk)
                voice_settings(processor, user, voice_sett_by_spk)
                # print(processor.speakers_settings)
            
        if processor.can_generate_video() and not request.GET.get('ajax',False):
            keep_orig_sil = request.POST.get("keep_orig_sil-switch", None)
            if keep_orig_sil == "on":
                vt_f.save_to_file_session(user,transl_user,{'keep_orig_sil':True})
            else: vt_f.save_to_file_session(user,transl_user,{'keep_orig_sil':False})
            if translated_video: 
                older = os.path.join(STATICFILES_DIRS[0], gen_video_path)
                os.remove(older)
            processor.translated_video = None

            print('bef',context['loading'])
            if to_loading(processor, transl_user, context, towards_loading=True):
                print('after',context['loading'])
                save_trans(processor, transl_user) 
                return render(request,template_name='translation.html',context=context)
            print('no ret after',context['loading'])
        if translated_video: 
            older = os.path.join(STATICFILES_DIRS[0], gen_video_path)
            
        # print(processor.speakers_settings)
        if processor.speakers_settings == None:
            vt_f.out_random_voice_sett(processor, user)
        try:
            keep_orig_sil = vt_f.get_file_session(user,transl_user,'keep_orig_sil',True)
            print('processor.voices_from_video',processor.voices_from_video,'\tkeep_orig_sil',keep_orig_sil)
            gen_video_path = os.path.join(vid_dir, processor.generate_video_main(mode='default', keep_orig_audio_in_sil=keep_orig_sil, watermark=watermark))
        except Exception as err:
            print(err)
            if request.method == 'POST' and request.POST.get('generate_video',False) != False:
                messages.error(request, _("Error while generating translated video"))
            save_trans(processor, transl_user) 
            context = update_context(context,processor,user,vid_dir)
            to_loading(processor, transl_user, context, towards_loading=False)
            return render(request,template_name='translation.html',context=context)
        
        if translated_video:
            try:
                os.remove(older)
            except Exception as err:
                print(err)
        processor.changes_not_applied['changes_in_transl_text'] = False
        save_trans(processor, transl_user)
        context = update_context(context,processor,user,vid_dir)
        # print(context)
        if request.method == 'POST' and request.POST.get('generate_video',False) != False:
            print('Video generated by generate_video button')
        to_loading(processor, transl_user, context, towards_loading=False)
        return render(request,template_name='translation.html',context=context)
 
    save_trans(processor, transl_user) 
    context = update_context(context,processor,user,vid_dir)
    # print(context)
    # print(transl_user.using_storage)
    to_loading(processor, transl_user, context, towards_loading=False)
    return render(request,template_name='translation.html',context=context)

def update_context(context:dict, processor:Process_Video, user:UserBase, vid_dir):
    if processor.source_phrases == None:
        context['source_text'] = 'default-auto'
    else:
        # (processor.source_video != None) and (processor.source_language != None) and (processor.source_phrases != None)
        context['default_lang_source'] = processor.source_language
        context['source_text'] = processor.source_phrases
        # context['source_text_color'] = vt_f.phr_dict_to_list(processor, processor.source_phrases)
        context['phrases_dict'] = vt_f.phr_2_dict_to_list(processor)

    if processor.translated_phrases == None:
        context['dest_text'] = 'default-auto'
    else:
        # (processor.dest_language != None) and (processor.translated_phrases != None)
        context['default_lang_dest'] = processor.dest_language
        context['dest_text'] = processor.translated_phrases
        # context['dest_text_color'] = vt_f.phr_dict_to_list(processor, processor.translated_phrases, True, True)
        context['phrases_dict'] = vt_f.phr_2_dict_to_list(processor)
        context['speaker_list'] = vt_f.speakers_list(processor, user)
        voices = vt_f.voices_list_from_lang(processor, user)
        context['voices_f'] = voices[0]
        context['voices_m'] = voices[1]
        context['voices_clone'] = voices[2]
    
    if processor.translated_video == None:
        context['gen_video'] = 'None'
    else:
        # (processor.translated_phrases != None) and (processor.translated_video != None) and (processor.phrases_settings != None) and (processor.speakers_settings != None)
        gen_video_path = os.path.join(vid_dir, processor.translated_video.video_name+'.mp4')
        context['gen_video'] = gen_video_path
        context['phrases_dict'] = vt_f.phr_2_dict_to_list(processor)
        
    context['changes_not_applied'] = processor.changes_not_applied
    return context

def get_voices_from_POST(request_POST:dict, speaker_list):
    """ Given request.POST returns a list of tuples (gender, voice_name) for each speaker"""
    if request_POST.get("voice_gender-1", False):
        voice_sett_by_spk = []
        for tup in speaker_list:
            spk = tup[0]
            gender = f"voice_gender-{ int(spk) }"
            voicef = f"voice-{ int(spk) }-F"
            voicem = f"voice-{ int(spk) }-M"
            voicec = f"voice-{ int(spk) }-clone"
            
            gender = request_POST.get(gender,False)
            if gender == 'female':
                voice = request_POST.get(voicef,False)
            elif gender == 'male': 
                voice = request_POST.get(voicem,False)
            elif gender == 'clone': 
                voice = request_POST.get(voicec,False)

            if gender == False or voice == False:
                return False
            if len(gender) == 0 or len(voice) == 0:
                return False
            
            voice_sett_by_spk.append((gender, voice))
    elif request_POST.get(f"voice_gender-1-gen",False):
        voice_sett_by_spk = []
        for tup in speaker_list:
            spk = tup[0]
            gender = f"voice_gender-{ int(spk) }-gen"
            voicef = f"voice-{ int(spk) }-F-gen"
            voicem = f"voice-{ int(spk) }-M-gen"
            voicec = f"voice-{ int(spk) }-clone-gen"
            
            gender = request_POST.get(gender,False)
            if gender == 'female':
                voice = request_POST.get(voicef,False)
            elif gender == 'male': 
                voice = request_POST.get(voicem,False)
            elif gender == 'clone': 
                voice = request_POST.get(voicec,False)
            
            if gender == False or voice == False:
                return False
            if len(gender) == 0 or len(voice) == 0:
                return False
            
            voice_sett_by_spk.append((gender, voice))
    print(voice_sett_by_spk)
    return voice_sett_by_spk

def voice_settings(processor, user, voices_list):
    # print(voices_list)
    voice_sett_by_spk = []
    for i, (gender, voice) in enumerate(voices_list):
        if gender == 'clone':
            sample = vt_f.__get_cloned_voice_sample(user, voice)
            voice_sett_by_spk.append(VoiceClone_XTTS(i, voice_name=voice, sample_audio=sample)) 
        else: voice_sett_by_spk.append(SpeakerSettings(i, gender=gender, voice_name=voice, cloned=False)) 
    # return voice_sett_by_spk
    processor.speakers_settings = voice_sett_by_spk

