# 2020 Alessio Gerace @ Inrim
import os
import time
import logging

import pyotp
import base64
import requests
import json


def get_services_from_manifest(manifest):
    pass


def get_widget_from_manifest(manifest):
    pass


def decode_request_templates(dic_templates, default):
    """
    Decode the dic extrat from payload of a call and create
    fisical file template in path for render the page
    Return also the mail template to render to execute the implies chain to.

    return:
        template_file_name --> for render template
    """
    filename = dic_templates.get("main_template", False)
    datas = dic_templates.get("file_templates", False)
    res = f"main/{filename}"
    content = ""
    for data in datas:
        filename = data
        tmpl_file = f"{app.config['TEMPLATES_FOLDER']}/main/{filename}"
        content = base64.b64decode(bytes(datas[data], "utf-8"))
        with open(tmpl_file, 'wb') as file:
            file.write(content)
    return res, content


def handle_request(service, default):
    res = default
    values = {}
    content = ""
    render_result = True
    if service:
        # TODO check oauth and pass jwt
        url = service["url"]
        r = requests.get(f"http://{url}", allow_redirects=True)
        # print("")
        # print("res", dir(r))
        # print("")

        if r.status_code == 200:
            posts = json.loads(r.text)
            if posts:
                values['data'] = posts['data']
                values["status"] = posts['status']
                render_result = templates = posts["templates"]
                if templates:
                    res, content = decode_request_templates(templates, default)
    return res, values, render_result, content


