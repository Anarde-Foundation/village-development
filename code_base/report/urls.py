from django.conf.urls import url
from django.urls import path, include
from . import views
from wkhtmltopdf.views import PDFTemplateView


app_name = 'report'
urlpatterns = [
path('pdf/<int:pk>', views.InvoicePDFView, name='pdf'),
path('graph_pdf/<int:pk>/<int:domain_id>', views.domain_graphs_pdf, name='graph_pdf'),
path('graph_pdf/<int:pk>/<int:domain_id>', views.domain_graphs_pdf, name='graph_pdf'),
path('get_survey_question_list_for_pdf/<int:pk>', views.get_survey_question_list_for_pdf, name='get_survey_question_list_for_pdf'),
path('new', PDFTemplateView.as_view(template_name='Metabase.html',
                                           filename='my_pdf.pdf'), name='pdf'),
    path('weasy_pdf', views.pdf_generation, name='weasy_pdf'),
    path('survey_pdf/<int:pk>', views.html_to_pdf_generation, name='survey_pdf'),
    path('survey_html_page/<int:pk>', views.survey_html, name='survey_html_page'),
    path('weasy_html_page', views.show_weasy_html_page, name='weasy_html_page'),
    path('weasy_embed_svg', views.weasy_embed_svg, name='weasy_embed_svg'),
]