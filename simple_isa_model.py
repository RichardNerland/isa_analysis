import numpy as np
import pandas as pd

class Year:
    """
    Simplified class for tracking economic parameters for each simulation year.
    """
    def __init__(self, initial_inflation_rate, initial_unemployment_rate, 
                 initial_isa_cap, initial_isa_threshold, num_years):
        self.year_count = 1
        self.inflation_rate = initial_inflation_rate
        self.stable_inflation_rate = initial_inflation_rate
        self.unemployment_rate = initial_unemployment_rate
        self.stable_unemployment_rate = initial_unemployment_rate
        self.isa_cap = initial_isa_cap
        self.isa_threshold = initial_isa_threshold
        self.deflator = 1

    def next_year(self):
        """Advance to the next year and update economic conditions"""
        self.year_count = self.year_count + 1
        self.inflation_rate = self.stable_inflation_rate * .45 + self.inflation_rate * .5 + np.random.normal(0, .01)
        self.unemployment_rate = self.stable_unemployment_rate * .33 + self.unemployment_rate * .25 + np.random.lognormal(0, 1) / 100
        self.isa_cap = self.isa_cap * (1 + self.inflation_rate)
        self.isa_threshold = self.isa_threshold * (1 + self.inflation_rate)
        self.deflator = self.deflator * (1 + self.inflation_rate)


class Student:
    """
    Simplified class for tracking student payments without debt seniority.
    """
    def __init__(self, degree, num_years):
        self.degree = degree
        self.num_years = num_years
        self.earnings_power = 0
        self.earnings = [0] * num_years
        self.payments = [0] * num_years
        self.real_payments = [0] * num_years
        self.is_graduated = False
        self.is_employed = False
        self.is_home = False
        self.years_paid = 0
        self.hit_cap = False
        self.years_experience = 0


class Degree:
    """
    Class representing different degree options with associated parameters.
    """
    def __init__(self, name, mean_earnings, stdev, experience_growth, years_to_complete, home_prob):
        self.name = name
        self.mean_earnings = mean_earnings
        self.stdev = stdev
        self.experience_growth = experience_growth
        self.years_to_complete = years_to_complete
        self.home_prob = home_prob


def simulate_simple(students, year, num_years, isa_percentage, limit_years, performance_fee_pct=0.15, gamma=False, price_per_student=30000, new_malengo_fee=False):
    """
    Run a single simulation for the given students over the specified number of years
    with a simple repayment structure.
    
    Parameters:
    - students: List of Student objects
    - year: Year object representing economic conditions
    - num_years: Total number of years to simulate
    - isa_percentage: Percentage of income to pay in ISA
    - limit_years: Maximum number of years to pay the ISA
    - performance_fee_pct: Percentage of payments that goes to Malengo (if using old structure)
    - gamma: Whether to use gamma distribution instead of normal for earnings
    - price_per_student: Cost per student (for new Malengo fee structure)
    - new_malengo_fee: Whether to use the new Malengo fee structure (1% of inflation-adjusted investment)
    
    Returns:
    - Dictionary of simulation results
    """
    total_payments = [0] * num_years
    total_real_payments = [0] * num_years
    malengo_payments = [0] * num_years
    malengo_real_payments = [0] * num_years
    investor_payments = [0] * num_years
    investor_real_payments = [0] * num_years
    
    # Track if students are graduated (for Malengo fee calculation)
    student_graduated = [False] * len(students)
    student_hit_cap = [False] * len(students)  # Track which students have hit the cap
    student_is_na = [False] * len(students)   # Track which students have NA degree
    
    for i in range(num_years):
        for student_idx, student in enumerate(students):
            if i < student.degree.years_to_complete:
                continue
            if i == student.degree.years_to_complete:
                student.is_graduated = True
                student_graduated[student_idx] = True  # Mark as graduated for Malengo fee
                student_is_na[student_idx] = (student.degree.name == 'NA')  # Mark if student has NA degree
                
                student.is_home = np.random.binomial(1, student.degree.home_prob) == 1
                if gamma:
                    student.earnings_power = max(0, np.random.gamma(student.degree.mean_earnings, student.degree.stdev))
                else:
                    student.earnings_power = max(0, np.random.normal(student.degree.mean_earnings, student.degree.stdev))
                if student.is_home:
                    if gamma:
                        student.earnings_power = max(0, np.random.gamma(67600/4761, 4761/26))
                    else:
                        student.earnings_power = max(0, np.random.normal(2600, 690))
            if year.unemployment_rate < 1:
                student.is_employed = np.random.binomial(1, 1 - year.unemployment_rate) == 1
            else:
                student.is_employed = False
            if student.is_employed:
                student.earnings[i] = student.earnings_power * year.deflator * (1 + student.degree.experience_growth) ** student.years_experience
                student.years_experience = student.years_experience + 1
                
                # Check if earnings exceed threshold
                if student.earnings[i] > year.isa_threshold:
                    student.years_paid = 1 + student.years_paid

                    if student.years_paid > limit_years:
                        student_hit_cap[student_idx] = True  # Stop Malengo fees when years cap is hit
                        continue
                    if student.hit_cap:
                        continue
                        
                    # Calculate payment as percentage of TOTAL income, not just excess
                    # The threshold is just a gate condition, not part of the calculation
                    potential_payment = isa_percentage * student.earnings[i]
                    
                    if (np.sum(student.payments) + potential_payment) > year.isa_cap:
                        student.payments[i] = year.isa_cap - np.sum(student.payments)
                        student.real_payments[i] = (year.isa_cap - np.sum(student.payments)) / year.deflator
                        student.hit_cap = True
                        student_hit_cap[student_idx] = True  # Update the cap tracking array
                    else:
                        student.payments[i] = potential_payment
                        student.real_payments[i] = potential_payment / year.deflator
                    
                    # Add to total payments
                    total_payments[i] += student.payments[i]
                    total_real_payments[i] += student.real_payments[i]
                    
            else:
                student.years_experience = max(0, student.years_experience-3)
                # If student is unemployed for a year after graduation, stop Malengo fees
                if student_graduated[student_idx] and not student_is_na[student_idx]:
                    student_hit_cap[student_idx] = True
        
        # Calculate Malengo's fee for the new structure
        if new_malengo_fee:
            for student_idx, student in enumerate(students):
                # Malengo gets 1% of inflation-adjusted initial investment only if:
                # 1. Student has graduated
                # 2. Student has not hit any cap (payment cap, years cap, or stopped payments)
                # 3. Student does not have an NA degree
                if (student_graduated[student_idx] and 
                    not student_hit_cap[student_idx] and
                    not student_is_na[student_idx] and
                    student.is_employed):  # Only charge fee if student is currently employed
                    annual_fee = price_per_student * 0.01 * year.deflator
                    malengo_payments[i] += annual_fee
                    malengo_real_payments[i] += annual_fee / year.deflator
            
            # Now calculate investor payments by subtracting Malengo fees
            investor_payments[i] = total_payments[i] - malengo_payments[i]
            investor_real_payments[i] = total_real_payments[i] - malengo_real_payments[i]

        year.next_year()

    data = {
        'Student': students,
        'Degree': [student.degree for student in students],
        'Earnings': [student.earnings for student in students],
        'Payments': [student.payments for student in students],
        'Real_Payments': [student.real_payments for student in students],
        'Total_Payments': total_payments,
        'Total_Real_Payments': total_real_payments,
        'Malengo_Payments': malengo_payments,
        'Malengo_Real_Payments': malengo_real_payments,
        'Investor_Payments': investor_payments,
        'Investor_Real_Payments': investor_real_payments
    }

    return data


def run_simple_simulation(
    program_type,
    num_students,
    num_sims,
    scenario='baseline',  # New parameter to select predefined scenarios
    salary_adjustment_pct=0,
    salary_std_adjustment_pct=0,
    initial_unemployment_rate=0.04,
    initial_inflation_rate=0.02,
    performance_fee_pct=0.15,
    home_prob=0.0,
    ba_pct=0,
    ma_pct=0, 
    voc_pct=0,
    nurse_pct=0,
    na_pct=0,
    # New parameters for fully customizable degrees
    ba_salary=41300,
    ba_std=13000,
    ba_growth=0.04,
    ma_salary=46709,
    ma_std=15000,
    ma_growth=0.04,
    voc_salary=31500,
    voc_std=4800,
    voc_growth=0.04,
    nurse_salary=44000,
    nurse_std=8400,
    nurse_growth=0.01,
    na_salary=2200,
    na_std=640,
    na_growth=0.01,
    # Custom ISA parameters
    isa_percentage=None,  # Will be set based on program_type if None
    isa_threshold=27000,
    isa_cap=None,        # Will be set based on program_type if None
    new_malengo_fee=True  # Default to new fee structure
):
    """
    Run multiple simulations for either University or TVET program with simplified parameters.
    
    Parameters:
    - program_type: 'University' or 'TVET'
    - num_students: Number of students to simulate
    - num_sims: Number of simulations to run
    - scenario: Predefined scenario to use ('baseline', 'conservative', or 'custom')
    - salary_adjustment_pct: Percentage adjustment to average salaries (legacy parameter)
    - salary_std_adjustment_pct: Percentage adjustment to salary standard deviations (legacy parameter)
    - initial_unemployment_rate: Starting unemployment rate
    - initial_inflation_rate: Starting inflation rate
    - performance_fee_pct: Percentage of payments that goes to Malengo (old fee structure)
    - home_prob: Probability of a student returning home after graduation
    - ba_pct, ma_pct, voc_pct, nurse_pct, na_pct: Custom degree distribution (if scenario='custom')
    - ba_salary, ba_std, ba_growth: Custom parameters for BA degree
    - ma_salary, ma_std, ma_growth: Custom parameters for MA degree
    - voc_salary, voc_std, voc_growth: Custom parameters for VOC degree
    - nurse_salary, nurse_std, nurse_growth: Custom parameters for Nurse degree
    - na_salary, na_std, na_growth: Custom parameters for NA degree
    - isa_percentage: Custom ISA percentage (defaults based on program type)
    - isa_threshold: Custom ISA threshold
    - isa_cap: Custom ISA cap (defaults based on program type)
    - new_malengo_fee: Whether to use the new Malengo fee structure
    
    Returns:
    - Dictionary of aggregated results from multiple simulations
    
    Predefined Scenarios:
    - University baseline: 100% BA
    - TVET baseline: 45% nurse, 45% vocational, 10% NA
    - TVET conservative: 25% nurse, 60% vocational, 15% NA
    
    Examples:
    # TVET Baseline scenario (45% nurse, 45% vocational, 10% NA)
    results_baseline = run_simple_simulation(
        program_type='TVET',
        num_students=100,
        num_sims=10,
        scenario='baseline'
    )
    
    # TVET Conservative scenario (25% nurse, 60% vocational, 15% NA)
    results_conservative = run_simple_simulation(
        program_type='TVET',
        num_students=100,
        num_sims=10,
        scenario='conservative'
    )
    
    # Custom scenario
    results_custom = run_simple_simulation(
        program_type='TVET',
        num_students=100,
        num_sims=10,
        scenario='custom',
        nurse_pct=30,
        voc_pct=50,
        na_pct=20
    )
    """
    # Fixed parameters
    num_years = 25
    limit_years = 10
    
    # Set default ISA parameters based on program type if not provided
    if isa_percentage is None:
        isa_percentage = 0.14 if program_type == 'University' else 0.12
    
    if isa_cap is None:
        isa_cap = 72500 if program_type == 'University' else 49950
    
    # Program-specific parameters
    if program_type == 'University':
        price_per_student = 29000
    elif program_type == 'TVET':
        price_per_student = 16650
    else:
        raise ValueError("Program type must be 'University' or 'TVET'")
    
    # Define all possible degree types with custom parameters
    base_degrees = {
        'BA': {
            'name': 'BA',
            'mean_earnings': ba_salary,
            'stdev': ba_std,
            'experience_growth': ba_growth/100.0,  # Convert from percentage to decimal
            'years_to_complete': 4
        },
        'MA': {
            'name': 'MA',
            'mean_earnings': ma_salary,
            'stdev': ma_std,
            'experience_growth': ma_growth/100.0,
            'years_to_complete': 6
        },
        'VOC': {
            'name': 'VOC',
            'mean_earnings': voc_salary,
            'stdev': voc_std,
            'experience_growth': voc_growth/100.0,
            'years_to_complete': 3
        },
        'NURSE': {
            'name': 'NURSE',
            'mean_earnings': nurse_salary,
            'stdev': nurse_std,
            'experience_growth': nurse_growth/100.0,
            'years_to_complete': 4
        },
        'NA': {
            'name': 'NA',
            'mean_earnings': na_salary,
            'stdev': na_std,
            'experience_growth': na_growth/100.0,
            'years_to_complete': 4
        }
    }
    
    # Set up degree distribution based on scenario
    degrees = []
    probs = []
    
    if scenario == 'baseline':
        if program_type == 'University':
            # University baseline: 100% BA
            degrees.append(Degree(
                name=base_degrees['BA']['name'],
                mean_earnings=base_degrees['BA']['mean_earnings'],
                stdev=base_degrees['BA']['stdev'],
                experience_growth=base_degrees['BA']['experience_growth'],
                years_to_complete=base_degrees['BA']['years_to_complete'],
                home_prob=home_prob
            ))
            probs = [1.0]
        else:  # TVET
            # TVET baseline: 45% nurse, 45% vocational, 10% NA
            degrees = [
                Degree(
                    name=base_degrees['NURSE']['name'],
                    mean_earnings=base_degrees['NURSE']['mean_earnings'],
                    stdev=base_degrees['NURSE']['stdev'],
                    experience_growth=base_degrees['NURSE']['experience_growth'],
                    years_to_complete=base_degrees['NURSE']['years_to_complete'],
                    home_prob=home_prob
                ),
                Degree(
                    name=base_degrees['VOC']['name'],
                    mean_earnings=base_degrees['VOC']['mean_earnings'],
                    stdev=base_degrees['VOC']['stdev'],
                    experience_growth=base_degrees['VOC']['experience_growth'],
                    years_to_complete=base_degrees['VOC']['years_to_complete'],
                    home_prob=home_prob
                ),
                Degree(
                    name=base_degrees['NA']['name'],
                    mean_earnings=base_degrees['NA']['mean_earnings'],
                    stdev=base_degrees['NA']['stdev'],
                    experience_growth=base_degrees['NA']['experience_growth'],
                    years_to_complete=base_degrees['NA']['years_to_complete'],
                    home_prob=0.8  # NA degree has fixed high home probability
                )
            ]
            probs = [0.45, 0.45, 0.10]
    
    elif scenario == 'conservative':
        if program_type == 'University':
            # University conservative: 100% BA (same as baseline for now)
            degrees.append(Degree(
                name=base_degrees['BA']['name'],
                mean_earnings=base_degrees['BA']['mean_earnings'],
                stdev=base_degrees['BA']['stdev'],
                experience_growth=base_degrees['BA']['experience_growth'],
                years_to_complete=base_degrees['BA']['years_to_complete'],
                home_prob=home_prob
            ))
            probs = [1.0]
        else:  # TVET
            # TVET conservative: 25% nurse, 60% vocational, 15% NA
            degrees = [
                Degree(
                    name=base_degrees['NURSE']['name'],
                    mean_earnings=base_degrees['NURSE']['mean_earnings'],
                    stdev=base_degrees['NURSE']['stdev'],
                    experience_growth=base_degrees['NURSE']['experience_growth'],
                    years_to_complete=base_degrees['NURSE']['years_to_complete'],
                    home_prob=home_prob
                ),
                Degree(
                    name=base_degrees['VOC']['name'],
                    mean_earnings=base_degrees['VOC']['mean_earnings'],
                    stdev=base_degrees['VOC']['stdev'],
                    experience_growth=base_degrees['VOC']['experience_growth'],
                    years_to_complete=base_degrees['VOC']['years_to_complete'],
                    home_prob=home_prob
                ),
                Degree(
                    name=base_degrees['NA']['name'],
                    mean_earnings=base_degrees['NA']['mean_earnings'],
                    stdev=base_degrees['NA']['stdev'],
                    experience_growth=base_degrees['NA']['experience_growth'],
                    years_to_complete=base_degrees['NA']['years_to_complete'],
                    home_prob=0.8  # NA degree has fixed high home probability
                )
            ]
            probs = [0.25, 0.60, 0.15]
    
    elif scenario == 'custom':
        # Use user-provided degree distribution
        if ba_pct > 0:
            degrees.append(Degree(
                name=base_degrees['BA']['name'],
                mean_earnings=base_degrees['BA']['mean_earnings'],
                stdev=base_degrees['BA']['stdev'],
                experience_growth=base_degrees['BA']['experience_growth'],
                years_to_complete=base_degrees['BA']['years_to_complete'],
                home_prob=home_prob
            ))
            probs.append(ba_pct)
        
        if ma_pct > 0:
            degrees.append(Degree(
                name=base_degrees['MA']['name'],
                mean_earnings=base_degrees['MA']['mean_earnings'],
                stdev=base_degrees['MA']['stdev'],
                experience_growth=base_degrees['MA']['experience_growth'],
                years_to_complete=base_degrees['MA']['years_to_complete'],
                home_prob=home_prob
            ))
            probs.append(ma_pct)
        
        if voc_pct > 0:
            degrees.append(Degree(
                name=base_degrees['VOC']['name'],
                mean_earnings=base_degrees['VOC']['mean_earnings'],
                stdev=base_degrees['VOC']['stdev'],
                experience_growth=base_degrees['VOC']['experience_growth'],
                years_to_complete=base_degrees['VOC']['years_to_complete'],
                home_prob=home_prob
            ))
            probs.append(voc_pct)

        if nurse_pct > 0:
            degrees.append(Degree(
                name=base_degrees['NURSE']['name'],
                mean_earnings=base_degrees['NURSE']['mean_earnings'],
                stdev=base_degrees['NURSE']['stdev'],
                experience_growth=base_degrees['NURSE']['experience_growth'],
                years_to_complete=base_degrees['NURSE']['years_to_complete'],
                home_prob=home_prob
            ))
            probs.append(nurse_pct)
        
        if na_pct > 0:
            degrees.append(Degree(
                name=base_degrees['NA']['name'],
                mean_earnings=base_degrees['NA']['mean_earnings'],
                stdev=base_degrees['NA']['stdev'],
                experience_growth=base_degrees['NA']['experience_growth'],
                years_to_complete=base_degrees['NA']['years_to_complete'],
                home_prob=0.8  # NA degree has fixed high home probability
            ))
            probs.append(na_pct)
        
        # Normalize probabilities to ensure they sum to 1
        if sum(probs) > 0:
            probs = [p/sum(probs) for p in probs]
        else:
            raise ValueError("At least one degree type must have a non-zero percentage")
    else:
        raise ValueError("Invalid scenario. Must be 'baseline', 'conservative', or 'custom'")
    
    # Prepare containers for results
    total_payment = {}
    investor_payment = {}
    malengo_payment = {}
    df_list = []
    
    # Track statistics across simulations
    employment_stats = []
    repayment_stats = []
    cap_stats = []
    
    # Calculate total investment
    total_investment = num_students * price_per_student
    
    # Run multiple simulations
    for trial in range(num_sims):
        # Initialize year class
        year = Year(
            initial_inflation_rate=initial_inflation_rate,
            initial_unemployment_rate=initial_unemployment_rate,
            initial_isa_cap=isa_cap,
            initial_isa_threshold=isa_threshold,
            num_years=num_years
        )
        
        # Assign degrees to each student
        test_array = np.array([np.random.multinomial(1, probs) for j in range(num_students)])
        degree_labels = np.array(degrees)[test_array.argmax(axis=1)]
        students = []
        for i in range(num_students):
            students.append(Student(degree_labels[i], num_years))
        
        # Run the simulation and store results
        df_list.append(simulate_simple(
            students=students,
            year=year,
            num_years=num_years,
            limit_years=limit_years,
            isa_percentage=isa_percentage,
            performance_fee_pct=performance_fee_pct,
            gamma=False,
            price_per_student=price_per_student,
            new_malengo_fee=new_malengo_fee
        ))
        
        # Track statistics for this simulation
        students_employed = 0
        students_made_payments = 0
        students_hit_payment_cap = 0
        students_hit_years_cap = 0
        students_hit_no_cap = 0
        
        # Track repayments by category
        total_repayment_cap_hit = 0
        total_years_cap_hit = 0
        total_no_cap_hit = 0
        
        # Count students in different categories
        for student in students:
            # Check if student was ever employed
            was_employed = False
            for i in range(num_years):
                if i >= student.degree.years_to_complete and student.earnings[i] > 0:
                    was_employed = True
                    break
            
            if was_employed:
                students_employed += 1
                
            # Check if student made any payments
            made_payment = sum(student.payments) > 0
            if made_payment:
                students_made_payments += 1
                
            # Check which cap (if any) the student hit
            if student.hit_cap:
                students_hit_payment_cap += 1
                total_repayment_cap_hit += sum(student.real_payments)
            elif student.years_paid >= limit_years:
                students_hit_years_cap += 1
                total_years_cap_hit += sum(student.real_payments)
            else:
                if made_payment:  # Only count students who made payments
                    students_hit_no_cap += 1
                    total_no_cap_hit += sum(student.real_payments)
        
        # Calculate averages (with safe division)
        avg_repayment_cap_hit = total_repayment_cap_hit / max(1, students_hit_payment_cap)
        avg_repayment_years_hit = total_years_cap_hit / max(1, students_hit_years_cap)
        avg_repayment_no_cap = total_no_cap_hit / max(1, students_hit_no_cap)
        
        # Store statistics for this simulation
        employment_stats.append(students_employed / num_students)
        repayment_stats.append(students_made_payments / num_students)
        
        cap_stats.append({
            'payment_cap_count': students_hit_payment_cap,
            'years_cap_count': students_hit_years_cap,
            'no_cap_count': students_hit_no_cap,
            'payment_cap_pct': students_hit_payment_cap / num_students,
            'years_cap_pct': students_hit_years_cap / num_students,
            'no_cap_pct': students_hit_no_cap / num_students,
            'avg_repayment_cap_hit': avg_repayment_cap_hit,
            'avg_repayment_years_hit': avg_repayment_years_hit,
            'avg_repayment_no_cap': avg_repayment_no_cap
        })
        
        # Extract and store payments
        total_payment[trial] = np.sum(pd.DataFrame([student.real_payments for student in students]), axis=0)
        investor_payment[trial] = df_list[trial]['Investor_Real_Payments']
        malengo_payment[trial] = df_list[trial]['Malengo_Real_Payments']
    
    # Calculate summary statistics
    payments_df = pd.DataFrame(total_payment)
    average_total_payment = np.sum(payments_df, axis=0).mean()
    average_duration = np.dot((payments_df.index + 1), payments_df / np.sum(payments_df, axis=0)).mean()
    
    # Calculate IRR (safely handle negative values)
    if average_total_payment > 0:
        IRR = np.log(max(1, average_total_payment) / total_investment) / average_duration
    else:
        IRR = -0.1  # Default negative return
    
    # Calculate investor payments
    investor_payments_df = pd.DataFrame(investor_payment)
    average_investor_payment = np.sum(investor_payments_df, axis=0).mean()
    
    # Calculate Malengo payments
    malengo_payments_df = pd.DataFrame(malengo_payment)
    average_malengo_payment = np.sum(malengo_payments_df, axis=0).mean()
    
    # Calculate investor IRR using total investment as base
    # The investor's return is lower because they only get a portion of the total payments
    if average_investor_payment > 0:
        investor_IRR = np.log(max(1, average_investor_payment) / total_investment) / average_duration
    else:
        investor_IRR = -0.1
    
    # Calculate quantile metrics
    payment_quantiles = {}
    for quantile in [0, 0.25, 0.5, 0.75, 1.0]:
        quantile_payment = np.sum(payments_df, axis=0).quantile(quantile)
        if quantile_payment > 0:
            payment_quantiles[quantile] = np.log(max(1, quantile_payment) / total_investment) / average_duration
        else:
            payment_quantiles[quantile] = -0.1 - (0.1 * (1-quantile))  # Lower default for lower quantiles
    
    # Prepare payment data for plotting
    payment_by_year = payments_df.mean(axis=1)
    investor_payment_by_year = investor_payments_df.mean(axis=1)
    malengo_payment_by_year = malengo_payments_df.mean(axis=1)
    
    # Calculate average employment and repayment statistics
    avg_employment_rate = np.mean(employment_stats)
    avg_repayment_rate = np.mean(repayment_stats)
    
    # Calculate average cap statistics
    avg_cap_stats = {
        'payment_cap_count': np.mean([stat['payment_cap_count'] for stat in cap_stats]),
        'years_cap_count': np.mean([stat['years_cap_count'] for stat in cap_stats]),
        'no_cap_count': np.mean([stat['no_cap_count'] for stat in cap_stats]),
        'payment_cap_pct': np.mean([stat['payment_cap_pct'] for stat in cap_stats]),
        'years_cap_pct': np.mean([stat['years_cap_pct'] for stat in cap_stats]),
        'no_cap_pct': np.mean([stat['no_cap_pct'] for stat in cap_stats]),
        'avg_repayment_cap_hit': np.mean([stat['avg_repayment_cap_hit'] for stat in cap_stats]),
        'avg_repayment_years_hit': np.mean([stat['avg_repayment_years_hit'] for stat in cap_stats]),
        'avg_repayment_no_cap': np.mean([stat['avg_repayment_no_cap'] for stat in cap_stats])
    }
    
    # Calculate and add degree distribution for return data
    degree_counts = {}
    degree_pcts = {}
    for i, degree in enumerate(degrees):
        degree_counts[degree.name] = probs[i] * num_students
        degree_pcts[degree.name] = probs[i]
    
    return {
        'program_type': program_type,
        'total_investment': total_investment,
        'price_per_student': price_per_student,
        'isa_percentage': isa_percentage,
        'isa_threshold': isa_threshold,
        'isa_cap': isa_cap,
        'IRR': IRR,
        'investor_IRR': investor_IRR,
        'average_total_payment': average_total_payment,
        'average_investor_payment': average_investor_payment,
        'average_malengo_payment': average_malengo_payment,
        'average_duration': average_duration,
        'payment_by_year': payment_by_year,
        'investor_payment_by_year': investor_payment_by_year,
        'malengo_payment_by_year': malengo_payment_by_year,
        'payments_df': payments_df,
        'investor_payments_df': investor_payments_df,
        'malengo_payments_df': malengo_payments_df,
        'payment_quantiles': payment_quantiles,
        'performance_fee_pct': performance_fee_pct,
        'adjusted_mean_salary': degrees[0].mean_earnings if len(degrees) > 0 else 0,
        'adjusted_salary_std': degrees[0].stdev if len(degrees) > 0 else 0,
        'employment_rate': avg_employment_rate,
        'repayment_rate': avg_repayment_rate,
        'cap_stats': avg_cap_stats,
        'home_prob': home_prob,
        'custom_degrees': True,
        'degree_counts': degree_counts,
        'degree_pcts': degree_pcts
    } 