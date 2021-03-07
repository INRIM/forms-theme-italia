# 2020 Alessio Gerace @ Inrim
import os
import importlib
import importlib.util
import json
from datetime import datetime
import logging
import base64
from typing import Union
import ipaddress as ipaddr
import requests
import re

logger = logging.getLogger()

alert_base = {
    "succcess": {
        "alert_type": "success",
        "message": "Dati aggiornati con successo",
        "add_class": " mx-auto col-6 ",
        "hide_close_btn": True
    },
    "error": {
        "alert_type": "danger",
        "message": "Errore aggiornamento dati",
        "add_class": "  mx-auto col-6 ",
        "hide_close_btn": True,
    },
    "warning": {
        "alert_type": "warning",
        "message": "Errore aggiornamento dati",
        "add_class": "  mx-auto col-6 ",
        "hide_close_btn": True,
    },
}

chips_base = {
    "base": {
        "alert_type": "primary",
        "label": "Selezionare",
        "icon": "it-info-circle"
    },
    "secondary": {
        "alert_type": "secondary",
        "label": "Selezionare",
        "icon": "it-info-circle"
    },
    "success": {
        "alert_type": "success",
        "label": "Ok",
        "icon": "it-check-circle"
    },
    "error": {
        "alert_type": "danger",
        "label": "Attenzione mancano tutti i dati",
        "icon": "it-error"
    },
    "warning": {
        "alert_type": "warning",
        "label": "Attenzione mancano alcuni dati",
        "icon": "it-warning-circle"
    },
}

button = {
    "submit": {
        "name": "",
        "type": "submit",
        "btn_class": False,
        "link": ""
    },
    "link": {
        "name": "",
        "type": "submit",
        "btn_class": False,
        "link": ""
    },
    "button": {
        "name": "",
        "type": "button",
        "btn_class": "False",
        "link": ""
    }
}

formio_map = {
    "textarea": "form_text_area.html",
    "address": "",
    "component": "",
    "componentmodal": "",
    "button": "form_button.html",
    "checkbox": "form_toggle.html",
    "columns": "form_row.html",
    "column": "form_col.html",
    "container": "block_container.html",
    "content": "",
    "currency": "",
    "datagrid": "table/table.html",
    "datagridRow": "table/table_row.html",
    "datamap": "",
    "datetime": "block_date.html",
    "day": "",
    "editgrid": "",
    "email": "form_input.html",
    "input": "form_input.html",
    "field": "",
    "multivalue": "",
    "fieldset": "",
    "file": "form_upload_file.html",
    "form": "page_form/form.html",
    "hidden": "",
    "htmlelement": "",
    "nested": "",
    "nesteddata": "",
    "nestedarray": "",
    "number": "form_number_input.html",
    "panel": "block_card_components.html",
    "password": "form_password_input.html",
    "phoneNumber": "form_input.html",
    "radio": "form_radio_container.html",
    "recaptcha": "",
    "resource": "form_select_search.html",
    "select": "form_select_search.html",
    "selectboxes": "form_select_multi.html",
    "signature": "",
    "survey": "",
    "table": "table.html",
    "tabs": "",
    "tags": "",
    "textfield": "form_input.html",
    "time": "",
    "tree": "",
    "unknown": "UnknownComponent",
    "url": "text_link.html",
    "well": "",
}

form_io_default_map = {
    "key": "key",
    "description": "desc",
    "customClass": "customClass",
    "label": "label",
    "title": "label",
    "action": "type",
    "placeholder": "placeholder",
    "data": {"values": "options"},
    "defaultValue": "value",
    "disabled": "disabled",
    "values": "rows",
    "validate": {"required": "required"},
    "propery": {"onchange": "onchange"},
}

formio_map_cfg = {
    "textarea": {},
    "address": {},
    "component": {},
    "componentmodal": {},
    "button": {},
    "checkbox": {},
    "columns": {},
    "container": {},
    "content": {},
    "currency": {},
    "datagrid": {},
    "datamap": {},
    "datetime": {},
    "day": {},
    "editgrid": {},
    "email": {},
    "input": {},
    "field": {},
    "multivalue": {},
    "fieldset": {},
    "file": {},
    "form": "{}",
    "hidden": {},
    "htmlelement": {},
    "nested": {},
    "nesteddata": {},
    "nestedarray": {},
    "number": {},
    "panel": {},
    "password": {},
    "phoneNumber": {},
    "radio": {},
    "recaptcha": {},
    "resource": {},
    "select": {},
    "selectboxes": {},
    "signature": {},
    "survey": {},
    "table": {},
    "tabs": {},
    "tags": {},
    "textfield": {},
    "time": {},
    "tree": {},
    "unknown": {},
    "url": {},
    "well": {},
}


def from_object(instance: Union[object, str]) -> {}:
    data = {}
    if isinstance(instance, str):
        try:
            path, config = instance.rsplit(".", 1)
        except ValueError:
            path = instance
            instance = importlib.import_module(path)
        else:
            module = importlib.import_module(path)
            instance = getattr(module, config)

    for key in dir(instance):
        if key.isupper():
            data[key] = getattr(instance, key)
    return data


def check_ip_local(ip) -> bool:
    """
    check if ip is in rage of setting key APP_SETTINGS - > INTERNAL_IP_NET
    ipv4 or ipv6 ready
    :param ip:
    :return: bool
    """
    settings = from_object(os.getenv("APP_SETTINGS"))
    if settings.get('INTERNAL_IP_NET') and ip:
        # print("IIIIII", ip,  ipaddr.ip_address(ip))
        if type(ipaddr.ip_address(ip)) is ipaddr.IPv4Address:
            res = ipaddr.IPv4Address(ip) in ipaddr.IPv4Network(settings['INTERNAL_IP_NET'])
        else:
            res = ipaddr.IPv6Address(ip) in ipaddr.IPv6Network(settings['INTERNAL_IP_NET'])
        # print(res)
        return res
    else:
        return False


def allowed_file(filename, ALLOWED_EXTENSIONS=['pdf']):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def string_to_number(str_data):
    if "." in str_data:
        try:
            res = float(str_data)
        except:
            res = str_data
    elif str_data.isdigit():
        res = int(str_data)
    else:
        res = str_data
    return res


def get_remote_avatar(url, key):
    headers = {"x-key": key}
    res = requests.get(url, headers=headers)
    return res.content.decode("utf-8")


def extract_mac_address(text):
    pattern = '(([0-9a-fA-F]{2}[:]){5}([0-9a-fA-F]{2}))'
    mac_addr_list = re.findall(pattern, text)
    return list(map(lambda x: x[0], mac_addr_list))


def get_default_error_alert_cfg():
    return alert_base['error']


def get_default_success_alert_cfg():
    return alert_base['succcess']


def get_default_warning_alert_cfg():
    return alert_base['warning']


def get_form_alert(values):
    if values.get("success"):
        kkwargs = get_default_success_alert_cfg()
    if values.get("error"):
        kkwargs = get_default_error_alert_cfg()
    if values.get("warning"):
        kkwargs = get_default_warning_alert_cfg()
    kwargs_def = {**kkwargs, **values}
    return kwargs_def


def get_update_alert_error(selector, message, cls=""):
    to_update = {}

    cfg = {
        "error": True,
        "message": message,
        "cls": " mx-auto mt-lg-n3 ",
        "name": selector
    }
    if not '#' in selector and not '.' in selector:
        selector = "#" + selector
    if cls:
        cfg['cls'] = cls
    to_update["value"] = get_form_alert(cfg)

    to_update["selector"] = selector
    return to_update


def get_update_alert_warning(selector, message, cls=""):
    to_update = {}

    cfg = {
        "warning": True,
        "message": message,
        "cls": " mx-auto mt-n5 ",
        "name": selector
    }
    if not '#' in selector and not '.' in selector:
        selector = "#" + selector
    if cls:
        cfg['cls'] = cls
    to_update["value"] = get_form_alert(cfg)

    to_update["selector"] = selector
    return to_update