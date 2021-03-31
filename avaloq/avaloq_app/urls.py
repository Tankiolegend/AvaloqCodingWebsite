from django.urls import path
from avaloq_app import views
from django.conf.urls import url

app_name = 'avaloq'

urlpatterns = [
    path('candidate-home/<u_id>', views.home, name='home'),
    path('code/<u_id>/<q_num>', views.get_code, name='get_code'),
    path('review/',views.review,name='review'),
    path('add-candidate/',views.add_candidate,name='add-candidate'),
    path('delete_candidate/', views.DeleteCandidateView.as_view(), name='delete_candidate'),
    path('code-review/<u_id>', views.code_review, name='code_review'),
    path('completion', views.completion, name='completion'),
    path('expired', views.expired, name='expired'),
    url(r'^create-staff/$', views.create_staff, name='create_staff'),
]
