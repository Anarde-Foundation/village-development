
from weasyprint import  CSS
from Anarde import settings

class kobo_form_constants:

    data_format = "/form.json"
    question_type = ['text', 'calculate', 'integer']
    question_type_having_options = ['select one', 'select all that apply']
    names_not_allowed = ['start', 'end', 'meta', '__version__', 'instanceID']

    questions_not_having_space = ['select all that apply']


class numeric_constants:
    one = 1
    zero = 0
    pattern_for_weights = '^[wW](\d*)_'
    before_images = 101001
    after_images = 101002


class code_group_names:
    survey_type = 100
    funder = "Funder"

class report_css_path:
    stylesheet = [CSS(settings.BASE_DIR +'/static/css/reportStyle.css'),
                  CSS(settings.BASE_DIR + '/static/css/report_bootstrap.min.css')]
    # position: relative;
    # border: 0
    # px;
    # width: calc(160
    # mm * 1.25);
    # height: calc(297
    # mm * 1.25);
    # padding: 0

