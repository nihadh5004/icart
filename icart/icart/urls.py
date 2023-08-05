"""
URL configuration for icart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


def custom_page_not_found_view(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_server_error_view(request):
    return render(request, 'errors/500.html', status=500)

handler404 = custom_page_not_found_view
handler500 = custom_server_error_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls') ),
    path('', include('productside.urls')),
    path('', include('cartside.urls')),
    path('', include('userside.urls')),
    path('', include('adminside.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
