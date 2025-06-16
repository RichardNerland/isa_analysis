# ISA Analysis Tool - User Guide

This comprehensive guide will help you understand and effectively use the ISA Analysis Tool for modeling Income Share Agreement financial outcomes.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the Interface](#understanding-the-interface)
3. [Basic Workflow](#basic-workflow)
4. [Advanced Features](#advanced-features)
5. [Interpreting Results](#interpreting-results)
6. [Common Use Cases](#common-use-cases)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Getting Started

### What is the ISA Analysis Tool?

The ISA Analysis Tool is a web-based simulation platform that models Income Share Agreement (ISA) programs. It helps analyze:
- Student repayment patterns
- Investor returns (IRR)
- Risk profiles across different scenarios
- Economic sensitivity analysis

### First Time Setup

1. **Launch the Application**
   ```bash
   python simple_app.py
   ```

2. **Open Your Browser**
   Navigate to: `http://localhost:10000`

3. **Familiarize Yourself with the Interface**
   The tool has several main tabs:
   - **About**: Background information and methodology
   - **Simulation**: Main analysis interface

## Understanding the Interface

### Tab Overview

#### About Tab
- **Background**: Learn about ISA programs and Malengo's model
- **Methodology**: Understand the simulation approach
- **Model Parameters**: Review degree types and earnings assumptions
- **Data Sources**: See references for graduation rates and salary data

#### Simulation Tab
The main working area with two panels:

**Left Panel - Parameters**
- Preset Scenarios
- Degree Distribution Controls
- ISA Parameter Settings
- Economic Environment Controls
- Simulation Controls

**Right Panel - Results**
- Summary Statistics
- Multiple Analysis Tabs
- Visualization Charts
- Comparison Tools

### Parameter Controls Explained

#### Preset Scenarios
Pre-configured combinations representing realistic program distributions:

- **Uganda Programs**: University-focused with BA/MA degrees
  - *Baseline*: Balanced mix (45% BA, 24% MA, 27% Assistant Shift, 4% No Advancement)
  - *Conservative*: More dropouts (32% BA, 11% MA, 42% Assistant Shift, 15% No Advancement)
  - *Optimistic*: Higher success (63% BA, 33% MA, 2.5% Assistant Shift, 1.5% No Advancement)

- **Kenya Programs**: Nursing and healthcare focused
  - *Baseline*: Mixed success (40% Assistant, 20% Assistant Shift, 25% Nursing, 15% No Advancement)
  - *Conservative*: Higher dropouts (33% Assistant, 17% Assistant Shift, 20% Nursing, 30% No Advancement)
  - *Optimistic*: High nursing success (27% Assistant, 13% Assistant Shift, 60% Nursing, 0% No Advancement)

- **Rwanda Programs**: Trade and vocational training
  - *Baseline*: Balanced trade focus (27% Assistant, 13% Assistant Shift, 40% Trade, 20% No Advancement)
  - *Conservative*: Higher trade dropouts (27% Assistant, 13% Assistant Shift, 20% Trade, 40% No Advancement)
  - *Optimistic*: High trade success (23% Assistant, 12% Assistant Shift, 60% Trade, 5% No Advancement)

#### Degree Distribution Parameters

Each degree type has configurable parameters:

| Parameter | Description | Impact on Results |
|-----------|-------------|-------------------|
| **Percentage (%)** | Share of students in this track | Higher percentages increase weight in overall results |
| **Average Salary ($)** | Mean annual earnings | Higher salaries increase ISA payments and returns |
| **Standard Deviation ($)** | Earnings variability | Higher variance increases outcome uncertainty |
| **Growth Rate (%)** | Annual salary progression | Higher growth improves long-term payments |

**Degree Types:**
- **BA/MA**: University degrees with high earning potential
- **Assistant (ASST)**: Direct vocational training (3 years)
- **Assistant Shift (ASST_SHIFT)**: Students who switch to vocational training (6 years total)
- **Nursing**: Healthcare profession training
- **Trade**: Skilled trades and technical training
- **No Advancement (NA)**: Students who don't complete programs (return home)

#### ISA Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| **ISA Percentage (%)** | Share of income above threshold | Uganda: 14%, Kenya/Rwanda: 12% |
| **ISA Threshold ($)** | Minimum income before payments | $27,000 (standardized) |
| **ISA Cap ($)** | Maximum total repayment | Uganda: $72,500, Kenya: $49,950, Rwanda: $45,000 |
| **Price per Student ($)** | Investment cost per student | Uganda: $29,000, Kenya/Rwanda: $16,650 |

#### Economic Environment

| Parameter | Description | Impact |
|-----------|-------------|--------|
| **Leave Labor Force (%)** | Annual probability of returning home | Higher values reduce long-term payments |
| **Unemployment Rate (%)** | Initial unemployment rate | Higher unemployment delays payment start |
| **Inflation Rate (%)** | Annual price level increases | Affects real vs nominal returns |

## Basic Workflow

### Running Your First Simulation

1. **Select a Preset Scenario**
   - Choose a program type (Uganda, Kenya, or Rwanda)
   - Select a scenario (Baseline, Conservative, or Optimistic)
   - Parameters will auto-populate

2. **Review Default Settings**
   - Number of students: 100 (good for initial testing)
   - Number of simulations: 50 (balance between speed and accuracy)
   - Other parameters: Use defaults initially

3. **Run the Simulation**
   - Click "Run Simulation"
   - Wait for completion (10-30 seconds)

4. **Review Results**
   - Check the Summary Statistics
   - Explore different result tabs

### Understanding Your First Results

After running a simulation, you'll see several key metrics:

**Key Performance Indicators:**
- **Investor IRR**: Your actual return rate after fees
- **Total IRR**: Return before Malengo fees
- **Average Payment**: Mean total payment per student
- **Employment Rate**: Percentage of graduates working annually
- **Repayment Rate**: Percentage of students making payments

## Advanced Features

### Custom Scenario Building

1. **Start with a Preset**
   Choose the closest preset to your intended scenario

2. **Modify Degree Distribution**
   - Adjust percentages to sum to 100%
   - Consider realistic combinations (e.g., Kenya programs typically don't include BA/MA)

3. **Tune Economic Parameters**
   - Test sensitivity to unemployment and inflation
   - Adjust leave labor force probability for different program types

4. **Experiment with ISA Terms**
   - Try different percentage rates
   - Test various caps and thresholds
   - Adjust price per student for different investment scenarios

### Scenario Comparison

1. **Save Multiple Scenarios**
   - Run a simulation
   - Enter a descriptive name
   - Click "Save Current Scenario"

2. **Build Your Portfolio**
   - Create 3-5 different scenarios
   - Include optimistic, baseline, and conservative cases
   - Test different program types

3. **Compare Results**
   - Click "Compare Selected Scenarios"
   - Review side-by-side metrics
   - Analyze risk-return profiles

### Monte Carlo Analysis

For robust risk assessment:

1. **Access Blended Monte Carlo Tab**
   Navigate to the advanced Monte Carlo features

2. **Configure Scenario Weights**
   - Assign probabilities to different scenarios
   - Example: 50% Baseline, 30% Conservative, 20% Optimistic

3. **Set Parameter Ranges**
   - Leave Labor Force: Test 0-10% range
   - Wage Penalty: Test -40% to 0% range

4. **Run Large-Scale Analysis**
   - Use 500-1000 simulations for robust results
   - Review distribution statistics
   - Analyze worst-case scenarios

## Interpreting Results

### Key Metrics Explained

#### IRR (Internal Rate of Return)
- **Nominal Investor IRR**: Your actual return including inflation
- **Real Investor IRR**: Inflation-adjusted return
- **Total IRR**: Return before Malengo fees

**Interpretation Guidelines:**
- 5-8%: Conservative return
- 8-12%: Moderate return
- 12%+: Aggressive return
- <0%: Loss scenario

#### Payment Statistics
- **Average Total Payment**: Expected payment per student
- **Payment Distribution**: How payments vary across students
- **Payment by Year**: Timeline of payment patterns

#### Student Outcomes
- **Employment Rate**: Annual percentage working
- **Ever Employed Rate**: Percentage who ever find work
- **Repayment Rate**: Percentage making any payments

#### Cap Analysis
Students fall into three categories:
- **Hit Payment Cap**: Reach maximum payment amount
- **Hit Years Cap**: Reach 10-year payment limit
- **Hit No Cap**: Pay based on actual earnings

### Risk Assessment

#### Distribution Analysis
Review the IRR distribution to understand:
- **Mean vs Median**: If mean > median, there are high-return outliers
- **Standard Deviation**: Higher values indicate more risk
- **Percentiles**: 10th percentile shows worst-case scenarios

#### Sensitivity Testing
Use Monte Carlo analysis to test:
- Parameter uncertainty
- Economic environment changes
- Scenario probability shifts

## Common Use Cases

### 1. Program Comparison
**Goal**: Compare Uganda vs Kenya vs Rwanda programs

**Steps**:
1. Run baseline scenarios for each program type
2. Use identical student counts and simulation numbers
3. Compare Investor IRR and risk profiles
4. Consider total investment requirements

### 2. Investor Due Diligence
**Goal**: Assess investment risk and return

**Steps**:
1. Run conservative scenarios for worst-case analysis
2. Use Monte Carlo to test parameter sensitivity
3. Review 10th percentile outcomes
4. Analyze payment timeline and cash flow

### 3. Program Optimization
**Goal**: Find optimal ISA terms

**Steps**:
1. Test different ISA percentages (10-16%)
2. Vary payment caps ($40k-$80k)
3. Adjust price per student
4. Compare student affordability vs investor returns

### 4. Economic Sensitivity
**Goal**: Understand macro-economic impact

**Steps**:
1. Test high unemployment scenarios (8-12%)
2. Vary inflation rates (1-5%)
3. Adjust leave labor force probabilities
4. Analyze impact on long-term returns

## Troubleshooting

### Common Issues

#### Simulation Won't Start
**Problem**: Clicking "Run Simulation" shows no response
**Solutions**:
- Check that degree percentages sum to 100%
- Ensure all required fields have values
- Refresh the browser page

#### Unexpected Results
**Problem**: IRR seems too high/low
**Solutions**:
- Review parameter settings for typos
- Check that decimal inputs use periods (not commas)
- Verify degree distribution makes sense for program type

#### Performance Issues
**Problem**: Simulations run slowly
**Solutions**:
- Reduce number of students (try 50-100)
- Use fewer simulations (try 20-50)
- Close other browser tabs
- Restart the application

#### Browser Compatibility
**Problem**: Interface doesn't display correctly
**Solutions**:
- Use Chrome, Firefox, or Safari
- Enable JavaScript
- Clear browser cache
- Disable ad blockers

### Getting Help

If you encounter issues:
1. Check this troubleshooting section
2. Review the console for error messages
3. Restart the application
4. Check GitHub Issues for known problems

## Best Practices

### Simulation Design

1. **Start Simple**
   - Begin with preset scenarios
   - Use moderate simulation counts (50-100)
   - Understand basic results before customizing

2. **Build Gradually**
   - Make one parameter change at a time
   - Compare results to baseline
   - Document significant findings

3. **Validate Results**
   - Run simulations multiple times
   - Check results make intuitive sense
   - Compare with external benchmarks

### Parameter Selection

1. **Use Realistic Values**
   - Base salaries on market research
   - Use conservative growth rate assumptions
   - Consider historical unemployment data

2. **Test Sensitivity**
   - Vary key parameters by ±20%
   - Focus on high-impact variables
   - Document parameter sources

3. **Consider Correlations**
   - Economic downturns affect multiple parameters
   - Program quality impacts both completion and earnings
   - Student selection affects multiple outcomes

### Risk Management

1. **Stress Testing**
   - Always run conservative scenarios
   - Test extreme parameter values
   - Consider multi-factor stress scenarios

2. **Portfolio Approach**
   - Diversify across program types
   - Balance optimistic and conservative bets
   - Consider geographic diversification

3. **Regular Updates**
   - Update assumptions with new data
   - Re-run analysis annually
   - Adjust for changing economic conditions

### Documentation

1. **Record Assumptions**
   - Document parameter sources
   - Note any custom modifications
   - Save scenario configurations

2. **Track Changes**
   - Version control important analyses
   - Note reasons for parameter updates
   - Maintain audit trail for decisions

3. **Share Results**
   - Export key charts and tables
   - Summarize findings clearly
   - Include uncertainty ranges

---

## Next Steps

After mastering the basics:
1. Review the [API Reference](API_REFERENCE.md) for programmatic access
2. Check the [Deployment Guide](DEPLOYMENT.md) for production setup
3. Contribute to the project via [Contributing Guide](CONTRIBUTING.md)

For additional support, consult the project's GitHub repository or contact the development team. 