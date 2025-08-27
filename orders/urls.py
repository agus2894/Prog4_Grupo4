from django.conf.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
	url(r'^create/$', views.order_create, name='order_create')
]
