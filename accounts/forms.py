from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        email = self.data.get('username', '')
        return email.strip().lower()


class RegisterForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Minimum 8 characters.'
    )
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    medical_license = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        # Keep username so the ModelForm is tied to User, but we'll make it NOT required.
        fields = ['username']
        widgets = {'username': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # <<< CRUCIAL: don't require username from the browser
        self.fields['username'].required = False

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email already registered.')
        return email

    def clean_password(self):
        pw = self.cleaned_data.get('password') or ''
        if len(pw) < 8:
            raise forms.ValidationError('Password must be at least 8 characters.')
        return pw

    def clean(self):
        """
        Inject username=email *during validation* so the required check doesn't fire.
        """
        cleaned = super().clean()
        email = (cleaned.get('email') or '').strip().lower()
        # Set username to email so the model requirement is satisfied
        cleaned['username'] = email
        return cleaned

    def save(self, commit=True):
        email = self.cleaned_data['email']  # already normalized
        user = User(username=email, email=email)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Update the profile created by the signal instead of creating a new one
            profile = user.profile
            profile.full_name = self.cleaned_data['full_name']
            profile.phone = self.cleaned_data['phone']
            profile.address = self.cleaned_data['address']
            profile.medical_license = self.cleaned_data['medical_license']
            profile.save()
        return user
from django import forms
from .models import Profile

ALLOWED_DOC_EXTS = {'.pdf', '.jpg', '.jpeg', '.png'}

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'phone', 'address', 'gov_id_type', 'gov_id_file']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gov_id_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Aadhaar, PAN, Drug License'}),
            # gov_id_file uses default ClearableFileInput
        }

    def clean_gov_id_file(self):
        f = self.cleaned_data.get('gov_id_file')
        if not f:
            return f
        name = (f.name or '').lower()
        if not any(name.endswith(ext) for ext in ALLOWED_DOC_EXTS):
            raise forms.ValidationError("Allowed file types: PDF, JPG, JPEG, PNG.")
        if f.size > 8 * 1024 * 1024:  # 8 MB
            raise forms.ValidationError("File too large (max 8 MB).")
        return f

class AddEmployeeForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Minimum 8 characters.'
    )

    class Meta:
        model = User
        fields = ['username']
        widgets = {'username': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email already registered.')
        return email

    def clean_password(self):
        pw = self.cleaned_data.get('password') or ''
        if len(pw) < 8:
            raise forms.ValidationError('Password must be at least 8 characters.')
        return pw

    def clean(self):
        cleaned = super().clean()
        email = (cleaned.get('email') or '').strip().lower()
        cleaned['username'] = email
        return cleaned

    def save(self, commit=True, employer=None):
        email = self.cleaned_data['email']
        user = User(username=email, email=email)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            profile = user.profile
            profile.full_name = self.cleaned_data['full_name']
            profile.role = 'EMPLOYEE'
            profile.employer = employer
            profile.save()
        return user
