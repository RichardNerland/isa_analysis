# Income Share Agreement (ISA) Simulation Model - Project Overview

## Introduction

This repository contains a sophisticated Python-based simulation model for Income Share Agreements (ISAs) used in educational financing. The model helps evaluate the financial performance and outcomes of ISA programs across different educational contexts, student populations, and economic conditions.

## Core Functionality

The model simulates:
- Student degree completion and graduation timing
- Post-graduation employment outcomes
- Income trajectories over time
- ISA payment calculations and caps
- Financial returns for investors and service providers

## Program Types

The simulation supports three main program types:
1. **University Programs (Uganda)** - Primarily bachelor's and master's degrees
2. **Nurse Programs (Kenya)** - Nursing and assistant tracks
3. **Trade Programs (Rwanda)** - Skilled trades and assistant tracks

## Key Components

### Degree Types
- **BA/MA**: Bachelor's and Master's degrees with higher starting salaries and growth rates
- **NURSE**: Nursing degree with moderate salary and growth
- **ASST/ASST_SHIFT**: Assistant tracks with lower starting salaries
- **TRADE**: Trade skills with moderate salary and growth
- **NA**: No advancement (students who don't complete their programs)

### Graduation Delay Modeling
The model uses degree-specific graduation delay distributions to realistically represent student completion patterns:

- **Bachelor's (BA) and Assistant (ASST) Programs**:
  - 50% graduate on time (no delay)
  - 25% graduate 1 year late
  - 12.5% graduate 2 years late
  - 6.25% graduate 3 years late
  - 6.25% graduate 4 years late

- **Master's (MA), Nursing (NURSE), and Trade (TRADE) Programs**:
  - 75% graduate on time (no delay)
  - 20% graduate 1 year late
  - 2.5% graduate 2 years late
  - 2.5% graduate 3 years late

This differentiated approach reflects the typically more structured nature of professional programs (MA/NURSE/TRADE) compared to traditional undergraduate degrees.

### Economic Modeling
- Dynamic inflation rates with realistic bounds
- Unemployment modeling
- Experience-based income growth
- Labor force participation dynamics
- International relocation modeling (students returning to home countries)

### Financial Modeling
- ISA payment calculations based on income thresholds
- Payment caps (amount-based and time-based)
- Investor and service provider fee structures
- IRR (Internal Rate of Return) calculations

## Simulation Parameters

The model supports extensive customization:
- Program type selection (Uganda, Kenya, Rwanda)
- Degree distribution configuration
- Economic parameter adjustment (inflation, unemployment)
- ISA structure parameters (percentage, threshold, cap)
- Student population size and simulation iterations
- Graduation delay modeling

## Predefined Scenarios

- **Baseline**: Standard expectations based on historical data
- **Conservative**: More pessimistic outcomes with higher dropout rates
- **Optimistic**: More favorable outcomes with higher completion rates
- **Custom**: User-defined degree distributions and parameters

## Analysis Capabilities

- Average payment calculations
- IRR computation for different stakeholders
- Employment and repayment rate analysis
- Graduation and degree completion statistics
- Payment cap analyses
- Monte Carlo simulations for risk assessment

## Technical Implementation

The codebase is structured around several key classes:
- `Year`: Manages economic conditions for each simulation year
- `Student`: Tracks individual student outcomes and payments
- `Degree`: Defines the characteristics of each degree type

Helper functions handle:
- Graduation delay calculation
- Employment status updates
- Fee calculations
- Degree distribution setup
- Statistical analysis and result aggregation

## User Interfaces

The model can be used through:
1. **Python API**: Direct function calls in Python scripts
2. **Command-line Interface**: Running simulations via terminal commands
3. **Web Application**: A Dash-based web app for interactive scenario testing (in `simple_app.py`)

## Future Development

Potential areas for enhancement include:
- Additional education sectors and program types
- More sophisticated economic models
- Enhanced visualization capabilities
- Integration with external data sources
- Expanded Monte Carlo simulation capabilities
- Sensitivity analysis tools
- Improved student life event modeling (e.g., parental leave, career changes)

## Financial Calculation Methodology

### Nominal vs Real Returns

The model calculates both nominal and real (inflation-adjusted) returns to provide a comprehensive view of investment performance:

- **Nominal Values**: Cash-on-cash returns without adjusting for inflation
  - Reflect the actual cash amounts that will be paid by students over time
  - Used as the default display in the UI for more intuitive interpretation
  - Typically higher than real returns in positive inflation environments
  - Calculated using the unadjusted payment amounts (`student.payments`)

- **Real Values**: Inflation-adjusted returns that show economic value
  - Account for the effects of inflation on the time value of money
  - Available in the backend model for economic analysis
  - Calculated using inflation-adjusted payment amounts (`student.real_payments`)
  - Provide a more economically accurate view of purchasing power

### Implementation Details

The codebase maintains parallel tracks for both nominal and real calculations:

1. **Data Collection**: The simulation captures both nominal payments (`student.payments`) and real payments (`student.real_payments`) for each student.

2. **Aggregation**: In `run_simple_simulation()`, both nominal and real payment data are collected and passed to the statistics calculation function.

3. **IRR Calculation**: The `_calculate_summary_statistics()` function calculates both nominal and real IRR using the same duration but different payment streams.

4. **Result Structure**: The results dictionary contains parallel sets of metrics with the following naming pattern:
   - Real metrics: `IRR`, `investor_IRR`, `average_total_payment`, etc.
   - Nominal metrics: `nominal_IRR`, `nominal_investor_IRR`, `average_nominal_total_payment`, etc.

This parallel structure allows for easy comparison between nominal and real returns while maintaining backward compatibility with earlier versions of the codebase.

## Code Structure and Implementation

### Core Simulation Classes

#### Year Class
```python
class Year:
    """Manages economic parameters for each simulation year."""
    def __init__(self, initial_inflation_rate, initial_unemployment_rate, 
                initial_isa_cap, initial_isa_threshold, num_years):
        # Initialize economic parameters
        
    def next_year(self, random_seed=None):
        # Update inflation, unemployment, and other economic conditions for the next year
```

#### Student Class
```python
class Student:
    """Tracks individual student outcomes and payments."""
    def __init__(self, degree, num_years):
        # Initialize student attributes and payment tracking arrays
```

#### Degree Class
```python
class Degree:
    """Defines characteristics of different degree types."""
    def __init__(self, name, mean_earnings, stdev, 
                experience_growth, years_to_complete, leave_labor_force_probability):
        # Set degree-specific parameters
```

### Key Helper Functions

#### Graduation Functions
```python
def _calculate_graduation_delay(base_years_to_complete):
    """Calculate realistic graduation delays based on degree type distribution."""
    # Implementation of probabilistic graduation delay

def _process_graduation(student, student_idx, student_graduated, student_is_na, gamma):
    """Process a student's graduation and set initial earnings power."""
    # Set graduation status and earnings based on degree
```

#### Employment Functions
```python
def _update_employment_status(student, year):
    """Update a student's employment status based on economic conditions."""
    # Determine if student is employed in current year
```

#### Payment Processing Functions
```python
def simulate_simple(students, year, num_years, isa_percentage, limit_years, 
                   performance_fee_pct=0.15, gamma=False, price_per_student=30000,
                   new_malengo_fee=False, apply_graduation_delay=False):
    """Run a single simulation for given students with specified parameters."""
    # Core simulation loop that processes payments and economic conditions
    
def _calculate_malengo_fees(students, student_idx, student_graduated, student_hit_cap,
                           student_is_na, price_per_student, year, current_year,
                           malengo_payments, malengo_real_payments):
    """Calculate service provider fees under the new fee structure."""
    # Implement fee calculations for service provider
```

### Main Simulation Functions

```python
def run_simple_simulation(program_type, num_students, num_sims, scenario='baseline', 
                         salary_adjustment_pct=0, salary_std_adjustment_pct=0,
                         initial_unemployment_rate=0.08, initial_inflation_rate=0.02,
                         performance_fee_pct=0.15, leave_labor_force_probability=0.05,
                         # Many other parameters with defaults
                         ):
    """Run multiple simulations with comprehensive parameter customization."""
    # Primary entrypoint for running ISA simulations
    
def _setup_degree_distribution(scenario, program_type, base_degrees, leave_labor_force_probability,
                              ba_pct, ma_pct, asst_pct, nurse_pct, na_pct, trade_pct, asst_shift_pct=0):
    """Configure degree distribution based on scenario and program type."""
    # Set up degrees and probabilities for simulation
    
def _create_students(num_students, degrees, probs, num_years):
    """Create student objects with assigned degrees."""
    # Generate and configure student population
```

### Statistics and Analysis Functions

```python
def _calculate_simulation_statistics(students, num_students, num_years, limit_years):
    """Calculate statistics for a single simulation run."""
    # Track employment rates, repayment rates, and cap statistics
    
def _calculate_summary_statistics(total_payment, investor_payment, malengo_payment,
                                 total_investment, degrees, probs, num_students,
                                 employment_stats, ever_employed_stats, repayment_stats, cap_stats):
    """Aggregate statistics across multiple simulation runs."""
    # Calculate IRR, average payments, and distribution metrics
```

### Web Application (simple_app.py)

The web application is built using Dash and provides an interactive interface for running simulations:

```python
# Main app components
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Layout defines the UI structure with tabs for:
# - About (background information)
# - Simulation (parameter configuration)
# - Results (visualization of simulation outputs)
# - Saved Scenarios (comparison of different configurations)
# - Monte Carlo (sensitivity analysis)

# Key callbacks include:
@app.callback(...) # Run simulation with specified parameters
def run_simulation(...):
    # Execute simulation and return results

@app.callback(...) # Update visualizations based on simulation results
def update_payment_distribution(results):
    # Generate visualization of payment distributions

@app.callback(...) # Run Monte Carlo analysis
def run_monte_carlo_simulation(...):
    # Execute multiple simulations with parameter variations
```

The web app features extensive visualization capabilities including:
- Payment distribution charts
- IRR distribution plots
- Student outcome statistics
- Degree completion graphs
- Scenario comparison tools
- Sensitivity analysis through Monte Carlo simulation

## Command-line Interface

The application can be run directly from the terminal:

```python
def main():
    """Command-line entrypoint for the ISA model."""
    # Parse arguments and run simulation with specified parameters
    # Display results or generate plots
```

The CLI supports all core parameters and can generate plots to visualize simulation results. 