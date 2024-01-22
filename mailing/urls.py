from django.urls import path
from django.views.decorators.cache import cache_page
from mailing.views import *

from mailing.apps import MailingConfig

app_name = MailingConfig.name
urlpatterns = [
    path('', cache_page(60)(HomeListView.as_view()), name='index'),
    path('contacts/', cache_page(60)(ContactsPageView.as_view()), name='contacts'),
    path('client_create/', ClientCreateView.as_view(), name='client_create'),
    path('client_list/', ClientListView.as_view(), name='client_list'),
    path('client_update/<int:pk>/', ClientUpdateView.as_view(), name='client_update'),
    path('client_delete/<int:pk>/', ClientDeleteView.as_view(), name='client_delete'),
    path('mailing_create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailing_list/', MailingListView.as_view(), name='mailing_list'),
    path('mailing_update/<int:pk>/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailing_delete/<int:pk>/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('toggle/<int:pk>/', toggle_status, name='toggle_status'),
    path('message_create/', MessageCreateView.as_view(), name='message_create'),
    path('message_list/', MessageListView.as_view(), name='message_list'),
    path('message_update/<int:pk>/', MessageUpdateView.as_view(), name='message_update'),
    path('message_delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),
    path('log_list/', LogListView.as_view(), name='log_list'),
]
