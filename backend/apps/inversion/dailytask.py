from .models import Idea
from datetime import date

def revisarSiFallida():
    ideas = Idea.publicas.all()
    for idea in ideas:
        if idea.fecha_limite < date.today():
            idea.estado = 'F'
            idea.save()

  