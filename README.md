# ISA Analysis Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/Dash-2.14.2-blue.svg)](https://dash.plotly.com/)

A comprehensive web-based simulation tool for analyzing Income Share Agreement (ISA) financial outcomes across different educational programs and economic scenarios.

## 🎯 Overview

The ISA Analysis Tool helps stakeholders understand the financial outcomes of Income Share Agreement programs by modeling student earnings, repayment patterns, and investor returns across various educational pathways. Built for organizations like [Malengo](https://www.malengo.org), this tool provides data-driven insights for educational financing decisions.

### Key Features

- **🌍 Multi-Program Support**: Models Uganda (university), Kenya (nursing), and Rwanda (trade) programs
- **📊 Interactive Dashboard**: Web-based interface with real-time scenario modeling
- **🎲 Monte Carlo Simulations**: Robust statistical analysis with configurable parameters
- **📈 Financial Modeling**: Calculate IRR, payment distributions, and risk metrics
- **🔧 Flexible Configuration**: Custom degree distributions, economic parameters, and ISA terms
- **💾 Scenario Comparison**: Save and compare multiple scenarios side-by-side
- **📱 Production Ready**: Docker support, logging, and deployment configurations

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd isa-analysis-tool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python simple_app.py
   ```

4. **Access the web interface**
   
   Open your browser to: `http://localhost:10000`

## 📚 Documentation

- **[User Guide](USER_GUIDE.md)** - Comprehensive usage instructions and tutorials
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[API Reference](API_REFERENCE.md)** - Detailed function and parameter documentation
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project

## 🏗️ Architecture

The tool consists of two main components:

1. **Simulation Engine** (`simple_isa_model.py`) - Core Monte Carlo simulation logic
2. **Web Interface** (`simple_app.py`) - Interactive Dash-based dashboard

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ISA Analysis Tool                            │
├─────────────────────────────────────────────────────────────────┤
│                  Web Interface (Dash)                          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────┐ │
│  │   About     │ Simulation  │ Comparison  │ Monte Carlo     │ │
│  │    Tab      │     Tab     │     Tab     │      Tab        │ │
│  └─────────────┴─────────────┴─────────────┴─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                 Simulation Engine                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Monte Carlo Simulation Framework                       │   │
│  │  • Student Generation                                   │   │
│  │  • Economic Modeling                                    │   │
│  │  • Payment Processing                                   │   │
│  │  • Statistical Analysis                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                    Data Models                                  │
│  ┌───────────┬─────────────┬─────────────┬─────────────────┐   │
│  │ Students  │   Degrees   │  Economics  │   ISA Terms     │   │
│  │  Class    │   Class     │   Class     │   Parameters    │   │
│  └───────────┴─────────────┴─────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🎮 Usage Examples

### Basic Simulation

```python
from simple_isa_model import run_simple_simulation

# Run Uganda baseline scenario
results = run_simple_simulation(
    program_type='Uganda',
    num_students=100,
    num_sims=50,
    scenario='baseline'
)

print(f"Investor IRR: {results['nominal_investor_IRR']*100:.2f}%")
print(f"Average Payment: ${results['average_nominal_total_payment']:,.2f}")
```

### Custom Parameters

```python
# Custom scenario with specific parameters
results = run_simple_simulation(
    program_type='Kenya',
    num_students=200,
    num_sims=100,
    scenario='custom',
    # Custom degree distribution
    nurse_pct=0.6,
    asst_pct=0.3,
    na_pct=0.1,
    # Custom ISA terms
    isa_percentage=0.15,
    price_per_student=20000,
    # Custom economic parameters
    initial_unemployment_rate=0.08,
    leave_labor_force_probability=0.05
)
```

### Command Line Interface

```bash
# Run simulation with command line
python simple_isa_model.py \
  --program Uganda \
  --scenario baseline \
  --students 100 \
  --sims 50 \
  --graduation-delay
```

## 🌐 Web Interface Features

### Simulation Tab
- **Preset Scenarios**: Pre-configured Uganda, Kenya, and Rwanda scenarios
- **Custom Parameters**: Adjust degree distributions, salaries, and growth rates
- **ISA Configuration**: Set percentage, threshold, cap, and price per student
- **Economic Controls**: Unemployment, inflation, and labor force parameters

### Analysis Tabs
- **Payment Distribution**: Visualize payment patterns over time
- **IRR Comparison**: Compare real vs nominal returns
- **Student Outcomes**: Track employment and repayment rates
- **Scenario Comparison**: Save and compare multiple scenarios

### Monte Carlo Features
- **Blended Scenarios**: Weight multiple scenarios with uncertainty ranges
- **Parameter Sensitivity**: Test robustness across parameter variations
- **Statistical Analysis**: Comprehensive distribution analysis and risk metrics

## 🔧 Configuration

### Environment Variables

```bash
# Application settings
DASH_HOST=0.0.0.0
DASH_PORT=10000
DASH_DEBUG=False

# Simulation defaults
DEFAULT_STUDENTS=100
DEFAULT_SIMULATIONS=50
```

### ISA Program Defaults

| Program | ISA % | Threshold | Cap | Price/Student |
|---------|-------|-----------|-----|---------------|
| Uganda  | 14%   | $27,000   | $72,500 | $29,000 |
| Kenya   | 12%   | $27,000   | $49,950 | $16,650 |
| Rwanda  | 12%   | $27,000   | $45,000 | $16,650 |

## 🚀 Deployment

### Production Deployment

See the [Deployment Guide](DEPLOYMENT.md) for detailed instructions on:
- Docker containerization
- Cloud platform deployment (AWS, GCP, Azure)
- Load balancing and scaling
- Security configurations
- Monitoring and logging

### Quick Deploy with Docker

```bash
# Build and run container
docker build -t isa-analysis-tool .
docker run -p 10000:10000 isa-analysis-tool
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Code standards and style guide
- Development setup
- Testing procedures
- Pull request process

## 📊 Model Assumptions

### Economic Parameters
- **Default Inflation**: 2% annually
- **Default Unemployment**: 4-8% range
- **Experience Growth**: Varies by degree type (0.5%-4% annually)
- **Immigrant Wage Penalty**: ~20% reduction from baseline earnings

### Degree Types

| Degree | Mean Salary | Growth Rate | Completion Time |
|--------|-------------|-------------|-----------------|
| Bachelor's (BA) | $41,300 | 3% | 4 years |
| Master's (MA) | $46,709 | 4% | 6 years |
| Assistant (ASST) | $31,500 | 0.5% | 3 years |
| Nursing | $40,000 | 2% | 4 years |
| Trade | $35,000 | 2% | 3 years |
| No Advancement | $2,200 | 1% | 4 years |

*All salaries include immigrant wage penalty and represent entry-level positions*

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check our [User Guide](USER_GUIDE.md) and [API Reference](API_REFERENCE.md)
- **Issues**: Report bugs via [GitHub Issues](https://github.com/your-org/isa-analysis-tool/issues)
- **Discussions**: Join our [GitHub Discussions](https://github.com/your-org/isa-analysis-tool/discussions)
- **Enterprise Support**: Contact us for dedicated support options

## 🏆 Acknowledgments

- Built for educational financing analysis and [Malengo](https://www.malengo.org) program optimization
- Inspired by research on migration economics and educational access
- Uses data from German education and labor market sources

---

**Made with ❤️ for educational equity and evidence-based policy making** 