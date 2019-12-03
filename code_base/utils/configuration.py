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

    is_production = True

    localhost = "http://localhost:8000"
    STATIC_URL = '/code_base/static/'
    currentDir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
    before_afterDir = currentDir + STATIC_URL + r"before_after/"

    before_afterDirStatic = "/static/before_after/"

    image_type_before = "before"
    image_type_after = "after"

    image_dir = r"before_after/"


class aws_bucket_constants:
    s3_bucket_path = "<bucket path>"
    aws_access_key_id = '<aws key id>'
    aws_secret_access_key = '<aws secret key>'
    region_name = '<bucket path>'
    bucket_name = '<bucket name>'

