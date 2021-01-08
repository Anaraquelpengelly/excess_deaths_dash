

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
app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='two columns div-user-controls',
                             children=[
                                 html.H2('Excess deaths per Local Authority in England and Wales in 2020'),
                                 html.P('Visualising Excess deaths in the UK in 2020 at the local authority level. Data was downloaded from the ONS website.')
                                 
                                ]
                             ),
                    html.Div(className='ten columns div-for-charts bg-grey',
                             children=[
                                 html.H1(f'Excess deaths in {lads} in 2020', id="graph-title"),
                                 html.H5('Pick a Local Authority or country from the dropdown below'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                         dcc.Dropdown(id='ladselector', options=[{'label': i, 'value': i} for i in lads],
                                        #  placeholder="Select a local authority",
                                         value='England',
                                         style={'backgroundColor': '#1E1E1E'},
                                         className='ladselector'
                                                      )
                                     ],
                                     
                                     style={'color': '#1E1E1E',
                                     'font-size': '18px'}),
                                     html.H3(f'The total number of excess deaths in 2020 in {lads} .', id='total-num'),
                                        dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=False),
                                     html.H1(f'Excess deaths in 2020', id='title_weeks'),
                                     html.Div(id='radio-item-container', 
                                     children=[
                                         html.H5("Choose a time period: "),
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
                                                html.H5(
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
                                                        html.H3(f'Excess deaths in week 2020.', id='weekly-excess-deaths'),
                                                        dcc.Graph(id='map', config={'displayModeBar': False}, animate=False
                                                        )
                             ])
                              ])
        ]

)


# Callback for timeseries deaths
@app.callback(Output('timeseries', 'figure'),
              [Input('ladselector', 'value')])
def update_graph(selected_dropdown_value):
    trace1 = []
    df_sub = df[df['Area_Name'] == selected_dropdown_value]
    trace1.append(go.Scatter(x=df_sub['Week_Number'],
                                 y=df_sub['reg_deaths_20'],
                                 mode='lines',
                                 marker_color = 'magenta',
                                 opacity=0.7,
                                 name="Deaths in 2020",
                                 textposition='bottom center'))
    trace2= []
    df_sub = df[df['Area_Name'] == selected_dropdown_value]
    trace2.append(go.Scatter(x=df_sub['Week_Number'],
                                 y=df_sub['avg_reg_deaths_15_19'],
                                 mode='lines',
                                 marker_color='mintcream',
                                 opacity=0.7,
                                 name="Average deaths from 2015 to 2019",
                                 textposition='bottom center'))
    
    traces = [trace1, trace2]
    data = [val for sublist in traces for val in sublist]
    layout = go.Layout(
        #title={'text': f"Excess deaths in "+selected_dropdown_value+ " in 2020", 'font': {'color': 'white'}, 'x': 0.5},
        #           title={'text': f'Excess deaths in {selected_dropdown_value} in 2020','y':0.9,'x':0.5,'xanchor': 'center',
        # 'yanchor': 'top'},
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  xaxis_title='Week Number',
                  yaxis_title='Number of Deaths',
                  font=dict(
                        family="Roboto",
                        size=18),
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  xaxis={'range': [df_sub['Week_Number'].min(), df_sub['Week_Number'].max()]}, 
                  yaxis={'range': [0, (df_sub['reg_deaths_20'].max())]}
              )
    figure=go.Figure(data=data, layout=layout)


    return figure

#callback graph title
@app.callback(Output("graph-title", "children"), [Input("ladselector", "value")])
def update_graph_title(selected_dropdown_value):
    return f"Graph of excess deaths in 2020 in  {selected_dropdown_value}"


#callback total excess deaths text
@app.callback(Output("total-num", "children"), [Input("ladselector", "value")])
def update_total_num(selected_dropdown_value):
    return f"The total number of excess deaths in 2020 in {selected_dropdown_value} is {round(np.sum(df[df['Area_Name'] == selected_dropdown_value]['excess_deaths_per_100t_20']), 1)} per 100,000 inhabitants."
    
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
        return f'Map of yearly excess deaths in 2020.'
    if period == 'Weekly':
        return f'Map of excess deaths in week {selected_value} of 2020'

#call back weekly excess deaths:

@app.callback(Output('weekly-excess-deaths', 'children'),
            [Input('period', 'value'),
            Input('weeks-slider', 'value')])
def update_w_ex_deaths(period, selected_value):
    if period == 'Yearly':
        x=round(np.sum(df[df['Area_Name'].isin(['England', 'Wales'])]['Excess_2020_from_avg']), 1)
        return f'The total excess deaths in England and Wales in 2020 compared to the average of 2015-2019 was {x}.' 
    if period == 'Weekly':
        x=round(np.sum(df_maps[df_maps['Week_Number'] == selected_value]['Excess_2020_from_avg']), 1)
        return f"The total excess deaths in week {selected_value} of 2020 compared to the average in 2015-2019 in week {selected_value} was {x}."



if __name__ == '__main__':
    app.run_server(debug=True)