from io import BytesIO
from reportlab.pdfgen import canvas
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

    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        # Create a canvas and add a rectangle to it
        c = canvas.Canvas(result)
        c.translate(inch, 9 * inch)
        c.rect(inch, inch, 1 * inch, 1 * inch, fill=1)

        # example.xlsx is in the same directory as the pdf
        c.linkURL(r'Metabase.html', (inch, inch, 2 * inch, 2 * inch), relative=1)
        c.save()
        return HttpResponse(result.getvalue(), content_type='application/pdf')

    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

def write_pdf_view(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Start writing the PDF here
    p.drawString(100, 100, 'Hello world.')
    # End writing

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response


