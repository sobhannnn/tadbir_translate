from django.apps import apps
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'melli_code', 'code', 'phone_number', 'age', 'roles', 'first_name',
                  'last_name')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'melli_code', 'code', 'phone_number', 'age', 'roles', 'first_name',
                  'last_name')


class CustomUserAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('melli_code', 'code', 'phone_number', 'age', 'roles')}),
    )
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('melli_code', 'code', 'phone_number', 'age', 'roles')}),
    )
    model = User
    list_display = ['id', 'username', 'melli_code', 'first_name', 'last_name']


admin.site.register(CostCategory, MPTTModelAdmin)
admin.site.register(User, CustomUserAdmin)
models = apps.get_models()

for model in models:
    if model == User:
        continue
    try:
        admin.site.register(model)
    except:
        continue
