from django.contrib import admin
from django.urls import path, include
from avaloq_app import views

urlpatterns = [
    path('', views.review, name='review'),
    path('avaloq/', include('avaloq_app.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('registration.backends.default.urls')),
]
handler404 = 'avaloq_app.views.page_not_found'
handler500='avaloq_app.views.server_error'
handler400='avaloq_app.views.bad_request'
handler403='avaloq_app.views.permission_denied'
