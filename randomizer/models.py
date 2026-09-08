from django.db import models
from django.db.models import JSONField


class Seed(models.Model):
    hash = models.CharField(max_length=1000, unique=True)
    seed = models.BigIntegerField()
    version = models.CharField(max_length=16)
    generated = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=16)
    debug_mode = models.BooleanField(default=False)
    flags = models.TextField(default="")
    file_select_char = models.CharField(max_length=100, default="")
    file_select_hash = models.CharField(max_length=100, default="")
    race_mode = models.BooleanField(default=False)
    spoiler = JSONField(default={})
    placement = models.TextField(default="", blank=True)


class SpriteRender(models.Model):
    """A cached SpriteCollection render for one seed and one PlayAsStarter value"""

    seed = models.ForeignKey(Seed, on_delete=models.CASCADE, related_name="sprite_renders")
    play_as_starter = models.BooleanField()
    blob = models.TextField()

    class Meta:
        unique_together = [
            ("seed", "play_as_starter"),
        ]


class Patch(models.Model):
    seed = models.ForeignKey(Seed, on_delete=models.CASCADE)
    region = models.CharField(max_length=8)
    sha1 = models.CharField(max_length=40)
    patch = models.TextField()

    class Meta:
        unique_together = [
            ("seed", "region"),
        ]
