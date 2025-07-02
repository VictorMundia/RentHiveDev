from django.urls import path  # Import the path function for defining URL patterns
from . import views  # Import views from the current package

app_name = 'properties'  # Set the application namespace for URL reversing

urlpatterns = [
    path('', views.property_list, name='property_list'),  # URL for listing all properties
    path('create/', views.property_create, name='property_create'),  # URL for creating a new property
    path('<int:pk>/', views.property_detail, name='property_detail'),  # URL for viewing details of a specific property
    path('<int:pk>/edit/', views.property_update, name='property_update'),  # URL for editing a specific property
    path('<int:pk>/delete/', views.property_delete, name='property_delete'),  # URL for deleting a specific property
    path('unit/<int:unit_id>/', views.unit_detail, name='unit_detail'),  # URL for viewing details of a specific unit
    path('unit/<int:unit_id>/invite/', views.invite_tenant, name='invite_tenant'),  # URL for inviting a tenant to a unit
    path('<int:pk>/invite/', views.invite_tenant_property, name='invite_tenant_property'),  # URL for inviting a tenant to a property
    path('<int:property_pk>/add_unit/', views.add_unit, name='add_unit'),  # URL for adding a unit to a property
]
