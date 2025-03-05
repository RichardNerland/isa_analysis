import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time

# Import the simplified model
from simple_isa_model import run_simple_simulation

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Expose the server variable for production

# Enable the app to be embedded in an iframe
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>ISA Analysis Tool</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Dropdown options for number of students
student_options = [
    {'label': '10 students', 'value': 10},
    {'label': '50 students', 'value': 50},
    {'label': '100 students', 'value': 100},
    {'label': '200 students', 'value': 200},
    {'label': '500 students', 'value': 500}
]

# Dropdown options for number of simulations
sim_options = [
    {'label': '10 simulations (faster)', 'value': 10},
    {'label': '50 simulations', 'value': 50},
    {'label': '100 simulations (recommended)', 'value': 100}
]

# Define the preset scenarios from the original notebook
preset_scenarios = {
    'Baseline': {
        'description': 'Standard distribution with balanced degree types.',
        'degrees': {'BA': 0.43, 'MA': 0.23, 'VOC': 0.25, 'NURSE': 0.0, 'NA': 0.09}
    },
    'Conservative': {
        'description': 'More vocational degrees, fewer advanced degrees.',
        'degrees': {'BA': 0.3, 'MA': 0.1, 'VOC': 0.4, 'NURSE': 0.0, 'NA': 0.2}
    },
    'Optimistic': {
        'description': 'Mostly bachelor and master degrees with very few dropouts.',
        'degrees': {'BA': 0.625, 'MA': 0.325, 'VOC': 0.025, 'NURSE': 0.0, 'NA': 0.025}
    },
    'High Immigration': {
        'description': 'High percentage of students who don\'t complete degrees or return home.',
        'degrees': {'BA': 0.3, 'MA': 0.1, 'VOC': 0.1, 'NURSE': 0.0, 'NA': 0.5}
    },
    'TVET Baseline': {
        'description': 'TVET baseline scenario with balanced nursing and vocational degrees.',
        'degrees': {'BA': 0.0, 'MA': 0.0, 'VOC': 0.45, 'NURSE': 0.45, 'NA': 0.1}
    },
    'TVET Conservative': {
        'description': 'Conservative TVET scenario with more vocational degrees.',
        'degrees': {'BA': 0.0, 'MA': 0.0, 'VOC': 0.60, 'NURSE': 0.25, 'NA': 0.15}
    }
}

# Define the layout of the app
app.layout = html.Div([
    html.H1("ISA Analysis Tool", style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    # Tabs for different sections
    dcc.Tabs([
        dcc.Tab(label='About', children=[
            html.Div([
                html.H2("About the ISA Analysis Tool", style={'marginBottom': '20px'}),
                
                html.Div([
                    html.H3("Overview"),
                    html.P([
                        "This tool simulates Income Share Agreement (ISA) outcomes for different educational programs. ",
                        "It models student earnings, payments, and returns to investors based on various economic and program-specific parameters."
                    ]),
                    
                    html.H3("Key Features"),
                    html.Ul([
                        html.Li("Simulate ISA outcomes for University and TVET programs"),
                        html.Li("Multiple predefined scenarios (baseline and conservative)"),
                        html.Li("Customizable degree distributions and parameters"),
                        html.Li("Detailed economic modeling including inflation, unemployment, and experience-based earnings growth"),
                        html.Li("Analysis of investor returns and student payment patterns")
                    ]),
                    
                    html.H3("Model Assumptions"),
                    html.H4("Degree Types and Earnings"),
                    html.P("The model includes several degree types with different earnings profiles:"),
                    
                    html.Div([
                        html.H5("Bachelor's Degree (BA)"),
                        html.Ul([
                            html.Li("Mean annual earnings: $41,300"),
                            html.Li("Standard deviation: $13,000"),
                            html.Li("Experience growth: 4% annually"),
                            html.Li("Years to complete: 4")
                        ])
                    ], style={'marginLeft': '20px'}),
                    
                    html.Div([
                        html.H5("Master's Degree (MA)"),
                        html.Ul([
                            html.Li("Mean annual earnings: $46,709"),
                            html.Li("Standard deviation: $15,000"),
                            html.Li("Experience growth: 4% annually"),
                            html.Li("Years to complete: 6")
                        ])
                    ], style={'marginLeft': '20px'}),
                    
                    html.Div([
                        html.H5("Vocational Training (VOC)"),
                        html.Ul([
                            html.Li("Mean annual earnings: $31,500"),
                            html.Li("Standard deviation: $4,800"),
                            html.Li("Experience growth: 4% annually"),
                            html.Li("Years to complete: 3")
                        ])
                    ], style={'marginLeft': '20px'}),
                    
                    html.Div([
                        html.H5("Nursing Degree (NURSE)"),
                        html.Ul([
                            html.Li("Mean annual earnings: $44,000"),
                            html.Li("Standard deviation: $8,400"),
                            html.Li("Experience growth: 1% annually"),
                            html.Li("Years to complete: 4")
                        ])
                    ], style={'marginLeft': '20px'}),
                    
                    html.Div([
                        html.H5("No Advancement (NA)"),
                        html.Ul([
                            html.Li("Mean annual earnings: $2,200"),
                            html.Li("Standard deviation: $640"),
                            html.Li("Experience growth: 1% annually"),
                            html.Li("Years to complete: 4"),
                            html.Li("High probability (80%) of returning to home country")
                        ])
                    ], style={'marginLeft': '20px'}),
                    
                    html.H4("Earnings Methodology"),
                    html.P([
                        "The earnings values were derived from average salary levels found in public data sources, ",
                        "with a 15% wage penalty applied to account for the fact that students are typically at the beginning ",
                        "of their careers and earn less than the average worker in their field."
                    ]),
                    
                    html.Div([
                        html.P([
                            html.Strong("Nursing Earnings: "),
                            "Based on median monthly wage of $4,056 (25th percentile: $3,608, 75th percentile: $4,552), ",
                            "annualized to $48,672 with a standard deviation of $8,400. A 15% student wage penalty was applied, ",
                            "resulting in $44,000 mean earnings."
                        ]),
                        html.P([
                            html.Strong("Vocational Earnings: "),
                            "Based on median monthly wage of $2,640 (25th percentile: $2,383, 75th percentile: $2,924), ",
                            "annualized to $31,680 with a standard deviation of $4,800. No additional wage penalty was applied ",
                            "as these values already reflect entry-level positions."
                        ])
                    ], style={'marginLeft': '20px'}),
                    
                    html.H4("Predefined Scenarios"),
                    html.Div([
                        html.H5("University Programs"),
                        html.Ul([
                            html.Li("Baseline: Standard distribution with balanced degree types"),
                            html.Li("Conservative: More vocational degrees, fewer advanced degrees"),
                            html.Li("Optimistic: Mostly bachelor and master degrees with very few dropouts"),
                            html.Li("High Immigration: High percentage of students who don't complete degrees or return home")
                        ])
                    ], style={'marginLeft': '20px'}),
                    
                    html.Div([
                        html.H5("TVET Programs"),
                        html.Ul([
                            html.Li("TVET Baseline: 45% nursing, 45% vocational, 10% no advancement"),
                            html.Li("TVET Conservative: 25% nursing, 60% vocational, 15% no advancement")
                        ])
                    ], style={'marginLeft': '20px'}),
                    
                    html.H4("Economic Parameters"),
                    html.Ul([
                        html.Li("Default inflation rate: 2% annually"),
                        html.Li("Default unemployment rate: 4%"),
                        html.Li("ISA threshold: $27,000 (minimum income before payments begin)"),
                        html.Li("ISA cap: Varies by program ($72,500 for University, $49,950 for TVET)"),
                        html.Li("ISA percentage: Varies by program (14% for University, 12% for TVET)")
                    ]),
                    
                    html.H4("Foreign Student Modeling"),
                    html.P([
                        "The model accounts for students who return to their home countries after graduation through the ",
                        "'home_prob' parameter. When a student returns home, their earnings are significantly reduced, ",
                        "reflecting the typically lower wages in developing countries. This is particularly relevant for ",
                        "students in the No Advancement (NA) category, who have an 80% probability of returning home."
                    ])
                ], style={'marginLeft': '20px', 'marginRight': '20px'})
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='Simulation', children=[
            html.Div([
                html.H1("ISA Analysis Dashboard", style={'textAlign': 'center', 'marginBottom': '30px'}),
                
                html.Div([
                    html.Div([
                        html.H3("Program Parameters", style={'marginBottom': '20px'}),
                        
                        html.Div([
                            html.Label("Program Type:"),
                            dcc.RadioItems(
                                id="program-type",
                                options=[
                                    {'label': 'University', 'value': 'University'},
                                    {'label': 'TVET', 'value': 'TVET'}
                                ],
                                value="University",
                                labelStyle={'display': 'block', 'marginBottom': '10px'},
                            ),
                        ], style={'marginBottom': '20px'}),
                        
                        html.Div([
                            html.Label("Degree Distribution:"),
                            dcc.RadioItems(
                                id="degree-distribution-type",
                                options=[
                                    {'label': 'Custom Distribution', 'value': 'custom'}
                                ],
                                value="custom",
                                labelStyle={'display': 'block', 'marginBottom': '10px'},
                            ),
                        ], style={'marginBottom': '15px'}),
                        
                        # Custom degree distribution section (visible by default now)
                        html.Div(id="custom-degree-section", children=[
                            html.Div([
                                html.Div([
                                    html.Label("Degree Parameters", style={'fontWeight': 'bold', 'fontSize': '16px', 'marginBottom': '10px'})
                                ], style={'textAlign': 'center', 'marginBottom': '15px'}),
                                
                                # Table headers
                                html.Div([
                                    html.Div([html.Label("Degree Type")], style={'width': '20%', 'display': 'inline-block', 'fontWeight': 'bold'}),
                                    html.Div([html.Label("Percentage (%)")], style={'width': '20%', 'display': 'inline-block', 'fontWeight': 'bold'}),
                                    html.Div([html.Label("Avg Salary ($)")], style={'width': '20%', 'display': 'inline-block', 'fontWeight': 'bold'}),
                                    html.Div([html.Label("Std Dev ($)")], style={'width': '20%', 'display': 'inline-block', 'fontWeight': 'bold'}),
                                    html.Div([html.Label("Growth Rate (%)")], style={'width': '20%', 'display': 'inline-block', 'fontWeight': 'bold'}),
                                ], style={'marginBottom': '10px', 'textAlign': 'center'}),
                                
                                # Bachelor's row
                                html.Div([
                                    html.Div([html.Label("Bachelor's (BA)")], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="ba-pct", 
                                            type="number", 
                                            value=43, 
                                            min=0, 
                                            max=100, 
                                            step=1,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="ba-salary", 
                                            type="number", 
                                            value=41300, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="ba-std", 
                                            type="number", 
                                            value=13000, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="ba-growth", 
                                            type="number", 
                                            value=4.0, 
                                            min=0, 
                                            max=20, 
                                            step=0.1,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                ], style={'marginBottom': '10px'}),
                                
                                # Master's row
                                html.Div([
                                    html.Div([html.Label("Master's (MA)")], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="ma-pct", 
                                            type="number", 
                                            value=23, 
                                            min=0, 
                                            max=100, 
                                            step=1,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="ma-salary", 
                                            type="number", 
                                            value=46709, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="ma-std", 
                                            type="number", 
                                            value=15000, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="ma-growth", 
                                            type="number", 
                                            value=4.0, 
                                            min=0, 
                                            max=20, 
                                            step=0.1,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                ], style={'marginBottom': '10px'}),
                                
                                # Nursing row
                                html.Div([
                                    html.Div([html.Label("Nursing (NURSE)")], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="nurse-pct", 
                                            type="number", 
                                            value=0, 
                                            min=0, 
                                            max=100, 
                                            step=1,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="nurse-salary", 
                                            type="number", 
                                            value=44000, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="nurse-std", 
                                            type="number", 
                                            value=8400, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="nurse-growth", 
                                            type="number", 
                                            value=1.0, 
                                            min=0, 
                                            max=20, 
                                            step=0.1,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                ], style={'marginBottom': '10px'}),
                                
                                # Vocational row
                                html.Div([
                                    html.Div([html.Label("Vocational (VOC)")], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="voc-pct", 
                                            type="number", 
                                            value=25, 
                                            min=0, 
                                            max=100, 
                                            step=1,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="voc-salary", 
                                            type="number", 
                                            value=31500, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="voc-std", 
                                            type="number", 
                                            value=4800, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="voc-growth", 
                                            type="number", 
                                            value=4.0, 
                                            min=0, 
                                            max=20, 
                                            step=0.1,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                ], style={'marginBottom': '10px'}),
                                
                                # No Degree row
                                html.Div([
                                    html.Div([html.Label("No Degree (NA)")], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="na-pct", 
                                            type="number", 
                                            value=9, 
                                            min=0, 
                                            max=100, 
                                            step=1,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="na-salary", 
                                            type="number", 
                                            value=2200, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="na-std", 
                                            type="number", 
                                            value=640, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="na-growth", 
                                            type="number", 
                                            value=1.0, 
                                            min=0, 
                                            max=20, 
                                            step=0.1,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                ], style={'marginBottom': '10px'}),
                                
                                html.Div(id="degree-sum-warning", style={'color': 'red', 'marginTop': '10px', 'textAlign': 'center'})
                            ])
                        ], style={'marginBottom': '20px', 'display': 'block', 'backgroundColor': '#f1f1f1', 'padding': '15px', 'borderRadius': '5px'}),
                        
                        # Add ISA Parameter Controls
                        html.Div([
                            html.Label("ISA Parameters", style={'fontWeight': 'bold', 'fontSize': '16px', 'marginBottom': '10px'}),
                            
                            html.Div([
                                html.Div([html.Label("ISA Percentage (%)")], style={'width': '33%', 'display': 'inline-block'}),
                                html.Div([html.Label("ISA Threshold ($)")], style={'width': '33%', 'display': 'inline-block'}),
                                html.Div([html.Label("ISA Cap ($)")], style={'width': '33%', 'display': 'inline-block'}),
                            ], style={'marginBottom': '5px', 'textAlign': 'center'}),
                            
                            html.Div([
                                html.Div([
                                    dcc.Input(
                                        id="isa-percentage-input", 
                                        type="number", 
                                        value=14,  # Default to University values
                                        min=0, 
                                        max=100, 
                                        step=0.1,
                                        style={'width': '100%'}
                                    )
                                ], style={'width': '33%', 'display': 'inline-block'}),
                                
                                html.Div([
                                    dcc.Input(
                                        id="isa-threshold-input", 
                                        type="number", 
                                        value=27000,
                                        min=0, 
                                        step=1000,
                                        style={'width': '100%'}
                                    )
                                ], style={'width': '33%', 'display': 'inline-block'}),
                                
                                html.Div([
                                    dcc.Input(
                                        id="isa-cap-input", 
                                        type="number", 
                                        value=72500,  # Default to University values
                                        min=0, 
                                        step=1000,
                                        style={'width': '100%'}
                                    )
                                ], style={'width': '33%', 'display': 'inline-block'}),
                            ], style={'marginBottom': '20px'}),
                        ], style={'marginBottom': '20px', 'backgroundColor': '#e6f7ff', 'padding': '15px', 'borderRadius': '5px'}),
                        
                        html.Div([
                            html.Label("Preset Scenarios:"),
                            dcc.Dropdown(
                                id="preset-scenario",
                                options=[{'label': k, 'value': k} for k in preset_scenarios.keys()],
                                value="Baseline",
                                placeholder="Select a preset scenario (optional)"
                            ),
                            html.Div(id="preset-description", style={'color': '#666', 'fontSize': '0.9em', 'marginTop': '5px'})
                        ], style={'marginBottom': '20px'}),
                        
                        html.Div([
                            html.Label("Number of Students:"),
                            dcc.Dropdown(
                                id="num-students",
                                options=student_options,
                                value=100
                            ),
                        ], style={'marginBottom': '20px'}),
                        
                        html.Div([
                            html.Label("Number of Simulations:"),
                            dcc.Dropdown(
                                id="num-sims",
                                options=sim_options,
                                value=50
                            ),
                        ], style={'marginBottom': '20px'}),
                        
                        html.Div([
                            html.Label("Home Probability (%):"),
                            dcc.Slider(
                                id="home-prob",
                                min=0,
                                max=50,
                                step=5,
                                value=0,
                                marks={i: f'{i}%' for i in range(0, 51, 10)},
                            ),
                        ], style={'marginBottom': '20px'}),
                        
                        html.Div([
                            html.Label("Initial Unemployment Rate (%):"),
                            dcc.Slider(
                                id="unemployment-rate",
                                min=0,
                                max=20,
                                step=1,
                                value=4,
                                marks={i: f'{i}%' for i in range(0, 21, 5)},
                            ),
                        ], style={'marginBottom': '20px'}),
                        
                        html.Div([
                            html.Label("Initial Inflation Rate (%):"),
                            dcc.Slider(
                                id="inflation-rate",
                                min=0,
                                max=10,
                                step=0.5,
                                value=2,
                                marks={i: f'{i}%' for i in range(0, 11, 2)},
                            ),
                        ], style={'marginBottom': '30px'}),
                        
                        html.Div([
                            html.Button(
                                "Run Simulation", 
                                id="run-simulation", 
                                n_clicks=0,
                                style={
                                    'backgroundColor': '#4CAF50',
                                    'color': 'white',
                                    'padding': '12px 20px',
                                    'borderRadius': '5px',
                                    'border': 'none',
                                    'fontSize': '16px',
                                    'cursor': 'pointer',
                                    'width': '100%',
                                    'fontWeight': 'bold'
                                }
                            ),
                            html.Div(id="loading-message", style={'marginTop': '10px', 'color': '#888'})
                        ])
                    ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'backgroundColor': '#f9f9f9', 'borderRadius': '8px'}),
                    
                    html.Div([
                        html.H3("Results"),
                        
                        html.Div([
                            html.Div(id="summary-stats", style={'marginBottom': '20px'}),
                            
                            dcc.Tabs([
                                dcc.Tab(label='Scenarios', children=[
                                    html.Div(id="scenario-info")
                                ]),
                                dcc.Tab(label='Payment Distribution', children=[
                                    dcc.Graph(id="payment-distribution")
                                ]),
                                dcc.Tab(label='Investor vs Malengo', children=[
                                    dcc.Graph(id="investor-malengo-split")
                                ]),
                                dcc.Tab(label='Degree Information', children=[
                                    html.Div(id="degree-info")
                                ]),
                                dcc.Tab(label='IRR Distribution', children=[
                                    dcc.Graph(id="irr-distribution")
                                ]),
                                dcc.Tab(label='Student Outcomes', children=[
                                    html.Div([
                                        html.Div(id="student-outcome-stats", style={'marginBottom': '15px'}),
                                        dcc.Graph(id="repayment-caps-chart")
                                    ])
                                ]),
                                dcc.Tab(label='Detailed Results', children=[
                                    html.Div(id="detailed-results")
                                ])
                            ], style={'marginTop': '20px'})
                        ])
                    ], style={'width': '65%', 'display': 'inline-block', 'padding': '20px', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'backgroundColor': '#f9f9f9', 'borderRadius': '8px'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px', 'marginBottom': '30px'}),
            ])
        ])
    ]),
    
    dcc.Store(id='simulation-results-store')
])

# Callback to toggle the custom degree section visibility
@app.callback(
    Output("custom-degree-section", "style"),
    [Input("degree-distribution-type", "value")]
)
def toggle_custom_degree_section(distribution_type):
    if distribution_type == "custom":
        return {'marginBottom': '20px', 'display': 'block', 'backgroundColor': '#f1f1f1', 'padding': '15px', 'borderRadius': '5px'}
    else:
        return {'marginBottom': '20px', 'display': 'none'}

# Callback to validate degree distribution percentages
@app.callback(
    Output("degree-sum-warning", "children"),
    [Input("ba-pct", "value"),
     Input("ma-pct", "value"),
     Input("voc-pct", "value"),
     Input("nurse-pct", "value"),
     Input("na-pct", "value")]
)
def validate_degree_sum(ba_pct, ma_pct, voc_pct, nurse_pct, na_pct):
    total = ba_pct + ma_pct + voc_pct + nurse_pct + na_pct
    if total == 0:
        return "Error: At least one degree type must have a percentage greater than 0."
    elif total != 100:
        return f"Warning: Percentages sum to {total}%, not 100%. Values will be normalized."
    else:
        return ""

# Callback to update sliders when a preset is selected
@app.callback(
    [Output("ba-pct", "value"),
     Output("ma-pct", "value"),
     Output("voc-pct", "value"),
     Output("nurse-pct", "value"),
     Output("na-pct", "value"),
     Output("degree-distribution-type", "value"),
     Output("preset-description", "children")],
    [Input("preset-scenario", "value"),
     Input("program-type", "value")]
)
def update_from_preset(preset_name, program_type):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Use different default presets based on program type
    if preset_name is None or preset_name not in preset_scenarios:
        if program_type == 'University':
            # Default to Baseline for University
            preset_name = 'Baseline'
        else:
            # Default to TVET Baseline for TVET
            preset_name = 'TVET Baseline'
    
    # If program type changed and we have a preset that's better suited for the new program type
    if triggered_id == 'program-type':
        if program_type == 'University' and preset_name in ['TVET Baseline', 'TVET Conservative']:
            preset_name = 'Baseline'
        elif program_type == 'TVET' and preset_name in ['Baseline', 'Conservative', 'Optimistic', 'High Immigration']:
            preset_name = 'TVET Baseline'
    
    # Get the preset
    preset = preset_scenarios[preset_name]
    degrees = preset['degrees']
    
    # Set the sliders to the preset values (multiply by 100 for percentages)
    return (
        degrees.get('BA', 0) * 100, 
        degrees.get('MA', 0) * 100, 
        degrees.get('VOC', 0) * 100,
        degrees.get('NURSE', 0) * 100,
        degrees.get('NA', 0) * 100, 
        "custom",  # Switch to custom mode
        preset['description']
    )

# Define callback for running the simulation
@app.callback(
    [Output("loading-message", "children"),
     Output("simulation-results-store", "data")],
    [Input("run-simulation", "n_clicks")],
    [State("program-type", "value"),
     State("degree-distribution-type", "value"),
     State("ba-pct", "value"),
     State("ma-pct", "value"),
     State("voc-pct", "value"),
     State("nurse-pct", "value"),
     State("na-pct", "value"),
     State("ba-salary", "value"),
     State("ba-std", "value"),
     State("ba-growth", "value"),
     State("ma-salary", "value"),
     State("ma-std", "value"),
     State("ma-growth", "value"),
     State("voc-salary", "value"),
     State("voc-std", "value"),
     State("voc-growth", "value"),
     State("nurse-salary", "value"),
     State("nurse-std", "value"),
     State("nurse-growth", "value"),
     State("na-salary", "value"),
     State("na-std", "value"),
     State("na-growth", "value"),
     State("isa-percentage-input", "value"),
     State("isa-threshold-input", "value"),
     State("isa-cap-input", "value"),
     State("num-students", "value"),
     State("num-sims", "value"),
     State("unemployment-rate", "value"),
     State("inflation-rate", "value"),
     State("home-prob", "value")]
)
def run_simulation(n_clicks, program_type, degree_dist_type, ba_pct, ma_pct, voc_pct, nurse_pct, na_pct,
                   ba_salary, ba_std, ba_growth, ma_salary, ma_std, ma_growth, 
                   voc_salary, voc_std, voc_growth, nurse_salary, nurse_std, nurse_growth,
                   na_salary, na_std, na_growth,
                   isa_percentage, isa_threshold, isa_cap,
                   num_students, num_sims, unemployment_rate, inflation_rate, 
                   home_prob):
    if n_clicks == 0:
        # Return empty results if the button hasn't been clicked
        return "Ready to run simulation", None
    
    # Show running message
    message = "Running simulation... This may take a moment."
    
    # Convert percentage values to decimals
    initial_unemployment_rate = unemployment_rate / 100.0
    initial_inflation_rate = inflation_rate / 100.0
    home_prob = home_prob / 100.0
    isa_percentage = isa_percentage / 100.0
    
    # Determine scenario based on degree distribution type
    scenario = 'custom'  # We now always use custom since we removed the default option
    
    # Convert percentages to decimals
    ba_pct_decimal = ba_pct / 100.0
    ma_pct_decimal = ma_pct / 100.0
    voc_pct_decimal = voc_pct / 100.0
    nurse_pct_decimal = nurse_pct / 100.0
    na_pct_decimal = na_pct / 100.0
    
    # Run the simulation
    try:
        results = run_simple_simulation(
            program_type=program_type,
            num_students=num_students,
            num_sims=num_sims,
            ba_salary=ba_salary,
            ba_std=ba_std,
            ba_growth=ba_growth,
            ma_salary=ma_salary,
            ma_std=ma_std,
            ma_growth=ma_growth,
            voc_salary=voc_salary,
            voc_std=voc_std,
            voc_growth=voc_growth,
            nurse_salary=nurse_salary,
            nurse_std=nurse_std,
            nurse_growth=nurse_growth,
            na_salary=na_salary,
            na_std=na_std,
            na_growth=na_growth,
            isa_percentage=isa_percentage,
            isa_threshold=isa_threshold,
            isa_cap=isa_cap,
            initial_unemployment_rate=initial_unemployment_rate,
            initial_inflation_rate=initial_inflation_rate,
            home_prob=home_prob,
            ba_pct=ba_pct_decimal,
            ma_pct=ma_pct_decimal,
            voc_pct=voc_pct_decimal,
            nurse_pct=nurse_pct_decimal,
            na_pct=na_pct_decimal,
            scenario=scenario,
            new_malengo_fee=True
        )
        
        # Convert DataFrames to JSON for storage
        serializable_results = {
            'program_type': results['program_type'],
            'total_investment': results['total_investment'],
            'price_per_student': results['price_per_student'],
            'isa_percentage': results['isa_percentage'],
            'isa_threshold': results['isa_threshold'],
            'isa_cap': results['isa_cap'],
            'IRR': results['IRR'],
            'investor_IRR': results['investor_IRR'],
            'average_total_payment': results['average_total_payment'],
            'average_investor_payment': results['average_investor_payment'],
            'average_malengo_payment': results['average_malengo_payment'],
            'average_duration': results['average_duration'],
            'payment_by_year': results['payment_by_year'].to_dict(),
            'investor_payment_by_year': results['investor_payment_by_year'].to_dict(),
            'malengo_payment_by_year': results['malengo_payment_by_year'].to_dict(),
            'payment_quantiles': results['payment_quantiles'],
            'employment_rate': results['employment_rate'],
            'repayment_rate': results['repayment_rate'],
            'cap_stats': results['cap_stats'],
            'home_prob': results['home_prob'],
            'custom_degrees': results['custom_degrees'],
            'degree_counts': results['degree_counts'],
            'degree_pcts': results['degree_pcts']
        }
        
        return "Simulation completed!", serializable_results
    
    except Exception as e:
        return f"Error in simulation: {str(e)}", None

# Update summary stats to include degree distribution
@app.callback(
    Output("summary-stats", "children"),
    [Input("simulation-results-store", "data")]
)
def update_summary_stats(results):
    if not results:
        return "Run a simulation to see results"
    
    # Create a list of summary statistics
    content_elements = [
        html.Div([
            html.Div([
                html.H4("Investment Parameters"),
                html.P(f"Total Investment: ${results['total_investment']:,.0f}"),
                html.P(f"Cost per Student: ${results['price_per_student']:,.0f}"),
                html.P(f"ISA Percentage: {results['isa_percentage']*100:.1f}%"),
                html.P(f"ISA Threshold: ${results['isa_threshold']:,.0f}"),
                html.P(f"ISA Cap: ${results['isa_cap']:,.0f}"),
            ], style={'width': '50%', 'display': 'inline-block'}),
            
            html.Div([
                html.H4("Economic Parameters"),
                html.P(f"Home Probability: {results['home_prob']*100:.1f}%", style={'marginTop': '10px'}),
            ], style={'width': '50%', 'display': 'inline-block'}),
        ]),
        
        html.Hr(),
        
        html.Div([
            html.Div([
                html.H4("Return Metrics"),
                html.P(f"Total IRR: {results['IRR']*100:.1f}%"),
                html.P(f"Investor IRR: {results['investor_IRR']*100:.1f}%"),
                html.P(f"Average Total Payment: ${results['average_total_payment']:,.0f}"),
                html.P(f"Average Duration: {results['average_duration']:.1f} years"),
            ], style={'width': '50%', 'display': 'inline-block'}),
            
            html.Div([
                html.H4("Student Metrics"),
                html.P(f"Employment Rate: {results['employment_rate']*100:.1f}%"),
                html.P(f"Repayment Rate: {results['repayment_rate']*100:.1f}%"),
            ], style={'width': '50%', 'display': 'inline-block'}),
        ]),
        
        html.Hr(),
        
        html.H4("Payment Quantiles (IRR)"),
        html.Table([
            html.Tr([
                html.Th("Percentile"),
                html.Th("IRR")
            ]),
            html.Tr([html.Td("0%"), html.Td(f"{float(results['payment_quantiles']['0'])*100:.1f}%")]),
            html.Tr([html.Td("25%"), html.Td(f"{float(results['payment_quantiles']['0.25'])*100:.1f}%")]),
            html.Tr([html.Td("50%"), html.Td(f"{float(results['payment_quantiles']['0.5'])*100:.1f}%")]),
            html.Tr([html.Td("75%"), html.Td(f"{float(results['payment_quantiles']['0.75'])*100:.1f}%")]),
            html.Tr([html.Td("100%"), html.Td(f"{float(results['payment_quantiles']['1.0'])*100:.1f}%")])
        ], style={'width': '100%', 'textAlign': 'left'})
    ]
    
    return html.Div(content_elements)

# Callback for payment distribution graph
@app.callback(
    Output("payment-distribution", "figure"),
    [Input("simulation-results-store", "data")]
)
def update_payment_distribution(results):
    if not results:
        return go.Figure()
    
    # Convert stored dict back to pandas Series
    payment_by_year = pd.Series(results['payment_by_year'])
    
    # Create the payment distribution graph
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=payment_by_year.index,
        y=payment_by_year.values,
        name="Average Payment by Year",
        marker_color='rgb(55, 83, 109)'
    ))
    
    # Add a horizontal line for the investment amount
    avg_annual_investment = results['total_investment'] / payment_by_year.shape[0]
    fig.add_trace(go.Scatter(
        x=[0, payment_by_year.shape[0]-1],
        y=[avg_annual_investment, avg_annual_investment],
        mode='lines',
        name='Avg. Annual Investment',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title=f"{results['program_type']} Program - Average Payments by Year",
        xaxis_title="Year",
        yaxis_title="Payment Amount ($)",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# Callback for investor vs malengo split graph
@app.callback(
    Output("investor-malengo-split", "figure"),
    [Input("simulation-results-store", "data")]
)
def update_investor_malengo_split(results):
    if not results:
        return go.Figure()
    
    # Convert stored dict back to pandas Series
    investor_payment_by_year = pd.Series(results['investor_payment_by_year'])
    malengo_payment_by_year = pd.Series(results['malengo_payment_by_year'])
    
    # Create the stacked bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=investor_payment_by_year.index,
        y=investor_payment_by_year.values,
        name="Investor Payments",
        marker_color='rgb(55, 83, 109)'
    ))
    
    fig.add_trace(go.Bar(
        x=malengo_payment_by_year.index,
        y=malengo_payment_by_year.values,
        name="Malengo Performance Fee",
        marker_color='rgb(26, 118, 255)'
    ))
    
    fig.update_layout(
        title=f"Payment Split Between Investors and Malengo (Fee: {results['isa_percentage']*100:.1f}%)",
        xaxis_title="Year",
        yaxis_title="Payment Amount ($)",
        barmode='stack',
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# Callback for IRR distribution
@app.callback(
    Output("irr-distribution", "figure"),
    [Input("simulation-results-store", "data")]
)
def update_irr_distribution(results):
    if not results:
        return go.Figure()
    
    # Create the IRR distribution graph
    fig = go.Figure()
    
    # Extract quantile values
    quantiles = results['payment_quantiles']
    
    # Create data for quantile plot
    quantile_labels = ['Minimum', '25th Percentile', 'Median', '75th Percentile', 'Maximum']
    quantile_values = [
        float(quantiles['0']), 
        float(quantiles['0.25']), 
        float(quantiles['0.5']), 
        float(quantiles['0.75']), 
        float(quantiles['1.0'])
    ]
    
    # Add a bar chart for quantiles
    fig.add_trace(go.Bar(
        x=quantile_labels,
        y=quantile_values,
        marker_color='rgb(158,202,225)',
        name='IRR Quantiles'
    ))
    
    # Add a horizontal line for the overall IRR
    fig.add_trace(go.Scatter(
        x=quantile_labels,
        y=[results['IRR']] * len(quantile_labels),
        mode='lines',
        name='Overall IRR',
        line=dict(color='rgb(55, 83, 109)', dash='dash', width=2)
    ))
    
    # Add a horizontal line for investor IRR
    fig.add_trace(go.Scatter(
        x=quantile_labels,
        y=[results['investor_IRR']] * len(quantile_labels),
        mode='lines',
        name='Investor IRR',
        line=dict(color='rgb(26, 118, 255)', width=2)
    ))
    
    fig.update_layout(
        title=f"{results['program_type']} Program - IRR Distribution",
        xaxis_title="Percentile",
        yaxis_title="IRR",
        yaxis_tickformat='.2%',
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# Callback for student outcome statistics
@app.callback(
    Output("student-outcome-stats", "children"),
    [Input("simulation-results-store", "data")]
)
def update_student_outcome_stats(results):
    if not results:
        return html.Div("Run a simulation to see student outcome statistics")
    
    # Calculate total students in each category
    cap_stats = results['cap_stats']
    total_students = cap_stats['payment_cap_count'] + cap_stats['years_cap_count'] + cap_stats['no_cap_count']
    
    # Create a table for cap statistics
    cap_table = pd.DataFrame({
        'Category': ['Hit Payment Cap', 'Hit 10-Years Cap', 'Hit No Cap'],
        'Count': [
            f"{cap_stats['payment_cap_count']:.1f}",
            f"{cap_stats['years_cap_count']:.1f}",
            f"{cap_stats['no_cap_count']:.1f}"
        ],
        'Percentage': [
            f"{cap_stats['payment_cap_pct']*100:.1f}%",
            f"{cap_stats['years_cap_pct']*100:.1f}%", 
            f"{cap_stats['no_cap_pct']*100:.1f}%"
        ],
        'Avg Repayment': [
            f"${cap_stats['avg_repayment_cap_hit']:,.0f}",
            f"${cap_stats['avg_repayment_years_hit']:,.0f}",
            f"${cap_stats['avg_repayment_no_cap']:,.0f}"
        ]
    })
    
    # Convert to Dash table
    table = dash_table.DataTable(
        data=cap_table.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in cap_table.columns],
        style_cell={'textAlign': 'center', 'padding': '10px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ]
    )
    
    # Add summary statistics
    summary_stats = html.Div([
        html.H4("Student Payment Categories", style={'marginBottom': '15px', 'textAlign': 'center'}),
        html.Div([
            html.P(f"Employment Rate: {results['employment_rate']*100:.1f}%", style={'fontWeight': 'bold'}),
            html.P(f"Students Making Payments: {results['repayment_rate']*100:.1f}%", style={'fontWeight': 'bold'}),
        ], style={'textAlign': 'center', 'marginBottom': '15px'}),
        table
    ])
    
    return summary_stats

# New callback for repayment caps chart
@app.callback(
    Output("repayment-caps-chart", "figure"),
    [Input("simulation-results-store", "data")]
)
def update_repayment_caps_chart(results):
    if not results:
        return go.Figure()
    
    cap_stats = results['cap_stats']
    
    # Create data for the figure
    categories = ['Hit Payment Cap', 'Hit 10-Years Cap', 'Hit No Cap']
    counts = [cap_stats['payment_cap_count'], cap_stats['years_cap_count'], cap_stats['no_cap_count']]
    avg_repayments = [cap_stats['avg_repayment_cap_hit'], cap_stats['avg_repayment_years_hit'], cap_stats['avg_repayment_no_cap']]
    
    # Create combined student count and average repayment chart
    fig = go.Figure()
    
    # Add student count bars
    fig.add_trace(go.Bar(
        x=categories,
        y=counts,
        name='Student Count',
        marker_color='rgb(55, 83, 109)',
        yaxis='y'
    ))
    
    # Add average repayment line
    fig.add_trace(go.Scatter(
        x=categories,
        y=avg_repayments,
        name='Avg Repayment ($)',
        marker_color='rgb(26, 118, 255)',
        mode='lines+markers',
        marker=dict(size=12),
        line=dict(width=4),
        yaxis='y2'
    ))
    
    # Add cost per student line
    fig.add_trace(go.Scatter(
        x=categories,
        y=[results['price_per_student']] * 3,
        name='Cost Per Student',
        marker_color='rgb(255, 99, 71)',
        mode='lines',
        line=dict(width=2, dash='dash'),
        yaxis='y2'
    ))
    
    # Update layout with secondary y-axis
    fig.update_layout(
        title='Student Outcomes by Repayment Category',
        xaxis_title='Repayment Category',
        yaxis=dict(
            title='Number of Students',
            side='left'
        ),
        yaxis2=dict(
            title='Amount ($)',
            side='right',
            overlaying='y',
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white'
    )
    
    return fig

# Callback for detailed results
@app.callback(
    Output("detailed-results", "children"),
    [Input("simulation-results-store", "data")]
)
def update_detailed_results(results):
    if not results:
        return "Run a simulation to see results"
    
    # Create a list of detailed statistics
    content_elements = [
        html.Div([
            html.H4("Repayment Statistics"),
            html.Table([
                html.Tr([html.Th("Metric"), html.Th("Value")]),
                html.Tr([
                    html.Td("Students Hitting Payment Cap"),
                    html.Td(f"{results['cap_stats']['payment_cap_pct']*100:.1f}%")
                ]),
                html.Tr([
                    html.Td("Students Hitting Years Cap"),
                    html.Td(f"{results['cap_stats']['years_cap_pct']*100:.1f}%")
                ]),
                html.Tr([
                    html.Td("Students Not Hitting Cap"),
                    html.Td(f"{results['cap_stats']['no_cap_pct']*100:.1f}%")
                ])
            ], style={'width': '100%', 'marginBottom': '20px'})
        ]),
        
        html.Div([
            html.H4("Average Repayment by Cap Type"),
            html.Table([
                html.Tr([html.Th("Category"), html.Th("Average Repayment")]),
                html.Tr([
                    html.Td("Payment Cap Hit"),
                    html.Td(f"${results['cap_stats']['avg_repayment_cap_hit']:,.0f}")
                ]),
                html.Tr([
                    html.Td("Years Cap Hit"),
                    html.Td(f"${results['cap_stats']['avg_repayment_years_hit']:,.0f}")
                ]),
                html.Tr([
                    html.Td("No Cap Hit"),
                    html.Td(f"${results['cap_stats']['avg_repayment_no_cap']:,.0f}")
                ])
            ], style={'width': '100%', 'marginBottom': '20px'})
        ]),
        
        html.Div([
            html.H4("Degree Distribution"),
            html.Table([
                html.Tr([html.Th("Degree Type"), html.Th("Percentage"), html.Th("Average Salary"), html.Th("Standard Deviation"), html.Th("Growth Rate")]),
                *[html.Tr([
                    html.Td(degree),
                    html.Td(f"{pct*100:.1f}%"),
                    html.Td(f"${results['degree_counts'][degree]:,.0f}" if degree in results.get('degree_counts', {}) else "-"),
                    html.Td(f"${results['degree_counts'][degree]:,.0f}" if degree in results.get('degree_counts', {}) else "-"),
                    html.Td(f"{results['degree_counts'][degree]:.1f}%" if degree in results.get('degree_counts', {}) else "-")
                ]) for degree, pct in results['degree_pcts'].items() if pct > 0]
            ], style={'width': '100%', 'marginBottom': '20px'})
        ])
    ]
    
    return html.Div(content_elements)

# Add a callback for the scenario info tab
@app.callback(
    Output("scenario-info", "children"),
    [Input("simulation-results-store", "data")]
)
def update_scenario_info(results):
    if not results:
        return "Run a simulation to see results"
    
    # Create a table with scenario information
    data = [
        {"Parameter": "Program Type", "Value": results['program_type']},
        {"Parameter": "Total Investment", "Value": f"${results['total_investment']:,.0f}"},
        {"Parameter": "Cost per Student", "Value": f"${results['price_per_student']:,.0f}"},
        {"Parameter": "ISA Percentage", "Value": f"{results['isa_percentage']*100:.1f}%"},
        {"Parameter": "ISA Threshold", "Value": f"${results['isa_threshold']:,.0f}"},
        {"Parameter": "ISA Cap", "Value": f"${results['isa_cap']:,.0f}"},
        {"Parameter": "Home Probability", "Value": f"{results['home_prob']*100:.1f}%"},
        {"Parameter": "Employment Rate", "Value": f"{results['employment_rate']*100:.1f}%"},
        {"Parameter": "Repayment Rate", "Value": f"{results['repayment_rate']*100:.1f}%"}
    ]
    
    return dash_table.DataTable(
        data=data,
        columns=[
            {"name": "Parameter", "id": "Parameter"},
            {"name": "Value", "id": "Value"}
        ],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ]
    )

# Callback for degree info - update to show custom degree distribution if used
@app.callback(
    Output("degree-info", "children"),
    [Input("simulation-results-store", "data")]
)
def update_degree_info(results):
    if not results:
        return "Run a simulation to see results"
    
    # Get degree percentages
    degree_pcts = results.get('degree_pcts', {})
    
    # Create a list of degree information
    content_elements = [
        html.Div([
            html.H4("Degree Distribution"),
            html.Table([
                html.Tr([html.Th("Degree Type"), html.Th("Percentage"), html.Th("Average Salary"), html.Th("Standard Deviation"), html.Th("Growth Rate")]),
                *[html.Tr([
                    html.Td(degree),
                    html.Td(f"{pct*100:.1f}%"),
                    html.Td(f"${results['degree_counts'][degree]:,.0f}" if degree in results.get('degree_counts', {}) else "-"),
                    html.Td(f"${results['degree_counts'][degree]:,.0f}" if degree in results.get('degree_counts', {}) else "-"),
                    html.Td(f"{results['degree_counts'][degree]:.1f}%" if degree in results.get('degree_counts', {}) else "-")
                ]) for degree, pct in degree_pcts.items() if pct > 0]
            ], style={'width': '100%', 'marginBottom': '20px'})
        ])
    ]
    
    return html.Div(content_elements)

# Add callback to update ISA parameters based on program type
@app.callback(
    [Output("isa-percentage-input", "value"),
     Output("isa-threshold-input", "value"),
     Output("isa-cap-input", "value")],
    [Input("program-type", "value")]
)
def update_isa_params(program_type):
    if program_type == "University":
        return 14, 27000, 72500
    else:  # TVET
        return 12, 27000, 49950

# Run the app
if __name__ == "__main__":
    # Use this for local development
    app.run_server(debug=False, host='0.0.0.0', port=10000) 