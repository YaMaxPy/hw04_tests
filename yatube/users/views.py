from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import (ChangePasswordForm, CreationForm, PasswordSetForm,
                    ResetPasswordForm)


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChangeView(CreateView):
    form_class = ChangePasswordForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_done.html'


class PasswordResetView(CreateView):
    form_class = ResetPasswordForm
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_done.html'


class SetPasswordView(CreateView):
    form_class = PasswordSetForm
    success_url = reverse_lazy('users:password_reset_complete')
    template_name = 'users/password_reset_complete.html'
