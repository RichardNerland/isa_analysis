# Income Share Agreement (ISA) Simulation Model

This repository contains a Python model for simulating Income Share Agreements (ISAs) for educational programs. The model allows for the simulation of different scenarios, degree types, and economic conditions to evaluate the financial performance of ISA programs.

## Overview

The ISA model simulates student outcomes after graduation, including:
- Employment status
- Earnings progression
- ISA payments
- Return on investment for investors and service providers

The model supports three main program types:
- University programs (primarily BA degrees)
- Nurse programs (nursing and assistant tracks)
- Trade programs (Skilled trades and assistant tracks)

## Key Features

- Multiple predefined scenarios (baseline, conservative)
- Custom degree distributions
- Configurable economic parameters (inflation, unemployment)
- Detailed payment tracking and statistics
- Calculation of IRR (Internal Rate of Return)
- Tracking of different payment caps and thresholds

## Recent Improvements

The codebase has been significantly improved with:

1. **Type Hints**: Added comprehensive type annotations for better code documentation and IDE support
2. **Code Organization**: Refactored large functions into smaller, more focused helper functions
3. **Improved Documentation**: Enhanced docstrings and comments
4. **Economic Model Enhancements**: Added bounds to inflation and unemployment rates
5. **Error Handling**: Better handling of edge cases and potential errors
6. **Reproducibility**: Added random seed support for reproducible simulations
7. **Command-line Interface**: Added a CLI for easy execution of simulations
8. **Visualization**: Added plotting capabilities for simulation results

## Usage

### Basic Usage

```python
from simple_isa_model import run_simple_simulation

# Run a baseline Nurse scenario
results = run_simple_simulation(
    program_type='Nurse',
    num_students=100,
    num_sims=10,
    scenario='baseline'
)

# Access key results
print(f"IRR: {results['IRR']*100:.2f}%")
print(f"Average Total Payment: ${results['average_total_payment']:.2f}")
```

### Command-line Interface

The model can also be run directly from the command line:

```bash
# Run a baseline Nurse scenario
python simple_isa_model.py --program Kenya --scenario baseline --students 100 --sims 10

# Run a custom University scenario with plots
python simple_isa_model.py --program Uganda --scenario baseline --students 200 --sims 20 --plot

# Run with a fixed random seed for reproducibility
python simple_isa_model.py --program Kenya --scenario conservative --seed 42
```

## Customization

The model supports extensive customization:

```python
# Custom degree distribution
results = run_simple_simulation(
    program_type='Nurse',
    num_students=100,
    num_sims=10,
    scenario='custom',
    nurse_pct=30,
    asst_pct=50,
    na_pct=20,
    # Custom economic parameters
    initial_inflation_rate=0.03,
    initial_unemployment_rate=0.10,
    # Custom ISA parameters
    isa_percentage=0.15,
    isa_threshold=30000,
    isa_cap=60000
)
```

## Requirements

- Python 3.6+
- NumPy
- Pandas
- Matplotlib (for plotting)

## Model Assumptions

### Degree Types and Earnings

The model includes several degree types with different earnings profiles:

1. **Bachelor's Degree (BA)**
   - Mean annual earnings: $41,300
   - Standard deviation: $13,000
   - Experience growth: 4% annually
   - Years to complete: 4

2. **Master's Degree (MA)**
   - Mean annual earnings: $46,709
   - Standard deviation: $15,000
   - Experience growth: 4% annually
   - Years to complete: 6

3. **Assistant Training (ASST)**
   - Mean annual earnings: $31,500
   - Standard deviation: $4,800
   - Experience growth: 1% annually
   - Years to complete: 3 (6 years in University program)
   - Note: The longer completion time for University programs reflects students who drop out of bachelor's programs and switch between programs before completing assistant training

4. **Nursing Degree (NURSE)**
   - Mean annual earnings: $44,000
   - Standard deviation: $8,400
   - Experience growth: 1% annually
   - Years to complete: 4

5. **No Advancement (NA)**
   - Mean annual earnings: $2,200
   - Standard deviation: $640
   - Experience growth: 1% annually
   - Years to complete: 4
   - High probability (80%) of returning to home country

### Earnings Methodology

The earnings values were derived from average salary levels found in public data sources, with a 15% wage penalty applied to account for the fact that students are typically at the beginning of their careers and earn less than the average worker in their field.

- **Nursing Earnings**: Based on median monthly wage of $4,056 (25th percentile: $3,608, 75th percentile: $4,552), annualized to $48,672 with a standard deviation of $8,400. A 15% student wage penalty was applied, resulting in $44,000 mean earnings.

- **Assistant Earnings**: Based on median monthly wage of $2,640 (25th percentile: $2,383, 75th percentile: $2,924), annualized to $31,680 with a standard deviation of $4,800. No additional wage penalty was applied as these values already reflect entry-level positions.

### Predefined Scenarios

1. **University Baseline**
   - 100% Bachelor's Degree students

2. **Nurse Baseline**
   - 45% Nursing students
   - 45% Assistant students
   - 10% No Advancement students

3. **Nurse Conservative**
   - 25% Nursing students
   - 60% Assistant students
   - 15% No Advancement students

### Economic Parameters

- Default inflation rate: 2% annually
- Default unemployment rate: 4%
- ISA threshold: $27,000 (minimum income before payments begin)
- ISA cap: Varies by program ($72,500 for University, $49,950 for Nurse)
- ISA percentage: Varies by program (14% for University, 12% for Nurse)

### Foreign Student Modeling

The model accounts for students who return to their home countries after graduation through the `home_prob` parameter. When a student returns home, their earnings are significantly reduced, reflecting the typically lower wages in developing countries. 