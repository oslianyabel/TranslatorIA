from django.urls import path, re_path, include
from video_translation import views
# app_name = 'video_translation'
urlpatterns = [

    path('', views.translation, name='translation'),
    path("<int:pk>/", views.translation, name="translation"),
    path('voice-generation/', views.voice_clone, name="voice-generation"),
    # path('i18n/', include('django.conf.urls.i18n')),
    path('languageactivate/<language_code>/', views.activate_language, name='activate_language'),

]