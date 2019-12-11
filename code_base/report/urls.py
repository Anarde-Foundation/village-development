from django.urls import path, include
from . import views


app_name = 'report'
urlpatterns = [

    path('survey_pdf/<int:pk>', views.html_to_pdf_generation, name='survey_pdf'),
    path('survey_html_page/<int:pk>', views.survey_html, name='survey_html_page'),
    path('svg/', views.svg_convert, name='svgc'),
    # path('svg/', views.get_svg, name='svgc'),
]