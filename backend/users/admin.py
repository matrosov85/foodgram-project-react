from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User, Subscribe


admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'date_joined', 'last_login', 'is_active',
    )
    list_display_links = ('username',)
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')

    class Meta:
        verbose_name = 'Пользователи'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')

    class Meta:
        verbose_name = 'Подписки'
