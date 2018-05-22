from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get_branch_details/$', views.branch_details, name='get_branch_details')
]
