from django.contrib import admin
from django.utils.html import format_html
from django.conf.urls import include, url
from django.template.response import TemplateResponse
from .api.models import City
from django.db.models import Q


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = ["city_slug", "city_name", "country_code"]
    list_display = ["city_slug", "city_name", "country_code"]
    list_filter = ["city_name", "country_code"]
