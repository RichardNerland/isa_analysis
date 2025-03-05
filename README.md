# ISA Analysis Tool

## Overview

This application simulates Income Share Agreement (ISA) outcomes for different educational programs. It models student earnings, payments, and returns to investors based on various economic and program-specific parameters.

## Key Features

- Simulate ISA outcomes for University and TVET (Technical and Vocational Education and Training) programs
- Multiple predefined scenarios (baseline and conservative)
- Customizable degree distributions and parameters
- Detailed economic modeling including inflation, unemployment, and experience-based earnings growth
- Analysis of investor returns and student payment patterns

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

3. **Vocational Training (VOC)**
   - Mean annual earnings: $31,500
   - Standard deviation: $4,800
   - Experience growth: 4% annually
   - Years to complete: 3

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

- **Vocational Earnings**: Based on median monthly wage of $2,640 (25th percentile: $2,383, 75th percentile: $2,924), annualized to $31,680 with a standard deviation of $4,800. No additional wage penalty was applied as these values already reflect entry-level positions.

### Predefined Scenarios

1. **University Baseline**
   - 100% Bachelor's Degree students

2. **TVET Baseline**
   - 45% Nursing students
   - 45% Vocational students
   - 10% No Advancement students

3. **TVET Conservative**
   - 25% Nursing students
   - 60% Vocational students
   - 15% No Advancement students

### Economic Parameters

- Default inflation rate: 2% annually
- Default unemployment rate: 4%
- ISA threshold: $27,000 (minimum income before payments begin)
- ISA cap: Varies by program ($72,500 for University, $49,950 for TVET)
- ISA percentage: Varies by program (14% for University, 12% for TVET)

### Foreign Student Modeling

The model accounts for students who return to their home countries after graduation through the `home_prob` parameter. When a student returns home, their earnings are significantly reduced, reflecting the typically lower wages in developing countries.

## How to Use the Model

```python
# Run a baseline TVET simulation
results_baseline = run_simple_simulation(
    program_type='TVET',
    num_students=100,
    num_sims=10,
    scenario='baseline'
)

# Run a conservative TVET simulation
results_conservative = run_simple_simulation(
    program_type='TVET',
    num_students=100,
    num_sims=10,
    scenario='conservative'
)

# Run a custom simulation
results_custom = run_simple_simulation(
    program_type='TVET',
    num_students=100,
    num_sims=10,
    scenario='custom',
    nurse_pct=30,
    voc_pct=50,
    na_pct=20
)
```

## Interpreting Results

The simulation returns a dictionary containing:
- Average total payments
- Average payment duration
- Employment statistics
- Repayment statistics
- Cap statistics (how many students hit payment caps)
- Degree distribution information

These results can be used to assess the financial viability of different ISA structures and to understand the risk profile of investments in different educational programs. 