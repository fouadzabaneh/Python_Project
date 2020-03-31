import base64
import io

import dash_html_components as html
import dash_core_components as dcc
import dash_table
import pandas as pd

PAGE_SIZE = 20

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

# Converting the uploaded files to Datatable and return datatable


def parse_contents(contents, filename, chart_dt):
    if 'datatable' in chart_dt:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' or 'txt' in filename:
                data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xlsx' or 'xls' in filename:
                data = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'])
        return html.Div([
            dash_table.DataTable(id="datatable-output",
                                 # Paging & numbering
                                 page_current=0,
                                 page_size=PAGE_SIZE,
                                 page_action='custom',

                                 # Sorting
                                 sort_action='custom',
                                 sort_mode='multi',
                                 sort_by=[],

                                 # Filtering
                                 filter_action='custom',
                                 filter_query='',

                                 virtualization=True,

                                 # Styling
                                 style_table={  # 'overflowX': 'scroll',
                                    'overflowY': 'auto',
                                     'maxHeight': 500,
                                     'border': '1px black solid'},
                                 fixed_rows={'headers': True, 'data': 0},
                                 style_header={'textAlign': 'center',
                                               'fontWeight': 'bold'},
                                 data=data.to_dict('records'),
                                 columns=[{'name': i, 'id': i}
                                          for i in data.columns]
                                 )])
    elif 'charts' in chart_dt:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' or 'txt' in filename:
                data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xlsx' or 'xls' in filename:
                data = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'])
        return data

# Display Graphs


def display_graphs(chartType, data, x_value, y_value, children):
    for t in chartType:

        if t == "Bar":
            children.append(html.Div(dcc.Graph(
                figure={
                    'data': [
                        {'x': data[i].unique(), 'y': data[j],
                            'type': t.lower(), 'name': j.title()}
                        for i in x_value
                        for j in y_value
                    ],
                    'layout': {'hovermode': 'closest',
                               "xaxis": {"automargin": False, },
                               "yaxis": {"automargin": True, }
                               }
                },
            )))

        elif t == "Lines":
            children.append(html.Div(dcc.Graph(
                figure={
                    'data': [
                        {'x': data[i].unique(), 'y': data[j],
                            'type': t.lower(), 'name': j.title()}
                        for i in x_value
                        for j in y_value
                    ],
                    'layout': {'hovermode': 'closest'}
                },
            )))

        elif t == "Markers":
            children.append(html.Div(dcc.Graph(
                figure={
                    'data': [
                        {'x': data[i].unique(), 'y': data[j],
                            'type': 'scatter',
                            'mode': 'markers',
                            'name': j.title()}
                        for i in x_value
                        for j in y_value
                    ],
                    'layout': {'hovermode': 'closest'}
                },
            )))

        elif t == "Scatter":
            children.append(html.Div(dcc.Graph(
                figure={
                    'data': [
                        {'x': data[i].unique(),
                         'y': data[j],
                         'type': t.lower(),
                         'mode': 'lines+markers',
                         'name':j.title(),
                         'unselected': {
                            'marker': {'opacity': 0.3},
                            # make text transparent when not selected
                            'textfont': {'color': 'white'}
                        }
                        } for i in x_value for j in y_value
                    ],
                    'layout': {
                        'margin': {'l': 30, 'r': 20, 'b': 35, 't': 5},
                        'dragmode': 'select',
                        'hovermode': 'closest',
                    }

                },

            )))

    return children

# Filter Function


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3
