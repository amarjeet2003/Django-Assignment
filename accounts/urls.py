from django.urls import path, reverse_lazy
from django.views.generic import DeleteView, DetailView

from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from .models import Blog
from . import views

urlpatterns = [
    path("", views.login_success, name='login_success'),
    path("login_success/", views.login_success, name='login_success'),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="login.html"),name='login'),
    path("accounts/logout/", auth_views.LogoutView.as_view(),name='logout'),
    path('accounts/signup/', views.RegisterView.as_view(), name='signup'),
    path("doctor_dashboard", login_required(auth_views.TemplateView.as_view(template_name="doctor_dashboard.html")),name='doctor_dashboard'),
    path("patient_dashboard", login_required(auth_views.TemplateView.as_view(template_name="patient_dashboard.html")),name='patient_dashboard'),
    path("blogs/", login_required(views.BlogListView.as_view()), name='blogs'),
    path("blogs/<pk>/", login_required(views.BlogUpdateView.as_view()), name='blog_update'),
    path("delete/blogs/<pk>/", login_required(DeleteView.as_view(model=Blog, success_url= reverse_lazy('blogs'))), name='blog_delete'),
    path("blog_detail/<pk>/", login_required(DetailView.as_view(template_name='blog_detail.html',model=Blog)), name='blog_detail'),
]
