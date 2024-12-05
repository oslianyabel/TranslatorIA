from django.urls import path, include
from home import views


urlpatterns = [

    # The home page
    path('', views.landing, name='landing'),
    path('projects/', views.user_projects, name='user_projects'),
    path('home/', views.index, name='home'),
    # path('i18n/', include('django.conf.urls.i18n')),
    path('languageactivate/<language_code>/', views.activate_language, name='activate_language'),
    # # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),

]