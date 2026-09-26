"""Forms for DRERS."""

import re

from django import forms
from django.contrib.auth.models import User

from .models import DisasterReport, Profile, Role, Status


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username, Email or Phone Number")
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    """Public registration. Always creates a CITIZEN account."""

    full_name = forms.CharField(max_length=120)
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=15, required=False)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_full_name(self):
        name = self.cleaned_data["full_name"].strip()
        if len(name) < 3:
            raise forms.ValidationError("Please enter your full name.")
        return name

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not re.fullmatch(r"[A-Za-z0-9_.]{3,30}", username):
            raise forms.ValidationError(
                "Username must be 3–30 characters (letters, numbers, _ or . only).")     
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("That username is already taken. Please choose another.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get("email","").strip().lower()

        if not email:
            return email
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

#when phone is empty return nothing 
    def clean_phone(self):
        phone = self.cleaned_data.get("phone","").strip()
        if not phone:
            return phone
        if not re.fullmatch(r"9\d{9}",phone):
            raise forms.ValidationError("Enter a valid 10-digit Nepali mobile number.")
        if Profile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("An account with phone number already exists.")
        return phone

    def clean_password(self):
        password = self.cleaned_data["password"]
        
        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")
        return password
    
    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")

        #User must provide exactly one 
        if not email and not phone:
            raise forms.ValidationError("Please provide either an email adddress or a phone number.")
        
        if email and phone:
            raise forms.ValidationError("Please either Email OR Phone Number, both.")

    def save(self):
        """Create the User + Profile. Role is hard-coded to Citizen."""
        data = self.cleaned_data
        first, _, last = data["full_name"].partition(" ")

        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            first_name=first,
            last_name=last,
        )
        
        # The post_save signal already made a Profile; just fill it in.
        profile = user.profile
        profile.phone = data.get("phone") or ""
        profile.role = Role.CITIZEN          # <- never taken from the browser
        profile.save()
        return user


class ReportForm(forms.ModelForm):
    """Citizens use this to submit a new incident."""

    class Meta:
        model = DisasterReport
        fields = ["disaster_type", "title", "description", "location", "severity", "photo"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "title": forms.TextInput(attrs={"placeholder": "Short summary of the incident"}),
            "location": forms.TextInput(attrs={"placeholder": "Ward / area, district"}),
        }


class StatusUpdateForm(forms.Form):
    """Responders / admins use this to progress a report."""

    new_status = forms.ChoiceField(choices=Status.choices)
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)


class AssignForm(forms.Form):
    """Admin assigns a responder to a report."""

    responder = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role=Role.RESPONDER),
        empty_label="— select a responder —",
    )
