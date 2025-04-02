# ISA Analysis Project - Development Workflow

## Project Context

The Income Share Agreement (ISA) simulation model helps investors analyze returns and sensitivities of educational financing contracts. The primary goal is to provide transparency so investors can thoroughly test assumptions and understand expected returns from Malengo contracts.

## Development Phases and Tasks

### Phase 0: Building Development Environment

- [x] **Task 0.1:** Summarize the current tool in the project overview
  - Read all of the markdown from the repo and generate a condensed description of the project's classes and functions and how they interact in the project_overview.md

### Phase 1: Economic Model Enhancements

- [x] **Task 1.0:** Improve Student graduation delays
  - The graduation delay is now degree-specific with different distributions for different degree types
  - BA/ASST: 50% on time, 25% +1 year, 12.5% +2 years, 6.25% +3 years, 6.25% +4 years
  - MA/NURSE/TRADE: 75% on time, 20% +1 year, 2.5% +2 years, 2.5% +3 years

- [x] **Task 1.1:** Implement nominal IRR calculation
  - Added nominal value calculations throughout the model
  - Nominal values are now the default displayed in the UI
  - Both nominal and real values remain accessible in the backend model
  - Nominal values represent cash-on-cash returns without inflation adjustment
  - Real values represent inflation-adjusted returns showing economic value

- [ ] **Task 1.2:** Expand student journey tracking
  - Implement comprehensive annual income tracking
  - Add employment status tracking for each simulation year
  - Create flags for payment cap events
  - Build aggregation functions for these metrics

- [ ] **Task 1.3:** Enhance data extraction capabilities
  - Refactor simulation output structure for more granular data access
  - Create exportable data formats (CSV, JSON)
  - Implement filtering capabilities for specific subsets of results

- [ ] **Task 1.4:** Add visualization for investor transparency
  - Create distribution plots for key outcome metrics
  - Implement individual student journey visualization
  - Add toggles between aggregate views and individual paths

### Phase 2: Life Event Modeling

- [ ] **Task 2.1:** Implement parental leave simulation
  - Add configurable parameters for occurrence likelihood and duration
  - Model income impacts during and after leave periods
  - Track statistics on how leave affects overall repayment

- [ ] **Task 2.2:** Create life event visualization components
  - Develop timeline views showing major life events
  - Implement impact analysis views for repayment schedules
  - Add comparison capabilities (with/without events)


## Past Experiences

### Successful Approaches

1.  **UI-Model Consistency**
   - Ensuring that changes to the simulation model are reflected in the UI display
   - Example: After updating the graduation delay calculations in `simple_isa_model.py`, we also updated the UI components in `simple_app.py` to show the new distributions
   - Pattern: When changing core simulation behavior, always update both the calculation functions and their explanatory UI elements
   - This consistency avoids user confusion and ensures that what's displayed matches what's actually being calculated