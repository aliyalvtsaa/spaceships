from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

import pandas as pd 
import numpy as np
from numpy import inf
import numpy as np

from scipy.spatial.distance import pdist, euclidean, squareform
import plotly.express as px
from plotly.graph_objs import *

spaceships = pd.read_csv('Ship game.csv', sep=';')
cols = [4,5,6]
spaceships.drop(spaceships.columns[cols],axis=1,inplace=True)
app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])


app.layout = html.Div([
    html.Div([html.P('Здравствуйте! Здесь вы можете произвести кластеризацию космических кораблей - передвигайте слайдер вправо.'),
             html.P('Номер означает количество групп + количество свободных кораблей')], style={"margin-bottom": 30, 'fontSize':21, 'font-weight':'bold', 'font-family':'Outfit'}),
    dcc.Slider(1, 7, step=1, 
               marks={7:'4', 6:'5',5: '6', 4:'7', 3:'8', 2:'9', 1:'10'},
               value=1,
               id='my-slider'
    ),
    dcc.Graph(id="clustering_graph"),
    html.Div(id="message_text", style={'fontSize':21, 'marginTop':30,'font-family':'Amatic'}),

], style={'marginTop': 45,'margin-left': 20, 'margin-right':20})

@callback(
    [Output('clustering_graph', 'figure'),
     Output('message_text', 'children')],
    [Input('my-slider', 'value')])


def c(number_of_groups):
    marks={10:'1',9:'2',8:'3',7:'4', 6:'5',5: '6', 4:'7', 3:'8', 2:'9', 1:'10'}
    number_of_groups=int(marks[number_of_groups])
    n=1
    attacking_spaceships=spaceships[2:12].reset_index(drop=True)
    attacking_spaceships['X_new']=attacking_spaceships['X_220'].copy()
    attacking_spaceships['Y_new']=attacking_spaceships['Y_220'].copy()
    attacking_spaceships['Z_new']=attacking_spaceships['Z_220'].copy()
    attacking_spaceships['group']=0
    num_of_iterations = len(attacking_spaceships) - number_of_groups
    if num_of_iterations==0:
        fig = px.scatter_3d(attacking_spaceships.sort_values(by='group'), x='X_220', y='Y_220', z='Z_220',
            color=attacking_spaceships.sort_values(by='group')['group'].astype(str), size_max=18, opacity=0.9, color_discrete_sequence=px.colors.qualitative.T10)
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
        camera = dict(eye=dict(x=1.7, y=-1.1, z=0.2))
        fig.update_layout(scene_camera=camera, template='plotly_dark', showlegend=False)
        message='Пока групп и свободных кораблей : 10'
        
    else:
        for i in range(num_of_iterations):  
            np_array=np.column_stack((attacking_spaceships['X_new'],attacking_spaceships['Y_new'],attacking_spaceships['Z_new']))
            distances = squareform(pdist(np_array, euclidean))
            np.fill_diagonal(distances, np.inf)
            distances[distances == 0] = inf
            smallest_distance_tuple=np.unravel_index(distances.argmin(), distances.shape)
            first_el_num=smallest_distance_tuple[0]
            second_el_num=smallest_distance_tuple[1]

            if attacking_spaceships['group'][first_el_num]==0 and attacking_spaceships['group'][second_el_num]==0:
                attacking_spaceships.loc[first_el_num, 'group'] = n
                attacking_spaceships.loc[second_el_num, 'group'] = n

                message=f"Создали новую группу {attacking_spaceships['Ship'][first_el_num]}+{attacking_spaceships['Ship'][second_el_num]}!"
            
            else:
                group_num=max(attacking_spaceships['group'][first_el_num], attacking_spaceships['group'][second_el_num])
                current_items=attacking_spaceships[attacking_spaceships['group']==group_num]['Ship'].to_list()
                
                current_items_string = '+'.join(current_items)
                smallest_distance_list=[attacking_spaceships['Ship'][first_el_num],attacking_spaceships['Ship'][second_el_num]]
                new_item=list(set(smallest_distance_list)- set(current_items))
                
                message=f'Добавили {new_item[0]} в группу {current_items_string}!\n => {current_items_string}+{new_item[0]}'
                
                attacking_spaceships.loc[first_el_num, 'group'] = group_num
                attacking_spaceships.loc[second_el_num, 'group'] = group_num
                
            number_group = attacking_spaceships['group'][first_el_num]
            n+=1
            indexes=attacking_spaceships[attacking_spaceships['group']==number_group].index.to_list()
            X_group = (attacking_spaceships['X_new'][first_el_num]+attacking_spaceships['X_new'][second_el_num])/2
            Y_group = (attacking_spaceships['Y_new'][first_el_num]+attacking_spaceships['Y_new'][second_el_num])/2
            Z_group = (attacking_spaceships['Z_new'][first_el_num]+attacking_spaceships['Z_new'][second_el_num])/2
            
            for item in indexes:
                attacking_spaceships.loc[item, 'X_new'] = X_group
                attacking_spaceships.loc[item, 'Y_new'] = Y_group
                attacking_spaceships.loc[item, 'Z_new'] = Z_group
            if i==num_of_iterations-1:

                fig = px.scatter_3d(attacking_spaceships.sort_values(by='group'), x='X_220', y='Y_220', z='Z_220',
                        color=attacking_spaceships.sort_values(by='group')['group'].astype(str), size_max=18, opacity=0.9, 
                        color_discrete_sequence=px.colors.qualitative.T10)
                fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
                camera = dict(eye=dict(x=1.7, y=-1.1, z=0.2))

                fig.update_layout(scene_camera=camera,  template='plotly_dark', showlegend=False)
                
    return fig, message

if __name__ == '__main__':
    app.run(debug=True)

