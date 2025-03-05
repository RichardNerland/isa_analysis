import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time

# Import the custom model
from isa_model import run_monte_carlo_simulations

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Degree probabilities options
degree_scenarios = {
    'Baseline': [0.43, 0.23, 0.25, 0.09],
    'Conservative': [0.3, 0.1, 0.4, 0.2],
    'Optimistic': [0.625, 0.325, 0.025, 0.025],
    'High Immigration': [0.3, 0.1, 0.1, 0.5]
}

# Define the layout of the app
app.layout = html.Div([
    html.H1("ISA Analysis Dashboard", style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    html.Div([
        html.Div([
            html.H3("Simulation Parameters", style={'marginBottom': '20px'}),
            
            html.Div([
                html.Label("Degree Distribution Scenario:"),
                dcc.Dropdown(
                    id="degree-scenario",
                    options=[{'label': k, 'value': k} for k in degree_scenarios.keys()],
                    value="Baseline"
                ),
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Label("Number of Students:"),
                dcc.Input(id="num-students", type="number", value=100, min=1, max=1000),
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Label("Number of Simulations:"),
                dcc.Input(id="num-sims", type="number", value=50, min=1, max=1000),
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Label("Number of Years:"),
                dcc.Input(id="num-years", type="number", value=25, min=1, max=50),
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Label("Limit Years:"),
                dcc.Input(id="limit-years", type="number", value=10, min=1, max=50),
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Label("ISA Percentage:"),
                dcc.Slider(
                    id="isa-percentage",
                    min=0.05,
                    max=0.25,
                    step=0.01,
                    value=0.14,
                    marks={i/100: f'{i}%' for i in range(5, 26, 5)},
                ),
            ], style={'marginBottom': '20px'}),
            
            html.Div([
                html.Label("Price per Student:"),
                dcc.Input(id="price-per-student", type="number", value=30000, min=1000),
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Label("Initial ISA Cap:"),
                dcc.Input(id="initial-isa-cap", type="number", value=90000, min=1000),
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Label("Initial ISA Threshold:"),
                dcc.Input(id="initial-isa-threshold", type="number", value=30000, min=1000),
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Label("Initial GDP Growth:"),
                dcc.Input(id="initial-gdp-growth", type="number", value=0.01, min=-0.05, max=0.1, step=0.01),
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Label("Initial Unemployment Rate:"),
                dcc.Input(id="initial-unemployment-rate", type="number", value=0.04, min=0, max=0.2, step=0.01),
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Label("Initial Inflation Rate:"),
                dcc.Input(id="initial-inflation-rate", type="number", value=0.02, min=-0.05, max=0.2, step=0.01),
            ], style={'marginBottom': '20px'}),
            
            html.Button(
                "Run Simulation", 
                id="run-simulation", 
                n_clicks=0,
                style={
                    'backgroundColor': '#4CAF50',
                    'color': 'white',
                    'padding': '10px 20px',
                    'borderRadius': '5px',
                    'border': 'none',
                    'fontSize': '16px',
                    'cursor': 'pointer',
                    'width': '100%'
                }
            ),
            
            html.Div(id="loading-message", style={'marginTop': '10px', 'color': '#888'})
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)'}),
        
        html.Div([
            html.H3("Results"),
            
            html.Div([
                html.Div(id="summary-stats", style={'marginBottom': '20px'}),
                
                dcc.Tabs([
                    dcc.Tab(label='Payment Distribution', children=[
                        dcc.Graph(id="payment-distribution")
                    ]),
                    dcc.Tab(label='Tranche Performance', children=[
                        dcc.Graph(id="tranche-performance")
                    ]),
                    dcc.Tab(label='IRR Distribution', children=[
                        dcc.Graph(id="irr-distribution")
                    ]),
                    dcc.Tab(label='Detailed Results', children=[
                        html.Div(id="detailed-results")
                    ])
                ])
            ])
        ], style={'width': '65%', 'display': 'inline-block', 'padding': '20px', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px', 'marginBottom': '30px'}),
    
    dcc.Store(id='simulation-results-store')
])

# Define callback for running the simulation
@app.callback(
    [Output("loading-message", "children"),
     Output("simulation-results-store", "data")],
    [Input("run-simulation", "n_clicks")],
    [State("degree-scenario", "value"),
     State("num-students", "value"),
     State("num-sims", "value"),
     State("num-years", "value"),
     State("limit-years", "value"),
     State("isa-percentage", "value"),
     State("price-per-student", "value"),
     State("initial-isa-cap", "value"),
     State("initial-isa-threshold", "value"),
     State("initial-gdp-growth", "value"),
     State("initial-unemployment-rate", "value"),
     State("initial-inflation-rate", "value")]
)
def run_simulation(n_clicks, degree_scenario, num_students, num_sims, num_years, limit_years, 
                  isa_percentage, price_per_student, initial_isa_cap, initial_isa_threshold,
                  initial_gdp_growth, initial_unemployment_rate, initial_inflation_rate):
    if n_clicks == 0:
        # Return empty results if the button hasn't been clicked
        return "Ready to run simulation", None
    
    # Show running message
    message = "Running simulation... This may take a moment."
    
    # Get the degree probabilities from the scenario
    degree_probs = degree_scenarios[degree_scenario]
    
    # Run the simulation
    results = run_monte_carlo_simulations(
        num_students=num_students,
        num_sims=num_sims,
        num_years=num_years,
        limit_years=limit_years,
        price_per_student=price_per_student,
        initial_isa_cap=initial_isa_cap,
        initial_isa_threshold=initial_isa_threshold,
        isa_percentage=isa_percentage,
        initial_gdp_growth=initial_gdp_growth,
        initial_unemployment_rate=initial_unemployment_rate,
        initial_inflation_rate=initial_inflation_rate,
        degree_probs=degree_probs
    )
    
    # Convert DataFrames to JSON for storage
    serializable_results = {
        'IRR': results['IRR'],
        'IRR_senior': results['IRR_senior'],
        'IRR_mezzanine': results['IRR_mezzanine'],
        'IRR_remainder': results['IRR_remainder'],
        'IRR_quantile_75': results['IRR_quantile_75'],
        'IRR_quantile_25': results['IRR_quantile_25'],
        'IRR_quantile_0': results['IRR_quantile_0'],
        'IRR_quantile_100': results['IRR_quantile_100'],
        'average_total_payment': results['average_total_payment'],
        'average_duration': results['average_duration'],
        'total_debt': results['total_debt'],
        'senior_debt': results['senior_debt'],
        'mezzanine_debt': results['mezzanine_debt'],
        'remainder_debt': results['remainder_debt'],
        'payment_by_year': results['payment_by_year'].to_dict(),
        'payments_df': results['payments_df'].to_dict(),
        'payments_df_senior': results['payments_df_senior'].to_dict(),
        'payments_df_mezzanine': results['payments_df_mezzanine'].to_dict(),
        'payments_df_remainder': results['payments_df_remainder'].to_dict(),
    }
    
    return "Simulation completed!", serializable_results

# Callback for summary stats
@app.callback(
    Output("summary-stats", "children"),
    [Input("simulation-results-store", "data")]
)
def update_summary_stats(results):
    if not results:
        return html.Div("Run a simulation to see results")
    
    # Format results for better display
    return html.Div([
        html.H4("Return Metrics"),
        html.Div([
            html.Div([
                html.P(f"Overall Rate of Return: {results['IRR']*100:.2f}%"),
                html.P(f"Senior IRR: {results['IRR_senior']*100:.2f}%"),
                html.P(f"Mezzanine IRR: {results['IRR_mezzanine']*100:.2f}%"),
                html.P(f"Remainder IRR: {results['IRR_remainder']*100:.2f}%"),
            ], style={'width': '50%', 'display': 'inline-block'}),
            
            html.Div([
                html.P(f"Total Debt: ${results['total_debt']:,.2f}"),
                html.P(f"Average Total Payment: ${results['average_total_payment']:,.2f}"),
                html.P(f"Average Duration: {results['average_duration']:.2f} years"),
                html.P(f"Return Spread (75th - 25th): {(results['IRR_quantile_75'] - results['IRR_quantile_25'])*100:.2f}%"),
            ], style={'width': '50%', 'display': 'inline-block'}),
        ]),
    ])

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
        name="Average Payment by Year"
    ))
    
    fig.update_layout(
        title="Average Payments by Year",
        xaxis_title="Year",
        yaxis_title="Payment Amount",
        template="plotly_white"
    )
    
    return fig

# Callback for tranche performance graph
@app.callback(
    Output("tranche-performance", "figure"),
    [Input("simulation-results-store", "data")]
)
def update_tranche_performance(results):
    if not results:
        return go.Figure()
    
    # Convert stored dict back to pandas DataFrames
    payments_df_senior = pd.DataFrame.from_dict(results['payments_df_senior'])
    payments_df_mezzanine = pd.DataFrame.from_dict(results['payments_df_mezzanine'])
    payments_df_remainder = pd.DataFrame.from_dict(results['payments_df_remainder'])
    
    # Calculate average payments by year for each tranche
    senior_by_year = payments_df_senior.mean(axis=1)
    mezzanine_by_year = payments_df_mezzanine.mean(axis=1)
    remainder_by_year = payments_df_remainder.mean(axis=1)
    
    # Create the tranche performance graph
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=senior_by_year.index,
        y=senior_by_year.values,
        name="Senior Tranche"
    ))
    
    fig.add_trace(go.Bar(
        x=mezzanine_by_year.index,
        y=mezzanine_by_year.values,
        name="Mezzanine Tranche"
    ))
    
    fig.add_trace(go.Bar(
        x=remainder_by_year.index,
        y=remainder_by_year.values,
        name="Remainder Tranche"
    ))
    
    fig.update_layout(
        title="Tranche Payments by Year",
        xaxis_title="Year",
        yaxis_title="Payment Amount",
        barmode='stack',
        template="plotly_white"
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
    
    # Add a single vertical line for each IRR value
    irr_values = [
        ('Overall', results['IRR']),
        ('Senior', results['IRR_senior']),
        ('Mezzanine', results['IRR_mezzanine']),
        ('Remainder', results['IRR_remainder'])
    ]
    
    # Add quantile range for overall IRR
    fig.add_shape(
        type="rect",
        x0=-0.5,
        x1=0.5,
        y0=results['IRR_quantile_25'],
        y1=results['IRR_quantile_75'],
        fillcolor="rgba(0, 0, 255, 0.2)",
        line=dict(width=0),
        layer="below"
    )
    
    # Add lines for each IRR value
    for i, (name, value) in enumerate(irr_values):
        fig.add_trace(go.Scatter(
            x=[i],
            y=[value],
            mode='markers',
            name=name,
            marker=dict(size=15)
        ))
        
        # Add horizontal line
        fig.add_shape(
            type="line",
            x0=i-0.4,
            x1=i+0.4,
            y0=value,
            y1=value,
            line=dict(color="red", width=3)
        )
    
    fig.update_layout(
        title="IRR by Tranche (with 25-75th Percentile Range for Overall)",
        xaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 2, 3],
            ticktext=['Overall', 'Senior', 'Mezzanine', 'Remainder']
        ),
        yaxis_title="IRR",
        yaxis_tickformat='.2%',
        template="plotly_white",
        showlegend=False
    )
    
    return fig

# Callback for detailed results
@app.callback(
    Output("detailed-results", "children"),
    [Input("simulation-results-store", "data")]
)
def update_detailed_results(results):
    if not results:
        return html.Div("Run a simulation to see detailed results")
    
    # Create a table of key statistics
    stats_table = pd.DataFrame({
        'Metric': [
            'Overall IRR', 
            'Senior IRR', 
            'Mezzanine IRR', 
            'Remainder IRR',
            'Average Duration',
            'Total Debt',
            'Average Total Payment',
            'Min IRR',
            'Max IRR',
            '25th Percentile IRR',
            '75th Percentile IRR'
        ],
        'Value': [
            f"{results['IRR']*100:.2f}%",
            f"{results['IRR_senior']*100:.2f}%",
            f"{results['IRR_mezzanine']*100:.2f}%",
            f"{results['IRR_remainder']*100:.2f}%",
            f"{results['average_duration']:.2f} years",
            f"${results['total_debt']:,.2f}",
            f"${results['average_total_payment']:,.2f}",
            f"{results['IRR_quantile_0']*100:.2f}%",
            f"{results['IRR_quantile_100']*100:.2f}%",
            f"{results['IRR_quantile_25']*100:.2f}%",
            f"{results['IRR_quantile_75']*100:.2f}%"
        ]
    })
    
    # Convert to Dash data table
    table = dash_table.DataTable(
        data=stats_table.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in stats_table.columns],
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
    
    return html.Div([
        html.H4("Detailed Statistics"),
        table
    ])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True) 