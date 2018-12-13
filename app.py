import base64
import io
import ast

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt


import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

import bio


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config['suppress_callback_exceptions']=True


# Incorporating multiple page support (If this is scaled it will all change.)

# app.layout = html.Div([
#     dcc.Location(id='url', refresh='False'),
#     html.Div(id='page-content')
# ])


# error_404 = html.Div([
#     html.H1("If you are seeing this, than things have gone horribly wrong."),
#     html.Br(),
#     dcc.Link('Go to the Portal', href='/main'),
#     html.Br(),
#     dcc.Link('Go to Neet', href='/neet')
# ])
#
#
# page_main_layout = html.Div([
#     html.H1("Welcome to the main page"),
#     dcc.Tabs(id='tabs', children=[
#         dcc.Tab(label='Hello World', children=[
#             dcc.Markdown('''
#             Hello there...''')
#         ])
#     ])
# ])



#----------------------------------------------------------------------------#
# Main Layout
#----------------------------------------------------------------------------#

app.layout = html.Div([
    html.Div(html.Img(src=app.get_asset_url('neet-logo-blue-tiny.png'), className='logo')),
    html.H1('uNbc sEquencing rEsearch Tool', className='logo-text'),

    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    dcc.Tabs(id='tabs', children=[
        # this is the tab that lets users search for genes by pathway
        dcc.Tab(label='Search by Pathway', children=[
            dcc.Markdown('''
Pathways must be entered in the form <organism-code><pathway-number>.  If you are unsure what 
the organism code is, use [this tool](https://www.genome.jp/kegg-bin/find_org_www?mode=abbr&obj=mode.map) to find it.
            '''),
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
                    'margin-top': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
            html.Div(id='output-data-upload'),
            html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
        ]),
        # this tab lets users pick specific genes that they would like to have visualized
        dcc.Tab(label='Search by Genes', children=[
            html.H6('Search for specific genes.  Enter list of genes then upload a file to view results.'),
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

                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
            html.Div(id='output-data-upload-g'),
            html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
        ], className='tabs'),
        # This tab displays User documentation
        dcc.Tab(label='Documentation', children=[
            # dcc.Input(id='input-box-go', type='text', value=''),
            # html.Button(id='submit-button-go', n_clicks=0, children='Submit'),
            # html.Div(id='output-state-go'),
            html.H1('Welcome to NEET')
        ])
    ])
],
style={
    # style for primary layout
    'margin-bottom':'100px'
})




# Updates the page index.
#
# @app.callback(dash.dependencies.Output('page-content', 'children'),
#               [dash.dependencies.Input('url', 'pathname')])
# def display_page(pathname):
#     if pathname =='/main' :
#         return page_main_layout
#     elif pathname =='/neet' :
#         return app.layout
#     else:
#         return error_404





#----------------------------------------------------------------------------#
# Functions
#----------------------------------------------------------------------------#

# this method is simply for calculating the delta between samples
def find_delta(h1, h2, h3, c1, c2, c3):
    return ((float(c1) + float(c2) + float(c3)) / 3) - ((float(h1) + float(h2) + float(h3)) / 3)


def compare_one(h1, h2, h3, c1):
    return float(c1) - ((float(h1) + float(h2) + float(h3)) / 3)


# take the uploaded file, search it for the genes specified earlier, and output a heat map and files split the file into
# genes that produce negative values and genes that produce positive values
def parse_contents(contents, filename, dates, genes, name):
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
            # Assume the user uploaded a space separated value table
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delim_whitespace=True)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    # get all columns that contain genes in the pathway
    selection = df[df['tracking_id'].isin(genes)]

    # send all the values to the find_delta method to compute the change between cold and thermal neutral values
    lst1 = []
    lst2 = []
    lst3 = []
    lst4 = []
    lst5 = []
    lst6 = []
    lst7 = []
    for row in selection.itertuples():
        lst1.append(find_delta(row[3], row[4], row[5], row[6], row[7], row[8]))
        lst2.append(compare_one(row[3], row[4], row[5], row[6]))
        lst3.append(compare_one(row[3], row[4], row[5], row[7]))
        lst4.append(compare_one(row[3], row[4], row[5], row[8]))
        lst5.append(compare_one(row[6], row[7], row[8], row[3]))
        lst6.append(compare_one(row[6], row[7], row[8], row[4]))
        lst7.append(compare_one(row[6], row[7], row[8], row[5]))
    selection['Delta'] = lst1
    selection['c1Comp'] = lst2
    selection['c2Comp'] = lst3
    selection['c3Comp'] = lst4
    selection['cn1Comp'] = lst5
    selection['cn2Comp'] = lst6
    selection['cn3Comp'] = lst7

    # sort the file in the same order as the pathway
    sorter_index = dict(zip(genes, range(len(genes))))
    selection['tracking_id_sort'] = selection['tracking_id'].map(sorter_index)
    selection.sort_values(['tracking_id_sort'], ascending=True, inplace=True)
    selection.drop('tracking_id_sort', 1, inplace=True)

    # split the hot and cold lists into 2 for easier visibility
    hot = selection[selection['Delta'] >= 0]
    cold = selection[selection['Delta'] < 0]
    hot = hot.drop(['c1Comp', 'c2Comp','c3Comp','cn1Comp','cn2Comp','cn3Comp'], axis=1)
    cold = cold.drop(['c1Comp', 'c2Comp', 'c3Comp', 'cn1Comp', 'cn2Comp', 'cn3Comp'], axis=1)
    trace = [go.Heatmap(z=selection['Delta'].values.tolist(), y=selection['tracking_id'].values.tolist(),
                        colorscale='Viridis')]
    view = selection.drop(['c1Comp', 'c2Comp','c3Comp','cn1Comp','cn2Comp','cn3Comp'], axis=1)
    # return the tables as html tables
    return html.Div([
        html.H5(filename),

        # Use the DataTable prototype component:
        # github.com/plotly/datatable-experiments

        #Tab for Control Group
        dcc.Tabs(id="groups", children=[
            dcc.Tab(label='Control Group', children=[
                dcc.Tabs(id="tables", children=[

                    # a heat map of all the delta values for the Control Group
                    dcc.Tab(label='Heatmap', children=[
                        dcc.Graph(
                            id='heatmap',
                            figure={
                                'data': [{
                                    'z': [
                                        selection['cn1Comp'],
                                        selection['cn2Comp'],
                                        selection['cn3Comp']
                                    ],
                                    'zmax': 5,
                                    'zmin': -5,
                                    'showscale': True,
                                    'text': [selection['tracking_id']],
                                    'type': 'heatmap',
                                    'colorscale': 'Blues'
                                }],
                                'layout': {
                                    'title': name,
                                }
                            }
                        ),
                    ])
                ])
            ]),

            # Tab for Experimental Group
            dcc.Tab(label='Experimental Group', children=[
                dcc.Tabs(id="tables", children=[
                    # a heat map of all the delta values for the Experimental Group
                    dcc.Tab(label='Heatmap', children=[
                        dcc.Graph(
                            id='heatmap',
                            figure={
                                'data': [{
                                    'z': [
                                        selection['c1Comp'],
                                        selection['c2Comp'],
                                        selection['c3Comp'],

                                    ],
                                    'zmax': 5,
                                    'zmin': -5,
                                    'showscale': True,
                                    'text': [selection['tracking_id']],
                                    'type': 'heatmap',
                                    'colorscale': 'Blues'
                                }],
                                'layout': {
                                    'title': name,
                                }
                            }
                        ),
                    ])
                ])
            ]),

            # Tab for Raw Data
            dcc.Tab(label='Raw Data', children=[
                dcc.Tabs(id="tables", children=[
                    dcc.Tab(label='Full Pathway', children=[
                        html.Div([
                            dt.DataTable(rows=view.to_dict('records'))
                        ])
                    ]),
                    # a table of all the positive delta values
                    dcc.Tab(label='Positive', children=[
                        html.Div([
                            dt.DataTable(rows=hot.to_dict('records')),
                        ])
                    ]),
                    # a table of all the negative delta values
                    dcc.Tab(label='Negative', children=[
                        dt.DataTable(rows=cold.to_dict('records')),
                    ]),
                ])
            ]),

        ]),

    ])


# returns a list of genes from the requested pathway
def get_genes_from_bioservices(genes):
    new_genes = []
    for gene in genes[1].values():
        new_genes.append(gene.split(';')[0])
    name = genes[0][0].split(' - ')[0]
    return name, new_genes


# called when a file is uploaded in the pathway tab
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified'),
               State('output-state', 'children')
               ])
def update_output(list_of_contents, list_of_names, list_of_dates, genes):
    if list_of_contents is not None:
        # build all the dash components to fill the output div
        name, genes = genes.split(' - ')
        genes = ast.literal_eval(genes)
        children = [
            parse_contents(c, n, d, genes, name) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


# called when a file is uploaded in the gene tab
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
            parse_contents(c, n, d, gene_list, '') for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


# Called when the submit button is clicked in the pathways tab.  Returns a list of genes in the pathway
@app.callback(Output('output-state', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('input-box', 'value')])
def get_pathway(n_clicks, value):
    if n_clicks is not None and n_clicks > 0:
        genes = bio.get_pathway(value)
        if type(genes) == int:
            return '''{} not found in the bioservices database.  Please try another pathway.'''.format(value)
        name, new_genes = get_genes_from_bioservices(genes)
        return str(name) + ' - ' + str(new_genes)
    return None


# Called when the submit button is clicked in the gene ontology tab
@app.callback(Output('output-state-go', 'children'),
              [Input('submit-button-go', 'n_clicks')],
              [State('input-box-go', 'value')])
def get_gene_ontology(n_clicks, value):
    if n_clicks is not None and n_clicks > 0:
        data = bio.get_go(value)
        stuff = ''
        for i in data[0]:
            stuff += str(i) + ' : ' + str(data[0][i]) + '\n'
        print(stuff)
        return stuff
    return None





if __name__ == '__main__':
    app.run_server(debug=True)





