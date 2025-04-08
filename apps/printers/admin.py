# printers/admin.py

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django import forms

from apps.printers.models import Printer
from apps.printers.utils.printer_discovery import scan_printers_with_names


class PrinterForm(forms.ModelForm):
    class Meta:
        model = Printer
        fields = '__all__'


class PrinterAdmin(admin.ModelAdmin):
    form = PrinterForm

    class Media:
        # The JavaScript file path should be relative to your static files directory
        js = ('admin/js/printer_scan.js',)

    def get_urls(self):

        custom_urls = [
            path(
                'scan-printers/',
                self.admin_site.admin_view(self.scan_printers_view),
                name='scan_printers'
            ),
        ]
        return custom_urls + super().get_urls()  # 👈 custom URLs əvvəl gəlməlidir!


    def scan_printers_view(self, request):
        """
        AJAX view that scans for available printers on the local network.
        Returns a JSON list of printers with their IP addresses and (dummy) names.
        """
        # Returns a list of dicts like [{'ip': '192.168.1.10', 'name': 'POS Printer'}, ...]
        printers = scan_printers_with_names()
        return JsonResponse(printers, safe=False)


admin.site.register(Printer, PrinterAdmin)
