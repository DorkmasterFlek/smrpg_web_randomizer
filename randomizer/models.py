from django.db import models
from jsonfield import JSONField

MODES = (
    ('standard', 'Standard'),
    ('open', 'Open'),
)

REGIONS = (
    ('US', 'US'),
    # ('JP', 'Japan'),
    ('EU', 'PAL'),
)


class Seed(models.Model):
    hash = models.CharField(max_length=10, unique=True)
    seed = models.BigIntegerField()
    version = models.CharField(max_length=16)
    generated = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=16, choices=MODES)
    debug_mode = models.BooleanField(default=False)
    flags = JSONField()
    file_select_char = models.CharField(max_length=100, default='')
    file_select_hash = models.CharField(max_length=100, default='')


class Patch(models.Model):
    seed = models.ForeignKey(Seed, on_delete=models.CASCADE)
    region = models.CharField(max_length=8, choices=REGIONS)
    sha1 = models.CharField(max_length=40)
    patch = models.TextField()

    class Meta:
        unique_together = [
            ('seed', 'region'),
        ]
