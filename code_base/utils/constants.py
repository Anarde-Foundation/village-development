
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

class report_css_path:
    stylesheet = [CSS(settings.BASE_DIR +'/static/css/appStyle.css'),
                  CSS(settings.BASE_DIR + '/static/theme/vendors/bootstrap/dist/css/bootstrap.min.css')]