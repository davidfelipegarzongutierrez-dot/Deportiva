from django.urls import path
from .views import registro, password_reset_demo

urlpatterns = [

    path(
        'registro/',
        registro,
        name='registro'
    ),

    path(
        'password-reset-demo/',
        password_reset_demo,
        name='password_reset_demo'
    ),
]