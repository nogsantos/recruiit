# -*- coding: utf-8 -*-
import re

import PyPDF2
import numpy as np
import pandas as pd
from threading import Timer
from django.conf import settings
from django.core import mail
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.filters import OrderingFilter
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from core.models import Candidate
from core.serializers import CandidateSerializer
from .forbidden_words import forbidden_words
from .key_words import key_words


class CandidateViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_fields = ['status', 'name']

    def get_queryset(self):
        queryset = Candidate.objects.all()
        return queryset

    def create(self, request, **kwargs):
        parser_class = (FileUploadParser,)

        serializer = self.get_serializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)

        f = request.data['file']
        _dir = f'{settings.BASE_DIR}/docs/'
        fs = FileSystemStorage(location=_dir, file_permissions_mode=0o600)
        fs.save(f.name, f)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class HealthCheckViewSet(viewsets.ViewSet):

    @action(methods=['GET'], detail=False, url_path='read')
    def read_key_words(self, request, pk=None):
        try:
            name = self.request.query_params.get("name", None)
            filename = f'{settings.BASE_DIR}/docs/{name}.pdf'

            pdf_file_obj = open(filename, 'rb')

            pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
            num_pages = pdf_reader.numPages

            count = 0
            text = ""

            while count < num_pages:
                page_obj = pdf_reader.getPage(count)
                count += 1
                text += page_obj.extractText()

            enc_text = text.lower()
            text = f'{enc_text}'

            words = re.findall(r'[a-zA-Z]\w+', text, re.UNICODE)

            df = pd.DataFrame(list(set(words)), columns=['words'])

            df['number_of_times_word_appeared'] = (
                df['words'].apply(lambda x: self.weightage(x, text)[0]))

            df = df.sort_values('number_of_times_word_appeared',
                                ascending=False)

            # Email confirmando submissão de currículo
            self._send_mail('subscription', "Inscrição Confirmada", 10.0, {
                'name': 'Candidato',
                'email': 'candidato@test.com',
                'phone': '46 9999-999',
            })

            self.score_cv(text)

            return Response(df, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_200_OK)

    def weightage(self, word, text, number_of_documents=1):
        word_list = re.findall(word, text)

        number_of_times_word_appeared = len(word_list)
        tf = number_of_times_word_appeared / float(len(text))
        idf = np.log(
            (number_of_documents) / float(number_of_times_word_appeared))
        tf_idf = tf * idf
        return number_of_times_word_appeared, tf, idf, tf_idf

    def score_cv(self, text):

        if self.get_forbidden_words_number(text) != 0:
            self._send_mail('reproved', "Candidatura Rejeitada", 20.0, {
                'name': 'Candidato',
                'email': 'candidato@test.com'
            })
        else:
            score = self.get_score(text)

            if score >= 50.0:
                self._send_mail('approved', "Aprovado para próxima fase", 20.0, {
                    'name': 'Candidato',
                    'email': 'candidato@test.com'
                })
            else:
                self._send_mail('quarantine', "Processo Seletivo Encerrado", 20.0, {
                    'name': 'Candidato',
                    'email': 'candidato@test.com'
                })

    def get_key_words_number(self, text):
        return int(self.sum_words(key_words, text))

    def get_forbidden_words_number(self, text):
        return int(self.sum_words(forbidden_words, text))

    def sum_words(self, arr, text):
        sum_words = 0

        for word in arr:
            sum_words += len(re.findall(word, text))

        return sum_words

    def get_score(self, text):
        return float(self.get_key_words_number(text) / len(key_words)) * 100

    def _send_mail(self, filename, subject, interval, context):
        template = f'email/{filename}'
        html_body = render_to_string(f'{template}.html', context)
        txt_body = render_to_string(f'{template}.txt', context)

        # Intervalo em segundos para enviar e-mail
        thr = Timer(interval=interval, function=mail.send_mail, kwargs={
            "subject": subject,
            "message": txt_body,
            "html_message": html_body,
            "from_email": settings.DEFAULT_FROM_EMAIL,
            "recipient_list": [
                settings.DEFAULT_FROM_EMAIL,
                context['email']
            ],
        })

        thr.start()

class FileUploadView(views.APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, filename, format=None):
        if 'file' not in request.data:
            raise ParseError("Empty content")

        f = request.data['file']
        _dir = f'{settings.BASE_DIR}/docs/'
        fs = FileSystemStorage(location=_dir, file_permissions_mode=0o600)
        fs.save(f.name, f)
        
        return Response(status=status.HTTP_201_CREATED)
