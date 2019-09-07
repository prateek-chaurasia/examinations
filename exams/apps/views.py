# Create your views here.
from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('teachers:test_change_list')
        else:
            return redirect('students:test_list')
    return render(request, 'home.html')
