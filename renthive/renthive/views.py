from django.shortcuts import render, redirect

def home(request):
    # You can customize this logic as needed
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    return render(request, 'base.html')
