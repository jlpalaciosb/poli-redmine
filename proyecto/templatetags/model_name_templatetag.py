from django import template

register = template.Library()


@register.filter
def model_name(model):
    """
    Obtiene el nombre del modelo en el templates
    :param model: Modelo
    :return: Nombre del modelo
    """
    return model.__class__.__name__
