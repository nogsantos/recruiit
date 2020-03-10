# -*- coding: utf-8 -*-
import re

import PyPDF2
import numpy as np
import pandas as pd
from .forbidden_words import forbidden_words
from .key_words import key_words
import slate3k as slate
from django.core.files.storage import FileSystemStorage
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from django.conf import settings


class HealthCheckViewSet(viewsets.ViewSet):

    @action(methods=['GET'], detail=False, url_path='read')
    def read_key_words(self, request, pk=None):
        try:
            name = self.request.query_params.get("name", None)
            filename = f'{settings.BASE_DIR}/docs/{name}.pdf'

            pdf_file_obj = open(filename, 'rb')
            # pdf_reader = slate.PDF(pdf_file_obj)
            pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
            num_pages = pdf_reader.numPages

            count = 0
            text = ""

            while count < num_pages:
                page_obj = pdf_reader.getPage(count)
                count += 1
                text += page_obj.extractText()

            enc_text = text.encode('ascii', 'ignore').lower()
            text = f'{enc_text}'

            words = re.findall(r'[a-zA-Z]\w+', text)

            df = pd.DataFrame(list(set(words)), columns=['words'])

            df['number_of_times_word_appeared'] = (df['words'].apply(lambda x: self.weightage(x, text)[0]))
            # df['tf'] = df['keywords'].apply(lambda x: self.weightage(x, text)[1])
            # df['idf'] = df['keywords'].apply(lambda x: self.weightage(x, text)[2])
            # df['tf_idf'] = (df['keywords'].apply(lambda x: self.weightage(x, text)[3]))

            df = df.sort_values('number_of_times_word_appeared', ascending=False)

            self.score_cv(text)

            return Response(df, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_200_OK)

    def weightage(self, word, text, number_of_documents=1):
        word_list = re.findall(word, text)
        number_of_times_word_appeared = len(word_list)
        tf = number_of_times_word_appeared / float(len(text))
        idf = np.log((number_of_documents) / float(number_of_times_word_appeared))
        tf_idf = tf * idf
        return number_of_times_word_appeared, tf, idf, tf_idf

    def score_cv(self, text):

        if self.get_forbidden_words_number(text) != 0:
            print("Nota:", 0)
        else:
            print("Nota:", self.get_score(text))

        print("Key Words:", self.get_key_words_number(text))
        print("Forbbiden Words:", self.get_forbidden_words_number(text))

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
