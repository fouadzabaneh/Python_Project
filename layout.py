import dash_html_components as html
import dash_core_components as dcc
from datetime import datetime as dt

from collections import deque


first_tab_layout = html.Div([
    html.H1("DashBoards"),
    html.Div([html.H4("Upload files")], className="flex-box-upload"),
    html.Div([
        dcc.Upload(id="upload-data",
                   children=html.Button(
                       "Browse", type='file', className="btn btn-primary mr-2"),
                   multiple=True
                   )
    ], className="flex-box-row-1"),
    html.Div(id="fileName",  className="flex-box-row-1"),
    html.Br(), html.Br(),
    html.Div([
        html.Div([html.H5("Choose Output"),
                  dcc.Checklist(id="chcklist-charts-table",
                                options=[
                                    {'label': "Data Table", 'value': "datatable"},
                                    {'label': "Charts", 'value': "charts"},
                                ],
                                value=[],
                                labelStyle={'display': 'block'}
                                )
                  ], className="flex-box-row-2"),
        html.Div([html.H5("Select Chart Type"),
                  dcc.Dropdown(id="dropdown-charts-list",
                               placeholder="Select Chart Type",
                               multi=True,
                               disabled=True
                               )
                  ], className="flex-box-row-2"),
        html.Div([html.H5("X-axis data"),
                  dcc.Dropdown(id="xaxis-data-columns",
                               placeholder="Select x-axis",
                               disabled=True,
                               multi=True
                               )
                  ], className="flex-box-row-2"),
        html.Div([html.H5("Y-axis data"),
                  dcc.Dropdown(id="yaxis-data-columns",
                               placeholder="Select y-axis",
                               disabled=True,
                               multi=True
                               )
                  ], className="flex-box-row-2")
    ], className="flex-box-container"),
    html.Br(),
    dcc.Store(id='store-data', storage_type='memory'),

    html.Div(id='display-datatable'),

    html.Div(id="display-charts"),
    html.Div(id="display-filtered-data-chart"),

])

radio_items = {"1 Second": 1, "5 Seconds": 5, "1 Minute": 60,
               "5 Minutes": 300, "10 Minutes": 600, "1 Hour": 3600}


# interval_time = 1*1000


second_tab_layout = html.Div([
    html.Div(html.H1("Stock Exchange Data Page")),
    html.Div([

        html.Div([html.H5("Enter Stock Name"),
                  dcc.Input(id="input-stock-name",
                            placeholder="Enter Stock name",
                            type="text",
                            value='',
                            style={"fontFamily": "Times"})
                  ], className="flex-box-input-stock"),

        html.Div([html.H5("Choose Date"),
                  dcc.DatePickerRange(id="date-picker-stock",
                                      min_date_allowed=dt(2000, 1, 1),
                                      initial_visible_month=dt.now(),
                                      start_date=dt.now(),
                                      #   end_date=dt.now(),
                                      end_date_placeholder_text='Select a date!'
                                      ),
                  html.Div(id="date-picker-range-output"),

                  ], className="flex-box-date-picker"),

        html.Div([html.H5("Choose update period"),
                  dcc.RadioItems(id="radioitems-period-update",
                                 options=[{'label': i, 'value': j}
                                          for i, j in radio_items.items()],
                                 value=5,
                                 labelStyle={"marginLeft": "7px"}
                                 )

                  ], className="flex-box-radioitems")
    ], className="flex-box-container"),
    html.Br(),

    html.Div([
        html.Div(id="live-update-output-graph"),
        dcc.Interval(id="live-update-interval",
                     n_intervals=0,
                     interval=10
                     )
    ])
])

basic_layout = html.Div([
    dcc.Tabs([
        dcc.Tab(id="tab-1",
                label="Data Table / Charts",
                children=first_tab_layout,
                ),
        dcc.Tab(id="tab-2",
                label="Stock Exchange Data",
                children=second_tab_layout)
    ], className="tabs")
])
