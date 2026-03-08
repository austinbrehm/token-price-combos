from django.urls import path
from . import views

urlpatterns = [
    path('', views.token_list, name='tokens'),  # Assuming this is your tokens page
]