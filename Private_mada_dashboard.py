#-------------------------------------------------------------------------
# Import libraries

import pandas as pd
import numpy as np
import re

import geopandas as gpd
import geojson

# from jupyter_dash import JupyterDash
import dash
# import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import dcc, html
import plotly.express as px
# import plotly.graph_objects as go
# import plotly.offline as pyo
# pyo.init_notebook_mode() # Set notebook mode to work in offline

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
np.set_printoptions(threshold=np.inf)

#-------------------------------------------------------------------------
# REAL APP

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

# -----------------------------------------------------------------------
# Import and clean data

# import and read the json file
states = gpd.read_file('georef-france-commune.geojson')

df = pd.read_csv('resultats_elections_martinique_1er_tour_2022.csv')

df2 = pd.read_csv('resultats_elections_martinique_2nd_tour_2022.csv')

# retirer les titres devant les noms des candidats
df['Liste des candidats'] = df['Liste des candidats'].apply(lambda x: re.sub('(M\.\s|Mme\s)', '', x))
df2['Liste des candidats'] = df2['Liste des candidats'].apply(lambda x: re.sub('(M\.\s|Mme\s)', '', x))

df['Commune_renamed'] = np.repeat(sorted(list(states['com_name'].unique())), df['Liste des candidats'].nunique())
df2['Commune_renamed'] = np.repeat(sorted(list(states['com_name'].unique())), df2['Liste des candidats'].nunique())

# -----------------------------------------------------------------------
# App Layout

app.layout = html.Div([

    html.Div([
        html.H1("Résultats des élections présidentielles du 1er tour en Martinique (2022)",
                style = {"textAlign": "center", "font-size": "30px"}),
        html.Hr()
    ]),

    html.Div([

        html.Div([
            html.P('Sélectionner un candidat :', style = {'font-size': '13.5px'}),

            html.Div([
                dcc.Dropdown(
                    id = 'candidate_name',
                    clearable = False,
                    value = 'Jean-Luc MÉLENCHON',
                    options = [{'label': x, 'value': x} for x in df['Liste des candidats'].unique()],
                    style = {'font-size': '13.5px'}
                )
            ], style = {'width': '30%'}),

            html.Div([
                dcc.Graph(id = 'mada_map')
            ], style = {'float': 'left', 'padding': 20, 'margin': 'auto'})

        ], className = 'six columns'),

        html.Div([
            html.P('Sélectionner une commune :', style = {'font-size': '13.5px'}),

            html.Div([
                dcc.Dropdown(
                    id = 'city_name',
                    clearable = False,
                    value = 'Le Diamant',
                    options = [{'label': x, 'value': x} for x in df['Commune_renamed'].unique()],
                    style = {'font-size': '13.5px'}
                )
            ], style = {'width': '25%'}),

            html.Div([
                dcc.Graph(id = 'candidate_bar')
            ], style = {'float': 'right', 'margin': 'auto'})

        ], className = 'six columns')
    ], className = 'row'),

    html.Br(),
    html.Br(),

    html.Div([
        html.H1("Résultats des élections présidentielles du 2nd tour en Martinique (2022)",
                style = {"textAlign": "center", "font-size": "30px"}),
        html.Hr()
    ]),

    html.Div([

        html.Div([
            html.P('Sélectionner un candidat :', style = {'font-size': '13.5px'}),

            html.Div([
                dcc.Dropdown(
                    id = 'candidate_name_2',
                    clearable = False,
                    value = 'Emmanuel MACRON',
                    options = [{'label': x, 'value': x} for x in df2['Liste des candidats'].unique()],
                    style = {'font-size': '13.5px'}
                )
            ], style = {'width': '30%'}),

            html.Div([
                dcc.Graph(id = 'mada_map_2')
            ], style = {'float': 'left', 'padding': 20, 'margin': 'auto'})

        ], className = 'six columns'),

        html.Div([
            html.P('Sélectionner une commune :', style = {'font-size': '13.5px'}),

            html.Div([
                dcc.Dropdown(
                    id = 'city_name_2',
                    clearable = False,
                    value = 'Le Diamant',
                    options = [{'label': x, 'value': x} for x in df2['Commune_renamed'].unique()],
                    style = {'font-size': '13.5px'}
                )
            ], style = {'width': '25%'}),

            html.Div([
                dcc.Graph(id = 'candidate_bar_2')
            ], style = {'float': 'right', 'margin': 'auto'})

        ], className = 'six columns')
    ], className = 'row')

], style = {'display': 'inline-block', 'padding': 25})


# -----------------------------------------------------------------------
# App Callback

@app.callback(
    [Output(component_id = 'mada_map', component_property = 'figure'),
     Output(component_id = 'candidate_bar', component_property = 'figure'),
     Output(component_id = 'mada_map_2', component_property = 'figure'),
     Output(component_id = 'candidate_bar_2', component_property = 'figure')],
    [Input(component_id = 'candidate_name', component_property = 'value'),
     Input(component_id = 'city_name', component_property = 'value'),
     Input(component_id = 'candidate_name_2', component_property = 'value'),
     Input(component_id = 'city_name_2', component_property = 'value')],
)
def update_graphs(candidate_chosen, city_chosen, candidate_chosen_2, city_chosen_2):
    df_candidate = df.copy(deep = True)
    df_candidate = df_candidate[df_candidate['Liste des candidats'] == candidate_chosen]

    df_city = df.copy(deep = True)
    df_city = df_city[df_city['Commune_renamed'] == city_chosen]

    df2_candidate = df2.copy(deep = True)
    df2_candidate = df2_candidate[df2_candidate['Liste des candidats'] == candidate_chosen_2]

    df2_city = df2.copy(deep = True)
    df2_city = df2_city[df2_city['Commune_renamed'] == city_chosen_2]

    fig_map = px.choropleth(
        df_candidate,
        geojson = states,
        locations = 'Commune_renamed',
        featureidkey = 'properties.com_name',
        color = '% Exprimés',
        projection = 'mercator',
        fitbounds = 'locations',
        basemap_visible = False,
        color_continuous_scale = px.colors.sequential.YlOrRd,
    )

    fig_map.update_traces(
        customdata = df_candidate[['Commune_renamed', '% Exprimés']],
        hovertemplate = (
                '<b>%{customdata[0]}</b><br>' + \
                '% Exprimés : %{customdata[1]} %<br>'
        )
    )

    fig_map.update_layout(margin = {"r": 0, "t": 0, "l": 0, "b": 0})

    fig_city = px.bar(
        df_city,
        y = 'Liste des candidats',
        x = '% Exprimés',
        color = 'Liste des candidats',
        color_discrete_sequence = px.colors.qualitative.G10,
        template = 'plotly_white',
        height = 475, width = 775
    )

    fig_city.update_traces(
        hovertemplate = '<br>'.join([
            '<b>%{y}</b><extra></extra>',
            '% Exprimés : %{x} %'
        ])
    )

    fig_city.update_layout(yaxis_title = None)

    fig_map_2 = px.choropleth(
        df2_candidate,
        geojson = states,
        locations = 'Commune_renamed',
        featureidkey = 'properties.com_name',
        color = '% Exprimés',
        projection = 'mercator',
        fitbounds = 'locations',
        basemap_visible = False,
        color_continuous_scale = px.colors.sequential.YlOrRd,
    )

    fig_map_2.update_traces(
        customdata = df2_candidate[['Commune_renamed', '% Exprimés']],
        hovertemplate = (
                '<b>%{customdata[0]}</b><br>' + \
                '% Exprimés : %{customdata[1]} %<br>'
        )
    )

    fig_map_2.update_layout(margin = {"r": 0, "t": 0, "l": 0, "b": 0})

    fig_city_2 = px.bar(
        df2_city,
        y = 'Liste des candidats',
        x = '% Exprimés',
        color = 'Liste des candidats',
        color_discrete_sequence = px.colors.qualitative.G10,
        template = 'plotly_white',
        height = 475, width = 775
    )

    fig_city_2.update_traces(
        hovertemplate = '<br>'.join([
            '<b>%{y}</b><extra></extra>',
            '% Exprimés : %{x} %'
        ])
    )

    fig_city_2.update_layout(yaxis_title = None)

    return fig_map, fig_city, fig_map_2, fig_city_2


# Run app and display result inline in the notebook
# app.run_server(mode='inline')
if __name__ == '__main__':
    app.run_server(debug = False)