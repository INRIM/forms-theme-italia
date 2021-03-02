import collections

from json2html import *
import pandas as pd
from .default_config_components import *
from . import custom_components
import logging

from .widgets_content import PageWidget

logger = logging.getLogger(__name__)


class TableWidget(PageWidget):

    def __init__(self, templates_engine, request, settings, schema={}, resource_ext=None, disabled=False):
        super(TableWidget, self).__init__(
            templates_engine, request, settings, schema=schema, resource_ext=resource_ext,
            disabled=disabled
        )
        self.cls_title = " text-center "
        self.api_action = "/"
        self.curr_row = []
        self.schema = schema
        self.form_name = ""
        self.name = "table_default"
        self.title = ""
        self.components_base_path = f"/{self.theme}/templates/components/table/"

    def get_table(self, values):
        df = self.get_df(**values)
        d = df.to_dict('records')
        tab_id = values['tab_id']
        if values.get('cls'):
            cls = values.get('cls')
        else:
            cls = "table table-borderless p-2"
        attr = f'id="{tab_id}" class="{cls}" '
        res = json2html.convert(
            json=json.dumps(d), table_attributes=attr.format(tab_id=tab_id), escape=False
        )
        return res

    def get_df(self, **values):
        df = pd.DataFrame(values['data_list'])
        df = df.rename_axis(None)
        if values['data_list']:
            for item in values.get('dates') or []:
                df[item] = [self.convert_date_server_ui(d, item) for d in df[item]]
            for item in values.get("bool") or []:
                df[item] = [self.convert_bool(b) for b in df[item]]
            for item in values.get("links") or []:
                df[item] = [self.convert_link(f"{self.components_base_path}item_link.html", l) for l in df[item]]
            for item in values.get('strings') or []:
                df[item] = [self.convert_str_server_ui(d) for d in df[item]]
            dfc = df[values['columns'].keys()]
            df = dfc.rename(columns=dict(values['columns']))
        return df

    def make_def_tabe(self, data, **kwargs):
        return self.render_def_table(data, **kwargs)

    def get_columns(self, data):
        keys = list(data[0].keys())[:]
        keys.insert(0, keys.pop(keys.index("_id")))
        print("get_columns", keys)
        keys2 = keys[:]
        cols = {keys[i]: keys2[i] for i in range(len(keys))}
        print(cols)
        return collections.OrderedDict(cols)

    def render_def_table(self, data_list, **kwargs):
        template = f"{self.components_base_path}base_datatable.html"
        columns = self.get_columns(data_list)
        click_url_base = kwargs.get("click_url", "/")
        table_view = {
            "title": self.title,
            'tab_id': self.name,
            'table': self.get_table({
                'data_list': data_list,
                "tab_id": self.name,
                "cls": "table table-borderless table-hover p-2",
                "columns": columns
            }),
            'columns_search': True,
            'page_menu': True,
            'tab_responsive': False,
            "full_width": True,
            "click_row": {
                "col": 0,
                "url": click_url_base,
            },
            "columnDefs": {
                "targets": [list(columns.keys()).index('_id')],
                "visible": False,
            },
            'pageLength': len(data_list),
            'dom_todo': 'itpr'
        }
        return self.render_template(template, table_view)