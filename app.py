import base64
import datetime
import io
import bio
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import pandas as pd
from textwrap import dedent

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.scripts.config.serve_locally = True

# TODO centering of text, replace markdown with html
app.layout = html.Div([
    dcc.Markdown(dedent('''
        #### Mystery App

        This app is made by Michael Kowal and Graeme Morgan for CPSC 450 - Bioinformatics

        ***

        To get started, either search for the organism you want or upload a .csv
        excel, or .fpkm spreadsheet into the field below.
    ''')),
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Search for organism', children=[
            html.H5('Organism to search for:'),
            html.Div([
                html.Div(dcc.Input(id='input-box1',
                                   type='text',
                                   style={
                                       'width': '40%',
                                       'height': '45px',
                                       'lineHeight': '60px',
                                       'borderWidth': '1px',
                                       'borderRadius': '5px',
                                       'textAlign': 'left',
                                       'margin': '10px'
                                   })),
                html.Button('Submit',
                            id='button1',
                            style={
                                'width': '160px',
                                'height': '40px',
                                'textAlign': 'center',
                                'margin': '10px'
                            }),
                html.Div(id='output-container-button1',
                         children='Enter a value and press submit')
            ])
        ]),
        dcc.Tab(label='Search for Pathways', children=[
            html.H5('Search by:'),
            dcc.RadioItems(
                options=[
                    {'label': 'Name', 'value': 'name'},
                    {'label': 'Gene ID', 'value': 'gid'},
                ],
                value='name'
            ),
            html.Div(dcc.Input(id='input-box2',
                               type='text',
                               style={
                                   'width': '40%',
                                   'height': '45px',
                                   'lineHeight': '60px',
                                   'borderWidth': '1px',
                                   'borderRadius': '5px',
                                   'textAlign': 'left',
                                   'margin': '10px'
                               }
                               )),
            html.Div(dcc.Input(id='input-box3',
                               type='text',
                               style={
                                   'width': '40%',
                                   'height': '45px',
                                   'lineHeight': '60px',
                                   'borderWidth': '1px',
                                   'borderRadius': '5px',
                                   'textAlign': 'left',
                                   'margin': '10px'
                               }
                               )),
            html.Button('Submit',
                        id='button2',
                        style={
                                'width': '160px',
                                'height': '40px',
                                'textAlign': 'center',
                                'margin': '10px'
                            }),
            html.Div(id='output-container-button2',
                     children='Enter a value and press submit')
        ]),
        dcc.Tab(label='Upload File', children=[
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '40%',
                    'height': '45px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
            html.Div(id='output-data-upload'),
            html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
        ]),
    ])
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delim_whitespace=True)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        # Use the DataTable prototype component:
        # github.com/plotly/dash-table-experiments
        dt.DataTable(rows=df.to_dict('records')),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(
    dash.dependencies.Output('output-container-button1', 'children'),
    [dash.dependencies.Input('button1', 'n_clicks')],
    [dash.dependencies.State('input-box1', 'value')])
def update_output(n_clicks, value):
    return 'The organism id is: {}'.format(bio.search_organism(value))


@app.callback(
    dash.dependencies.Output('output-container-button2', 'children'),
    [dash.dependencies.Input('button2', 'n_clicks')],
    [dash.dependencies.State('input-box2', 'value')])
def update_output(value):
    return


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


if __name__ == '__main__':
    app.run_server(debug=True)
