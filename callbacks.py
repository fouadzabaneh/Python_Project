from collections import deque
from datetime import datetime as dt
from datetime import timedelta

import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from Functions import display_graphs, parse_contents, split_filter_part
from layout import basic_layout

chart_list = ['Bar', 'Lines', 'Markers', 'Scatter']

################################# DATA TABLE / CHARTS PAGE ###############################

@app.callback(Output('fileName', 'children'),
              [Input('upload-data', 'filename')])
def update_label(filename):
    if filename is None:
        raise PreventUpdate
    else:
        filename = '--'.join(filename)
        return html.H5(children=filename, style={'fontSize': "large", 'fontStyle': "italic"})

# Create the DataTable


@app.callback(Output('display-datatable', 'children'),
              [Input('upload-data', 'contents'),
               Input('chcklist-charts-table', 'value')],
              [State('upload-data', 'filename')])
def update_dataTable(contents, value_type, filename):
    if contents is not None and value_type is not None:
        if 'datatable' in value_type:
            return [parse_contents(contents, filename, value_type) for contents, filename in zip(contents, filename)]

# Update the X-axis


@app.callback([Output('xaxis-data-columns', 'options'),
               Output('xaxis-data-columns', 'disabled')],
              [Input('chcklist-charts-table', 'value'),
               Input('store-data', 'data')])
def update_xaxis(value, data):
    if value is not None and data is not None:
        if 'charts' in value:
            return [{'label': i, 'value': i} for i in data[0].keys()], False
    else:
        return [], True

# Update the Y-axis


@app.callback([Output('yaxis-data-columns', 'options'),
               Output('yaxis-data-columns', 'disabled')],
              [Input('chcklist-charts-table', 'value'),
               Input('store-data', 'data')])
def update_yaxis(value, data):
    if value is not None and data is not None:
        if 'charts' in value:
            return [{'label': i, 'value': i} for i in data[0].keys()], False
    else:
        return [], True

# Show/update the Chart Type Dropdown


@app.callback([Output('dropdown-charts-list', 'options'),
               Output('dropdown-charts-list', 'disabled')],
              [Input('chcklist-charts-table', 'value')],
              [State('upload-data', 'filename')])
def enable_dropbox(chartlist, filename):
    if chartlist is not None and filename is not None:
        if 'charts' in chartlist:
            return [{'label': i, 'value': i} for i in chart_list], False
        else:
            return [], True
    else:
        raise PreventUpdate

# Store table in memory


@app.callback(Output('store-data', 'data'),
              [Input('upload-data', 'contents'),
               Input('chcklist-charts-table', 'value')],
              [State('upload-data', 'filename')])
def update_store_data(contents, value_type, filename):
    try:
        if contents is not None and value_type is not None:
            if 'charts' in str(value_type):
                data = parse_contents(str(contents), str(filename), 'charts')
                return data.to_dict('records')
        else:
            raise PreventUpdate
    except Exception as e:
        print(e)

# Update the Graphs


@app.callback(Output('display-charts', 'children'),
              [Input('store-data', 'data'),
               Input('chcklist-charts-table', 'value'),
               Input('dropdown-charts-list', 'value'),
               Input('xaxis-data-columns', 'value'),
               Input('yaxis-data-columns', 'value')],
              [State('display-charts', 'children')])
def display_charts(data, chart_value, chart_type, x_value, y_value, children):
    if (data and chart_value and chart_type and x_value and y_value) is not None:
        if 'charts' in chart_value:
            df = pd.DataFrame(data)
            children = []
            return display_graphs(chart_type, df, x_value, y_value, children)
        else:
            return {}

# Displaying filter datatable


@app.callback(
    Output('datatable-output', 'data'),
    [Input('datatable-output', "page_current"),
     Input('datatable-output', "page_size"),
     Input('datatable-output', 'sort_by'),
     Input('datatable-output', 'filter_query'),
     Input('datatable-output', 'derived_virtual_data')])
def update_table(page_current, page_size, sort_by, filter_query, rows):
    if rows is not None:
        filtering_expressions = filter_query.split(' && ')
        data = pd.DataFrame(rows)
        for filter_part in filtering_expressions:
            col_name, operator, filter_value = split_filter_part(filter_part)

            if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
                # these operators match pandas series operator method names
                data = data.loc[getattr(
                    data[col_name], operator)(filter_value)]
            elif operator == 'contains':
                data = data.loc[data[col_name].str.contains(filter_value)]
            elif operator == 'datestartswith':
                # this is a simplification of the front-end filtering logic,
                # only works with complete fields in standard format
                data = data.loc[data[col_name].str.startswith(filter_value)]

        if len(sort_by):
            data = data.sort_values(
                by=[col['column_id'] for col in sort_by],
                ascending=[col['direction'] == 'asc' for col in sort_by],
                inplace=False)

        return data.iloc[
            page_current*page_size:(page_current + 1)*page_size].to_dict('records')


"""
@app.callback(Output('print', 'children'),
              [Input('chcklist-charts-table', 'value')])
def Store(value):
    if 'datatable' in str(value) and 'charts' in str(value):
        return str(value)
        # show_charts_table
 """

#################### STOCK EXCHANGE DATA PAGE ######################################


@app.callback(Output('date-picker-range-output', 'children'),
              [Input('date-picker-stock', 'start_date'),
               Input('date-picker-stock', 'end_date')])
def update_text(start_date, end_date):
    string_prefix = "You have selected"

    if start_date is not None and end_date is not None:
        start_date = dt.strptime(start_date.split('T')[0], '%Y-%m-%d')
        start_date_string = start_date.strftime('%B %d, %Y')

        string_prefix = string_prefix + " a Start Date of " + start_date_string + " | "

        end_date = dt.strptime(end_date.split('T')[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%B %d, %Y')

        days_selected = (end_date - start_date).days
        # prior_start_date = start_date - timedelta(days_selected + 1)
        # prior_start_date_string = dt.strftime(prior_start_date, '%B %d, %Y')

        # prior_end_date = end_date - timedelta(days_selected + 1)
        # prior_end_date_string = dt.strftime(prior_end_date, '%B %d, %Y')

        string_prefix = string_prefix + " End Date of " + end_date_string + ", for a total of " + \
            str(days_selected + 1) + " Days."
        # + prior_end_date_string + " | End Date: " + prior_end_date_string + "."

    if len(string_prefix) == len("You have selected: "):
        return "Select a date to see it displayed here"
    else:
        return string_prefix


#### Update Graph #####


@app.callback(Output('live-update-output-graph', 'children'),
              [Input('input-stock-name', 'value'),
               Input('date-picker-stock', 'start_date'),
               Input('date-picker-stock', 'end_date'),
               Input('radioitems-period-update', 'value')],
              [State('live-update-output-graph', 'children')])
def disply_live_graph(stock_name, start_date, end_date, interval_time, children):
    stock_name = 'bb.to'
    try:
        if stock_name != "" and start_date is not None and end_date is not None:
            start_date = dt.strptime(start_date.split("T")[0], "%Y-%m-%d")
            end_date = dt.strptime(end_date.split("T")[0], "%Y-%m-%d")

            stock_df = web.DataReader(
                stock_name, 'yahoo', start=start_date, end=end_date)

            children = []

            children.append(
                html.Div([
                    dcc.Graph(
                        figure={
                            'data': [
                                go.Candlestick(x=stock_df.index,
                                               open=stock_df['Open'],
                                               close=stock_df['Close'],
                                               low=stock_df['Low'],
                                               high=stock_df['High'])],
                            'layout': go.Layout(
                                xaxis_rangeslider_visible=False,
                                hovermode='closest',
                                title=stock_name.upper() + " Stock"
                            )
                        }, animate=True),

                    dcc.Interval(id="live-update-interval",
                                 n_intervals=0,
                                 interval=10
                                 )
                ])
            )

            children.append(
                html.Div([
                    dcc.Graph(
                        figure={
                            'data': [
                                go.Ohlc(x=stock_df.index,
                                        open=stock_df['Open'],
                                        close=stock_df['Close'],
                                        low=stock_df['Low'],
                                        high=stock_df['High'])
                            ],
                            'layout': go.Layout(
                                xaxis_rangeslider_visible=False,
                                hovermode='closest',
                                title=stock_name.upper() + " Stock"
                            )
                        }, animate=True),

                    dcc.Interval(id="live-update-interval",
                                 n_intervals=0,
                                 interval=interval_time*1000
                                 )
                ])
            )

            children.append(
                html.Div([
                    dcc.Graph(
                        figure={
                            'data': [
                                go.Scatter(x=stock_df.index,
                                           y=stock_df[i],
                                           name=i.title(),
                                           mode="lines")
                                for i in stock_df.columns if i not in ['Volume', 'Adj Close']
                            ],
                            'layout': go.Layout(hovermode="closest",
                                                title=stock_name.upper() + " Stock")
                        }, animate=True),

                    dcc.Interval(id="live-update-interval",
                                 n_intervals=0,
                                 interval=interval_time*1000
                                 )
                ])
            )

            return children
    except Exception as e:
        print(e)


##### Updating the interval time in milliseconds###

""" 
@app.callback(Output('live-update-interval', 'interval'),
              [Input('radioitems-period-update', 'value')])
def update_interval(interval_time):
    interval_time = interval_time * 1000
    return interval_time
 """
