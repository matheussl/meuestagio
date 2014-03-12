#-*- coding: utf-8 -*-
from datetime import datetime
from django.db import models


class Area(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    imagem = models.ImageField(upload_to='categorias', null=True, blank=True)

    class Meta:
        verbose_name = 'Área'

    def __unicode__(self):
        return self.nome


TURNOS = (
    (1, 'Manhã'),
    (2, 'Tarde'),
    (3, 'Noite'),
)

class Estagio(models.Model):
    area = models.ForeignKey(Area, related_name='estagios')
    titulo = models.CharField(max_length=200, verbose_name=u'Título')
    slug = models.SlugField(unique=True)
    descricao = models.TextField(verbose_name=u'Descrição')
    vagas = models.IntegerField(default=1)
    turno = models.IntegerField(choices=TURNOS)
    contato = models.EmailField()

    criado_em = models.DateTimeField(auto_now_add=True, editable=False, default=datetime.now)
    atualizado_em = models.DateTimeField(auto_now=True, editable=False, default=datetime.now)

    class Meta:
        verbose_name = 'Estágio'

    def __unicode__(self):
        return self.titulo

