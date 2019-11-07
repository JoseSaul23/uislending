from rest_framework.serializers import ValidationError
from datetime import date

def validarEstadoIdea(inversion):
    if (inversion.idea.estado != "P"):
        raise ValidationError(
            "No se puede invertir en una idea no publicada."
        )

def validarUsuarioInversor(inversion):
    if (inversion.usuario == inversion.idea.usuario):
        raise ValidationError(
            "No puede invertir en su propia idea."
        )

def validarMontoInvertido(inversion): #enviar solo el monto y buscar el usuario(saldo) y la idea(monto objetivo y monto actual)
    if inversion.monto_invertido > inversion.usuario.saldo:
        raise ValidationError("No tiene saldo suficiente")
    if inversion.monto_invertido > inversion.idea.monto_objetivo - inversion.idea.monto_actual:
        raise ValidationError(
            "La inversión no puede ser mayor a lo que falta para el objetivo."
        )

def validarFechas(idea): #enviar solo fecha inicial y fecha final
    if idea.fecha_limite > idea.fecha_reembolso:
        raise ValidationError(
            "La fecha de reembolso no puede estar antes de la fecha limite"
        )
    if idea.fecha_limite < date.today(): #None, para que solo lo  haga cuando
        raise ValidationError(                               #se inserta por primera vez.
            "La fecha limite no puede estar antes de la fecha de hoy"
        )

def validarMontoActual(idea): #enviar monto actual
    if (idea.monto_actual > idea.monto_objetivo):
        raise ValidationError(
            "El monto actual no puede ser mayor al monto objetivo"
        ) 