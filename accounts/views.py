from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import User, Blog
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.shortcuts import render




class RegisterView(TemplateView):
    template_name = "signup.html"

    def post(self, request):
        if request.POST.get("password1") != request.POST.get("password2"):
            return render(request, self.template_name, context={"error": "Passwords don't match"})
        if User.objects.filter(email=request.POST.get("email")).exists():
            return render(request, self.template_name, context={"error": "Account already exists with this email"})
        new_user = User.objects.create(
                                    first_name=request.POST.get('first_name'),
                                    last_name=request.POST.get('last_name'),
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
    

class BookAppointmentView(ListView):
    model = User
    template_name = "book_appointment.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user_type="doctor")
        
        return queryset
    

class AppointmentDetailsView(DetailView):
    model = User
    template_name = "appointment_details.html"

 
    def post(self, request, pk):
        # Retrieve the form data
        speciality = request.POST.get('speciality')
        date_of_appointment = request.POST.get('date_of_appointment')
        starting_time = request.POST.get('starting_time')

        # Calculate the end time of the appointment
        start_datetime = datetime.datetime.strptime(date_of_appointment + starting_time, '%Y-%m-%d%H:%M')
        end_datetime = start_datetime + datetime.timedelta(minutes=45)
        end_time = end_datetime.strftime('%I:%M %p')

        # Create the calendar event
        service_account_file = 'credentials.json'
        scopes = ['https://www.googleapis.com/auth/calendar']
        credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
        service = build('calendar', 'v3', credentials=credentials)

        event = {
        'summary': 'Appointment for ' + speciality,
        'description': 'Appointment Schedule',
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        }

        try:
            event = service.events().insert(calendarId='200390amarjeet@gmail.com', body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))
        except HttpError as error:
            print('An error occurred: %s' % error)

        user_instance = User.objects.get(pk=pk)
        appointment_details = {
            'doctor_name': user_instance.get_full_name(),  # Replace with the actual doctor's name
            'appointment_date': date_of_appointment,
            'start_time': starting_time,
            'end_time': end_time,
        }

        return render(request, 'confirmation.html', {'appointment_details': appointment_details})
