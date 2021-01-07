import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import pathlib
import json
#read data

DATA_PATH = pathlib.Path(__file__).parent.joinpath("data")
ASSET_PATH = pathlib.Path(__file__).parent.joinpath("assets")

df = pd.read_csv(DATA_PATH.joinpath('excess_deaths_uk_w51.csv'))
#list of LADs for graphs:
lads= df['Area_Name'].unique().tolist()
#df for chloropleth (without england and wales)
df_maps=df[~df['Area_Name'].isin(['Wales', 'England'])]
#list of lads for map:
areas= df_maps['Area_Name'].unique().tolist()
#create a week '53' row to represent the whole year
for l in areas:
    new_row = {'Area_Code': list(df_maps[df_maps['Area_Name'] == l]['Area_Code'])[0], 
               'Area_Name': l, 
              'Week_Number':53, 
               'reg_deaths_15':np.sum(df_maps[df_maps['Area_Name'] == l]['reg_deaths_15']),
               'reg_deaths_16':np.sum(df_maps[df_maps['Area_Name'] == l]['reg_deaths_16']), 
                'reg_deaths_17':np.sum(df_maps[df_maps['Area_Name'] == l]['reg_deaths_17']),
                'reg_deaths_18':np.sum(df_maps[df_maps['Area_Name'] == l]['reg_deaths_18']), 
                'reg_deaths_19': np.sum(df_maps[df_maps['Area_Name'] == l]['reg_deaths_19']),
       'avg_reg_deaths_15_19':np.sum(df_maps[df_maps['Area_Name'] == l]['avg_reg_deaths_15_19']),
        'reg_deaths_20': np.sum(df_maps[df_maps['Area_Name'] == l]['reg_deaths_20']), 
        'Excess_2020_from_avg':np.sum(df_maps[df_maps['Area_Name'] == l]['Excess_2020_from_avg']),
       'estimated_2019_pop': list(df_maps[df_maps['Area_Name'] == l]['estimated_2019_pop'])[0],
        'excess_deaths_per_100t_20': np.sum(df_maps[df_maps['Area_Name'] == l]['excess_deaths_per_100t_20'])}
    #append row to the dataframe
    df_maps = df_maps.append(new_row, ignore_index=True)
#VERY IMPORTANT: create a column in the df_maps that has the name 'lad17nm' which corresponds to the json file name:
df_maps['lad17nm']=df_maps['Area_Name']
df_maps['lad17cd']=df_maps['Area_Code']
#list of weeks:
weeks= list(range(1,53))
#list of periods:
periods = ['Weekly', 'Yearly']
# get geojson for the choropleth
with open(ASSET_PATH.joinpath('Local_Authority_Districts_(December_2017)_Generalised_Clipped_Boundaries_in_Great_Britain.geojson')) as f:
    const = json.load(f)


#initialise the app:

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

#define layout
app.layout = html.Div(className='ten columns div-for-charts bg-grey',
                             children=[
                                     html.H1(f'Excess deaths in 2020'),
                                     html.Div(id='radio-item-container', 
                                     children=[
                                         html.H3("Choose a time period: "),
                                         dcc.RadioItems(
                                            id='period', 
                                            options=[{'value': x, 'label': x} 
                                                    for x in periods],
                                            value=periods[1],
                                            labelStyle={ "color": "white", 'font-family':'Roboto' }
                                        )]),
                                     html.Div(
                                        id="slider-container",
                                        children=[
                                                html.H3(
                                                id="slider-text",
                                                children="Drag the slider to change the week:"),
                                                dcc.Slider(
                                                    id="weeks-slider",
                                                    min=min(weeks),
                                                    max=max(weeks),
                                                    value=min(weeks),
                                                    marks={
                                                        str(w): {
                                                        "label": str(w),
                                                        "style": {"color": "white", 'font-family':'Roboto'},} for w in weeks})
                                                        ]),
                                                        html.H2(f'Excess deaths in week 2020.', id='title_weeks'),
                                                        dcc.Graph(id='map', config={'displayModeBar': False}, animate=False
                                                        )
                             ])


# Callback for map deaths
@app.callback(Output('map', 'figure'),
              [Input('period', 'value'),
              Input('weeks-slider', 'value')], 
              [State('map', 'figure')])
def update_chloro(period, selected_value, figure):

        if period == 'Yearly':
            df=df_maps[df_maps['Week_Number'] == 53]
            
            df['text'] = " "+ df['Area_Name'] + '<br>' + \
            ' Excess deaths per 100,000: ' + round(df['excess_deaths_per_100t_20'],2).astype(str) + '<br>' + \
            ' Raw excess deaths: ' + round(df['Excess_2020_from_avg'], 2).astype(str)


            fig=go.Figure(data=go.Choropleth(
                locations=df['lad17cd'], # Spatial coordinates
                z = df["excess_deaths_per_100t_20"].astype(float), # Data to be color-coded
        #     locationmode = 'USA-states', # set of locations match entries in `locations`
                colorscale = 'Reds',
                text = df['text'],
                hoverinfo = 'text',
                colorbar_title = f"Excess deaths <br> per 100 thousand <br>",
                geojson=const,
                featureidkey="properties.lad17cd", 
                locationmode="geojson-id",
                marker_line_color='white',
                autocolorscale=True,
                reversescale=True, 
                zmax=270,
                zmin=-210
                ))
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                font=dict(
                family="Roboto",
                size=20,
                color="white"),
                template='plotly_dark',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                geo = dict(
                projection=go.layout.geo.Projection(type = 'mercator'),
                showlakes=True, # lakes
                lakecolor='rgb(255, 255, 255)'),
                height=1000)
            return fig

        if period == 'Weekly':
            df=df_maps[df_maps['Week_Number'] == selected_value]
        
            df['text'] = " "+ df['Area_Name'] + '<br>' + \
            ' Excess deaths per 100,000: ' + round(df['excess_deaths_per_100t_20'],2).astype(str) + '<br>' + \
            ' Raw excess deaths: ' + round(df['Excess_2020_from_avg'], 2).astype(str)


            fig=go.Figure(data=go.Choropleth(
                locations=df['lad17cd'], # Spatial coordinates
                z = df["excess_deaths_per_100t_20"].astype(float), # Data to be color-coded
        #     locationmode = 'USA-states', # set of locations match entries in `locations`
                colorscale = 'Reds',
                text = df['text'],
                hoverinfo = 'text',
                colorbar_title = f"Excess deaths <br> per 100 thousand <br><br>",
                geojson=const,
                featureidkey="properties.lad17cd", 
                locationmode="geojson-id",
                marker_line_color='white',
                autocolorscale=True,
                reversescale=True, 
                zmax=100,
                zmin=-65
                ))
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                font=dict(
                family="Roboto",
                size=20,
                color="white"),
                template='plotly_dark',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                geo = dict(
                projection=go.layout.geo.Projection(type = 'mercator'),
                showlakes=True, # lakes
                lakecolor='rgb(255, 255, 255)'),
                height=1000)

            return fig



#callback map title    
@app.callback(Output('title_weeks', 'children'),
            [Input('period', 'value'),
            Input('weeks-slider', 'value')])
def update_map_title(period, selected_value):
    if period == 'Yearly':
        return f'Yearly excess deaths in 2020.'
    if period == 'Weekly':
        return f'Excess deaths in week {selected_value}'


if __name__ == '__main__':
    app.run_server(debug=True)