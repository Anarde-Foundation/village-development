from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from cgi import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = context_dict
    html  = template.render(context)
    result = BytesIO()
    # data = list(context_dict)
    # t = Table(data, 5 * [0.4 * inch], 4 * [0.4 * inch])
    # t.setStyle(TableStyle([('ALIGN', (1, 1), (-2, -2), 'RIGHT'), ('TEXTCOLOR', (1, 1), (-2, -2), colors.red),
    #                        ('VALIGN', (0, 0), (0, -1), 'TOP'), ('TEXTCOLOR', (0, 0), (0, -1), colors.blue),
    #                        ('ALIGN', (0, -1), (-1, -1), 'CENTER'), ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
    #                        ('TEXTCOLOR', (0, -1), (-1, -1), colors.green),
    #                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    #                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ]))
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))