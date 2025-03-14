import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import random

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
        'degrees': {'BA': 0.43, 'MA': 0.23, 'VOC': 0.25, 'NURSE': 0.0, 'NA': 0.09, 'LABOR': 0.0}
    },
    'Conservative': {
        'description': 'More vocational degrees, fewer advanced degrees.',
        'degrees': {'BA': 0.3, 'MA': 0.1, 'VOC': 0.4, 'NURSE': 0.0, 'NA': 0.2, 'LABOR': 0.0}
    },
    'Optimistic': {
        'description': 'Mostly bachelor and master degrees with very few dropouts.',
        'degrees': {'BA': 0.625, 'MA': 0.325, 'VOC': 0.025, 'NURSE': 0.0, 'NA': 0.025, 'LABOR': 0.0}
    },
    'TVET Baseline': {
        'description': 'TVET baseline scenario with more vocational than nursing degrees.',
        'degrees': {'BA': 0.0, 'MA': 0.0, 'VOC': 0.60, 'NURSE': 0.25, 'NA': 0.15, 'LABOR': 0.0}
    },
    'TVET Conservative': {
        'description': 'Conservative TVET scenario with higher dropout rate.',
        'degrees': {'BA': 0.0, 'MA': 0.0, 'VOC': 0.50, 'NURSE': 0.20, 'NA': 0.30, 'LABOR': 0.0}
    },
    'TVET Optimistic': {
        'description': 'Optimistic TVET scenario with no dropouts, more nursing degrees.',
        'degrees': {'BA': 0.0, 'MA': 0.0, 'VOC': 0.40, 'NURSE': 0.60, 'NA': 0.0, 'LABOR': 0.0}
    },
    'Labor Baseline': {
        'description': 'Labor baseline scenario with 75% labor degrees and 25% NA.',
        'degrees': {'BA': 0.0, 'MA': 0.0, 'VOC': 0.0, 'NURSE': 0.0, 'NA': 0.25, 'LABOR': 0.75}
    },
    'Labor Conservative': {
        'description': 'Conservative Labor scenario with 60% labor degrees and 40% NA.',
        'degrees': {'BA': 0.0, 'MA': 0.0, 'VOC': 0.0, 'NURSE': 0.0, 'NA': 0.40, 'LABOR': 0.60}
    },
    'Labor Optimistic': {
        'description': 'Optimistic Labor scenario with 95% labor degrees and minimal dropouts.',
        'degrees': {'BA': 0.0, 'MA': 0.0, 'VOC': 0.0, 'NURSE': 0.0, 'NA': 0.05, 'LABOR': 0.95}
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
                
                html.H3("Overview", style={'marginTop': '30px'}),
                html.P([
                    "This tool simulates Income Share Agreement (ISA) outcomes for students in various educational programs, ",
                    "including university degrees, vocational training, and specific labor or nursing tracks. By modeling student earnings, ",
                    "payment thresholds, and potential dropouts or returns to home countries, it provides a comprehensive view of ",
                    "investor returns and student payment patterns under different scenarios."
                ]),
                
                html.H3("Key Features", style={'marginTop': '30px'}),
                html.Ul([
                    html.Li("Program Simulation: Model ISA outcomes separately for University, TVET, and Labor pathways."),
                    html.Li("Multiple Scenarios: Choose among baseline, conservative, or optimistic enrollment and graduation distributions."),
                    html.Li("Degree Distributions: Adjust the proportion of students pursuing different degrees, such as bachelor's, master's, and vocational programs."),
                    html.Li("Economic Modeling: Incorporate inflation, unemployment, and experience-based earnings growth to reflect real-world variability."),
                    html.Li("Investor Returns & Student Payments: Estimate how changes in program parameters, dropouts, or home-country returns affect the financial outcomes for all parties.")
                ]),
                
                html.H3("Model Assumptions", style={'marginTop': '30px'}),
                
                html.H4("1. Degree Types & Earnings", style={'marginTop': '20px'}),
                html.P([
                    "The model uses several distinct tracks, each with mean earnings, variances, and completion times that approximate real-world data. ",
                    "A 20% wage penalty is applied to some programs to account for immigrant status and the fact that new graduates typically earn below the field average. ",
                    "The six degree categories are:"
                ]),
                
                html.Div([
                    html.H5("Bachelor's Degree (BA)"),
                    html.Ul([
                        html.Li("Mean earnings: $41,300/year"),
                        html.Li("SD: $13,000"),
                        html.Li("Annual Experience Growth: 3%"),
                        html.Li("Years to Complete: 4")
                    ])
                ], style={'marginLeft': '20px', 'marginBottom': '15px'}),
                
                html.Div([
                    html.H5("Master's Degree (MA)"),
                    html.Ul([
                        html.Li("Mean earnings: $46,709/year"),
                        html.Li("SD: $15,000"),
                        html.Li("Annual Experience Growth: 4%"),
                        html.Li("Years to Complete: 6")
                    ])
                ], style={'marginLeft': '20px', 'marginBottom': '15px'}),
                
                html.Div([
                    html.H5("Vocational Training (VOC)"),
                    html.Ul([
                        html.Li("Mean earnings: $31,500/year"),
                        html.Li("SD: $4,800"),
                        html.Li("Annual Experience Growth: 1%"),
                        html.Li("Years to Complete: 3")
                    ])
                ], style={'marginLeft': '20px', 'marginBottom': '15px'}),
                
                html.Div([
                    html.H5("Nursing Degree (NURSE)"),
                    html.Ul([
                        html.Li("Mean earnings: $44,000/year"),
                        html.Li("SD: $8,400"),
                        html.Li("Annual Experience Growth: 1%"),
                        html.Li("Years to Complete: 4")
                    ])
                ], style={'marginLeft': '20px', 'marginBottom': '15px'}),
                
                html.Div([
                    html.H5("Labor Program (LABOR)"),
                    html.Ul([
                        html.Li("Mean earnings: $35,000/year"),
                        html.Li("SD: $5,000"),
                        html.Li("Annual Experience Growth: 2%"),
                        html.Li("Years to Complete: 3")
                    ])
                ], style={'marginLeft': '20px', 'marginBottom': '15px'}),
                
                html.Div([
                    html.H5("No Advancement (NA)"),
                    html.Ul([
                        html.Li("Mean earnings: $2,200/year"),
                        html.Li("SD: $640"),
                        html.Li("Annual Experience Growth: 1%"),
                        html.Li("Years to Complete: 4"),
                        html.Li("100% Probability of Returning Home: Lower wages reflect a situation where a student does not gain additional skills or remains employed in a low-wage home country context.")
                    ])
                ], style={'marginLeft': '20px', 'marginBottom': '15px'}),
                
                html.H4("2. Earnings Methodology", style={'marginTop': '20px'}),
                html.P([
                    "We derive salary levels from public labor data and research on earnings for new graduates in high-income countries. ",
                    "This baseline is then adjusted for the following:"
                ]),
                html.Ul([
                    html.Li("Immigrant Wage Penalty (~20%) – Reflects both potential employer bias and the reality that newcomers to a field/country typically earn less early in their careers."),
                    html.Li("Career Stage – The model targets entry-level and early-career professionals. Over time, the annual experience growth rate builds in realistic wage increases.")
                ]),
                
                html.H5("University Program Earnings", style={'marginTop': '15px'}),
                html.P([
                    "In addition to the general BA or MA earnings, we refine earnings for university students based on a detailed degree mix:"
                ]),
                html.Ul([
                    html.Li("Tax & Law (21%): ~€60,000 initial (after 20% penalty), growing to ~€600k–€700k total over 10 years."),
                    html.Li("Business & Management (19%): ~€63,000 initial, ~€650k–€750k over 10 years."),
                    html.Li("Engineering (21%): ~€52,000 initial, ~€500k–€600k over 10 years."),
                    html.Li("Natural Sciences (18%): ~€49,000 initial, ~€450k–€550k over 10 years."),
                    html.Li("Information Technology (7%): ~€45,000 initial, ~€400k–€500k over 10 years."),
                    html.Li("Agriculture (7%): ~€35,000 initial, ~€300k–€400k over 10 years."),
                    html.Li("Humanities & Arts (3%): ~€36k–€40k initial, ~€350k–€450k over 10 years."),
                    html.Li("Other Fields (4%): ~€40,000 initial, ~€400k total over 10 years.")
                ]),
                html.P([
                    "Overall, university graduates fall in the €40–€60k range early in their careers. Some pursue master's degrees, ",
                    "boosting their initial pay ~13% above the typical bachelor's start."
                ]),
                
                html.H5("TVET Program Earnings", style={'marginTop': '15px'}),
                html.Ul([
                    html.Li("Nursing (NURSE): Average $48,672 annually, adjusted to $44,000 for new arrivals. Stable wages with a modest 1% annual growth."),
                    html.Li("Vocational (VOC): Median $31,680 annually with a $4,800 SD. Reflects entry-level positions in skilled trades, also with 1% annual growth.")
                ]),
                
                html.H5("Labor Program Earnings", style={'marginTop': '15px'}),
                html.P([
                    "The Labor track features trades like plumbing, electrical work, and other skilled manual roles. ",
                    "A $35,000 mean salary with a 2% annual growth captures steady wage progression in these fields."
                ]),
                
                html.H4("Predefined Scenarios", style={'marginTop': '20px'}),
                html.P([
                    "To facilitate comparison, the model includes preset enrollment distributions for each program category:"
                ]),
                
                html.H5("University Programs", style={'marginTop': '15px'}),
                html.Ul([
                    html.Li("Baseline: 43% BA, 23% MA, 25% VOC, 9% NA"),
                    html.Li("Conservative: 30% BA, 10% MA, 40% VOC, 20% NA"),
                    html.Li("Optimistic: 62.5% BA, 32.5% MA, 2.5% VOC, 2.5% NA")
                ]),
                
                html.H5("TVET Programs", style={'marginTop': '15px'}),
                html.Ul([
                    html.Li("Baseline: 45% Nursing, 45% Vocational, 10% No Advancement"),
                    html.Li("Conservative: 20% Nursing, 60% Vocational, 20% No Advancement")
                ]),
                
                html.H5("Labor Programs", style={'marginTop': '15px'}),
                html.Ul([
                    html.Li("Baseline: 75% Labor, 25% No Advancement"),
                    html.Li("Conservative: 60% Labor, 40% No Advancement")
                ]),
                
                html.H4("Economic Parameters", style={'marginTop': '20px'}),
                html.Ul([
                    html.Li("Inflation: 2% annually"),
                    html.Li("Unemployment: 4% default rate"),
                    html.Li(html.Span(["ISA Caps:", html.Br(),
                                      "University: $72,500", html.Br(),
                                      "TVET: $49,950", html.Br(),
                                      "Labor: $45,000"])),
                    html.Li(html.Span(["ISA Percentage:", html.Br(),
                                      "University: 14%", html.Br(),
                                      "TVET: 12%", html.Br(),
                                      "Labor: 10%"]))
                ]),
                html.P([
                    "These parameters shape the cash flow between students and investors. For example, if a student's earnings exceed $27,000, ",
                    "they pay a fixed percentage until reaching the ISA cap (which protects them from disproportionately high repayment if incomes skyrocket)."
                ]),
                
                html.H4("Foreign Student Modeling", style={'marginTop': '20px'}),
                html.P([
                    "We account for the possibility that some graduates leave the labor force after completing (or dropping out of) their program:"
                ]),
                html.Ul([
                    html.Li("The leave_labor_force_probability parameter determines the likelihood of leaving the labor force."),
                    html.Li("Once out of the labor force, a student's earnings are much lower, reflecting the typically lower wages or lack of employment."),
                    html.Li("The No Advancement (NA) category defaults to a 100% leave labor force probability to signify no sustained earnings improvement or job market constraints.")
                ]),
                html.P([
                    "This allows the tool to distinguish between high-earning paths (where students remain in the host country or another HIC) ",
                    "and those that revert to lower wages if the student does not remain abroad or does not advance academically."
                ]),
                
                html.H4("Putting It All Together", style={'marginTop': '20px'}),
                html.P([
                    "By combining:"
                ]),
                html.Ul([
                    html.Li("Program and degree distributions (e.g., percentage of students choosing each path)"),
                    html.Li("Earnings profiles (with immigrant penalties, growth rates, and standard deviations)"),
                    html.Li("Return-home probabilities and economic parameters (inflation, unemployment)"),
                    html.Li("ISA mechanics (thresholds, caps, and rates)")
                ]),
                html.P([
                    "…the model forecasts total student earnings, ISA payment streams, and ultimate returns to investors or lenders. ",
                    "Through this flexible and data-informed approach, users can test different assumptions about student pathways and labor market outcomes, ",
                    "then see how changes in these factors drive key financial results—both for the students and for the financing entity behind the ISAs."
                ])
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
                                    {'label': 'TVET', 'value': 'TVET'},
                                    {'label': 'Labor', 'value': 'Labor'}
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
                                            value=2.0, 
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
                                            value=3.0, 
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
                                            value=1.0, 
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
                                            value=1, 
                                            min=0, 
                                            max=20, 
                                            step=0.1,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                ], style={'marginBottom': '10px'}),
                                
                                # Labor Degree row
                                html.Div([
                                    html.Div([html.Label("Labor Degree")], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="labor-pct", 
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
                                            id="labor-salary", 
                                            type="number", 
                                            value=35000, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="labor-std", 
                                            type="number", 
                                            value=5000, 
                                            min=0, 
                                            step=100,
                                            style={'width': '100%'}
                                        )
                                    ], style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Input(
                                            id="labor-growth", 
                                            type="number", 
                                            value=2, 
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
                            html.Label("Leave Labor Force Probability (%):"),
                            dcc.Slider(
                                id="leave-labor-force-prob",
                                min=0,
                                max=50,
                                step=5,
                                value=5,
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
                                ]),
                                dcc.Tab(label='Scenario Comparison', children=[
                                    html.Div([
                                        html.H4("Compare Saved Scenarios", style={'marginBottom': '15px'}),
                                        html.P("Save multiple scenarios and compare their results side by side."),
                                        
                                        html.Div([
                                            html.Div([
                                                html.Label("Scenario Name:"),
                                                dcc.Input(
                                                    id="scenario-name-input",
                                                    type="text",
                                                    placeholder="Enter a name for this scenario",
                                                    style={'width': '100%'}
                                                )
                                            ], style={'width': '60%', 'display': 'inline-block'}),
                                            
                                            html.Div([
                                                html.Button(
                                                    "Save Current Scenario", 
                                                    id="save-scenario-button", 
                                                    n_clicks=0,
                                                    style={
                                                        'backgroundColor': '#4CAF50',
                                                        'color': 'white',
                                                        'padding': '10px',
                                                        'borderRadius': '5px',
                                                        'border': 'none',
                                                        'width': '100%',
                                                        'cursor': 'pointer'
                                                    }
                                                )
                                            ], style={'width': '35%', 'display': 'inline-block', 'float': 'right'})
                                        ], style={'marginBottom': '20px'}),
                                        
                                        html.Div([
                                            html.H5("Saved Scenarios", style={'marginBottom': '10px'}),
                                            html.Div(id="saved-scenarios-list"),
                                            html.Div([
                                                html.Button(
                                                    "Compare Selected Scenarios", 
                                                    id="compare-scenarios-button", 
                                                    n_clicks=0,
                                                    style={
                                                        'backgroundColor': '#2196F3',
                                                        'color': 'white',
                                                        'padding': '10px',
                                                        'borderRadius': '5px',
                                                        'border': 'none',
                                                        'marginRight': '10px',
                                                        'cursor': 'pointer'
                                                    }
                                                ),
                                                html.Button(
                                                    "Clear All Scenarios", 
                                                    id="clear-scenarios-button", 
                                                    n_clicks=0,
                                                    style={
                                                        'backgroundColor': '#f44336',
                                                        'color': 'white',
                                                        'padding': '10px',
                                                        'borderRadius': '5px',
                                                        'border': 'none',
                                                        'cursor': 'pointer'
                                                    }
                                                )
                                            ], style={'marginTop': '15px', 'marginBottom': '20px'})
                                        ], style={'marginBottom': '20px'}),
                                        
                                        html.Div(id="scenario-comparison-results")
                                    ])
                                ]),
                                
                                dcc.Tab(label='Monte Carlo Simulation', children=[
                                    html.Div([
                                        html.H4("Monte Carlo Return Distribution", style={'marginBottom': '15px'}),
                                        html.P("Simulate thousands of possible outcomes by varying multiple parameters simultaneously:"),
                                        
                                        html.Div([
                                            html.Div([
                                                html.Label("Number of Simulations:"),
                                                dcc.Dropdown(
                                                    id="monte-carlo-sims",
                                                    options=[
                                                        {'label': '100 simulations (faster)', 'value': 100},
                                                        {'label': '500 simulations', 'value': 500},
                                                        {'label': '1000 simulations (recommended)', 'value': 1000}
                                                    ],
                                                    value=500
                                                )
                                            ], style={'width': '48%', 'display': 'inline-block'}),
                                            
                                            html.Div([
                                                html.Label("Simulation Complexity:"),
                                                dcc.Dropdown(
                                                    id="monte-carlo-complexity",
                                                    options=[
                                                        {'label': 'Simple', 'value': 'Simple'},
                                                        {'label': 'Medium', 'value': 'Medium'},
                                                        {'label': 'Advanced (slower)', 'value': 'Advanced'}
                                                    ],
                                                    value='Medium'
                                                )
                                            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
                                        ], style={'marginBottom': '20px'}),
                                        
                                        html.Div([
                                            html.H5("Parameter Variation Ranges", style={'marginBottom': '15px'}),
                                            
                                            html.Div([
                                                html.Div([
                                                    html.Label("Unemployment Rate (%):"),
                                                    dcc.RangeSlider(
                                                        id="mc-unemployment-range",
                                                        min=2,
                                                        max=15,
                                                        step=0.5,
                                                        value=[4, 12],
                                                        marks={i: f'{i}%' for i in range(2, 16, 2)},
                                                    )
                                                ], style={'marginBottom': '20px'}),
                                                
                                                html.Div([
                                                    html.Label("Leave Labor Force Probability (%):"),
                                                    dcc.RangeSlider(
                                                        id="mc-leave-labor-force-range",
                                                        min=0,
                                                        max=20,
                                                        step=2,
                                                        value=[0, 10],
                                                        marks={i: f'{i}%' for i in range(0, 21, 5)},
                                                    )
                                                ], style={'marginBottom': '20px'}),
                                                
                                                html.Div([
                                                    html.Label("Wage Penalty (%):"),
                                                    dcc.RangeSlider(
                                                        id="mc-wage-penalty-range",
                                                        min=-40,
                                                        max=0,
                                                        step=5,
                                                        value=[-30, -10],
                                                        marks={i: f'{i}%' for i in range(-40, 1, 10)},
                                                    )
                                                ], style={'marginBottom': '20px'})
                                            ], style={'backgroundColor': '#f1f1f1', 'padding': '15px', 'borderRadius': '5px'})
                                        ], style={'marginBottom': '20px'}),
                                        
                                        html.Button(
                                            "Run Monte Carlo Simulation", 
                                            id="run-monte-carlo-button", 
                                            n_clicks=0,
                                            style={
                                                'backgroundColor': '#4CAF50',
                                                'color': 'white',
                                                'padding': '10px 20px',
                                                'borderRadius': '5px',
                                                'border': 'none',
                                                'fontSize': '16px',
                                                'cursor': 'pointer',
                                                'width': '100%',
                                                'marginBottom': '20px'
                                            }
                                        ),
                                        
                                        html.Div(id="monte-carlo-loading", style={'color': '#888', 'textAlign': 'center'}),
                                        html.Div(id="monte-carlo-results")
                                    ])
                                ]),
                                
                                dcc.Tab(label='Blended Scenario Monte Carlo', children=[
                                    html.Div([
                                        html.H4("Blended Scenario Monte Carlo", style={'marginBottom': '15px'}),
                                        html.P("Simulate outcomes by blending multiple scenarios with different weights:"),
                                        
                                        html.Div([
                                            html.Div([
                                                html.Label("Number of Simulations:"),
                                                dcc.Dropdown(
                                                    id="blended-monte-carlo-sims",
                                                    options=[
                                                        {'label': '100 simulations (faster)', 'value': 100},
                                                        {'label': '500 simulations', 'value': 500},
                                                        {'label': '1000 simulations (recommended)', 'value': 1000}
                                                    ],
                                                    value=500
                                                )
                                            ], style={'width': '100%', 'marginBottom': '20px'}),
                                            
                                            html.H5("Scenario 1", style={'marginBottom': '10px'}),
                                            html.Div([
                                                html.Div([
                                                    html.Label("Scenario Type:"),
                                                    dcc.Dropdown(
                                                        id="scenario1-type",
                                                        options=[
                                                            {'label': 'Baseline', 'value': 'baseline'},
                                                            {'label': 'Conservative', 'value': 'conservative'},
                                                            {'label': 'Optimistic', 'value': 'optimistic'},
                                                            {'label': 'Custom', 'value': 'custom'}
                                                        ],
                                                        value='baseline'
                                                    )
                                                ], style={'width': '48%', 'display': 'inline-block'}),
                                                
                                                html.Div([
                                                    html.Label("Weight (%):"),
                                                    dcc.Input(
                                                        id="scenario1-weight",
                                                        type="number",
                                                        min=0,
                                                        max=100,
                                                        value=50,
                                                        style={'width': '100%'}
                                                    )
                                                ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
                                            ], style={'marginBottom': '20px'}),
                                            
                                            html.H5("Scenario 2", style={'marginBottom': '10px'}),
                                            html.Div([
                                                html.Div([
                                                    html.Label("Scenario Type:"),
                                                    dcc.Dropdown(
                                                        id="scenario2-type",
                                                        options=[
                                                            {'label': 'Baseline', 'value': 'baseline'},
                                                            {'label': 'Conservative', 'value': 'conservative'},
                                                            {'label': 'Optimistic', 'value': 'optimistic'},
                                                            {'label': 'Custom', 'value': 'custom'}
                                                        ],
                                                        value='conservative'
                                                    )
                                                ], style={'width': '48%', 'display': 'inline-block'}),
                                                
                                                html.Div([
                                                    html.Label("Weight (%):"),
                                                    dcc.Input(
                                                        id="scenario2-weight",
                                                        type="number",
                                                        min=0,
                                                        max=100,
                                                        value=30,
                                                        style={'width': '100%'}
                                                    )
                                                ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
                                            ], style={'marginBottom': '20px'}),
                                            
                                            html.H5("Scenario 3", style={'marginBottom': '10px'}),
                                            html.Div([
                                                html.Div([
                                                    html.Label("Scenario Type:"),
                                                    dcc.Dropdown(
                                                        id="scenario3-type",
                                                        options=[
                                                            {'label': 'Baseline', 'value': 'baseline'},
                                                            {'label': 'Conservative', 'value': 'conservative'},
                                                            {'label': 'Optimistic', 'value': 'optimistic'},
                                                            {'label': 'Custom', 'value': 'custom'}
                                                        ],
                                                        value='optimistic'
                                                    )
                                                ], style={'width': '48%', 'display': 'inline-block'}),
                                                
                                                html.Div([
                                                    html.Label("Weight (%):"),
                                                    dcc.Input(
                                                        id="scenario3-weight",
                                                        type="number",
                                                        min=0,
                                                        max=100,
                                                        value=20,
                                                        style={'width': '100%'}
                                                    )
                                                ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
                                            ], style={'marginBottom': '20px'}),
                                            
                                            html.Div(id="weight-sum-warning", style={'color': 'red', 'marginBottom': '20px'}),
                                            
                                            html.Div([
                                                html.Label("Leave Labor Force Probability (%):"),
                                                dcc.RangeSlider(
                                                    id="blended-leave-labor-force-range",
                                                    min=0,
                                                    max=20,
                                                    step=2,
                                                    value=[0, 10],
                                                    marks={i: f'{i}%' for i in range(0, 21, 5)},
                                                )
                                            ], style={'marginBottom': '20px'}),
                                            
                                            html.Div([
                                                html.Label("Wage Penalty (%):"),
                                                dcc.RangeSlider(
                                                    id="blended-wage-penalty-range",
                                                    min=-40,
                                                    max=0,
                                                    step=5,
                                                    value=[-30, -10],
                                                    marks={i: f'{i}%' for i in range(-40, 1, 10)},
                                                )
                                            ], style={'marginBottom': '20px'})
                                        ], style={'backgroundColor': '#f1f1f1', 'padding': '15px', 'borderRadius': '5px', 'marginBottom': '20px'}),
                                        
                                        html.Button(
                                            "Run Blended Monte Carlo Simulation", 
                                            id="run-blended-monte-carlo-button", 
                                            n_clicks=0,
                                            style={
                                                'backgroundColor': '#4CAF50',
                                                'color': 'white',
                                                'padding': '10px 20px',
                                                'borderRadius': '5px',
                                                'border': 'none',
                                                'fontSize': '16px',
                                                'cursor': 'pointer',
                                                'width': '100%',
                                                'marginBottom': '20px'
                                            }
                                        ),
                                        
                                        html.Div(id="blended-monte-carlo-loading", style={'color': '#888', 'textAlign': 'center'}),
                                        html.Div(id="blended-monte-carlo-results")
                                    ])
                                ])
                            ], style={'marginTop': '20px'})
                        ])
                    ], style={'width': '65%', 'display': 'inline-block', 'padding': '20px', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'backgroundColor': '#f9f9f9', 'borderRadius': '8px'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px', 'marginBottom': '30px'}),
            ])
        ])
    ]),
    
    dcc.Store(id='simulation-results-store'),
    dcc.Store(id='saved-scenarios-store', data={"scenarios": []})
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
     Input("na-pct", "value"),
     Input("labor-pct", "value")]
)
def validate_degree_sum(ba_pct, ma_pct, voc_pct, nurse_pct, na_pct, labor_pct):
    total = ba_pct + ma_pct + voc_pct + nurse_pct + na_pct + labor_pct
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
     Output("labor-pct", "value"),
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
        elif program_type == 'TVET':
            # Default to TVET Baseline for TVET
            preset_name = 'TVET Baseline'
        else:
            # Default to Labor Baseline for Labor
            preset_name = 'Labor Baseline'
    
    # If program type changed and we have a preset that's better suited for the new program type
    if triggered_id == 'program-type':
        if program_type == 'University' and preset_name in ['TVET Baseline', 'TVET Conservative', 'TVET Optimistic', 'Labor Baseline', 'Labor Conservative', 'Labor Optimistic']:
            preset_name = 'Baseline'
        elif program_type == 'TVET' and preset_name in ['Baseline', 'Conservative', 'Optimistic', 'Labor Baseline', 'Labor Conservative', 'Labor Optimistic']:
            preset_name = 'TVET Baseline'
        elif program_type == 'Labor' and preset_name in ['Baseline', 'Conservative', 'Optimistic', 'TVET Baseline', 'TVET Conservative', 'TVET Optimistic']:
            preset_name = 'Labor Baseline'
    
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
        degrees.get('LABOR', 0) * 100,
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
     State("labor-pct", "value"),
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
     State("labor-salary", "value"),
     State("labor-std", "value"),
     State("labor-growth", "value"),
     State("isa-percentage-input", "value"),
     State("isa-threshold-input", "value"),
     State("isa-cap-input", "value"),
     State("num-students", "value"),
     State("num-sims", "value"),
     State("unemployment-rate", "value"),
     State("inflation-rate", "value"),
     State("leave-labor-force-prob", "value")]
)
def run_simulation(n_clicks, program_type, degree_dist_type, ba_pct, ma_pct, voc_pct, nurse_pct, na_pct, labor_pct,
                   ba_salary, ba_std, ba_growth, ma_salary, ma_std, ma_growth, 
                   voc_salary, voc_std, voc_growth, nurse_salary, nurse_std, nurse_growth,
                   na_salary, na_std, na_growth, labor_salary, labor_std, labor_growth,
                   isa_percentage, isa_threshold, isa_cap,
                   num_students, num_sims, unemployment_rate, inflation_rate, 
                   leave_labor_force_prob):
    if n_clicks is None:
        raise PreventUpdate
    
    # Convert percentages to decimals
    unemployment_rate = unemployment_rate / 100.0
    inflation_rate = inflation_rate / 100.0
    leave_labor_force_prob = leave_labor_force_prob / 100.0
    isa_percentage = isa_percentage / 100.0
    
    # Determine scenario based on degree distribution type
    scenario = 'custom'  # We now always use custom since we removed the default option
    
    # Convert percentages to decimals
    ba_pct_decimal = ba_pct / 100.0
    ma_pct_decimal = ma_pct / 100.0
    voc_pct_decimal = voc_pct / 100.0
    nurse_pct_decimal = nurse_pct / 100.0
    na_pct_decimal = na_pct / 100.0
    labor_pct_decimal = labor_pct / 100.0
    
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
            labor_salary=labor_salary,
            labor_std=labor_std,
            labor_growth=labor_growth,
            isa_percentage=isa_percentage,
            isa_threshold=isa_threshold,
            isa_cap=isa_cap,
            initial_unemployment_rate=unemployment_rate,
            initial_inflation_rate=inflation_rate,
            leave_labor_force_probability=leave_labor_force_prob,
            ba_pct=ba_pct_decimal,
            ma_pct=ma_pct_decimal,
            voc_pct=voc_pct_decimal,
            nurse_pct=nurse_pct_decimal,
            na_pct=na_pct_decimal,
            labor_pct=labor_pct_decimal,
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
            'investor_payment_quantiles': results.get('investor_payment_quantiles', {}),
            'employment_rate': results['employment_rate'],
            'ever_employed_rate': results.get('ever_employed_rate', 0),
            'repayment_rate': results['repayment_rate'],
            'cap_stats': results['cap_stats'],
            'leave_labor_force_probability': results['leave_labor_force_probability'],
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
    
    # Instead of showing redundant information, just display a message directing users to the tabs
    return html.Div([
        html.H4("Simulation Complete", style={'color': '#4CAF50'}),
        html.P("Your simulation has completed successfully. Please explore the tabs below to view detailed results and analysis."),
        html.P("Each tab contains different visualizations and metrics to help you understand the simulation outcomes.")
    ], style={'padding': '15px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px', 'marginBottom': '20px'})

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
    
    # Extract quantile values - use investor quantiles if available, otherwise fall back to total payment quantiles
    if 'investor_payment_quantiles' in results:
        quantiles = results['investor_payment_quantiles']
    else:
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
        name='Investor IRR Quantiles'
    ))
    
    # Add a horizontal line for investor IRR
    fig.add_trace(go.Scatter(
        x=quantile_labels,
        y=[results['investor_IRR']] * len(quantile_labels),
        mode='lines',
        name='Average Investor IRR',
        line=dict(color='rgb(26, 118, 255)', width=3)
    ))
    
    # Add a horizontal line for the overall IRR (less prominent)
    fig.add_trace(go.Scatter(
        x=quantile_labels,
        y=[results['IRR']] * len(quantile_labels),
        mode='lines',
        name='Overall IRR (before fees)',
        line=dict(color='rgb(55, 83, 109)', dash='dash', width=1.5)
    ))
    
    fig.update_layout(
        title=f"{results['program_type']} Program - Investor IRR Distribution",
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
            html.P(f"Annual Employment Rate: {results['employment_rate']*100:.1f}%", style={'fontWeight': 'bold'}),
            html.P(f"Ever Employed Rate: {results.get('ever_employed_rate', 0)*100:.1f}%", style={'fontWeight': 'bold'}),
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
                html.Tr([html.Th("Degree Type"), html.Th("Percentage"), html.Th("Count")]),
                *[html.Tr([
                    html.Td(degree),
                    html.Td(f"{pct*100:.1f}%"),
                    html.Td(f"{results['degree_counts'].get(degree, 0):.1f}" if degree in results.get('degree_counts', {}) else "-"),
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
    if results is None:
        return html.Div()
    
    scenario_info = [
        html.H4("Scenario Parameters"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Parameter"),
                html.Th("Value")
            ])),
            html.Tbody([
                html.Tr([html.Td("Program Type:"), html.Td(results['program_type'])]),
                html.Tr([html.Td("ISA Percentage:"), html.Td(f"{results['isa_percentage']*100:.1f}%")]),
                html.Tr([html.Td("ISA Threshold:"), html.Td(f"${results['isa_threshold']:.2f}")]),
                html.Tr([html.Td("ISA Cap:"), html.Td(f"${results['isa_cap']:.2f}")]),
                html.Tr([html.Td("Initial Unemployment:"), html.Td(f"{results.get('initial_unemployment_rate', 0.08)*100:.1f}%")]),
                html.Tr([html.Td("Initial Inflation:"), html.Td(f"{results.get('initial_inflation_rate', 0.02)*100:.1f}%")]),
                html.Tr([html.Td("Leave Labor Force Probability:"), html.Td(f"{results['leave_labor_force_probability']*100:.1f}%")]),
            ])
        ], className="table table-striped table-sm")
    ]
    
    return html.Div(scenario_info)

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
                html.Tr([html.Th("Degree Type"), html.Th("Percentage"), html.Th("Count")]),
                *[html.Tr([
                    html.Td(degree),
                    html.Td(f"{pct*100:.1f}%"),
                    html.Td(f"{results['degree_counts'].get(degree, 0):.1f}" if degree in results.get('degree_counts', {}) else "-"),
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
    if program_type == 'University':
        return 14, 27000, 72500
    elif program_type == 'TVET':
        return 12, 27000, 49950
    elif program_type == 'Labor':
        return 12, 27000, 45000  # Changed from 10% to 12%
    else:
        return 12, 27000, 50000  # Default values

# Add callbacks for scenario comparison functionality
@app.callback(
    [Output("saved-scenarios-store", "data"),
     Output("saved-scenarios-list", "children")],
    [Input("save-scenario-button", "n_clicks"),
     Input("clear-scenarios-button", "n_clicks")],
    [State("scenario-name-input", "value"),
     State("simulation-results-store", "data"),
     State("saved-scenarios-store", "data")]
)
def manage_saved_scenarios(save_clicks, clear_clicks, scenario_name, current_results, saved_scenarios):
    ctx = dash.callback_context
    if not ctx.triggered:
        # Initial load - return empty list
        return {}, []
    
    # Initialize saved_scenarios if it doesn't exist
    if saved_scenarios is None:
        saved_scenarios = {}
    
    # Handle clear button click
    if ctx.triggered[0]['prop_id'] == 'clear-scenarios-button.n_clicks' and clear_clicks:
        return {}, []
    
    # Handle save button click
    if ctx.triggered[0]['prop_id'] == 'save-scenario-button.n_clicks' and save_clicks:
        if not scenario_name or not current_results:
            return saved_scenarios, [html.Div("Please enter a scenario name and run a simulation first.")]
        
        # Add current results to saved scenarios
        saved_scenarios[scenario_name] = current_results
        
        # Create list of saved scenarios
        scenario_items = []
        for name in saved_scenarios:
            irr_value = saved_scenarios[name].get('investor_IRR', 0) * 100
            scenario_items.append(html.Div([
                html.Button(
                    f"{name} - IRR: {irr_value:.1f}%",
                    id={'type': 'scenario-button', 'index': name},
                    n_clicks=0,
                    style={
                        'backgroundColor': '#e1f5fe',
                        'border': '1px solid #81d4fa',
                        'borderRadius': '4px',
                        'padding': '8px 12px',
                        'marginRight': '10px',
                        'cursor': 'pointer',
                        'width': '100%',
                        'textAlign': 'left'
                    }
                )
            ], style={'marginBottom': '10px'}))
        
        return saved_scenarios, scenario_items
    
    # Return current state if no action taken
    return saved_scenarios, dash.no_update

@app.callback(
    Output("scenario-comparison-results", "children"),
    [Input("compare-scenarios-button", "n_clicks")],
    [State("saved-scenarios-store", "data")]
)
def compare_scenarios(n_clicks, saved_scenarios):
    if not n_clicks or not saved_scenarios:
        return html.Div("Save scenarios to compare them.")
    
    # Get all saved scenarios
    selected_scenarios = []
    for name, data in saved_scenarios.items():
        selected_scenarios.append({
            "name": name,
            "data": data
        })
    
    if not selected_scenarios:
        return html.Div("No scenarios available for comparison.")
    
    # Create comparison elements
    comparison_elements = []
    
    # 1. IRR Comparison Chart
    irr_data = []
    for scenario in selected_scenarios:
        irr_data.append({
            'Scenario': scenario['name'],
            'Investor IRR': scenario['data'].get('investor_IRR', 0) * 100,
            'Total IRR': scenario['data'].get('IRR', 0) * 100
        })
    
    irr_df = pd.DataFrame(irr_data)
    
    irr_fig = go.Figure()
    irr_fig.add_trace(go.Bar(
        x=irr_df['Scenario'],
        y=irr_df['Investor IRR'],
        name='Investor IRR',
        marker_color='rgb(26, 118, 255)'
    ))
    
    irr_fig.add_trace(go.Bar(
        x=irr_df['Scenario'],
        y=irr_df['Total IRR'],
        name='Total IRR (before fees)',
        marker_color='rgb(55, 83, 109)',
        opacity=0.7
    ))
    
    irr_fig.update_layout(
        title='IRR Comparison by Scenario',
        xaxis_title='Scenario',
        yaxis_title='IRR (%)',
        barmode='group',
        template='plotly_white'
    )
    
    comparison_elements.append(dcc.Graph(figure=irr_fig))
    
    # 2. Key Metrics Comparison
    metrics_data = []
    for scenario in selected_scenarios:
        metrics_data.append({
            'Scenario': scenario['name'],
            'Investor IRR': f"{scenario['data'].get('investor_IRR', 0)*100:.1f}%",
            'Avg Payment': f"${scenario['data'].get('average_total_payment', 0):,.0f}",
            'Repayment Rate': f"{scenario['data'].get('repayment_rate', 0)*100:.1f}%",
            'Employment Rate': f"{scenario['data'].get('employment_rate', 0)*100:.1f}%",
            'Ever Employed': f"{scenario['data'].get('ever_employed_rate', 0)*100:.1f}%",
            'Duration': f"{scenario['data'].get('average_duration', 0):.1f} years"
        })
    
    metrics_table = dash_table.DataTable(
        data=metrics_data,
        columns=[{"name": col, "id": col} for col in metrics_data[0].keys()],
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
    
    comparison_elements.append(html.Div([
        html.H5("Key Metrics by Scenario", style={'marginTop': '30px', 'marginBottom': '15px'}),
        metrics_table
    ]))
    
    # 3. Student Outcomes Comparison
    outcomes_data = []
    for scenario in selected_scenarios:
        outcomes_data.append({
            'Scenario': scenario['name'],
            'Employment Rate': f"{scenario['data'].get('employment_rate', 0)*100:.1f}%",
            'Ever Employed': f"{scenario['data'].get('ever_employed_rate', 0)*100:.1f}%",
            'Repayment Rate': f"{scenario['data'].get('repayment_rate', 0)*100:.1f}%",
            'Payment Cap %': f"{scenario['data'].get('cap_stats', {}).get('payment_cap_pct', 0)*100:.1f}%",
            'Years Cap %': f"{scenario['data'].get('cap_stats', {}).get('years_cap_pct', 0)*100:.1f}%",
            'No Cap %': f"{scenario['data'].get('cap_stats', {}).get('no_cap_pct', 0)*100:.1f}%"
        })
    
    outcomes_table = dash_table.DataTable(
        data=outcomes_data,
        columns=[{"name": col, "id": col} for col in outcomes_data[0].keys()],
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
    
    comparison_elements.append(html.Div([
        html.H5("Student Outcomes by Scenario", style={'marginTop': '30px', 'marginBottom': '15px'}),
        outcomes_table
    ]))
    
    # 4. Degree Distribution Comparison
    degree_data = []
    for scenario in selected_scenarios:
        degree_pcts = scenario['data'].get('degree_pcts', {})
        degree_data.append({
            'Scenario': scenario['name'],
            'BA': f"{degree_pcts.get('BA', 0)*100:.1f}%",
            'MA': f"{degree_pcts.get('MA', 0)*100:.1f}%",
            'VOC': f"{degree_pcts.get('VOC', 0)*100:.1f}%",
            'NURSE': f"{degree_pcts.get('NURSE', 0)*100:.1f}%",
            'NA': f"{degree_pcts.get('NA', 0)*100:.1f}%",
            'LABOR': f"{degree_pcts.get('LABOR', 0)*100:.1f}%"
        })
    
    degree_table = dash_table.DataTable(
        data=degree_data,
        columns=[{"name": col, "id": col} for col in degree_data[0].keys()],
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
    
    comparison_elements.append(html.Div([
        html.H5("Degree Distribution by Scenario", style={'marginTop': '30px', 'marginBottom': '15px'}),
        degree_table
    ]))
    
    return html.Div(comparison_elements)

@app.callback(
    [Output("monte-carlo-loading", "children"),
     Output("monte-carlo-results", "children")],
    [Input("run-monte-carlo-button", "n_clicks")],
    [State("monte-carlo-sims", "value"),
     State("monte-carlo-complexity", "value"),
     State("mc-unemployment-range", "value"),
     State("mc-leave-labor-force-range", "value"),
     State("mc-wage-penalty-range", "value"),
     State("program-type", "value"),
     State("ba-pct", "value"),
     State("ma-pct", "value"),
     State("voc-pct", "value"),
     State("nurse-pct", "value"),
     State("na-pct", "value"),
     State("labor-pct", "value"),
     State("ba-salary", "value"),
     State("ma-salary", "value"),
     State("voc-salary", "value"),
     State("nurse-salary", "value"),
     State("na-salary", "value"),
     State("labor-salary", "value"),
     State("isa-percentage-input", "value"),
     State("isa-threshold-input", "value"),
     State("isa-cap-input", "value"),
     State("num-students", "value"),
     State("inflation-rate", "value")]
)
def run_monte_carlo_simulation(n_clicks, num_sims, complexity, 
                              unemployment_range, leave_labor_force_range, wage_penalty_range,
                              program_type, ba_pct, ma_pct, voc_pct, nurse_pct, na_pct, labor_pct,
                              ba_salary, ma_salary, voc_salary, nurse_salary, na_salary, labor_salary,
                              isa_percentage, isa_threshold, isa_cap,
                              num_students, inflation_rate):
    if not n_clicks:
        return "", html.Div("Click 'Run Monte Carlo Simulation' to see results")
    
    # Start with a loading message
    loading_message = "Running Monte Carlo simulation... This may take a moment."
    
    # Set default values for None parameters
    if isa_percentage is None:
        if program_type == 'University':
            isa_percentage = 14
        elif program_type == 'TVET':
            isa_percentage = 12
        elif program_type == 'Labor':
            isa_percentage = 12  # Changed from 10 to 12
        else:
            isa_percentage = 12
    
    if isa_threshold is None:
        isa_threshold = 27000
    
    if isa_cap is None:
        if program_type == 'University':
            isa_cap = 72500
        elif program_type == 'TVET':
            isa_cap = 49950
        elif program_type == 'Labor':
            isa_cap = 45000
        else:
            isa_cap = 50000
    
    if inflation_rate is None:
        inflation_rate = 2
    
    # Set default values for degree percentages if None
    if ba_pct is None: ba_pct = 0
    if ma_pct is None: ma_pct = 0
    if voc_pct is None: voc_pct = 0
    if nurse_pct is None: nurse_pct = 0
    if na_pct is None: na_pct = 0
    if labor_pct is None: labor_pct = 0
    
    # Set default values for salary parameters if None
    if ba_salary is None: ba_salary = 41300
    if ma_salary is None: ma_salary = 46709
    if voc_salary is None: voc_salary = 31500
    if nurse_salary is None: nurse_salary = 44000
    if na_salary is None: na_salary = 2200
    if labor_salary is None: labor_salary = 35000
    
    # Prepare parameters for simulation
    params = {
        'unemployment': (unemployment_range[0] + unemployment_range[1]) / 2,
        'leave_labor_force': (leave_labor_force_range[0] + leave_labor_force_range[1]) / 2,
        'wage_penalty': (wage_penalty_range[0] + wage_penalty_range[1]) / 2
    }
    
    # Determine number of parameters to vary based on complexity
    if complexity == 'Simple':
        num_params = 2  # Unemployment and Leave Labor Force
    elif complexity == 'Medium':
        num_params = 3  # Add Wage Penalty
    else:
        num_params = 3  # Keep at 3 for now
    
    # Generate parameter combinations
    min_unemployment, max_unemployment = unemployment_range
    min_leave_labor_force, max_leave_labor_force = leave_labor_force_range
    min_wage_penalty, max_wage_penalty = wage_penalty_range
    
    # Calculate number of variations per parameter
    variations_per_param = max(2, int(np.ceil(num_sims ** (1/num_params))))
    
    # Generate parameter values
    unemployment_values = np.linspace(min_unemployment, max_unemployment, variations_per_param)
    leave_labor_force_values = np.linspace(min_leave_labor_force, max_leave_labor_force, variations_per_param)
    wage_penalty_values = np.linspace(min_wage_penalty, max_wage_penalty, variations_per_param)
    
    # Create parameter grid
    param_grid = []
    for unemp in unemployment_values:
        for leave_labor_force in leave_labor_force_values:
            for wage_penalty in wage_penalty_values:
                param_grid.append({
                    'unemployment': unemp,
                    'leave_labor_force': leave_labor_force,
                    'wage_penalty': wage_penalty,
                    'adjusted_wage_penalty': wage_penalty + 20.0  # Apply +20% shift
                })
    
    # Limit to requested number of simulations
    if len(param_grid) > num_sims:
        param_grid = random.sample(param_grid, num_sims)
    
    # Run simulations
    results = []
    for params in param_grid:
        # Apply wage penalty to all salary parameters
        penalty_factor = 1 + (params['adjusted_wage_penalty'] / 100.0)
        adjusted_ba_salary = ba_salary * penalty_factor
        adjusted_ma_salary = ma_salary * penalty_factor
        adjusted_voc_salary = voc_salary * penalty_factor
        adjusted_nurse_salary = nurse_salary * penalty_factor
        adjusted_na_salary = na_salary * penalty_factor
        adjusted_labor_salary = labor_salary * penalty_factor
        
        # Run simulation with current parameter set
        sim_result = run_simple_simulation(
            program_type=program_type,
            num_students=num_students or 100,
            num_sims=1,  # Single simulation per parameter set
            scenario='custom',
            ba_pct=ba_pct / 100.0,
            ma_pct=ma_pct / 100.0,
            voc_pct=voc_pct / 100.0,
            nurse_pct=nurse_pct / 100.0,
            na_pct=na_pct / 100.0,
            labor_pct=labor_pct / 100.0,
            ba_salary=adjusted_ba_salary,
            ma_salary=adjusted_ma_salary,
            voc_salary=adjusted_voc_salary,
            nurse_salary=adjusted_nurse_salary,
            na_salary=adjusted_na_salary,
            labor_salary=adjusted_labor_salary,
            isa_percentage=(isa_percentage or 12) / 100.0,
            isa_threshold=isa_threshold or 27000,
            isa_cap=isa_cap or 50000,
            initial_unemployment_rate=params['unemployment'] / 100.0,
            initial_inflation_rate=(inflation_rate or 2) / 100.0,
            leave_labor_force_probability=params['leave_labor_force'] / 100.0
        )
        
        # Store results with parameter values
        results.append({
            'unemployment': params['unemployment'],
            'leave_labor_force': params['leave_labor_force'],
            'wage_penalty': params['wage_penalty'],
            'adjusted_wage_penalty': params['adjusted_wage_penalty'],
            'investor_irr': sim_result['investor_IRR'] * 100,
            'total_irr': sim_result['IRR'] * 100,
            'repayment_rate': sim_result['repayment_rate'] * 100,
            'employment_rate': sim_result['employment_rate'] * 100,
            'ever_employed_rate': sim_result['ever_employed_rate'] * 100,
            'average_payment': sim_result['average_total_payment'],
            'average_duration': sim_result['average_duration'],
            'payment_cap_pct': sim_result['cap_stats']['payment_cap_pct'] * 100,
            'years_cap_pct': sim_result['cap_stats']['years_cap_pct'] * 100,
            'no_cap_pct': sim_result['cap_stats']['no_cap_pct'] * 100
        })
    
    # Convert to DataFrame for easier analysis
    results_df = pd.DataFrame(results)
    
    # Create visualization elements
    viz_elements = []
    
    # Create tabs for different visualizations
    tabs = []
    
    # Tab 1: Simulation Parameters
    param_summary = html.Div([
        html.H4("Simulation Parameters", className="mt-4"),
        html.Div([
            html.Div([
                html.H5("Program Parameters"),
                html.Table([
                    html.Tr([html.Td("Program Type:"), html.Td(program_type)]),
                    html.Tr([html.Td("Number of Students:"), html.Td(f"{num_students}")]),
                    html.Tr([html.Td("Number of Simulations:"), html.Td(f"{len(results_df)}")]),
                    html.Tr([html.Td("ISA Percentage:"), html.Td(f"{isa_percentage}%")]),
                    html.Tr([html.Td("ISA Threshold:"), html.Td(f"${isa_threshold:,.0f}")]),
                    html.Tr([html.Td("ISA Cap:"), html.Td(f"${isa_cap:,.0f}")]),
                    html.Tr([html.Td("Base Inflation Rate:"), html.Td(f"{inflation_rate}%")])
                ], className="table table-sm")
            ], className="col-md-6"),
            
            html.Div([
                html.H5("Varied Parameters"),
                html.Table([
                    html.Tr([html.Td("Unemployment Range:"), html.Td(f"{min_unemployment}% to {max_unemployment}%")]),
                    html.Tr([html.Td("Leave Labor Force Range:"), html.Td(f"{min_leave_labor_force}% to {max_leave_labor_force}%")]),
                    html.Tr([html.Td("Wage Penalty Range:"), html.Td(f"{min_wage_penalty}% to {max_wage_penalty}%")]),
                    html.Tr([html.Td("Adjusted Wage Penalty:"), html.Td(f"{min_wage_penalty+20}% to {max_wage_penalty+20}%")]),
                    html.Tr([html.Td("Note:"), html.Td("Wage penalty is shifted by +20% in calculations")])
                ], className="table table-sm")
            ], className="col-md-6")
        ], className="row"),
        
        html.Div([
            html.H5("Degree Parameters", className="mt-3"),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Degree Type"),
                    html.Th("Percentage"),
                    html.Th("Base Salary"),
                    html.Th("Adjusted Salary")
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td("BA"),
                        html.Td(f"{ba_pct}%"),
                        html.Td(f"${ba_salary:,.0f}"),
                        html.Td(f"${ba_salary * (1 + (min_wage_penalty+20)/100):,.0f} to ${ba_salary * (1 + (max_wage_penalty+20)/100):,.0f}")
                    ]),
                    html.Tr([
                        html.Td("MA"),
                        html.Td(f"{ma_pct}%"),
                        html.Td(f"${ma_salary:,.0f}"),
                        html.Td(f"${ma_salary * (1 + (min_wage_penalty+20)/100):,.0f} to ${ma_salary * (1 + (max_wage_penalty+20)/100):,.0f}")
                    ]),
                    html.Tr([
                        html.Td("VOC"),
                        html.Td(f"{voc_pct}%"),
                        html.Td(f"${voc_salary:,.0f}"),
                        html.Td(f"${voc_salary * (1 + (min_wage_penalty+20)/100):,.0f} to ${voc_salary * (1 + (max_wage_penalty+20)/100):,.0f}")
                    ]),
                    html.Tr([
                        html.Td("NURSE"),
                        html.Td(f"{nurse_pct}%"),
                        html.Td(f"${nurse_salary:,.0f}"),
                        html.Td(f"${nurse_salary * (1 + (min_wage_penalty+20)/100):,.0f} to ${nurse_salary * (1 + (max_wage_penalty+20)/100):,.0f}")
                    ]),
                    html.Tr([
                        html.Td("LABOR"),
                        html.Td(f"{labor_pct}%"),
                        html.Td(f"${labor_salary:,.0f}"),
                        html.Td(f"${labor_salary * (1 + (min_wage_penalty+20)/100):,.0f} to ${labor_salary * (1 + (max_wage_penalty+20)/100):,.0f}")
                    ]),
                    html.Tr([
                        html.Td("NA"),
                        html.Td(f"{na_pct}%"),
                        html.Td(f"${na_salary:,.0f}"),
                        html.Td(f"${na_salary * (1 + (min_wage_penalty+20)/100):,.0f} to ${na_salary * (1 + (max_wage_penalty+20)/100):,.0f}")
                    ])
                ])
            ], className="table table-striped table-sm")
        ])
    ])
    
    tabs.append(dcc.Tab(label="Simulation Parameters", children=[param_summary]))
    
    # Tab 2: IRR Distribution
    # Create IRR histogram
    irr_fig = go.Figure()
    irr_fig.add_trace(go.Histogram(
        x=results_df['investor_irr'],
        nbinsx=20,
        marker_color='rgb(55, 83, 109)',
        opacity=0.7,
        name='Investor IRR'
    ))
    
    irr_fig.update_layout(
        title='Distribution of Investor IRR',
        xaxis_title='Investor IRR (%)',
        yaxis_title='Frequency',
        template='plotly_white'
    )
    
    # Calculate IRR statistics
    irr_stats = html.Div([
        html.H4("Return Metrics", className="mt-4"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Metric"),
                html.Th("Value")
            ])),
            html.Tbody([
                html.Tr([html.Td("Mean Investor IRR:"), html.Td(f"{results_df['investor_irr'].mean():.2f}%")]),
                html.Tr([html.Td("Median Investor IRR:"), html.Td(f"{results_df['investor_irr'].median():.2f}%")]),
                html.Tr([html.Td("Min Investor IRR:"), html.Td(f"{results_df['investor_irr'].min():.2f}%")]),
                html.Tr([html.Td("Max Investor IRR:"), html.Td(f"{results_df['investor_irr'].max():.2f}%")]),
                html.Tr([html.Td("Std Dev Investor IRR:"), html.Td(f"{results_df['investor_irr'].std():.2f}%")]),
                html.Tr([html.Td("10th Percentile IRR:"), html.Td(f"{results_df['investor_irr'].quantile(0.1):.2f}%")]),
                html.Tr([html.Td("25th Percentile IRR:"), html.Td(f"{results_df['investor_irr'].quantile(0.25):.2f}%")]),
                html.Tr([html.Td("75th Percentile IRR:"), html.Td(f"{results_df['investor_irr'].quantile(0.75):.2f}%")]),
                html.Tr([html.Td("90th Percentile IRR:"), html.Td(f"{results_df['investor_irr'].quantile(0.9):.2f}%")])
            ])
        ], className="table table-striped table-sm"),
        
        html.H4("Payment Quantiles", className="mt-4"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Metric"),
                html.Th("Value")
            ])),
            html.Tbody([
                html.Tr([html.Td("Mean Payment:"), html.Td(f"${results_df['average_payment'].mean():.2f}")]),
                html.Tr([html.Td("Median Payment:"), html.Td(f"${results_df['average_payment'].median():.2f}")]),
                html.Tr([html.Td("Min Payment:"), html.Td(f"${results_df['average_payment'].min():.2f}")]),
                html.Tr([html.Td("Max Payment:"), html.Td(f"${results_df['average_payment'].max():.2f}")]),
                html.Tr([html.Td("Mean Duration:"), html.Td(f"{results_df['average_duration'].mean():.2f} years")]),
                html.Tr([html.Td("Median Duration:"), html.Td(f"{results_df['average_duration'].median():.2f} years")])
            ])
        ], className="table table-striped table-sm")
    ])
    
    irr_tab_content = html.Div([
        dcc.Graph(figure=irr_fig),
        irr_stats
    ])
    
    tabs.append(dcc.Tab(label="IRR Distribution", children=[irr_tab_content]))
    
    # Tab 3: Scatter Plots
    # 1. Scatter Plot of Unemployment vs IRR
    scatter_fig = go.Figure()
    
    scatter_fig.add_trace(go.Scatter(
        x=results_df['unemployment'],
        y=results_df['investor_irr'],
        mode='markers',
        marker=dict(
            size=8,
            color=results_df['leave_labor_force'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Leave Labor Force %'),
            opacity=0.7
        ),
        text=[f"IRR: {irr:.1f}%<br>Unemployment: {unemp:.1f}%<br>Leave Labor Force: {llf:.1f}%<br>Wage Penalty: {wp:.1f}%" 
              for irr, unemp, llf, wp in zip(
                  results_df['investor_irr'], 
                  results_df['unemployment'], 
                  results_df['leave_labor_force'], 
                  results_df['wage_penalty']
              )],
        hoverinfo='text'
    ))
    
    scatter_fig.update_layout(
        title='Relationship Between Unemployment Rate and Investor IRR',
        xaxis_title='Unemployment Rate (%)',
        yaxis_title='Investor IRR (%)',
        template='plotly_white'
    )
    
    # 2. Scatter Plot of Leave Labor Force Probability vs IRR
    llf_scatter_fig = go.Figure()
    
    llf_scatter_fig.add_trace(go.Scatter(
        x=results_df['leave_labor_force'],
        y=results_df['investor_irr'],
        mode='markers',
        marker=dict(
            size=8,
            color=results_df['wage_penalty'],
            colorscale='RdBu',
            showscale=True,
            colorbar=dict(title='Wage Penalty %'),
            opacity=0.7
        ),
        text=[f"IRR: {irr:.1f}%<br>Leave Labor Force: {llf:.1f}%<br>Wage Penalty: {wp:.1f}%<br>Repayment: {rep:.1f}%" 
              for irr, llf, wp, rep in zip(
                  results_df['investor_irr'], 
                  results_df['leave_labor_force'], 
                  results_df['wage_penalty'], 
                  results_df['repayment_rate']
              )],
        hoverinfo='text'
    ))
    
    llf_scatter_fig.update_layout(
        title='Relationship Between Leave Labor Force Probability and Investor IRR',
        xaxis_title='Leave Labor Force Probability (%)',
        yaxis_title='Investor IRR (%)',
        template='plotly_white'
    )
    
    # 3. Scatter Plot of Wage Penalty vs IRR
    wp_scatter_fig = go.Figure()
    
    wp_scatter_fig.add_trace(go.Scatter(
        x=results_df['wage_penalty'],
        y=results_df['investor_irr'],
        mode='markers',
        marker=dict(
            size=8,
            color=results_df['leave_labor_force'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Leave Labor Force %'),
            opacity=0.7
        ),
        text=[f"IRR: {irr:.1f}%<br>Wage Penalty: {wp:.1f}%<br>Adjusted: {adj_wp:.1f}%<br>Leave Labor Force: {llf:.1f}%" 
              for irr, wp, adj_wp, llf in zip(
                  results_df['investor_irr'], 
                  results_df['wage_penalty'], 
                  results_df['adjusted_wage_penalty'],
                  results_df['leave_labor_force']
              )],
        hoverinfo='text'
    ))
    
    wp_scatter_fig.update_layout(
        title='Relationship Between Wage Penalty and Investor IRR',
        xaxis_title='Wage Penalty (%)',
        yaxis_title='Investor IRR (%)',
        template='plotly_white'
    )
    
    scatter_tab_content = html.Div([
        dcc.Graph(figure=scatter_fig),
        dcc.Graph(figure=llf_scatter_fig),
        dcc.Graph(figure=wp_scatter_fig)
    ])
    
    tabs.append(dcc.Tab(label="Parameter Relationships", children=[scatter_tab_content]))
    
    # Tab 4: Student Outcomes
    # Create student outcomes visualization
    outcomes_fig = go.Figure()
    
    outcomes_fig.add_trace(go.Scatter(
        x=results_df['unemployment'],
        y=results_df['employment_rate'],
        mode='markers',
        marker=dict(
            size=8,
            color=results_df['leave_labor_force'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Leave Labor Force %'),
            opacity=0.7
        ),
        text=[f"Employment Rate: {emp:.1f}%<br>Unemployment: {unemp:.1f}%<br>Leave Labor Force: {llf:.1f}%" 
              for emp, unemp, llf in zip(
                  results_df['employment_rate'], 
                  results_df['unemployment'], 
                  results_df['leave_labor_force']
              )],
        hoverinfo='text',
        name='Employment Rate'
    ))
    
    outcomes_fig.update_layout(
        title='Employment Rate vs Unemployment Rate',
        xaxis_title='Unemployment Rate (%)',
        yaxis_title='Employment Rate (%)',
        template='plotly_white'
    )
    
    # Create repayment categories visualization
    repayment_fig = go.Figure()
    
    # Calculate average repayment categories
    avg_payment_cap = results_df['payment_cap_pct'].mean()
    avg_years_cap = results_df['years_cap_pct'].mean()
    avg_no_cap = results_df['no_cap_pct'].mean()
    
    repayment_fig.add_trace(go.Pie(
        labels=['Hit Payment Cap', 'Hit Years Cap', 'No Cap Hit'],
        values=[avg_payment_cap, avg_years_cap, avg_no_cap],
        textinfo='percent+label',
        marker=dict(colors=['rgb(55, 83, 109)', 'rgb(26, 118, 255)', 'rgb(95, 158, 160)'])
    ))
    
    repayment_fig.update_layout(
        title='Average Repayment Categories',
        template='plotly_white'
    )
    
    # Create student outcomes summary table
    outcomes_stats = html.Div([
        html.H4("Student Outcomes Summary", className="mt-4"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Metric"),
                html.Th("Mean"),
                html.Th("Median"),
                html.Th("Min"),
                html.Th("Max")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td("Employment Rate"),
                    html.Td(f"{results_df['employment_rate'].mean():.1f}%"),
                    html.Td(f"{results_df['employment_rate'].median():.1f}%"),
                    html.Td(f"{results_df['employment_rate'].min():.1f}%"),
                    html.Td(f"{results_df['employment_rate'].max():.1f}%")
                ]),
                html.Tr([
                    html.Td("Ever Employed Rate"),
                    html.Td(f"{results_df['ever_employed_rate'].mean():.1f}%"),
                    html.Td(f"{results_df['ever_employed_rate'].median():.1f}%"),
                    html.Td(f"{results_df['ever_employed_rate'].min():.1f}%"),
                    html.Td(f"{results_df['ever_employed_rate'].max():.1f}%")
                ]),
                html.Tr([
                    html.Td("Repayment Rate"),
                    html.Td(f"{results_df['repayment_rate'].mean():.1f}%"),
                    html.Td(f"{results_df['repayment_rate'].median():.1f}%"),
                    html.Td(f"{results_df['repayment_rate'].min():.1f}%"),
                    html.Td(f"{results_df['repayment_rate'].max():.1f}%")
                ]),
                html.Tr([
                    html.Td("Payment Cap %"),
                    html.Td(f"{results_df['payment_cap_pct'].mean():.1f}%"),
                    html.Td(f"{results_df['payment_cap_pct'].median():.1f}%"),
                    html.Td(f"{results_df['payment_cap_pct'].min():.1f}%"),
                    html.Td(f"{results_df['payment_cap_pct'].max():.1f}%")
                ]),
                html.Tr([
                    html.Td("Years Cap %"),
                    html.Td(f"{results_df['years_cap_pct'].mean():.1f}%"),
                    html.Td(f"{results_df['years_cap_pct'].median():.1f}%"),
                    html.Td(f"{results_df['years_cap_pct'].min():.1f}%"),
                    html.Td(f"{results_df['years_cap_pct'].max():.1f}%")
                ]),
                html.Tr([
                    html.Td("No Cap %"),
                    html.Td(f"{results_df['no_cap_pct'].mean():.1f}%"),
                    html.Td(f"{results_df['no_cap_pct'].median():.1f}%"),
                    html.Td(f"{results_df['no_cap_pct'].min():.1f}%"),
                    html.Td(f"{results_df['no_cap_pct'].max():.1f}%")
                ])
            ])
        ], className="table table-striped table-sm")
    ])
    
    outcomes_tab_content = html.Div([
        dcc.Graph(figure=outcomes_fig),
        dcc.Graph(figure=repayment_fig),
        outcomes_stats
    ])
    
    tabs.append(dcc.Tab(label="Student Outcomes", children=[outcomes_tab_content]))
    
    # Combine all tabs
    viz_elements = []
    for tab in tabs:
        viz_elements.append(tab)
    
    return "", html.Div(viz_elements)

@app.callback(
    Output("weight-sum-warning", "children"),
    [Input("scenario1-weight", "value"),
     Input("scenario2-weight", "value"),
     Input("scenario3-weight", "value")]
)
def validate_weight_sum(weight1, weight2, weight3):
    if weight1 is None or weight2 is None or weight3 is None:
        return "Please enter weights for all scenarios."
    
    total = weight1 + weight2 + weight3
    
    if total != 100:
        return f"Warning: Weights sum to {total}%, not 100%. Please adjust the weights."
    
    return ""

@app.callback(
    [Output("blended-monte-carlo-loading", "children"),
     Output("blended-monte-carlo-results", "children")],
    [Input("run-blended-monte-carlo-button", "n_clicks")],
    [State("blended-monte-carlo-sims", "value"),
     State("scenario1-type", "value"),
     State("scenario2-type", "value"),
     State("scenario3-type", "value"),
     State("scenario1-weight", "value"),
     State("scenario2-weight", "value"),
     State("scenario3-weight", "value"),
     State("blended-leave-labor-force-range", "value"),
     State("blended-wage-penalty-range", "value"),
     State("program-type", "value"),
     State("ba-pct", "value"),
     State("ma-pct", "value"),
     State("voc-pct", "value"),
     State("nurse-pct", "value"),
     State("na-pct", "value"),
     State("labor-pct", "value"),
     State("ba-salary", "value"),
     State("ma-salary", "value"),
     State("voc-salary", "value"),
     State("nurse-salary", "value"),
     State("na-salary", "value"),
     State("labor-salary", "value"),
     State("isa-percentage-input", "value"),
     State("isa-threshold-input", "value"),
     State("isa-cap-input", "value"),
     State("num-students", "value"),
     State("inflation-rate", "value")]
)
def run_blended_monte_carlo(n_clicks, num_sims, 
                           scenario1_type, scenario2_type, scenario3_type,
                           scenario1_weight, scenario2_weight, scenario3_weight,
                           leave_labor_force_range, wage_penalty_range,
                           program_type, ba_pct, ma_pct, voc_pct, nurse_pct, na_pct, labor_pct,
                           ba_salary, ma_salary, voc_salary, nurse_salary, na_salary, labor_salary,
                           isa_percentage, isa_threshold, isa_cap,
                           num_students, inflation_rate):
    if n_clicks == 0:
        return "", html.Div("Click 'Run Blended Monte Carlo Simulation' to see results")
    
    # Start with a loading message
    loading_message = "Running Blended Monte Carlo simulation... This may take a moment."
    
    # Validate weights
    if scenario1_weight is None or scenario2_weight is None or scenario3_weight is None:
        return "", html.Div("Please enter weights for all scenarios.", style={'color': 'red'})
    
    # Set default values for None parameters
    if isa_percentage is None:
        if program_type == 'University':
            isa_percentage = 14
        elif program_type == 'TVET':
            isa_percentage = 12
        elif program_type == 'Labor':
            isa_percentage = 12  # Changed from 10 to 12
        else:
            isa_percentage = 12
    
    if isa_threshold is None:
        isa_threshold = 27000
    
    if isa_cap is None:
        if program_type == 'University':
            isa_cap = 72500
        elif program_type == 'TVET':
            isa_cap = 49950
        elif program_type == 'Labor':
            isa_cap = 45000
        else:
            isa_cap = 50000
    
    if inflation_rate is None:
        inflation_rate = 2
    
    # Set default values for degree percentages if None
    if ba_pct is None: ba_pct = 0
    if ma_pct is None: ma_pct = 0
    if voc_pct is None: voc_pct = 0
    if nurse_pct is None: nurse_pct = 0
    if na_pct is None: na_pct = 0
    if labor_pct is None: labor_pct = 0
    
    # Set default values for salary parameters if None
    if ba_salary is None: ba_salary = 41300
    if ma_salary is None: ma_salary = 46709
    if voc_salary is None: voc_salary = 31500
    if nurse_salary is None: nurse_salary = 44000
    if na_salary is None: na_salary = 2200
    if labor_salary is None: labor_salary = 35000
    
    # Normalize weights to sum to 1
    total_weight = scenario1_weight + scenario2_weight + scenario3_weight
    if total_weight != 100:
        return "", html.Div(f"Weights must sum to 100%. Current sum: {total_weight}%", style={'color': 'red'})
    
    # Normalize weights to probabilities
    weights = [scenario1_weight / 100.0, scenario2_weight / 100.0, scenario3_weight / 100.0]
    scenarios = [scenario1_type, scenario2_type, scenario3_type]
    
    # Prepare base parameters for custom scenario
    base_params = {
        'program_type': program_type,
        'num_students': num_students or 100,  # Default to 100 if None
        'num_sims': 5,  # Use minimal simulations per run for speed
        'ba_pct': (ba_pct or 0) / 100.0,
        'ma_pct': (ma_pct or 0) / 100.0,
        'voc_pct': (voc_pct or 0) / 100.0,
        'nurse_pct': (nurse_pct or 0) / 100.0,
        'na_pct': (na_pct or 0) / 100.0,
        'labor_pct': (labor_pct or 0) / 100.0,
        'ba_salary': ba_salary or 41300,
        'ma_salary': ma_salary or 46709,
        'voc_salary': voc_salary or 31500,
        'nurse_salary': nurse_salary or 44000,
        'na_salary': na_salary or 2200,
        'labor_salary': labor_salary or 35000,
        'isa_percentage': (isa_percentage or 12) / 100.0,
        'isa_threshold': isa_threshold or 27000,
        'isa_cap': isa_cap or 50000,
        'initial_inflation_rate': (inflation_rate or 2) / 100.0
    }
    
    # Unpack ranges
    min_leave_labor_force, max_leave_labor_force = leave_labor_force_range
    min_wage_penalty, max_wage_penalty = wage_penalty_range
    
    # Run Monte Carlo simulations
    results = []
    np.random.seed(42)
    
    for i in range(num_sims):
        # Randomly select a scenario based on weights
        selected_scenario = np.random.choice(scenarios, p=weights)
        
        # Generate random parameters for this simulation
        sim_params = base_params.copy()
        sim_params['scenario'] = selected_scenario
        
        # Apply leave labor force probability
        sim_params['leave_labor_force_probability'] = np.random.uniform(min_leave_labor_force, max_leave_labor_force) / 100.0
        
        # Apply wage penalty to all salary parameters
        # Shift the wage penalty by 20% (e.g., -20% becomes 0%, -40% becomes -20%)
        raw_wage_penalty = np.random.uniform(min_wage_penalty, max_wage_penalty) / 100.0
        adjusted_wage_penalty = raw_wage_penalty + 0.2  # Shift by 20%
        penalty_factor = 1 + adjusted_wage_penalty
        
        sim_params['ba_salary'] = ba_salary * penalty_factor
        sim_params['ma_salary'] = ma_salary * penalty_factor
        sim_params['voc_salary'] = voc_salary * penalty_factor
        sim_params['nurse_salary'] = nurse_salary * penalty_factor
        sim_params['na_salary'] = na_salary * penalty_factor
        sim_params['labor_salary'] = labor_salary * penalty_factor
        
        # Add a random seed for each simulation
        sim_params['random_seed'] = np.random.randint(1, 10000)
        
        try:
            # Run the simulation with the varied parameters
            sim_result = run_simple_simulation(**sim_params)
            
            # Extract key metrics
            results.append({
                'investor_irr': sim_result.get('investor_IRR', 0) * 100,  # Convert to percentage
                'total_irr': sim_result.get('IRR', 0) * 100,
                'avg_payment': sim_result.get('average_total_payment', 0),
                'duration': sim_result.get('average_duration', 0),
                'repayment_rate': sim_result.get('repayment_rate', 0) * 100,
                'employment_rate': sim_result.get('employment_rate', 0) * 100,
                'ever_employed_rate': sim_result.get('ever_employed_rate', 0) * 100,
                'leave_labor_force': sim_params.get('leave_labor_force_probability', 0) * 100,
                'wage_penalty': raw_wage_penalty * 100,
                'adjusted_wage_penalty': adjusted_wage_penalty * 100,
                'scenario': selected_scenario
            })
        except Exception as e:
            # If simulation fails, skip this iteration
            continue
    
    if not results:
        return "", html.Div("No valid simulation results. Try different parameters.")
    
    # Convert results to DataFrame for analysis
    results_df = pd.DataFrame(results)
    
    # Create tabs for different visualizations
    tabs = []
    
    # Scenario labels for display
    scenario_labels = {
        'baseline': 'Baseline',
        'conservative': 'Conservative',
        'optimistic': 'Optimistic',
        'custom': 'Custom'
    }
    
    # Tab 1: Simulation Parameters
    param_summary = html.Div([
        html.H4("Blended Monte Carlo Parameters", className="mt-4"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Parameter"),
                html.Th("Value")
            ])),
            html.Tbody([
                html.Tr([html.Td("Number of Simulations"), html.Td(f"{len(results_df)}")]),
                html.Tr([html.Td("Program Type"), html.Td(f"{program_type}")]),
                html.Tr([html.Td("Scenario 1"), html.Td(f"{scenario_labels.get(scenario1_type, scenario1_type)} ({scenario1_weight}%)")]),
                html.Tr([html.Td("Scenario 2"), html.Td(f"{scenario_labels.get(scenario2_type, scenario2_type)} ({scenario2_weight}%)")]),
                html.Tr([html.Td("Scenario 3"), html.Td(f"{scenario_labels.get(scenario3_type, scenario3_type)} ({scenario3_weight}%)")]),
                html.Tr([html.Td("Leave Labor Force Range"), html.Td(f"{min_leave_labor_force}% to {max_leave_labor_force}%")]),
                html.Tr([html.Td("Wage Penalty Range"), html.Td(f"{min_wage_penalty}% to {max_wage_penalty}%")]),
                html.Tr([html.Td("Wage Penalty Adjustment"), html.Td("+20% (applied to all wage penalties)")])
            ])
        ], className="table table-striped table-sm"),
        
        # Add scenario distribution pie chart
        html.H4("Scenario Distribution", className="mt-4"),
        dcc.Graph(figure=go.Figure(data=[go.Pie(
            labels=[scenario_labels.get(s, s) for s in results_df['scenario'].value_counts().index],
            values=results_df['scenario'].value_counts().values,
            hole=.3,
            marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        )]).update_layout(
            title='Distribution of Selected Scenarios',
            template='plotly_white'
        ))
    ])
    
    tabs.append(dcc.Tab(label="Simulation Parameters", children=[param_summary]))
    
    # Tab 2: IRR Distribution
    # Create IRR histogram
    irr_fig = go.Figure()
    irr_fig.add_trace(go.Histogram(
        x=results_df['investor_irr'],
        name='Investor IRR',
        marker_color='rgb(26, 118, 255)',
        opacity=0.75,
        nbinsx=30
    ))
    
    # Add vertical lines for key statistics
    median_irr = results_df['investor_irr'].median()
    mean_irr = results_df['investor_irr'].mean()
    p10_irr = results_df['investor_irr'].quantile(0.1)
    p90_irr = results_df['investor_irr'].quantile(0.9)
    
    irr_fig.add_vline(x=median_irr, line_dash="dash", line_color="black", annotation_text=f"Median: {median_irr:.1f}%")
    irr_fig.add_vline(x=mean_irr, line_dash="solid", line_color="red", annotation_text=f"Mean: {mean_irr:.1f}%")
    irr_fig.add_vline(x=p10_irr, line_dash="dot", line_color="orange", annotation_text=f"P10: {p10_irr:.1f}%")
    irr_fig.add_vline(x=p90_irr, line_dash="dot", line_color="green", annotation_text=f"P90: {p90_irr:.1f}%")
    
    irr_fig.update_layout(
        title='Blended Monte Carlo Distribution of Investor IRR',
        xaxis_title='Investor IRR (%)',
        yaxis_title='Frequency',
        template='plotly_white',
        bargap=0.1
    )
    
    # IRR statistics table
    irr_stats = html.Div([
        html.H4("IRR Distribution Statistics", className="mt-4"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Statistic"),
                html.Th("Value")
            ])),
            html.Tbody([
                html.Tr([html.Td("Mean IRR"), html.Td(f"{results_df['investor_irr'].mean():.2f}%")]),
                html.Tr([html.Td("Median IRR"), html.Td(f"{results_df['investor_irr'].median():.2f}%")]),
                html.Tr([html.Td("Standard Deviation"), html.Td(f"{results_df['investor_irr'].std():.2f}%")]),
                html.Tr([html.Td("10th Percentile"), html.Td(f"{results_df['investor_irr'].quantile(0.1):.2f}%")]),
                html.Tr([html.Td("25th Percentile"), html.Td(f"{results_df['investor_irr'].quantile(0.25):.2f}%")]),
                html.Tr([html.Td("75th Percentile"), html.Td(f"{results_df['investor_irr'].quantile(0.75):.2f}%")]),
                html.Tr([html.Td("90th Percentile"), html.Td(f"{results_df['investor_irr'].quantile(0.9):.2f}%")]),
                html.Tr([html.Td("Minimum IRR"), html.Td(f"{results_df['investor_irr'].min():.2f}%")]),
                html.Tr([html.Td("Maximum IRR"), html.Td(f"{results_df['investor_irr'].max():.2f}%")]),
                html.Tr([html.Td("Probability of IRR > 5%"), html.Td(f"{(results_df['investor_irr'] > 5).mean()*100:.1f}%")]),
                html.Tr([html.Td("Probability of IRR > 8%"), html.Td(f"{(results_df['investor_irr'] > 8).mean()*100:.1f}%")]),
                html.Tr([html.Td("Probability of IRR < 0%"), html.Td(f"{(results_df['investor_irr'] < 0).mean()*100:.1f}%")])
            ])
        ], className="table table-striped table-sm")
    ])
    
    irr_tab_content = html.Div([
        dcc.Graph(figure=irr_fig),
        irr_stats
    ])
    
    tabs.append(dcc.Tab(label="IRR Distribution", children=[irr_tab_content]))
    
    # Tab 3: Scenario Comparison
    # IRR by Scenario Box Plot
    scenario_box = go.Figure()
    
    for scenario in results_df['scenario'].unique():
        scenario_data = results_df[results_df['scenario'] == scenario]
        scenario_box.add_trace(go.Box(
            y=scenario_data['investor_irr'],
            name=scenario_labels.get(scenario, scenario),
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
        ))
    
    scenario_box.update_layout(
        title='IRR Distribution by Scenario',
        yaxis_title='Investor IRR (%)',
        template='plotly_white'
    )
    
    # Scenario statistics table
    scenario_stats = html.Div([
        html.H4("Scenario Comparison", className="mt-4"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Scenario"),
                html.Th("Count"),
                html.Th("Mean IRR"),
                html.Th("Median IRR"),
                html.Th("Min IRR"),
                html.Th("Max IRR")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(scenario_labels.get(scenario, scenario)),
                    html.Td(f"{len(results_df[results_df['scenario'] == scenario])}"),
                    html.Td(f"{results_df[results_df['scenario'] == scenario]['investor_irr'].mean():.2f}%"),
                    html.Td(f"{results_df[results_df['scenario'] == scenario]['investor_irr'].median():.2f}%"),
                    html.Td(f"{results_df[results_df['scenario'] == scenario]['investor_irr'].min():.2f}%"),
                    html.Td(f"{results_df[results_df['scenario'] == scenario]['investor_irr'].max():.2f}%")
                ]) for scenario in results_df['scenario'].unique()
            ])
        ], className="table table-striped table-sm")
    ])
    
    scenario_tab_content = html.Div([
        dcc.Graph(figure=scenario_box),
        scenario_stats
    ])
    
    tabs.append(dcc.Tab(label="Scenario Comparison", children=[scenario_tab_content]))
    
    # Tab 4: Parameter Relationships
    # Scatter Plot of Leave Labor Force vs IRR colored by Scenario
    llf_scatter_fig = go.Figure()
    
    for scenario in results_df['scenario'].unique():
        scenario_data = results_df[results_df['scenario'] == scenario]
        llf_scatter_fig.add_trace(go.Scatter(
            x=scenario_data['leave_labor_force'],
            y=scenario_data['investor_irr'],
            mode='markers',
            name=scenario_labels.get(scenario, scenario),
            text=[f"IRR: {irr:.1f}%<br>Leave Labor Force: {llf:.1f}%<br>Scenario: {scenario_labels.get(s, s)}" 
                  for irr, llf, s in zip(
                      scenario_data['investor_irr'], 
                      scenario_data['leave_labor_force'],
                      scenario_data['scenario']
                  )],
            hoverinfo='text'
        ))
    
    llf_scatter_fig.update_layout(
        title='Relationship Between Leave Labor Force Probability and Investor IRR by Scenario',
        xaxis_title='Leave Labor Force Probability (%)',
        yaxis_title='Investor IRR (%)',
        template='plotly_white'
    )
    
    # Scatter Plot of Wage Penalty vs IRR colored by Scenario
    wp_scatter_fig = go.Figure()
    
    for scenario in results_df['scenario'].unique():
        scenario_data = results_df[results_df['scenario'] == scenario]
        wp_scatter_fig.add_trace(go.Scatter(
            x=scenario_data['wage_penalty'],
            y=scenario_data['investor_irr'],
            mode='markers',
            name=scenario_labels.get(scenario, scenario),
            text=[f"IRR: {irr:.1f}%<br>Wage Penalty: {wp:.1f}%<br>Scenario: {scenario_labels.get(s, s)}" 
                  for irr, wp, s in zip(
                      scenario_data['investor_irr'], 
                      scenario_data['wage_penalty'],
                      scenario_data['scenario']
                  )],
            hoverinfo='text'
        ))
    
    wp_scatter_fig.update_layout(
        title='Relationship Between Wage Penalty and Investor IRR by Scenario',
        xaxis_title='Wage Penalty (%)',
        yaxis_title='Investor IRR (%)',
        template='plotly_white'
    )
    
    parameter_tab_content = html.Div([
        dcc.Graph(figure=llf_scatter_fig),
        dcc.Graph(figure=wp_scatter_fig)
    ])
    
    tabs.append(dcc.Tab(label="Parameter Relationships", children=[parameter_tab_content]))
    
    # Tab 5: Student Outcomes
    # Create student outcomes visualization
    outcomes_fig = go.Figure()
    
    # Add employment rate vs IRR scatter plot
    outcomes_fig.add_trace(go.Scatter(
        x=results_df['employment_rate'],
        y=results_df['investor_irr'],
        mode='markers',
        marker=dict(
            size=8,
            color=results_df['scenario'].map({s: i for i, s in enumerate(results_df['scenario'].unique())}),
            colorscale='Viridis',
            showscale=False,
            opacity=0.7
        ),
        text=[f"IRR: {irr:.1f}%<br>Employment Rate: {emp:.1f}%<br>Scenario: {scenario_labels.get(s, s)}" 
              for irr, emp, s in zip(
                  results_df['investor_irr'], 
                  results_df['employment_rate'],
                  results_df['scenario']
              )],
        hoverinfo='text',
        name='Employment Rate vs IRR'
    ))
    
    outcomes_fig.update_layout(
        title='Relationship Between Employment Rate and Investor IRR',
        xaxis_title='Employment Rate (%)',
        yaxis_title='Investor IRR (%)',
        template='plotly_white'
    )
    
    # Create repayment rate vs IRR scatter plot
    repayment_fig = go.Figure()
    
    repayment_fig.add_trace(go.Scatter(
        x=results_df['repayment_rate'],
        y=results_df['investor_irr'],
        mode='markers',
        marker=dict(
            size=8,
            color=results_df['scenario'].map({s: i for i, s in enumerate(results_df['scenario'].unique())}),
            colorscale='Viridis',
            showscale=False,
            opacity=0.7
        ),
        text=[f"IRR: {irr:.1f}%<br>Repayment Rate: {rep:.1f}%<br>Scenario: {scenario_labels.get(s, s)}" 
              for irr, rep, s in zip(
                  results_df['investor_irr'], 
                  results_df['repayment_rate'],
                  results_df['scenario']
              )],
        hoverinfo='text',
        name='Repayment Rate vs IRR'
    ))
    
    repayment_fig.update_layout(
        title='Relationship Between Repayment Rate and Investor IRR',
        xaxis_title='Repayment Rate (%)',
        yaxis_title='Investor IRR (%)',
        template='plotly_white'
    )
    
    # Create student outcomes summary table
    outcomes_stats = html.Div([
        html.H4("Student Outcomes by Scenario", className="mt-4"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Scenario"),
                html.Th("Employment Rate"),
                html.Th("Ever Employed Rate"),
                html.Th("Repayment Rate")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(scenario_labels.get(scenario, scenario)),
                    html.Td(f"{results_df[results_df['scenario'] == scenario]['employment_rate'].mean():.1f}%"),
                    html.Td(f"{results_df[results_df['scenario'] == scenario]['ever_employed_rate'].mean():.1f}%"),
                    html.Td(f"{results_df[results_df['scenario'] == scenario]['repayment_rate'].mean():.1f}%")
                ]) for scenario in results_df['scenario'].unique()
            ])
        ], className="table table-striped table-sm")
    ])
    
    outcomes_tab_content = html.Div([
        dcc.Graph(figure=outcomes_fig),
        dcc.Graph(figure=repayment_fig),
        outcomes_stats
    ])
    
    tabs.append(dcc.Tab(label="Student Outcomes", children=[outcomes_tab_content]))
    
    # Combine all tabs
    viz_elements = html.Div([
        dcc.Tabs(tabs)
    ])
    
    return "", viz_elements

# Run the app
if __name__ == "__main__":
    # Use this for local development
    app.run_server(debug=False, host='0.0.0.0', port=10000) 