from django.urls import path, include
from . import views


app_name = 'report'
urlpatterns = [

    path('weasy_pdf', views.pdf_generation, name='weasy_pdf'),
    path('survey_pdf/<int:pk>', views.html_to_pdf_generation, name='survey_pdf'),
    path('survey_html_page/<int:pk>', views.survey_html, name='survey_html_page'),
    path('weasy_html_page', views.show_weasy_html_page, name='weasy_html_page'),
    path('weasy_embed_svg', views.weasy_embed_svg, name='weasy_embed_svg'),
]