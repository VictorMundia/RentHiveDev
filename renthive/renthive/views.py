# Import the render function from Django's shortcuts module
from django.shortcuts import render

# Define a view function named 'home' that takes an HTTP request as a parameter
def home(request):
    # Render and return the 'landing.html' template as an HTTP response
    return render(request, 'landing.html')
