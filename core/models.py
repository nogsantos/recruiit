# -*- coding: utf-8 -*-
import uuid

from django.db import models


class BaseModel(models.Model):
    public_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                 editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Candidate(BaseModel):
    STATUS = (
        ('processing', 'Análise do curriculo em processamento'),
        ('approved', 'Candidato aprovado'),
        ('reproved', 'Candidato reprovado'),
        ('quarantine', 'Candidato em quarentena'),
    )
    name = models.CharField(max_length=250)
    email = models.CharField(max_length=250)
    phone = models.CharField(max_length=250)
    resume = models.CharField(max_length=250)
    status = models.CharField(max_length=30, choices=STATUS,
                              default=STATUS[0][0])
