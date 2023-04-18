from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

from .models import User


class RegisterView(TemplateView):
    template_name = "signup.html"

    def post(self, request):
        if request.POST.get("password1") != request.POST.get("password2"):
            return render(request, self.template_name, context={"error": "Passwords don't match"})
        if User.objects.filter(email=request.POST.get("email")).exists():
            return render(request, self.template_name, context={"error": "Account already exists with this email"})
        # if User.objects.filter(username=request.POST.get("username")).exists():
        #     return render(request, self.template_name, context={"error": "Account already exists with this username"})
        new_user = User.objects.create(
                                    first_name=request.POST.get('first_name'),
                                    last_name=request.POST.get('last_name'),
                                    # username=request.POST.get('username'),
                                    email=request.POST.get("email"), 
                                    profile_picture=request.FILES.get("profile_picture"), 
                                    address_line1=request.POST.get("address_line1"),
                                    city=request.POST.get("city"),
                                    state=request.POST.get("state"),
                                    pincode=request.POST.get("pincode"),
                                    user_type=request.POST.get("user_type"))
                                    
        new_user.set_password(request.POST.get("password1"))
        new_user.save()
        return HttpResponseRedirect('/accounts/login')
    
def login_success(request):
    if request.user.user_type == 'patient':
        return HttpResponseRedirect('/patient_dashboard')
    
    if request.user.user_type == 'doctor':
        return HttpResponseRedirect('/doctor_dashboard')
