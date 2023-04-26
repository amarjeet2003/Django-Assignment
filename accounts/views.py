from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import User, Blog


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
        return HttpResponseRedirect(reverse('login'))
    
    
def login_success(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'patient':
            return redirect("patient_dashboard")
        if request.user.user_type == 'doctor':
            return redirect('doctor_dashboard')
    else:
        return redirect('login')
    
    

class BlogListView(CreateView, ListView):
    template_name = 'blog_list.html'
    model = Blog
    
    fields = ['title','image','category','summary','content']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if len(self.request.GET.get("category", "")) > 0:
            print(1, self.request.GET.get("category"))
            context['object_list'] = context["object_list"].filter(category=self.request.GET.get("category"))
        if self.request.GET.get("created_by_me", "") == "on":
            print(2, self.request.user)
            context['object_list'] = context["object_list"].filter(created_by=self.request.user)
        if self.request.user.user_type == "patient":
            context['object_list'] = context["object_list"].filter(is_draft=False)
        return context

    def post(self, request):
        is_draft = True if request.POST.get("is_draft")=='True' else False
        blog_instance = Blog.objects.create(title=request.POST.get("title"), image=request.FILES.get("image"), category=request.POST.get("category"), summary=request.POST.get("summary"), content=request.POST.get("content"), is_draft = is_draft, created_by=request.user)
        # return HttpResponseRedirect('/blogs')
        return HttpResponseRedirect(reverse('blogs'))
    

class BlogUpdateView(UpdateView):
    template_name = "blog_update.html"
    model = Blog

    fields = ['title','image','category','summary','content']

    def post(self, request, pk):
        is_draft = True if request.POST.get("is_draft")=='True' else False
        blog_instance = Blog.objects.get(pk=pk)
        blog_instance.title=request.POST.get("title")
        blog_instance.image=request.FILES.get("image")
        blog_instance.category=request.POST.get("category")
        blog_instance.summary=request.POST.get("summary")
        blog_instance.content=request.POST.get("content")
        blog_instance.is_draft = is_draft
        blog_instance.created_by=request.user
        blog_instance.save()

        return HttpResponseRedirect(reverse('blogs'))
