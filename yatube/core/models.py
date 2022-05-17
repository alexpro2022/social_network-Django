from django.db import models


class CreatedFieldModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True
        ordering = ('-created',)
        verbose_name = 'Дата создания'
        verbose_name_plural = 'Даты создания'
