from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase


class WelcomeTest(APITestCase):

    def test_welcome(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         {'message': 'Welcome to the URL shortener API'})


class UrlShortenerTest(APITestCase):

    def test_shorten_url(self):
        response = self.client.post('/url_shortener/',
                                    {'url': 'https://www.google.com/'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['url'], 'https://www.google.com/')
        self.assertEqual(len(response.data['short_url']), 6)
        # test cache
        self.assertEqual(
            cache.get(response.data['short_url'])["url"],
            'https://www.google.com/')

    def test_shorten_invalid_url(self):
        response = self.client.post('/url_shortener/', {'url': 'invalid_url'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Invalid URL'})

    def test_shorten_already_shortened_url(self):
        response = self.client.post('/url_shortener/',
                                    {'url': 'https://www.google.com/'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post('/url_shortener/',
                                    {'url': 'https://www.google.com/'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'URL already shortened'})

    def test_list_urls(self):
        response = self.client.get('/urls/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        self.client.post('/url_shortener/', {'url': 'https://www.google.com/'},
                         format='json')
        response = self.client.get('/urls/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['url'], 'https://www.google.com/')
        self.assertEqual(len(response.data[0]['short_url']), 6)
        # test cache
        self.assertEqual(cache.get('/urls/'), response.data)

    def test_info(self):
        response = self.client.post('/url_shortener/',
                                    {'url': 'https://www.google.com/'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        short_url = response.data['short_url']
        response = self.client.get(f'/info/{short_url}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['url'], 'https://www.google.com/')
        self.assertEqual(response.data['on_clicks'], 0)
        # test cache
        _cache = cache.get(short_url)
        self.assertEqual(_cache['url'], 'https://www.google.com/')
        self.assertEqual(_cache['on_clicks'], 0)

    def test_invalid_info(self):
        response = self.client.get('/info/invalid_url/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_url(self):
        response = self.client.post('/url_shortener/',
                                    {'url': 'https://www.google.com/'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        short_url = response.data['short_url']
        list_urls_cache = self.client.get('/urls/')
        response = self.client.delete(f'/info/{short_url}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(f'/info/{short_url}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # test cache
        self.assertEqual(cache.get(f'/info/{short_url}/'), None)
        self.assertEqual(cache.get(f'/urls/'), None)

    def test_redirect(self):
        response = self.client.post('/url_shortener/',
                                    {'url': 'https://www.google.com/'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        short_url = response.data['short_url']
        response = self.client.get(f'/url/{short_url}/')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, 'https://www.google.com/')
        response = self.client.get(f'/info/{short_url}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['url'], 'https://www.google.com/')
        self.assertEqual(response.data['on_clicks'], 1)
        # test cache
        _cache = cache.get(short_url)
        self.assertEqual(_cache['url'], 'https://www.google.com/')
        self.assertEqual(_cache['on_clicks'], 1)

    def test_invalid_url(self):
        response = self.client.get('/url/invalid_url/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
