from django.shortcuts import render
from django.views import generic

# Create your views here.
class MainPageView(generic.TemplateView):
  template_name = 'index.html'
  
main_page = MainPageView.as_view()