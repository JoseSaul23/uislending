from django.contrib import admin

from .models import User, Categoria, Idea, Inversion


admin.site.register(User)
admin.site.register(Categoria)
admin.site.register(Idea)
admin.site.register(Inversion)
