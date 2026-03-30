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
    name_ru = models.CharField(max_length=100, blank=True, default="")
    name_uz = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

    def __str__(self) -> str:
        return self.name


class Industry(models.Model):
    """Industry / sector reference data."""

    slug = models.SlugField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100, blank=True, default="")
    name_uz = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "industries"

    def __str__(self) -> str:
        return self.name


class Skill(models.Model):
    """Skill reference data for CV builder and job matching."""

    slug = models.SlugField(max_length=100, primary_key=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        ordering = ["category", "name"]

    def __str__(self) -> str:
        return self.name


class Language(models.Model):
    """Language reference data (ISO 639-1)."""

    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class EducationLevel(models.Model):
    """Education level reference data."""

    slug = models.SlugField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return self.name
