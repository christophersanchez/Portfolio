from dash import Dash
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
from machine_learning import kmeans_dates, kmeans_aircraft_info, kmeans_type


df = pd.read_csv('faainquiry.csv')

df['Expiration Date'] = pd.to_datetime(df['Expiration Date'])
df['Type Aircraft'] = df['Type Aircraft'].astype(str)
# Create cluster column with KMeans
df = kmeans_dates(df)
df = kmeans_aircraft_info(df)
df = kmeans_type(df)


app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


app.layout = html.Div([
    dbc.Row([
        dbc.Col(html.H1("FAA Analysis"), md=12)
    ]),
    dbc.Row([
        dbc.Col(dbc.Select(
            id='manufacturer-dropdown',
            options=[{'label': i, 'value': i} for i in df['Manufacturer Name'].unique()],
            value=df['Manufacturer Name'].unique()[0]
        ), md=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='engine-pie'), md=4),
        dbc.Col(dcc.Graph(id='bar-chart'), md=4),
        dbc.Col(dcc.Graph(id='line-chart'), md=4)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='pie-chart'), md=4),
        dbc.Col(dcc.Graph(id='scatter-plot'), md=4),
        dbc.Col(dcc.Graph(id='stacked-bar-chart'), md=4)
    ]),
    dbc.Row([
        dbc.Col(dbc.Select(
                id='cluster-date-dropdown',
                options=sorted([{'label': i, 'value': i} for i in df['dates_cluster'].unique()], key=lambda x: x['value']),
                value=0,
                ), md=4),

        dbc.Col(dbc.Select(
                id='cluster-aircraft-dropdown',
                options=sorted([{'label': i, 'value': i} for i in df['aircraft_cluster'].unique()], key=lambda x: x['value']),
                value=0,
                ), md=4),
        dbc.Col(dbc.Select(
                id='cluster-type-dropdown',
                options=sorted([{'label': i, 'value': i} for i in df['type_cluster'].unique()], key=lambda x: x['value']),
                value=0,
                ), md=4)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='dates-scatter-chart'), md=4),
        dbc.Col(dcc.Graph(id='aircraft-scatter-chart'), md=4),
        dbc.Col(dcc.Graph(id='type-scatter-chart'), md=4)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='choropleth-country-map'), md=20)
])

], className="mt-4")


### BAR CHART ###
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('manufacturer-dropdown', 'value')]
)
def update_bar_chart(manufacturer):
    filtered_df = df[df['Manufacturer Name'] == manufacturer]
    trace = go.Bar(x=filtered_df['Model'].unique(),
                   y=filtered_df.groupby('Model').size())
    return {'data': [trace],
            'layout': go.Layout(title='Number of Aircrafts by Model',
                                xaxis={'title': 'Model'},
                                yaxis={'title': 'Number of Aircrafts'})
            }

### PIE CHART ###
@app.callback(
    Output('engine-pie', 'figure'),
    [Input('manufacturer-dropdown', 'value')]
)
def update_engine_pie(manufacturer):
    filtered_df = df[df['Manufacturer Name'] == manufacturer]
    values = filtered_df.groupby('Type Engine').size()
    labels = values.index
    trace = go.Pie(labels=labels, values=values)
    return {'data': [trace],
            'layout': go.Layout(title='Engine Type Distribution')}


### LINE CHART ###
@app.callback(
    Output('line-chart', 'figure'),
    [Input('manufacturer-dropdown', 'value')]
)
def update_line_chart(manufacturer):
    filtered_df = df[df['Manufacturer Name'] == manufacturer]
    filtered_df = filtered_df.replace([np.inf, -np.inf, 'None', '0000', 0000], np.nan)
    filtered_df = filtered_df.dropna(subset=['MFR Year'])
    filtered_df['MFR Year'] = filtered_df['MFR Year'].astype(int)
    filtered_df = filtered_df[filtered_df['MFR Year'].apply(lambda x: len(str(x)) == 4)]

    x = filtered_df.groupby('MFR Year').size().index
    y = filtered_df.groupby('MFR Year').size().values
    y_min = min(y)
    y_max = max(y)
    trace = go.Scatter(x=x, y=y, mode='lines+markers',
                       marker=dict(color='rgb(255,0,0)', size=10))
    return {'data': [trace],
            'layout': go.Layout(title='Number of Aircrafts by Year Manufactured',
                                xaxis=dict(title='Year'),
                                yaxis=dict(title='Number of Aircrafts',
                                range=[y_min, y_max]))}

### PIE CHART ###
@app.callback(
    Output('pie-chart', 'figure'),
    [Input('manufacturer-dropdown', 'value')]
)
def update_pie_chart(manufacturer):
    filtered_df = df[df['Manufacturer Name'] == manufacturer]

    values = filtered_df.groupby('Type Registration').size()
    labels = [value for value in filtered_df['Type Registration'].unique() if value in values.index]
    trace = go.Pie(labels=labels, values=values, textinfo='value',
                   textfont={'color': 'white'}, hoverinfo='label+value+percent',
                   sort=False, name='Registratipn Type Distribution')
    return {'data': [trace],
            'layout': go.Layout(title='Registratipn Type Distribution', legend=dict(title='Type R'))}

# Add a new column 'Closest Expiration' with the closest expiration date
df['Closest Expiration'] = df.groupby(['Manufacturer Name','Name'])['Expiration Date'].transform(min)

# Create a scatter plot with the closest expiration date for each manufacturer
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('manufacturer-dropdown', 'value')]
)
def update_scatter_plot(manufacturer):
    filtered_df = df[df['Manufacturer Name'] == manufacturer]
    trace = go.Scatter(x=filtered_df['Manufacturer Name'],
                       y=filtered_df['Closest Expiration'],
                       mode='markers',
                       text=filtered_df['Name'])
    return {'data': [trace],
            'layout': go.Layout(title='Closest Expiration Dates by Manufacturer',
                                xaxis={'title': 'Manufacturer'},
                                yaxis={'title': 'Closest Expiration Date'})}


@app.callback(
    Output('stacked-bar-chart', 'figure'),
    [Input('manufacturer-dropdown', 'value')]
)
def update_stacked_bar(manufacturer):
    colors = {'Individual': 'rgb(255,0,0)', 'Partnership': 'rgb(255,255,0)', 'Corporation': 'rgb(0,0,255)', 'Co-Owned': 'rgb(0,255,0)', 'Government': 'rgb(255,0,255)', 'LLC': 'rgb(255,255,255)', 'Non Citizen Corporation': 'rgb(0,255,255)', 'Non Citizen Co-Owned': 'rgb(255,0,0)'}
    # Filter the dataframe by the selected manufacturer
    df_filtered = df[df['Manufacturer Name'] == manufacturer]

    # Group the dataframe by Type Registration and Type Aircraft columns
    df_grouped = df_filtered.groupby(['Type Registration', 'Type Aircraft']).size().reset_index(name='counts')

    # Create a trace for each Type Registration value
    traces = []
    for type_r, df_type_r in df_grouped.groupby('Type Registration'):
        traces.append(go.Bar(
            x=df_type_r['Type Aircraft'],
            y=df_type_r['counts'],
            name=type_r,
            marker=dict(color=colors[type_r]),
            ))

    return {
        'data': traces,
        'layout': go.Layout(
            barmode='stack',
            xaxis=dict(title='Aircraft Type'),
            yaxis=dict(title='Count'),
            title=f'Type R vs Aircraft Type for {manufacturer}',
            margin={'t': 50, 'b': 120}
        )
    }


@app.callback(
    Output('dates-scatter-chart', 'figure'),
    [Input('cluster-date-dropdown', 'value')]
)
def update_graph(cluster):
    filtered_df = df[df['dates_cluster'] == int(cluster)]
    traces = []
    for i in range(3):
        cluster_df = filtered_df[filtered_df['dates_cluster'] == i]
        trace = go.Scatter(
            x=cluster_df['Certificate Issue Date'],
            y=cluster_df['Expiration Date'],
            mode='markers',
            marker={
                'size': 12,
                'color': 'rgb(51,204,153)',
                'symbol': 'circle',
                'line': {'width': 2}
            },
            name='dates_cluster {}'.format(i)
        )
        traces.append(trace)

    return {
        'data': traces,
        'layout': go.Layout(
            title='Aircraft Certification and Expiration Dates by Cluster',
            xaxis={'title': 'Certification Date'},
            yaxis={'title': 'Expiration Date'}
        )
    }



@app.callback(
    Output('aircraft-scatter-chart', 'figure'),
    [Input('cluster-aircraft-dropdown', 'value')]
)
def update_graph(cluster):
    filtered_df = df[df['aircraft_cluster'] == int(cluster)]

    x = [i[:12] for i in filtered_df['Model']]
    y = [i[:15] for i in filtered_df['Manufacturer Name']]
    traces = []
    trace = go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker={
            'size': 12,
            'color': 'rgb(51,204,153)',
            'symbol': 'circle',
            'line': {'width': 2}
        },
        name='Cluster {}'.format(cluster)
    )
    traces.append(trace)

    return {
        'data': traces,
        'layout': go.Layout(
            title='Manufacturer, Model, and Type of Engine Cluster',
            margin={'l': 150, 'r': 10, 't': 50, 'b': 120},
            xaxis={'title': 'Model'},
            yaxis={'title': 'Manufacturer Name'}
        )
    }

@app.callback(
    Output('type-scatter-chart', 'figure'),
    [Input('cluster-type-dropdown', 'value')]
)
def update_graph(cluster):
    filtered_df = df[df['type_cluster'] == int(cluster)]
    traces = []
    x = [str(i)[:12] for i in filtered_df['Type Registration']]
    y = [str(i)[:15] for i in filtered_df['Type Aircraft']]
    for i in range(3):
        cluster_df = filtered_df[filtered_df['type_cluster'] == i]
        trace = go.Scatter(
            x=x,
            y=y,
            mode='markers',
            marker={
                'size': 12,
                'color': 'rgb(51,204,153)',
                'symbol': 'circle',
                'line': {'width': 2}
            },
            name='type_cluster {}'.format(i)
        )
        traces.append(trace)

    return {
        'data': traces,
        'layout': go.Layout(
            title='Aircraft and Registration Type Cluster',
            xaxis={'title': 'Type R'},
            yaxis={'title': 'Aircraft Type'},
            margin={'l': 150, 'r': 10, 't': 50, 'b': 120}
        )
    }


@app.callback(
    Output('choropleth-country-map', 'figure'),
    [Input('manufacturer-dropdown', 'value')]
)
def update_choropleth(manufacturer):
    filtered_df = df[df['Manufacturer Name'] == manufacturer].groupby('Country').size()
    trace = go.Choropleth(locations=filtered_df.index,
                         locationmode='country names',
                         z=filtered_df.values)
    return {'data': [trace],
            'layout': go.Layout(title='Aircraft per Country',
                                geo={'scope': 'world'})}

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
