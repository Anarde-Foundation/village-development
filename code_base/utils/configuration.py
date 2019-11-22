# from code_base.Anarde import settings
import os

class kobo_constants:
    user_name = "<kobo account user name>"
    pwd = "<kobo account password>"

    authorization_token = "<kobo auth Token >"

    kobo_form_link = "<kobo form metadata url>"
    #kobo_data_link = "http://kc.kobo.local/api/v1/data/"
    kobo_data_link = "<kobo form data url>"


class metabase_constants:

    metabase_site_url = "<metabase url>"
    metabase_secret_key = "<metabase secret key>"

class image_constants:

    localhost = "http://localhost:8000"
    STATIC_URL = '/code_base/static/'

    Static_path = "/static/"
    currentDir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
    staticDir = currentDir + STATIC_URL

    before_afterDir = staticDir + r"before_after/"
    before_afterDirStatic = Static_path + r"before_after/"
    image_type_before = "before"
    image_type_after = "after"