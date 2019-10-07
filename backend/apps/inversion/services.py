from . import models

def getUsuarios(**filtro):
    return models.User.objects.all().filter(**filtro)

def getCategorias(**filtro):
    return models.Categoria.objects.all().filter(**filtro)

def getIdeas(**filtro):
    return models.Idea.objects.all().filter(**filtro)

def getInversiones(**filtro):
    return models.Inversion.objects.all().filter(**filtro)