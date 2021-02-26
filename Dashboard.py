import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import joblib
from datetime import datetime
import plotly.graph_objs as go
import math 
import pyowm
import pandas as pd
import json as js 

with open("/home/juniorwafo/App/parameters.json","r")as f:
	DashBordParameter=js.load(f)
with open("/home/juniorwafo/App/variete.json","r")as f:
	Varietes=js.load(f)
new= pd.read_csv("./savoigne.csv", sep=";")
new["Date"]=new["Date"].apply(lambda x:datetime.strptime(x,"%d/%m/%Y"))
def calcul_Kc(day):
	d1 = datetime.strptime(DashBordParameter["Semis"]["value"], "%Y-%m-%d")
	delta = abs((day-d1).days)
	h = len(Varietes["phases"]["dates"])
	j = -1
	Kc = 0.5 
	while j < h-1 and delta  >= Varietes["phases"]["dates"][j+1]:
		j += 1
	if 0 <= j < h-1:
		print(delta)
		duree = Varietes["phases"]["dates"][j+1]-Varietes["phases"]["dates"][j]
		coeff = ( Varietes["phases"]["Kc"][j+1]-Varietes["phases"]["Kc"][j] )/duree
		Kc = (delta-Varietes["phases"]["dates"][j])*coeff+Varietes["phases"]["Kc"][j]
	return Kc
def calcul_Ra(day):
	year=day.year
	d1 = datetime.strptime(f"{year}-01-01", "%Y-%m-%d")
	delta = abs((day-d1).days)
	Ra = DashBordParameter["Ra0"]["value"]*(1+DashBordParameter["Ra_constant"]["value"]*math.cos(2*math.pi*delta/365))
	return Ra
def calcul_Etp(day,tmax,tmin):
	Ra = calcul_Ra(day)
	delta = tmax-tmin
	Et0 = DashBordParameter["Etp_reducer"]["value"]*(DashBordParameter["Etp_intercept"]["value"]+delta*0.5)*((delta)**0.5)*Ra*DashBordParameter["Etp_conversion"]["value"]
	return Et0
new["Ra"] = new["Date"].apply(calcul_Ra)
new["Kc"] = new["Date"].apply(calcul_Kc)
new["Etp"] = new.apply(lambda x: x["Kc"]*calcul_Etp(x["Date"],x["Tmax"],x["Tmin"]),axis=1)
print(new["Etp"].mean())
app = dash.Dash()

app.layout = html.Div(id="main", children=[

    html.H1(id="title",children='Irrigation monitoring dashboard', style={'textAlign': 'center'}),
    html.Form(id="Parameters",
    	style={"position":"fixed",
    			"right":"0px",
    			"z-index":"1000"
    	},
    	children=[html.Label(style={"display":"flex", "justify-content":"space-Between"},children=[f"{x}",dcc.Input(id=x,value=DashBordParameter[x]["value"],type= DashBordParameter[x]["type"],min=DashBordParameter[x]["min"],max=DashBordParameter[x]["max"],step=DashBordParameter[x]["step"])])
    	for x in DashBordParameter if x!="Semis"
    	]
    	),
    html.Div(id="graphs", 
    	style={"display":"flex",
    	"flex-direction":"row",
    	"flex-wrap":"wrap"},
    	children=[
    dcc.Graph( id='Temperature' ,
    	figure = {
            'data': [
                go.Scatter(
                    x=new['Date'],
                    y=new["Tmax"],
                    name="Tmax",
                    mode='lines+markers',
                    opacity=0.7,
                    marker={
                        'size': 5,
                        'line': {'width': 0.5, 'color': 'green'}
                    },
                ),
                go.Scatter(
                    x=new['Date'],
                    y=new["Tmin"],
                    name="Tmin",
                    mode='lines+markers',
                    opacity=0.7,
                    marker={
                        'size': 5,
                        'line': {'width': 0.5, 'color': 'green'}
                    },
                )
            ],
            'layout': go.Layout(
                xaxis={'title': 'date'},
                yaxis={'title': 'Temperature'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                width=500,height=250,
                hovermode='closest'
            )
        }
    ),
    dcc.Graph(
        id='Precipitation',
        figure={
            'data': [
                go.Scatter(
                    x=new['Date'],
                    y=new["Pluie"],
                    mode='lines+markers',
                    opacity=0.7,
                    marker={
                        'size': 5,
                        'line': {'width': 0.2, 'color': 'white'}
                    },
                ),
            ],
            'layout': go.Layout(
                xaxis={ 'title': 'Date'},
                yaxis={'title': 'Precipitation'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                width=500,height=250,
                hovermode='closest'
            )
        }
    ),
    
    dcc.Graph(
        id='Ra',
        figure={
            'data': [
                go.Scatter(
                    x=new['Date'],
                    y=new["Ra"],
                    mode='lines+markers',
                    opacity=0.7,
                    marker={
                        'size': 5
                    },
                    line = {
                    'width': 0.2, 
                    'color': 'red',
                    'dash':"5",
                    'shape':"spline"
                    }
                ),
            ],
            'layout': go.Layout(
                xaxis={ 'title': 'Date'},
                yaxis={'title': 'Ra'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                width=500,height=250,
                hovermode='closest'
            )
        }
    ),
    dcc.Graph(
        id='Kc',
        figure={
            'data': [
                go.Scatter(
                    x=new['Date'],
                    y=new["Kc"],
                    mode='lines+markers',
                    opacity=0.7,
                    marker={
                        'size': 5
                    },
                    line = {
                    'width': 0.2, 
                    'color': 'red',
                    'dash':"5",
                    'shape':"spline"
                    }
                ),
            ],
            'layout': go.Layout(
                xaxis={ 'title': 'Date'},
                yaxis={'title': 'Kc'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                width=500,height=250,
                hovermode='closest'
            )
        }
    ),
    dcc.Graph(
        id='Evapotranspiration',
        figure={
            'data': [
                go.Scatter(
                    x=new['Date'],
                    y=new["Etp"],
                    mode='lines+markers',
                    opacity=0.7,
                    marker={
                        'size': 5,
                        'line': {'width': 0.2, 'color': 'red'}
                    },
                ),
            ],
            'layout': go.Layout(
                xaxis={ 'title': 'Date'},
                yaxis={'title': 'Evapotranspiration reelle'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                width=500,height=250,
                hovermode='closest'
            )
        }
    ),
])])


# @app.callback(
#     Output(component_id='result', component_property='children'),
#     [Input(component_id='years-of-experience', component_property='value')])
# def update_years_of_experience_input(years_of_experience):
#     if years_of_experience not in ['', None]:
#         try:
#             salary = model.predict([[float(years_of_experience)]])[0]
#             return 'With {} years of experience you should earn a salary of ${:,.2f}'.\
#                 format(years_of_experience, salary, 2)
#         except ValueError:
#             return 'Unable to give years of experience'


if __name__ == '__main__':
    app.run_server(debug=True)