from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# from django.template import loader
# from django.http import HttpResponse, HttpResponseRedirect
from home.functions.functions import handle_uploaded_file, check_video_duration  
from home.forms import VideoForm
from home.models import File
from video_translation import functions as vt_f
from accounts.models import UserBase, TranslationInfo_User, Saved_voices_user
from core.common.common import iso_code_2_dict
from django.utils.translation import gettext as _
from django.utils.translation import to_locale, get_language
from django.views.generic import View
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import os


# @login_required(login_url="/login/")
def index(request):
    # file = VideoForm() 
    # print(file)
    # print(request.user)
    context = {'segment': 'index'}
    # print(request.POST)
    if request.method == 'POST' and request.POST.get('switch-user-type',False) != False:
        user: UserBase = request.user
        print("before: Free =",user.is_free)
        user.is_free = not user.is_free
        print("after: Free =",user.is_free)
        user.save()
        file = VideoForm() 
        context ['form'] = file 
        return render(request,template_name='index.html',context=context)

    if request.method == 'POST' and request.FILES.get('file', False):
        context['posted'] = True
        file = VideoForm(request.POST, request.FILES)  
        if file.is_valid():
            # now check video duration if user is logged
            name, path = handle_uploaded_file(request.FILES['file']) 
            if request.user.is_free:
                dur = check_video_duration(path)
                # print(dur)
                if dur > request.user.max_video_duration_sec:
                    # TODO error pop-up
                    print('the video is to long', dur,' >> ',request.user.max_video_duration_sec)
                    file = VideoForm() 
                    context ['form'] = file 
                    return render(request,template_name='index.html',context=context)
            context['posted'] = False  
            context ['form'] = file 
            
            request.session['video_path'] = name, path
            request.session['got_video'] = False
            request.session['translation_pk'] = None
            
            return redirect("translation")
        
        context ['form'] = file
        return render(request,template_name='index.html',context=context)
    else:  
        context['posted'] = False 
        file = VideoForm() 
        context ['form'] = file
    return render(request,template_name='index.html',context=context)

@login_required(login_url="/accounts/login/")
def user_projects(request):
    print('hi')  
    # print(request.session.keys() )  
    user:UserBase = request.user
    print(user)
    system_messages = messages.get_messages(request)
    for message in system_messages:
        # This iteration is necessary
        pass
    file = VideoForm() 
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
                
    if request.method == 'POST' and request.FILES.get('file', False) and request.POST.get('voice_gender', False):
        file = VideoForm(request.POST, request.FILES)  
        if request.POST.get('transl_name', "") != "":
            if file.is_valid():
                # now check video duration if user is logged
                media = os.path.join(settings.BASE_DIR,'media')
                filename = str(request.FILES['file'])
                print(os.path.join(media,filename))
                try:
                    os.remove(os.path.join(media,filename))
                except Exception as er:
                    print(er)
                name, path = handle_uploaded_file(request.FILES['file']) 
                # print(name, path)
                # print(request.POST)

                # video_path, transl_name, source_lang, tts_language, folder, voice 
                transl_name = request.POST.get('transl_name', False)
                source_lang = request.POST.get('source_lang', False)
                dest_lang = request.POST.get('dest_lang', False)
                request.session['video_path'] = name, path
                # request.session['got_video'] = False
                request.session['transl_name'] = transl_name
                request.session['source_lang'] = source_lang
                request.session['dest_lang'] = dest_lang
                request.session['translation_pk'] = None

                auto_voice = request.POST.get("auto-detect-voices_switch", None)
                
                if auto_voice == "on": # use the voices from the video
                    print(transl_name, source_lang, dest_lang, 'auto')
                    request.session['voice_gender'] = 'auto'
                    request.session['voice'] = 'auto'
                else: # use the selected voice 
                    voice_gender = request.POST.get('voice_gender', False)
                    voice_name = f"voice-{dest_lang}-"
                    if voice_gender == "female":
                        voice_name += "F"
                    elif voice_gender == "male":
                        voice_name += "M"
                    elif voice_gender == "clone":
                        voice_name += "clone"
                    voice = request.POST.get(voice_name, False)
                    print(transl_name, source_lang, dest_lang, voice_gender)
                    print('voice: ', voice)

                    request.session['voice_gender'] = voice_gender
                    request.session['voice'] = voice
                
                return redirect("translation")
            else:
                messages.error(request, _("File not valid error. Try again"))
    
    if request.method == 'POST' and request.POST.get('delete_voice',False) != False:
        voice_pk = request.POST['voice_id']
        voice_user = Saved_voices_user.objects.filter(pk=voice_pk, to_show=True)[0]
        voice_user.user_delete()

    if request.method == 'POST' and request.POST.get('delete_translation',False) != False:
        trans_pk = request.POST['translation_id']
        translation = TranslationInfo_User.objects.filter(pk=trans_pk, to_show=True)[0]
        translation.user_delete()

    if request.method == 'POST' :
        if request.POST.get('transl_name', "") == "":
            messages.error(request, _("Project Name required"))


    # if request.method == 'POST' and request.FILES.get('file', False) and request.POST.get('upload_video',False) != False:
    #     # context['posted'] = True
    #     print(request.POST)
    #     file = VideoForm(request.POST, request.FILES)  
    #     if file.is_valid():
    #         # now check video duration if user is logged
    #         name, path = handle_uploaded_file(request.FILES['file']) 
    #         # if request.user.is_free:
    #         #     dur = check_video_duration(path)
    #         #     # print(dur)
    #         #     if dur > request.user.max_video_duration_sec:
    #         #         # TODO error pop-up
    #         #         print('the video is to long', dur,' >> ',request.user.max_video_duration_sec)
    #         #         file = VideoForm() 
    #         #         context ['form'] = file 
    #         #         return render(request,template_name='user_projects.html',context=context)
    #         # context['posted'] = False  
    #         # context ['form'] = file 
            
    #         # video_path, transl_name, source_lang, tts_language, folder, voice 
    #         request.session['video_path'] = name, path
    #         request.session['got_video'] = False
    #         request.session['transl_name'] = request.POST.get('transl_name',False)
    #         request.session['translation_pk'] = None
            
    #         return redirect("translation")
        
    #     context ['form'] = file
    #     return render(request,template_name='user_projects.html',context=context)
    # else:  
        # # context['posted'] = False 
        # file = VideoForm() 
        # context ['form'] = file
    user.update_storage()
    translations = TranslationInfo_User.objects.filter(user=user, using_storage=True, to_show=True)
    voices_user = Saved_voices_user.objects.filter(user=user, to_show=True)
    default_lang = dict(settings.LANGUAGES).get(get_language(),'Spanish')
    intern_languages = vt_f.s2t_and_tts_lang_i18n(None, to_locale(get_language()))

    max_storage = user.max_storage_capacity_MB
    max_duration = user.max_video_duration_ms / 1000
    storage_used = user.storage_MB_used
    storage_left = max_storage - storage_used
    time_used = user.videos_time_used_ms / 1000
    time_left_today = max_duration - time_used

    context = { 'redirect_to': request.path,
                'max_storage': max_storage,
                'max_duration': max_duration,
                'storage_used': round(storage_used, 2),
                'storage_left': round(storage_left, 2),
                'time_used': round(time_used),
                'time_left_today': round(time_left_today),
                'source_languages': intern_languages[0],
                'tts_languages': intern_languages[1],
                'clone_languages': intern_languages[2],
                'selected_lang_source': default_lang,
                'selected_lang_dest': default_lang,
                'voices_by_lang' : vt_f.voices_list_by_lang(processor=None, user=user, lang_tuple_list=intern_languages[1]),
                'messages':messages.get_messages(request),
                }
    # print(context['voices_by_lang'])
    
    context ['form'] = file

    voice_table = []

    for v in voices_user:
        name = v.voice_name 
        # index = list(iso_code_2_dict.values()).index(v.language)
        # language = list(iso_code_2_dict.keys())[index]
        # if to_locale(get_language()) == 'es':
        #     language = vt_f.EU_languages_en_es[language]
        voice_table.append({'name':name, 'id':v.pk})
    
    context ['translations'] = vt_f.translation_to_dict(translations, to_locale(get_language()))
    context ['cloned_voices'] = voice_table
    
    if len(translations) == 0:
        context['translations'] = 'None'
    if len(voice_table) == 0:
        context['cloned_voices'] = 'None'
    return render(request,template_name='user_projects.html',context=context)

def landing(request): 
    # print(request.user, request.user.is_authenticated)
    # email1 = 'nileygf@gmail.com'
    # email2 = 'arianpzv@gmail.com'
    # user = UserBase.objects.get(email=email2)
    # print(user)
    # user.delete()
    if request.method == 'POST' and request.POST.get('switch-user-type', False) != False:
        user: UserBase = request.user
        print("before: Free =",user.is_free)
        user.is_free = not user.is_free
        print("after: Free =",user.is_free)
        user.save()
        
    context = {'redirect_to': request.path }
    return render(request, template_name='Landing_Page.html', context=context)

def activate_language(request, language_code):
    next_url = request.GET.get("next", request.META.get('HTTP_REFERER', '/'))
    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=404)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code)
    return response

class ActivateLanguageView(View):
    
    def get(self, request, language_code, **kwargs):
        next_url = self.request.GET.get("next", self.request.META.get('HTTP_REFERER', '/'))
        response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=404)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code)
        return response
