from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterForm(forms.ModelForm):
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.set_password(self.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user, role=self.cleaned_data['role'])
        return user

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role:
            raise forms.ValidationError("Please select a role.")
        return role
