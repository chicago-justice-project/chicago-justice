from cjp.settings.base import CJP_ROOT      # TODO: don't rely on this
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth.models import User
from django import forms

class UserForm(forms.Form):
    firstName = forms.CharField(label="First Name", required=False, max_length=30)
    lastName = forms.CharField(label="Last Name", required=False, max_length=30)
    email = forms.EmailField(label="Email", required=False, max_length=75)

    def clean(self):
        cleanedData = self.cleaned_data
        password = cleanedData.get("password")
        password2 = cleanedData.get("password2")

        if ((password and not password2) or
            (not password and password2) or
            (password and password2 and password != password2)):

            msg = u"passwords do not match."
            self._errors["password"] = self.error_class([msg])

            del cleanedData["password"]
            del cleanedData["password2"]

        return cleanedData

class AddUserForm(UserForm):
    username = forms.CharField(label="Username", required=True, max_length=30)
    password = forms.CharField(widget=forms.PasswordInput, label="Password", required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Repeat Password", required=True)

class UpdateUserForm(UserForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password", required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Repeat Password", required=False)
    inactive = forms.BooleanField(label="Inactive User", required=False)

def manage(request, action = None):
    if not (request.user.is_authenticated and request.user.is_superuser):
        return redirect(CJP_ROOT)

    addUserForm = AddUserForm()

    if action == 'addUser' and request.POST:
        addUserForm = AddUserForm(request.POST)
        if addUserForm.is_valid():
            cleanedData = addUserForm.cleaned_data
            user = User(
                username = cleanedData.get('username').strip(),
                first_name = cleanedData.get('firstName').strip(),
                last_name = cleanedData.get('lastName').strip(),
                email = cleanedData.get('email').strip(),
                is_staff = False,
                is_active = True,
                is_superuser = False,
            )
            user.set_password(cleanedData.get('password'))
            user.save()
            addUserForm = AddUserForm()

    users = User.objects.all().order_by('username')

    data = {'users' : users,
            'userCreationForm': addUserForm}
    return render(request, 'registration/users.html', data)


def userUpdate(request, userId):
    if not (request.user.is_authenticated and request.user.is_superuser):
        return redirect(CJP_ROOT)

    updateSuccess = False
    try:
        managedUser = User.objects.get(pk=userId)
        if request.POST:
            userForm = UpdateUserForm(request.POST)
            if userForm.is_valid() and (managedUser.username == request.POST.get('username')):
                cleanedData = userForm.cleaned_data
                password = cleanedData.get('password')
                if len(password) > 0:
                    managedUser.set_password(password)
                managedUser.first_name = cleanedData.get('firstName').strip()
                managedUser.last_name = cleanedData.get('lastName').strip()
                managedUser.email = cleanedData.get('email').strip()
                managedUser.is_active = not cleanedData.get('inactive')

                if not managedUser.is_active:
                    managedUser.password = 'PaSsWoRdIsDiSaBlEd  '

                managedUser.save()
                updateSuccess = True

                userForm = UpdateUserForm({
                    'firstName' : managedUser.first_name,
                    'lastName' : managedUser.last_name,
                    'email' : managedUser.email,
                    'inactive' : not managedUser.is_active
                })
        else:
            userForm = UpdateUserForm({
                'firstName' : managedUser.first_name,
                'lastName' : managedUser.last_name,
                'email' : managedUser.email,
                'inactive' : not managedUser.is_active
            })
    except Exception as e:
        managedUser = None

    data = {'managedUser' : managedUser,
            'userForm': userForm,
            'updateSuccess': updateSuccess}

    return render(request, 'registration/userUpdate.html', data)
