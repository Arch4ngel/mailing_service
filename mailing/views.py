from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, View, UpdateView, ListView, DeleteView

from blog.models import Post
from mailing.forms import ClientForm, MailingForm, MessageForm
from mailing.models import Client, Mailing, Message, Log
from mailing.services import MessageService


class HomeListView(ListView):
    model = Post
    template_name = 'mailing/index.html'

    def get_queryset(self):
        return Post.objects.all()[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailings = Mailing.objects.all()
        active_mailings = Mailing.objects.filter(status='start')
        client = Client.objects.all()
        context['title'] = 'Главная страница'
        context['count'] = mailings.count()
        context['client'] = client.distinct().count()
        context['active_mailings'] = active_mailings.count()
        return context


class ContactsPageView(View):
    def get(self, request):
        context = {'title': 'Контакты'}
        return render(request, 'mailing/contacts.html', context)

    def post(self, request):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        print(f'{name} ({phone}): {message}')
        context = {'title': 'Контакты'}
        return render(request, 'mailing/contacts.html', context)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = Client.objects.all()
        else:
            queryset = Client.objects.filter(user=user)

        return queryset


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailing:client_list')


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('mailing:client_list')
    permission_denied_message = 'mailing.delete_client'


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):

        self.object = form.save()
        self.object.user = self.request.user
        self.object.status = 'create'
        message_service = MessageService(self.object)
        message_service.create_task()
        message_service.send_mailing()
        self.object.status = 'start'
        self.object.save()

        return super().form_valid(form)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    extra_context = {'title': 'Рассылки'}

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = Mailing.objects.all()
        else:
            queryset = Mailing.objects.filter(user=user)

        return queryset


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mailing:mailing_list')


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        self.object = self.get_object()
        message_service = MessageService(self.object)
        message_service.delete_task()
        return super().form_valid(form)



def toggle_status(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    message_service = MessageService(mailing)
    if mailing.status == 'start' or mailing.status == 'created':
        message_service.delete_task()
        mailing.status = 'finish'
    else:
        message_service.create_task()
        mailing.status = 'start'

    mailing.save()

    return redirect(reverse('mailing:mailing_list'))


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    extra_context = {'title': 'Сообщения'}

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = Message.objects.all()
        else:
            queryset = Message.objects.filter(user=user)

        return queryset


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('mailing:message_list')


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy('mailing:message_list')


class LogListView(LoginRequiredMixin, ListView):
    model = Log

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "История рассылок"
        context['log_list'] = Log.objects.all()
        return context
