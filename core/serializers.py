# -*- coding: utf-8 -*-
from rest_framework import serializers

from core.models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = (
            'public_id',
            'name',
            'email',
            'grade',
            'phone',
            'resume',
            'status',
            'created_at',
            'updated_at',
        )
