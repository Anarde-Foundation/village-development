#from code_base.Anarde import settings
import os
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

class image_constants:


    STATIC_URL = '/code_base/static/'

    currentDir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
    staticDir = currentDir + STATIC_URL

    before_afterDir = staticDir + r"before_after/"
    image_type_before = "before"
    image_type_after = "after"