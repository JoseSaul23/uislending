from rest_framework import routers
from apps.inversion import views as myapp_views
from djoser import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, base_name='usuarios')
router.register(r'notificaciones', myapp_views.NotificacionView, base_name='notificaciones')
router.register(r'categorias', myapp_views.CategoriaView, base_name='categorias')
router.register(r'ideas', myapp_views.IdeaView, base_name='ideas')
router.register(r'inversiones', myapp_views.InversionView, base_name='inversiones')
