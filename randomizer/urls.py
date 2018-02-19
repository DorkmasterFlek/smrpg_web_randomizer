from django.urls import path

from . import views

app_name = 'randomizer'

urlpatterns = [
    # Main
    path('', views.AboutView.as_view(), name='home'),
    path('randomize', views.RandomizeView.as_view(), name='randomize'),

    # Help
    path('difficulties', views.AboutView.as_view(), name='difficulties'),
    path('options', views.OptionsView.as_view(), name='options'),
    path('updates', views.UpdatesView.as_view(), name='updates'),

    # Generation
    path('seed', views.GenerateView.as_view(), name='generate'),
    path('h/<slug:hash>', views.HashView.as_view(), name='patch-from-hash'),
    path('hash/<slug:hash>/<slug:region>', views.GenerateFromHashView.as_view(), name='generate-from-hash'),
    path('pack', views.PackingView.as_view(), name='pack'),
]
