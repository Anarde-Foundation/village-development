# from code_base.Anarde import settings
import os


class kobo_constants:
    user_name = "<kobo_user name>"
    pwd = "<kobo pwd>"

    authorization_token = "<kobo authorization token>"

    kobo_form_link = "<kobo form link>"
    kobo_data_link = "<kobo data link>"


class metabase_constants:

    metabase_site_url = "<metabase site url>"
    metabase_secret_key = "<metabase site secret key>"


class image_constants:

    is_production = False
    localhost = "<machine_ip>"
    STATIC_URL = '/code_base/static/'
    currentDir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
    before_afterDir = currentDir + STATIC_URL + r"before_after/"
    before_afterDirStatic = "/static/before_after/"

    metabase_images = currentDir + STATIC_URL + r"metabase_images/"
    metabase_images_localhost = "/static/metabase_images/"

    image_type_before = "before"
    image_type_after = "after"

    image_dir = r"before_after/"


class aws_bucket_constants:
    s3_bucket_path = "<aws bucket path>"
    aws_access_key_id = '<aws access key>'
    aws_secret_access_key = '<aws secret key access>'
    region_name = '<region name>'
    bucket_name = '<bucket name>'

