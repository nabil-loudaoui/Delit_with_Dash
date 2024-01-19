
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
import geoviews as gv
import geopandas as gpd
from bokeh.plotting import show
from bokeh.resources import INLINE
from geoviews import dim 
import folium
import requests
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px



delit = pd.read_csv("delit.csv", sep=";", encoding="ISO-8859-1", decimal=',')

# Carte graphique :
geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson'
response = requests.get(geojson_url)
geojson_data = response.json()


noms_departements = [feature['properties']['nom'] for feature in geojson_data['features']]
delit['Departement'] = noms_departements

# Créer la carte choroplèthe avec Plotly Express
fig = px.choropleth_mapbox(delit, geojson=geojson_data, locations='Departement',
                           color='Delit',
                           featureidkey="properties.nom",
                           color_continuous_scale="YlOrRd",
                           mapbox_style="carto-positron",
                           center={"lat": 46.603056, "lon": 1.888334},
                           zoom=4,
                           opacity=0.7,
                           labels={'Delit': 'Taux de délit'})


# Box Plot :
columns_to_convert = ['Population', 'Revenu_median', 'Taux_pauvrete',
                        'Scolarisation', 'Taux_chomage', 'Immigration']
delit[columns_to_convert] = delit[columns_to_convert].apply(pd.to_numeric, errors='coerce')

# Créer une Figure avec des sous-graphiques
fig3 = make_subplots(rows=1, cols=len(columns_to_convert), subplot_titles=columns_to_convert)

# Ajouter les box plots à chaque position spécifiée
for i, col in enumerate(columns_to_convert):
    fig3.add_trace(go.Box(y=delit[col], name=col, boxpoints='all'), row=1, col=i + 1)

# Mettre en forme la mise en page
fig3.update_layout(title_text='Box Plot des Variables par Département',
                  showlegend=False, height=400, width=1200)

# 
fig_delit = go.Figure()

# Ajouter la première trace pour la variable "Delit"
fig_delit.add_trace(go.Scatter(x=delit['Departement'], y=delit['Delit'], mode='lines', name='Délit'))

# Créer un axe Y secondaire pour la variable "Police"
fig_delit.add_trace(go.Scatter(x=delit['Departement'], y=delit['Taux_pauvrete'], mode='lines', name='Taux_pauvrete', yaxis='y2'))

# Mettre à jour la mise en page avec deux axes Y
fig_delit.update_layout(
    title='Délit et Taux de pauvrete par département',
    yaxis=dict(title='Délit'),
    yaxis2=dict(title='Taux de pauvrete', overlaying='y', side='right')
)

# Nuage de points
scatter = px.scatter(delit, x='Revenu_median', y='Delit', title='Nuage de points - Delit vs Taux_chomage',
                     labels={'Delit': 'Taux de délit', 'Taux_chomage': 'Taux de chômage'},
                     hover_name='Departement', color='Taux_chomage', color_continuous_scale='Viridis')


from dash import Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20%",
    "padding": "1rem 1rem",
    "background-color": "deepskyblue"
}

CONTENT_STYLE = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "80%",
    "padding": "1rem 1rem",
    "background-color": "oldlace"
}



sidebar = html.Div(
    [
        html.H2("Déterminants de l'Insécurité en France"),
        html.Hr(),
        html.H5("Analyse de l'Insécurité en France"),
        dbc.Nav(
        children=[
            dbc.NavLink("Introduction", href="/", active="exact", style={'color': 'black'}),
            dbc.NavLink("Analyse Géographique ", href="/page-1", active="exact", style={'color': 'black'}),
            dbc.NavLink("Analyse des Variables par Département", href="/page-2", active="exact", style={'color': 'black'}),
            dbc.NavLink(" Relation entre le Revenu Médian et le Taux de Délit", href="/page-3", active="exact", style={'color': 'black'}),
            dbc.NavLink(" Relations entre Delit et Taux de pauvrete", href="/page-4", active="exact", style={'color': 'black'})
        ],
            vertical=True,
            pills=True
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page_content(pathname):
    if pathname == "/":
        titre = html.H2("Introduction :")
        introduction = html.P("La visualisation ci-dessous présente une représentation cartographique des taux de délit pour chaque département en France métropolitaine, basée sur les données de l'année 2018. Les informations géographiques sont associées à des indicateurs socio-économiques, offrant un aperçu de la répartition des taux de délit à travers le pays. ")
        introduction2 = html.P(" Cette représentation utilise une échelle de couleurs pour indiquer les variations des taux de délit, allant des tons plus clairs aux tons plus foncés. Les départements les plus foncés indiquent des taux de délit plus élevés, tandis que les tons plus clairs représentent des taux plus bas.")
        obj = html.H2("Objectifs :")
        objectifs = html.P("L'objectif de cette visualisation est de permettre une compréhension rapide des tendances géographiques des taux de délit en France métropolitaine, offrant ainsi un aperçu visuel pour des analyses plus approfondies.")
        return [titre, introduction, introduction2, obj, objectifs]
    elif pathname == "/page-1":
        titre = html.H5("Comprendre les Facteurs et les Disparités Régionales")
        text = html.P(" La carte interactive ci-dessous présente une analyse géographique du taux de délit en France.")
        graph = html.Div(children=[
        dcc.Graph(figure=fig)
        ])
        text2 = html.P("L'analyse des données révèle des variations significatives dans les taux de délits entre différents départements. Les départements tels que le Val-de-Marne, la Seine-Saint-Denis et l'Essonne présentent des taux de délits relativement élevés, tandis que d'autres comme la Lozère, la Creuse et l'Ardèche affichent des taux plus bas. Ces disparités suggèrent des différences potentielles dans les facteurs socio-économiques, démographiques ou géographiques qui pourraient influencer les niveaux de criminalité dans ces régions. Cette observation souligne l'importance d'une analyse approfondie pour comprendre les dynamiques spécifiques à chaque département et élaborer des stratégies ciblées en matière de prévention et de sécurité publique.")
        return [titre, text, graph, text2]
    elif pathname == "/page-2":
        titre  = html.H2("Box_plots")
        texte = html.P("Les box plots ci-dessous présentent la distribution des principales variables pour chaque département en France.")
        graph = html.Div(children=[
            dcc.Graph(figure = fig3 )
        ])
        return [titre, texte, graph]
    elif pathname == "/page-3":
        titre  = html.H2("Exploration des Corrélations Éventuelles")
        texte = html.P("Cette visualisation présente un aperçu de la relation entre le revenu médian et le taux de délit pour chaque département en France. En examinant les variations des taux de délit en fonction du revenu médian, nous cherchons à identifier d'éventuelles corrélations socio-économiques.")
        graph = html.Div(children=[
            dcc.Graph(figure = scatter)
        ])
        text2 = html.P("L'analyse de la relation entre le revenu médian et le taux de délit met en lumière une tendance générale de corrélation négative, suggérant que, dans l'ensemble, les départements affichant un revenu médian plus élevé ont tendance à présenter des taux de délit plus bas. Cependant, des variations régionales et des cas exceptionnels soulignent l'importance d'une analyse contextuelle approfondie, mettant en évidence la complexité des facteurs locaux qui contribuent à la dynamique observée.")
        return [titre, texte, graph,text2]
    elif pathname == "/page-4":
        titre = html.H2("Comparaison entre Délit et Taux de pauvreté par département")
        texte = html.P("Ce graphique compare le délit et le taux de pauvreté dans chaque département. Il vise à mettre en évidence toute corrélation ou tendance entre ces deux variables.")
        graph = html.Div(children=[
            dcc.Graph(figure=fig_delit)
        ])
        text2 =html.P("En analysant la corrélation entre les variables Delit et Taux de pauvrete à travers la visualisation graphique, il ressort une tendance notable. Les départements présentant des taux de délit plus élevés semblent être associés à des niveaux de pauvreté plus élevés, suggérant une possible corrélation entre ces deux aspects socio-économiques. Cette observation initiale souligne l'importance d'approfondir l'analyse et d'explorer d'autres facteurs potentiels qui pourraient influencer cette relation complexe.")
        return [titre, texte, graph, text2]
        text2 =html.P("En analysant la corrélation entre les variables Delit et Taux de pauvrete à travers la visualisation graphique, il ressort une tendance notable. Les départements présentant des taux de délit plus élevés semblent être associés à des niveaux de pauvreté plus élevés, suggérant une possible corrélation entre ces deux aspects socio-économiques. Cette observation initiale souligne l'importance d'approfondir l'analyse et d'explorer d'autres facteurs potentiels qui pourraient influencer cette relation complexe.")
        return [titre, texte, graph, text2]

if __name__ == "__main__":
    app.run(debug=True)


with open(html_file, "w") as file:
    file.write(app.index_string())
