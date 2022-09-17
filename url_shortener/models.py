from django.db import models


class Url(models.Model):
    url = models.URLField(max_length=1000)
    short_url = models.CharField(max_length=6, unique=True, null=True)
    on_clicks = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url

    class Meta:
        ordering = ('on_clicks', )
