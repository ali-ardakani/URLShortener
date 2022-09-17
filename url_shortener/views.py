from http.client import HTTPResponse
from string import ascii_letters, digits

from django.core.validators import URLValidator
from rest_framework import generics
from rest_framework.views import APIView
# Http404
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from . import serializers
from .models import Url
from .short_url_generator.generator import RandomGenerator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from django.core.cache import cache
from threading import Thread
from django.views.decorators.cache import cache_page


class WelcomeView(generics.GenericAPIView):
    """
    Welcome to the URL shortener API
    
    This API allows you to shorten URLs.
    
    For more information, please visit documentation at [here](/redoc/).

    """
    serializer_class = serializers.WelcomeSerializer

    def get(self, request):
        serializer = self.get_serializer(data={'message': 'Welcome to the URL shortener API'})
        serializer.is_valid()
        return Response(serializer.data)

@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_summary="Get a shortened URL",
    operation_id="url_shortener_get_short_url",
    request_body=serializers.UrlSerializer,
    responses={
        200: openapi.Response(
            description="Shortened URL",
            examples={
                'application/json': {
                    'url': 'https://www.google.com',
                    'short_url': 'random string',
                    'on_clicks': 0,
                    'created': '2020-05-17T19:01:41.000Z'
                }
            }
        ),
        400: openapi.Response(
            description="Bad request",
            examples={
                'application/json': {
                    'url': ['Enter a valid URL.']
                }
            }
        ),
    }
))
class UrlShortenerCreateView(generics.CreateAPIView):
    """
    A URL shortener reduces the number of characters in a URL, making it easier to read, remember, and share.
    
    Note
    ----
    The algorithm used to generate the shortened URL is seeded with the last URL's ID. This means that if the last URL's ID is 0, the algorithm will start from 0. If the last URL's ID is 1, the algorithm will start from 1. This is to ensure that the shortened URLs are unique.(The output of the algorithm is a string of characters chosen randomly from the set of characters in `ascii_letters + digits` and the length of the string is equal to the `max_length` of the `short_url` field in the `Url` model.)
    The use of seed was to prevent the replication of random generator loop. For example, if the loop method was used, it would be necessary to check our database for the existence of the generated string. This would be a costly operation. The use of seed ensures that the algorithm will not repeat itself.
    All the steps above are done in the database(you can see the SQL query in the `url_shortener/migrations/queries/sql_generator.text` file). This is to ensure that the database is not locked for a long time.
    """
    serializer_class = serializers.UrlSerializer

    def __init__(self):
        super().__init__()
        # Set the generator to be used
        last_url = Url.objects.last()
        seed = last_url.id if last_url else 0
        max_length = Url._meta.get_field('short_url').max_length
        self.generator = RandomGenerator(ascii_letters + digits, max_length,
                                         seed)

    def create(self, request, *args, **kwargs):
        # Check if the URL has already been shortened
        if Url.objects.filter(url=request.data['url']).exists():
            return Response({'error': 'URL already shortened'}, status=400)
        super().create(request, *args, **kwargs)
        response = Url.objects.filter(url=request.data['url']).values()[0]
        del response['id']
        cache.set(response['short_url'], {
            'url': response['url'],
            'on_clicks': response['on_clicks'],
            'created': response['created']})
        # Delete the cache urls
        if cache.has_key('/urls/'):
            cache.delete('/urls/')
        return Response(response, status=201)

    def post(self, request, *args, **kwargs):
        # Validate the URL
        validator = URLValidator()
        try:
            validator(request.data['url'])
        except:
            return Response({'error': 'Invalid URL'}, status=400)
        return super().post(request, *args, **kwargs)
        
@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Get list of URLs",
    operation_id="url_shortener_get_original_url",
    responses={
        200: openapi.Response(
            description="List of URLs",
            examples={
                'application/json': [
                    {
                        'url': 'https://www.google.com',
                        'short_url': 'random string',
                        'on_clicks': 0,
                        'created': '2020-05-17T19:01:41.000Z'
                    }
                ]
            }
        ),
    }
))
class UrlListView(generics.ListAPIView):
    """
    Get a list of all shortened URLs.
    
    Note
    ----
    The list is ordered by the number of times the shortened URL has been clicked.
    """
    # queryset with fields url, short_url, created
    queryset = Url.objects.all().values('url', 'short_url', 'created')
    serializer_class = serializers.UrlSerializerList
    
    def get(self, request):
        _cache = cache.get("/urls/")
        if _cache:
            return Response(_cache)
        response = super().get(request)

        cache.set("/urls/", response.data)
        return response
    
@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Get details of a shortened URL",
    operation_description="Returns the details of a shortened URL.",
    operation_id="url_shortener_get_delete_url",
    responses={
        200: openapi.Response(
            description="URL",
            examples={
                'application/json': {
                    'url': 'https://www.google.com',
                    'short_url': 'random string',
                    'on_clicks': 0,
                    'created': '2020-05-17T19:01:41.000Z'
                }
            }
        ),
        404: openapi.Response(
            description="Not found",
            examples={
                'application/json': {
                    'detail': 'URL not found'
                }
            }
        ),
    }
))
@method_decorator(name='delete', decorator=swagger_auto_schema(
    operation_summary="Delete a shortened URL",
    operation_description="Deletes a shortened URL.",
    operation_id="url_shortener_delete_url",
    responses={
        204: openapi.Response(
            description="URL deleted",
        ),
        404: openapi.Response(
            description="Not found",
            examples={
                'application/json': {
                    'detail': 'URL not found'
                }
            }
        ),
    }
))
class UrlDetailView(generics.RetrieveDestroyAPIView):
    """
    Get/Delete details of a shortened URL.
    
    get:
    Returns the details of a shortened URL.
    
    delete:
    Deletes a shortened URL.
    """
    queryset = Url.objects.all()
    serializer_class = serializers.UrlSerializerDetail
    
    def get_object(self):
        _cache = cache.get(self.kwargs['short_url'])
        if _cache:
            return _cache
        obj = Url.objects.filter(short_url=self.kwargs['short_url']).first()
        if obj:
            result = {
                'url': obj.url,
                'on_clicks': obj.on_clicks,
                'created': obj.created
            }
            cache.set(self.kwargs['short_url'], result)
            return obj
        else:
            raise NotFound(detail='URL not found', code=404)
        
    def delete(self, request, *args, **kwargs):
        if cache.has_key(self.kwargs['short_url']):
            cache.delete(self.kwargs['short_url'])
        Url.objects.filter(short_url=self.kwargs['short_url']).delete()
        return Response(status=204)

@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_summary="Redirect to original URL",
    operation_description="Redirects to the original URL.",
    operation_id="url_shortener_redirect",
    responses={
        200: None,
        302: openapi.Response(
            description="Redirect to original URL",
        ),
        404: openapi.Response(
            description="Not found",
            examples={
                'application/json': {
                    'detail': 'URL not found'
                }
            }
        ),
    }
))
class UrlRedirectView(APIView):
    """Redirect to the original URL"""
    
    def update_on_clicks(self, short_url):
        url = Url.objects.filter(short_url=short_url).first()
        if url:
            url.on_clicks += 1
            url.save()
            
    def get(self, request, short_url):
        _cache = cache.get(short_url)
        if _cache:
            url = _cache['url']
            _cache['on_clicks'] += 1
            cache.set(short_url, _cache)
            thread = Thread(target=self.update_on_clicks, args=(short_url,))
            thread.start()
        else:
            obj = Url.objects.filter(short_url=short_url).first()
            if obj:
                url = obj.url
                obj.on_clicks += 1
                obj.save()
                cache.set(short_url, {
                    'url': url,
                    'on_clicks': obj.on_clicks,
                    'created': obj.created
                })
            else:
                return Response({'error': 'URL not found'}, status=404)
        return HttpResponseRedirect(url)