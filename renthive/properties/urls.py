from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('create/', views.property_create, name='property_create'),
    path('<int:pk>/', views.property_detail, name='property_detail'),
    path('<int:pk>/edit/', views.property_update, name='property_update'),
    path('<int:pk>/delete/', views.property_delete, name='property_delete'),
    path('unit/<int:unit_id>/', views.unit_detail, name='unit_detail'),
    path('unit/<int:unit_id>/invite/', views.invite_tenant, name='invite_tenant'),
    path('<int:pk>/invite/', views.invite_tenant_property, name='invite_tenant_property'),
    path('<int:property_pk>/add_unit/', views.add_unit, name='add_unit'),
]
