from django.views.generic import *
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import *
from .forms import *
EventCategory.objects.all()  # Replace 'your_app' with your actual app name

# Event category list view
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import EventCategory

class EventCategoryListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = EventCategory
    template_name = 'events/event_category.html'
    context_object_name = 'event_categories'  # Updated for clarity

    def get_queryset(self):
        print("Current User:", self.request.user)  # Debug statement
        return EventCategory.objects.filter(created_user=self.request.user)


class EventCategoryCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = EventCategory
    fields = ['name', 'status']
    template_name = 'events/create_event_category.html'

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        form.instance.updated_user = self.request.user
        return super().form_valid(form)


class EventCategoryUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = EventCategory
    fields = ['name', 'code', 'status']
    template_name = 'events/edit_event_category.html'


class EventCategoryDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model =  EventCategory
    template_name = 'events/event_category_delete.html'
    success_url = reverse_lazy('event-category-list')



import qrcode
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from events.models import EventCategory

def generate_qr_code(request, category_id):
    category = get_object_or_404(EventCategory, id=category_id)
    
    # Generate the URL using the unique code
    url = request.build_absolute_uri(f'/join/{category.code}/')  # Use the code attribute for the link
    
    # Generate the QR code
    qr = qrcode.make(url)
    
    # Create an HttpResponse object and set the content type to image/png
    response = HttpResponse(content_type='image/png')
    qr.save(response, 'PNG')
    return response

from django.shortcuts import render, get_object_or_404
from events.models import EventCategory

def your_join_view(request, code):
    category = get_object_or_404(EventCategory, code=code)
    
    # Handle the logic for joining the category, e.g., adding a member, etc.
    # This is where you would implement your specific join logic.

    context = {'category': category}
    return render(request, 'join_category.html', context)  # Adjust the template as needed



@login_required(login_url='login')
def create_event(request):
    event_form = EventForm()
    event_image_form = EventImageForm()
    event_agenda_form = EventAgendaForm()
    catg = EventCategory.objects.all()
    if request.method == 'POST':
        event_form = EventForm(request.POST)
        event_image_form = EventImageForm(request.POST, request.FILES)
        event_agenda_form = EventAgendaForm(request.POST)
        if event_form.is_valid() and event_image_form.is_valid() and event_agenda_form.is_valid():
            ef = event_form.save()
            created_updated(Event, request)
            event_image_form.save(commit=False)
            event_image_form.event_form = ef
            event_image_form.save()
            
            event_agenda_form.save(commit=False)
            event_agenda_form.event_form = ef
            event_agenda_form.save()
            return redirect('event-list')
    context = {
        'form': event_form,
        'form_1': event_image_form,
        'form_2': event_agenda_form,
        'ctg': catg
    }
    return render(request, 'events/create.html', context)

class EventCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    form_class = EventCreateMultiForm
    template_name = 'events/create_event.html'
    success_url = reverse_lazy('event-list')

    def form_valid(self, form):
        evt = form['event'].save()
        event_image = form['event_image'].save(commit=False)
        event_image.event = evt
        event_image.save()

        event_agenda = form['event_agenda'].save(commit=False)
        event_agenda.event = evt
        event_agenda.save()

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['ctg'] = EventCategory.objects.all()
        return context


from django.views.generic import ListView
from .models import Event, EventCategoryUser

class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        user = self.request.user
        
        # Fetch categories that the user has joined
        joined_categories = EventCategoryUser.objects.filter(user=user).values_list('category_id', flat=True)

        # Fetch events that belong to the joined categories
        events = Event.objects.filter(category__id__in=joined_categories)

        return events




class EventUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Event
    fields = ['category', 'name', 'uid', 'description', 'venue', 'start_date', 'end_date', 'location', 'points', 'maximum_attende', 'status']
    template_name = 'events/edit_event.html'


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'


class EventDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Event
    template_name = 'events/delete_event.html'
    success_url = reverse_lazy('event-list')


class AddEventMemberCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = EventMember
    fields = ['event', 'user', 'email', 'college']
    template_name = 'events/add_event_member.html'

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        form.instance.updated_user = self.request.user
        return super().form_valid(form)


class JoinEventListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = EventMember
    template_name = 'events/joinevent_list.html'
    context_object_name = 'eventmember'


class RemoveEventMemberDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = EventMember
    template_name = 'events/remove_event_member.html'
    success_url = reverse_lazy('join-event-list')




class UpdateEventStatusView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Event
    fields = ['status']
    template_name = 'events/update_event_status.html'


class CompleteEventList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Event
    template_name = 'events/complete_event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(status='completed')




class CreateUserMark(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = UserCoin
    fields = ['user', 'event', 'status']
    template_name = 'events/create_user_mark.html'

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        form.instance.updated_user = self.request.user
        return super().form_valid(form)


class UserMarkList(ListView):
    # login_url = 'login'
    model = UserCoin
    template_name = 'events/user_mark_list.html'
    context_object_name = 'usermark'


@login_required(login_url='login')
def search_event_category(request):
    if request.method == 'POST':
       data = request.POST['search']
       event_category = EventCategory.objects.filter(name__icontains=data)
       context = {
           'event_category': event_category
       }
       return render(request, 'events/event_category.html', context)
    return render(request, 'events/event_category.html')


def search_event(request):
    if request.method == 'POST':
       data = request.POST['search']
       events = Event.objects.filter(name__icontains=data)
       context = {
           'events': events
       }
       return render(request, 'events/event_list.html', context)
    return render(request, 'events/event_list.html')


def event_catogery(request):
    return render(request, 'event_catogery.html')


def events_dashboard(request):
    return render(request, 'events_dashboard.html')



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import EventCategory, EventCategoryUser

@login_required
def join_event_category(request, code):
    # Get the category by its code
    category = get_object_or_404(EventCategory, code=code)
    
    # Check if the user has already joined
    if EventCategoryUser.objects.filter(user=request.user, category=category).exists():
        # Redirect if already joined or show a message
        return redirect('event-category-list')  # or some message that user is already part of this category

    # Create an EventCategoryUser to store the user and category
    EventCategoryUser.objects.create(user=request.user, category=category, approved=True)  # You can change approved to False for admin approval

    return redirect('event-category-list')  # Redirect after joining
