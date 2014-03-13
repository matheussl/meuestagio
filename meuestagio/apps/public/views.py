from django.shortcuts import render, get_object_or_404
from models import Area, Estagio


def context_processor(request):
    areas = Area.objects.all().order_by('nome')
    return {'areas': areas}


def home(request):
    return render(request, 'home.html')


def area(request, slug):
    area = get_object_or_404(Area, slug=slug)
    context = {'area': area}
    return render(request, 'area.html', context)


def estagio(request, slug_area, slug):
    estagio = get_object_or_404(Estagio, slug=slug, area__slug=slug_area)
    context = {'estagio': estagio}
    return render(request, 'estagio.html', context)



