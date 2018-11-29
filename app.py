import base64
import io
import ast

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import pandas as pd
import plotly.graph_objs as go
import plotly.plotly as py
import plotly.figure_factory as ff
from dash.dependencies import Input, Output, State

import bio

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Bioinformatics'),
    dcc.Tabs(id='tabs', children=[
        dcc.Tab(label='Search by Pathway', children=[
            dcc.Input(id='input-box', type='text', value=''),
            html.Button(id='submit-button', n_clicks=0, children='Submit'),
            html.Div(id='output-state'),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
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
        dcc.Tab(label='Search by Genes', children=[
            dcc.Textarea(
                id='textarea',
                placeholder='Enter list of genes, separated by commas',
                style={'width': '100%'}
            ),
            dcc.Upload(
                id='upload-data-g',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
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
            html.Div(id='output-data-upload-g'),
            html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
        ])
    ])
])


def find_delta(h1, h2, h3, c1, c2, c3):
    return ((float(c1) + float(c2) + float(c3)) / 3) - ((float(h1) + float(h2) + float(h3)) / 3)


def parse_contents(contents, filename, dates, genes):
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
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delim_whitespace=True)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    # get all columns that contain genes in the pathway
    selection = df[df['tracking_id'].isin(genes)]

    # send all the values to the find_delta method to compute the change between cold and thermo-neutral values
    lst = []
    for row in selection.itertuples():
        lst.append(find_delta(row[3], row[4], row[5], row[6], row[7], row[8]))
    selection['Delta'] = lst

    # sort the file in the same order as the pathway
    sorter_index = dict(zip(genes, range(len(genes))))
    selection['tracking_id_sort'] = selection['tracking_id'].map(sorter_index)
    selection.sort_values(['tracking_id_sort'], ascending=True, inplace=True)
    selection.drop('tracking_id_sort', 1, inplace=True)

    # split the hot and cold lists into 2 for easier visibility
    hot = selection[selection['Delta'] >= 0]
    cold = selection[selection['Delta'] < 0]
    trace = [go.Heatmap(z=selection['Delta'].values.tolist(), y=selection['tracking_id'].values.tolist(),
                        colorscale='Viridis')]
    # return the tables as html tables
    return html.Div([
        html.H5(filename),

        # Use the DataTable prototype component:
        # github.com/plotly/datatable-experiments
        dcc.Tabs(id="tables", children=[
            dcc.Tab(label='Full Pathway', children=[
                html.Div([
                    dt.DataTable(rows=selection.to_dict('records'))
                ])
            ]),
            dcc.Tab(label='Cold', children=[
                html.Div([
                    dt.DataTable(rows=hot.to_dict('records')),
                ])
            ]),
            dcc.Tab(label='Thermal Neutral', children=[
                dt.DataTable(rows=cold.to_dict('records')),
            ]),
            dcc.Tab(label='Heatmap', children=[
                dcc.Graph(
                    id='heatmap',
                    figure={
                        'data': [{
                            'z': [selection['Delta']],
                            'zmax': 5,
                            'zmin': -5,
                            'showscale': True,
                            'text': [selection['tracking_id']],
                            'type': 'heatmap'
                        }]
                    }
                ),
            ])
        ]),
    ])


def get_genes_from_bioservices(genes):
    new_genes = []
    for gene in genes.values():
        new_genes.append(gene.split(';')[0])
    return new_genes


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified'),
               State('output-state', 'children')
               ])
def update_output(list_of_contents, list_of_names, list_of_dates, genes):
    if list_of_contents is not None:
        gene_list = ast.literal_eval(genes)
        children = [
            parse_contents(c, n, d, gene_list) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('output-data-upload-g', 'children'),
              [Input('upload-data-g', 'contents')],
              [State('upload-data-g', 'filename'),
               State('upload-data-g', 'last_modified'),
               State('textarea', 'value')
               ])
def update_output_g(list_of_contents, list_of_names, list_of_dates, genes):
    if list_of_contents is not None:
        gene_list = genes.split(',')
        children = [
            parse_contents(c, n, d, gene_list) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('output-state', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('input-box', 'value')])
def get_pathway(n_clicks, input):
    if n_clicks is not None and n_clicks > 0:
        genes = bio.get_pathway(input)
        if type(genes) == int:
            return '''{} not found in the bioservices database.  Please try another pathway.'''.format(input)
        new_genes = get_genes_from_bioservices(genes)
        return str(new_genes)
    return None


if __name__ == '__main__':
    app.run_server(debug=True)
