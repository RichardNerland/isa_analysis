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

- [ ] **Task 2.2:** Enhance degree switching and delay logic
  - Improve existing graduation delay system with more realistic timing
  - Add explicit degree switching mechanics between programs
  - Model financial impacts of educational path changes

- [ ] **Task 2.3:** Create life event visualization components
  - Develop timeline views showing major life events
  - Implement impact analysis views for repayment schedules
  - Add comparison capabilities (with/without events)

### Phase 3: Web Application Improvements

- [ ] **Task 3.1:** Enhance user interface for investors
  - Redesign layout for improved information hierarchy
  - Add guided tutorials for first-time users
  - Implement preset configurations with explanatory details

- [ ] **Task 3.2:** Create program type creation interface
  - Build UI for configuring new program types
  - Implement validation for program parameters
  - Add save/load functionality for custom programs

- [ ] **Task 3.3:** Implement comprehensive documentation
  - Add contextual tooltips throughout the interface
  - Create help sections explaining model assumptions
  - Develop guidance for interpreting results

### Phase 4: Testing and Validation

- [ ] **Task 4.1:** Implement basic automated tests
  - Add unit tests for core calculation functions
  - Create integration tests for simulation pipeline
  - Implement UI tests for critical web application features

- [ ] **Task 4.2:** Add sensitivity analysis capabilities
  - Create tornado charts for parameter sensitivity
  - Implement scenario comparison tools
  - Enhance Monte Carlo simulation visualizations

## Past Experiences

### Successful Approaches

1. **Modular Function Design**
   - Breaking down complex simulation logic into smaller helper functions has proven effective
   - Example: Separating `_calculate_graduation_delay()`, `_process_graduation()`, and `_update_employment_status()` led to more maintainable code
   - Future tasks should continue this pattern of modular design

2. **Type Annotations**
   - Adding comprehensive type hints has improved code clarity and IDE support
   - This has reduced bugs related to parameter misunderstanding
   - All new functions should include proper type annotations

3. **Parameter Defaulting**
   - Providing sensible defaults while allowing overrides has made the API flexible
   - Example: The degree parameters in `run_simple_simulation()` have appropriate defaults but can be customized
   - Continue this pattern for new parameters

4. **Economic Model Bounds**
   - Adding realistic bounds to economic parameters (inflation, unemployment) has created more plausible simulations
   - Example: `self.inflation_rate = max(-0.02, min(0.15, self.inflation_rate))`
   - Similar constraints should be applied to new economic variables

5. **Degree-specific Graduation Delays**
   - Implementing different graduation delay distributions for different degree types
   - This creates more realistic outcomes by recognizing that MA/NURSE/TRADE programs have different completion patterns
   - Approach: Adding degree type as a parameter to delay functions and using it to select appropriate distributions
   - Implementation pattern: Maintaining parallel model and UI logic for consistency in simulation and visualization
   - Impact: More accurate representation of program-specific graduation timelines leads to better financial projections

6. **UI-Model Consistency**
   - Ensuring that changes to the simulation model are reflected in the UI display
   - Example: After updating the graduation delay calculations in `simple_isa_model.py`, we also updated the UI components in `simple_app.py` to show the new distributions
   - Pattern: When changing core simulation behavior, always update both the calculation functions and their explanatory UI elements
   - This consistency avoids user confusion and ensures that what's displayed matches what's actually being calculated

### Challenges and Failures

1. **Over-complex Parameter Structure**
   - The large number of parameters in `run_simple_simulation()` has become unwieldy
   - Future: Consider using parameter objects or configuration dictionaries for cleaner interfaces

2. **Lack of Intermediate Data Access**
   - Currently difficult to extract specific metrics during simulation
   - Need to restructure data collection to allow more granular access to simulation states

3. **Limited Visualization Capabilities**
   - Current plots are basic and don't allow interactive exploration
   - Need to implement more sophisticated visualization with drill-down capabilities

4. **Scenario Management**
   - Managing and comparing multiple scenarios is cumbersome
   - Need a better system for scenario storage and comparison

5. **Hard-coded Distribution Values**
   - Using hard-coded probability values in both the model and UI can lead to inconsistencies
   - Future improvement: Define graduation delay distributions as constants in a shared configuration file

## Technical Implementation Guidelines for LLM Agent

1. **Code Organization**
   - Place new functions in appropriate sections of existing files
   - For major features, consider creating new modules
   - Maintain consistent naming conventions with existing code

2. **Error Handling**
   - Implement robust validation for all user inputs
   - Add informative error messages for invalid parameters
   - Consider graceful degradation for edge cases

3. **Performance Considerations**
   - Use vectorized operations (NumPy) where possible
   - For web app features, consider lazy loading for large datasets
   - Limit redundant calculations in visualization code

4. **Documentation Standards**
   - Add docstrings to all new functions explaining parameters and return values
   - Update README.md when adding significant features
   - Include example usage in docstrings

5. **Testing Approach**
   - Write unit tests for core calculation functions
   - For UI components, focus on critical user paths
   - Include edge case tests for economic parameter bounds 