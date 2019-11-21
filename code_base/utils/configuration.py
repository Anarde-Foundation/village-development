# from code_base.Anarde import settings
import os

class kobo_constants:
    user_name = "developer"
    pwd = "softcorner"

    #form_info_link = "http://kc.kobo.local/api/v1/forms/2/form.json"    # 2 = form_id and form.json denotes the type of format
    authorization_token = "Token 327a67c406bc8f2d8bf061502b33164e77a5a6d9"

    kobo_form_link = "https://kc.humanitarianresponse.info/api/v1/forms"
    #kobo_data_link = "http://kc.kobo.local/api/v1/data/"
    kobo_data_link = "https://kc.humanitarianresponse.info/api/v1/data"


class metabase_constants:

    metabase_site_url = "http://localhost:3000"
    metabase_secret_key = "670f338d49bcfbdd7837ca7f5abbf01733cf82be6f731fd0464210d52c222ea6"  # anarde metabase


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