from django.shortcuts import render

def login(request):
    return render(request,'core/login.html')
def signup(request):
    return render(request,'core/signup.html')
def profile(request):
    return render(request,'core/profile.html')
def page_not_found(request, exception):
    return render(request,'core/404.html', status=404)
def server_error(request):
    return render(request,'core/500.html', status=500)