# -*- coding: utf-8 -*-
import re

import PyPDF2
import numpy as np
import pandas as pd
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
            # filename = ''

            pdf_file_obj = open(filename, 'rb')
            pdf_reader = slate.PDF(pdf_file_obj)
            #PyPDF2.PdfFileReader(pdf_file_obj)
            num_pages = pdf_reader.numPages

            count = 0
            text = ""

            while count < num_pages:
                page_obj = pdf_reader.getPage(count)
                count += 1
                text += page_obj.extractText()

            enc_text = text.encode('ascii', 'ignore').lower()
            text = f'{enc_text}'

            keywords = re.findall(r'[a-zA-Z]\w+', text)

            df = pd.DataFrame(list(set(keywords)), columns=['keywords'])

            df['number_of_times_word_appeared'] = (
                df['keywords'].apply(lambda x: self.weightage(x, text)[0])
            )
            df['tf'] = df['keywords'].apply(lambda x: self.weightage(x, text)[1])
            df['idf'] = df['keywords'].apply(lambda x: self.weightage(x, text)[2])
            df['tf_idf'] = (
                df['keywords'].apply(lambda x: self.weightage(x, text)[3])
            )

            df = df.sort_values('tf_idf', ascending=True)
            df.head(25)

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
