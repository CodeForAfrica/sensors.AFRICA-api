"""sensorsafrica URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# from django.conf.urls import include, url "django.conf.urls.url() was deprecated in Django 3.0, and is removed in Django 4.0+."
from django.urls import re_path as url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView
from feinstaub.sensors.views import AddSensordeviceView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.documentation import include_docs_urls

from .api.v1.router import api_urls as sensors_api_v1
from .api.v2.router import api_urls as sensors_api_v2

urlpatterns = [
    url(r"^$", RedirectView.as_view(url="/docs/", permanent=False)),
    url(r"^admin/", admin.site.urls),
    url(r"^v1/", include(sensors_api_v1)),
    url(r"^v2/", include(sensors_api_v2)),
    url(r"^get-auth-token/", obtain_auth_token),
    url(r"^auth/", include("rest_framework.urls", namespace="rest_framework")),
    url(r"^docs/", include_docs_urls(title="sensors.Africa API")),
    url(r"^adddevice/", AddSensordeviceView.as_view(), name="adddevice"),
] + staticfiles_urlpatterns()
