from django.urls import path

from . import views

app_name = 'randomizer'

urlpatterns = [
    # Main
    path('', views.AboutView.as_view(), name='home'),
    path('randomize', views.RandomizeView.as_view(), name='randomize'),
    path('contribute', views.ContributeView.as_view(), name='contribute'),
    path('community', views.CommunityView.as_view(), name='community'),

    # Help
    path('how-to-play', views.HowToPlayView.as_view(), name='how-to-play'),
    path('difficulties', views.AboutView.as_view(), name='difficulties'),
    path('options', views.OptionsView.as_view(), name='options'),
    path('resources', views.ResourcesView.as_view(), name='resources'),
    path('checks', views.ChecksView.as_view(), name='checks'),
    path('guide', views.GuideView.as_view(), name='guide'),
    path('updates', views.UpdatesView.as_view(), name='updates'),
    path('remake', views.RemakeView.as_view(), name='remake'),

    # Generation
    path('seed', views.GenerateView.as_view(), name='generate'),
    path('seed/status/<slug:seed_id>', views.GenerateStatusView.as_view(), name='generate-status'),
    path('h/<slug:hash>', views.HashView.as_view(), name='patch-from-hash'),
    path('hash/<slug:hash>', views.GenerateFromHashView.as_view(), name='generate-from-hash'),
    path('pack', views.PackingView.as_view(), name='pack'),

    # API
    path('api/v1/generate', views.APIGenerateView.as_view(), name='api-v1-generate'),
    path('api/v1/flags', views.APIFlags.as_view(), name='api-v1-flags'),
]
