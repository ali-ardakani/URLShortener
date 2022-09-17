from django.urls import path
from . import views

app_name = 'url_shortener'

urlpatterns = [
    path('', views.WelcomeView.as_view(), name='welcome'),
    path('url_shortener/',
         views.UrlShortenerCreateView.as_view(),
         name='url_shortener'),
    path('urls/', views.UrlListView.as_view(), name='urls'),
    path('info/<str:short_url>/', views.UrlDetailView.as_view(), name='info'),
    path('url/<str:short_url>/',
         views.UrlRedirectView.as_view(),
         name='url_redirect'),
]