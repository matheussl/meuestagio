from django.shortcuts import render, get_object_or_404
from models import Area, Estagio


def context_processor(request):
    areas = Area.objects.all()
    return {'areas': areas}


def home(request):
    ultimos_estagios = Estagio.objects.all().order_by('criado_em')
    context = {'ultimos_estagios': ultimos_estagios}
    return render(request, 'home.html', context)


def estagio(request, slug):
    estagio = get_object_or_404(Estagio, slug=slug)
    context = {'estagio': estagio}
    return render(request, 'estagio.html', context)



