# 2020 Alessio Gerace @ Inrim
import os
import logging
import base64

logger = logging.getLogger()


def get_base_result(request):
    """
    Prepare base response data
        for S2S service templates is false
        for C2S templetes containt file in base64
    """
    return {
        "status": "success",
        "data": request.form,
        "templates": False
    }


def get_dic_templates(position, template):
    '''

    This method make dictionary with:
        *template --> the fle template that you need to render
        *file_templates --> dictionary with each fle load in position folder encoded in base64
    '''
    tmpl_file = f"{current_app.config['TEMPLATES_FOLDER']}/{position}/"
    res = {
        "main_template": template,
        "file_templates": {}
    }
    for r, d, f in os.walk(tmpl_file):
        for file in f:
            if ".html" in file:
                data = open(os.path.join(r, file), "r").read()
                res['file_templates'][file] = base64.b64encode(bytes(data, "utf-8")).decode('utf-8')
    return res
