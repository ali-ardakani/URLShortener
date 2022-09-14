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
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(short_url=self.generator.generate())

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
    
    queryset = Url.objects.all().order_by('-on_clicks')
    serializer_class = serializers.UrlSerializer
    
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
    serializer_class = serializers.UrlSerializer
    
    def get_object(self):
        url = Url.objects.filter(short_url=self.kwargs['short_url']).first()
        if url:
            return url
        else:
            raise NotFound(detail='URL not found', code=404)

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
    def get(self, request, short_url):
        url = Url.objects.filter(short_url=short_url).first()
        if url:
            url.on_clicks += 1
            url.save()
            return HttpResponseRedirect(url.url)
        return Response({'error': 'URL not found'}, status=404)
