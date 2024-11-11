from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
import json
from django.http import HttpResponse,JsonResponse

class ApiView(generics.GenericAPIView):
    def get(self, request):
        data = {
            'name': 'Boopathy',
            'role': 'backend developer'
        }
        print(data,'************')

        return JsonResponse(data)
