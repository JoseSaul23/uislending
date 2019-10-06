from rest_framework import routers
from apps.inversion import views as myapp_views

router = routers.DefaultRouter()
router.register(r'usuarios', myapp_views.UserView)
router.register(r'categorias', myapp_views.CategoriaView)
router.register(r'ideas', myapp_views.IdeaView)
router.register(r'inversiones', myapp_views.InversionView)
