import uuid

from django.db import models
from django.urls import reverse


class Seed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hash = models.CharField(max_length=1000, unique=True)
    seed = models.BigIntegerField()
    version = models.CharField(max_length=16)
    generated = models.DateTimeField(auto_now_add=True)
    debug_mode = models.BooleanField(default=False)
    flags = models.TextField(default="")
    file_select_char = models.CharField(max_length=100, default="")
    file_select_hash = models.CharField(max_length=100, default="")
    race_mode = models.BooleanField(default=False)
    spoiler = models.JSONField(default=dict)
    placement = models.BinaryField(null=True, blank=True)

    @property
    def permalink(self) -> str:
        return reverse("randomizer:patch-from-hash", kwargs={"hash": self.hash})


class SpriteRender(models.Model):
    """A cached SpriteCollection render for one seed and one PlayAsStarter value"""

    seed = models.ForeignKey(Seed, on_delete=models.CASCADE, related_name="sprite_renders")
    play_as_starter = models.BooleanField()
    blob = models.BinaryField()

    class Meta:
        unique_together = [
            ("seed", "play_as_starter"),
        ]


class Patch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seed = models.ForeignKey(Seed, on_delete=models.CASCADE)
    hash = models.CharField(max_length=1000)
    patch = models.BinaryField(null=True, blank=True)
    generated = models.DateTimeField(auto_now_add=True)

    @property
    def permalink(self) -> str:
        return self.seed.permalink
