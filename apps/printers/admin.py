# printers/admin.py

from django import forms
from django.contrib import admin, messages
from django.http import JsonResponse
from django.urls import path

from apps.printers.models import Printer
from apps.printers.utils.print_test_page import send_test_page
from apps.printers.utils.printer_discovery import discover_all_printers


class PrinterForm(forms.ModelForm):
    class Meta:
        model = Printer
        fields = '__all__'


class PrinterAdmin(admin.ModelAdmin):
    form = PrinterForm
    actions = ["send_test_page_action"]
    class Media:
        # The JavaScript file path should be relative to your static files directory
        js = ('admin/js/printer_scan.js',)

    def send_test_page_action(self, request, queryset):
        for printer in queryset:
            success, msg = send_test_page(printer.name)
            if success:
                self.message_user(request, msg, level=messages.SUCCESS)
            else:
                self.message_user(request, f"Failed to send test page to {printer.name}: {msg}", level=messages.ERROR)

    send_test_page_action.short_description = "Send test page to selected printers"

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
        printers = discover_all_printers()
        return JsonResponse(printers, safe=False)


admin.site.register(Printer, PrinterAdmin)
