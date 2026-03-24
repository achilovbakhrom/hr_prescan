import uuid

from django.db import models


class BaseModel(models.Model):
    """Abstract base model with UUID primary key and timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Country(models.Model):
    """ISO 3166-1 alpha-2 country reference data."""

    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

    def __str__(self) -> str:
        return self.name


class Industry(models.Model):
    """Industry / sector reference data."""

    slug = models.SlugField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "industries"

    def __str__(self) -> str:
        return self.name
