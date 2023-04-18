from django.urls import path

from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("accounts/base/", auth_views.TemplateView.as_view(template_name="base.html")),
    path('accounts/signup/', views.RegisterView.as_view(), name='signup'),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="login.html"),name='login'),
    path("login_success/", views.login_success, name='login_success'),
    path("doctor_dashboard", auth_views.TemplateView.as_view(template_name="doctor_dashboard.html"),name='doctor_dashboard'),
    path("patient_dashboard", auth_views.TemplateView.as_view(template_name="patient_dashboard.html"),name='patient_dashboard'),
]
