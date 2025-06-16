# API Reference - ISA Analysis Tool

## Main Function

### run_simple_simulation()

Primary function for running ISA simulations.

```python
def run_simple_simulation(
    program_type: str,
    num_students: int,
    num_sims: int,
    scenario: str = 'baseline',
    price_per_student: Optional[float] = None,
    isa_percentage: Optional[float] = None,
    isa_threshold: float = 27000,
    isa_cap: Optional[float] = None,
    random_seed: Optional[int] = None,
    # ... additional parameters
) -> Dict[str, Any]
```

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `program_type` | `str` | Program type: "Uganda", "Kenya", or "Rwanda" |
| `num_students` | `int` | Number of students to simulate (1-1000) |
| `num_sims` | `int` | Number of Monte Carlo simulations (1-1000) |

#### Key Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scenario` | `str` | `'baseline'` | Scenario: "baseline", "conservative", "optimistic", "custom" |
| `price_per_student` | `Optional[float]` | `None` | Investment cost per student (auto-set by program) |
| `isa_percentage` | `Optional[float]` | `None` | ISA payment percentage (auto-set by program) |
| `isa_threshold` | `float` | `27000` | Minimum income threshold for payments |
| `isa_cap` | `Optional[float]` | `None` | Maximum total payment cap (auto-set by program) |
| `random_seed` | `Optional[int]` | `None` | Random seed for reproducibility |

#### Program Defaults

| Program | ISA % | Cap | Price/Student | Focus |
|---------|-------|-----|---------------|-------|
| Uganda | 14% | $72,500 | $29,000 | University (BA/MA) |
| Kenya | 12% | $49,950 | $16,650 | Nursing/Healthcare |
| Rwanda | 12% | $45,000 | $16,650 | Trade/Vocational |

#### Return Value

Returns a dictionary with simulation results:

**Key Metrics:**
- `nominal_investor_IRR`: Investor return rate after fees
- `average_nominal_total_payment`: Average payment per student
- `employment_rate`: Annual employment percentage
- `repayment_rate`: Percentage making payments
- `total_investment`: Total investment amount

**Data Series:**
- `payment_by_year`: Year-by-year payment data
- `active_students_by_year`: Active student counts
- `cap_stats`: Payment cap statistics

#### Example Usage

```python
from simple_isa_model import run_simple_simulation

# Basic simulation
results = run_simple_simulation(
    program_type="Uganda",
    num_students=100,
    num_sims=50,
    scenario="baseline"
)

print(f"Investor IRR: {results['nominal_investor_IRR']*100:.2f}%")
print(f"Average Payment: ${results['average_nominal_total_payment']:,.2f}")

# Custom scenario
results = run_simple_simulation(
    program_type="Kenya",
    num_students=200,
    num_sims=100,
    scenario="custom",
    nurse_pct=0.6,
    asst_pct=0.3,
    na_pct=0.1,
    price_per_student=20000,
    random_seed=42
)
```

## Additional Functions

### simulate_simple()
Lower-level simulation function (internal use)

## Classes

### Student
Represents individual student with earnings and payment history

### Degree  
Defines degree program parameters (salary, growth, completion time)

### Year
Manages economic environment (inflation, unemployment)

---

For detailed examples and tutorials, see [USER_GUIDE.md](USER_GUIDE.md). 