
# Import necessary modules
from data_loader import DataLoader
from simulation import Simulation
from analysis import Analysis

# Step 1: Load the Data
data_path = '/mnt/data/CI_Final-Catholic_University_Of_Rwanda-EPF_LPF Calculation.xlsx'
loader = DataLoader(data_path)
fund_simulation_data = loader.load_fund_simulation()

# Step 2: Set up initial parameters for the simulation
initial_params = {
    'initial_gdp_growth': 0.03,  # Example value
    'initial_inflation_rate': 0.02,  # Example value
    'initial_unemployment_rate': 0.05,  # Example value
    'initial_isa_cap': 20000,  # Example ISA cap
    'initial_isa_threshold': 15000,  # Example ISA threshold
    'num_years': 10,  # Duration of the simulation
    'senior_debt_threshold': 100000,  # Example senior debt threshold
    'mezzanine_debt_threshold': 50000  # Example mezzanine debt threshold
}

# Step 3: Run the simulation
simulation = Simulation(years=10, initial_params=initial_params)
simulation_results = simulation.run_simulation()

# Step 4: Analyze the results
analysis = Analysis(simulation_results)
summary = analysis.summarize_results()
irr = analysis.calculate_irr()
repayment_performance = analysis.calculate_repayment_performance()

# Output the results
print("Simulation Summary:")
print(summary)

print("\nCalculated IRR:")
print(irr)

print("\nRepayment Performance Metrics:")
print(repayment_performance)
