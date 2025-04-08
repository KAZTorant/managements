# printers/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _


class Printer(models.Model):
    name = models.CharField(_('Printer Name'), max_length=100)
    ip_address = models.GenericIPAddressField(_('IP Address'))
    port = models.IntegerField(_('Port'), default=9100)
    description = models.TextField(
        _('Description'),
        blank=True,
        help_text=_('Additional details about the printer')
    )
    is_main = models.BooleanField(
        _('Is Main'),
        default=False,
        help_text=_('Check if this is the main printer')
    )

    class Meta:
        verbose_name = _('Printer')
        verbose_name_plural = _('Printers')

    def __str__(self):
        return f"{self.name} ({self.ip_address})"
