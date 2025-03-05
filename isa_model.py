import numpy as np
import pandas as pd

class Year:
    """
    Class for tracking and updating economic parameters for each simulation year.
    """
    def __init__(self, initial_gdp_growth, initial_inflation_rate, initial_unemployment_rate, 
                 initial_isa_cap, initial_isa_threshold, num_years, senior_debt_threshold, mezzanine_debt_threshold):
        self.year_count = 1
        self.gdp_growth = initial_gdp_growth
        self.stable_gdp_growth = initial_gdp_growth
        self.inflation_rate = initial_inflation_rate
        self.stable_inflation_rate = initial_inflation_rate
        self.unemployment_rate = initial_unemployment_rate
        self.stable_unemployment_rate = initial_unemployment_rate
        self.isa_cap = initial_isa_cap
        self.isa_threshold = initial_isa_threshold
        self.deflator = 1
        self.hit_senior_cap = False
        self.hit_mezzanine_cap = False
        self.senior_payments = [0] * num_years
        self.mezzanine_payments = [0] * num_years
        self.remainder_payments = [0] * num_years
        self.senior_real_payments = [0] * num_years
        self.mezzanine_real_payments = [0] * num_years
        self.remainder_real_payments = [0] * num_years
        self.senior_debt_threshold = senior_debt_threshold
        self.mezzanine_debt_threshold = mezzanine_debt_threshold

    def next_year(self):
        """Advance to the next year and update economic conditions"""
        self.year_count = self.year_count + 1
        self.gdp_growth = self.stable_gdp_growth * .33 + self.gdp_growth * .5 + np.random.normal(0, .02)
        self.inflation_rate = self.stable_inflation_rate * .45 + self.inflation_rate * .5 + np.random.normal(0, .01)
        self.unemployment_rate = self.stable_unemployment_rate * .33 + self.unemployment_rate * .25 + np.random.lognormal(0, 1) / 100
        self.isa_cap = self.isa_cap * (1 + self.inflation_rate)
        self.isa_threshold = self.isa_threshold * (1 + self.inflation_rate)
        self.deflator = self.deflator * (1 + self.inflation_rate)
        if not self.hit_senior_cap:
            self.senior_debt_threshold = self.senior_debt_threshold * (1 + self.inflation_rate)
        if not self.hit_mezzanine_cap:
            self.mezzanine_debt_threshold = self.mezzanine_debt_threshold * (1 + self.inflation_rate)


class Student:
    """
    Class for tracking the state and payment history of individual students.
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


def simulate(students, year, num_years, isa_percentage, limit_years, gamma=False):
    """
    Run a single simulation for the given students over the specified number of years.
    
    Parameters:
    - students: List of Student objects
    - year: Year object representing economic conditions
    - num_years: Total number of years to simulate
    - isa_percentage: Percentage of income to pay in ISA
    - limit_years: Maximum number of years to pay the ISA
    - gamma: Whether to use gamma distribution instead of normal for earnings
    
    Returns:
    - Dictionary of simulation results
    """
    for i in range(num_years):
        for student in students:
            if i < student.degree.years_to_complete:
                continue
            if i == student.degree.years_to_complete:
                student.is_graduated = True
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
                excess = max(0, student.earnings[i] - year.isa_threshold)
                if excess > 0:
                    student.years_paid = 1 + student.years_paid

                    if student.years_paid > limit_years:
                        continue
                    if student.hit_cap:
                        continue
                    if (np.sum(student.payments) + isa_percentage * excess) > year.isa_cap:
                        student.payments[i] = year.isa_cap - np.sum(student.payments)
                        student.real_payments[i] = (year.isa_cap - np.sum(student.payments)) / year.deflator
                        student.hit_cap = True
                    else:
                        student.payments[i] = isa_percentage * excess
                        student.real_payments[i] = isa_percentage * excess / year.deflator

                    if (year.hit_mezzanine_cap == True) & (year.hit_senior_cap == True):
                        year.remainder_payments[i] = year.remainder_payments[i] + student.payments[i]
                        year.remainder_real_payments[i] = year.remainder_real_payments[i] + student.real_payments[i]
                    elif (year.hit_mezzanine_cap == False) & (year.hit_senior_cap == True):
                        if np.sum(year.mezzanine_payments) + student.payments[i] <= year.mezzanine_debt_threshold:
                            year.mezzanine_payments[i] = year.mezzanine_payments[i] + student.payments[i]
                            year.mezzanine_real_payments[i] = year.mezzanine_real_payments[i] + student.real_payments[i]
                        else:
                            remainder_payment = student.payments[i] - min(student.payments[i], year.mezzanine_debt_threshold - np.sum(year.mezzanine_payments))
                            year.remainder_payments[i] = year.remainder_payments[i] + remainder_payment
                            year.remainder_real_payments[i] = year.remainder_real_payments[i] + (remainder_payment / year.deflator)
                            year.mezzanine_payments[i] = year.mezzanine_payments[i] + min(student.payments[i], year.mezzanine_debt_threshold - np.sum(year.mezzanine_payments))
                            year.mezzanine_real_payments[i] = year.mezzanine_real_payments[i] + min(student.real_payments[i], year.mezzanine_debt_threshold - np.sum(year.mezzanine_payments))
                            year.hit_mezzanine_cap = True
                    else:
                        if np.sum(year.senior_payments) + student.payments[i] <= year.senior_debt_threshold:
                            year.senior_payments[i] = year.senior_payments[i] + student.payments[i]
                            year.senior_real_payments[i] = year.senior_real_payments[i] + student.real_payments[i]
                        else:
                            year.mezzanine_payments[i] = year.mezzanine_payments[i] + (student.payments[i] - min(student.payments[i], year.senior_debt_threshold - np.sum(year.senior_payments)))
                            year.mezzanine_real_payments[i] = year.mezzanine_real_payments[i] + (student.real_payments[i] - min(student.real_payments[i], year.senior_debt_threshold - np.sum(year.senior_real_payments)))
                            year.senior_payments[i] = year.senior_payments[i] + min(student.payments[i], year.senior_debt_threshold - np.sum(year.senior_payments))
                            year.senior_real_payments[i] = year.senior_real_payments[i] + min(student.real_payments[i], year.senior_debt_threshold - np.sum(year.senior_real_payments))
                            year.hit_senior_cap = True
            else:
                student.years_experience = max(0, student.years_experience-3)

        year.next_year()

    data = {
        'Student': students,
        'Degree': [student.degree for student in students],
        'Earnings': [student.earnings for student in students],
        'Payments': [student.payments for student in students],
        'Real_Payments': [student.real_payments for student in students],
        'Cohort_Senior_Payments': year.senior_payments,
        'Cohort_Senior_Real_Payments': year.senior_real_payments,
        'Cohort_Mezzanine_Payments': year.mezzanine_payments,
        'Cohort_Mezzanine_Real_Payments': year.mezzanine_real_payments,
        'Cohort_Remainder_Payments': year.remainder_payments,
        'Cohort_Remainder_Real_Payments': year.remainder_real_payments
    }

    return data


def run_monte_carlo_simulations(
    num_students,
    num_sims,
    num_years,
    limit_years,
    price_per_student,
    initial_isa_cap,
    initial_isa_threshold,
    isa_percentage,
    initial_gdp_growth,
    initial_unemployment_rate,
    initial_inflation_rate,
    degree_probs
):
    """
    Run multiple simulations and return aggregated results.
    
    Parameters are the same as required by the simulation function.
    
    Returns:
    - Dictionary of aggregated results from multiple simulations
    """
    
    # Define degrees
    degrees = [
        Degree(name='BA', mean_earnings=41300, stdev=13000, experience_growth=0.04, years_to_complete=5, home_prob=0.0),
        Degree(name='MA', mean_earnings=46709, stdev=15000, experience_growth=0.04, years_to_complete=7, home_prob=0.0),
        Degree(name='VOC', mean_earnings=31500, stdev=8000, experience_growth=0.04, years_to_complete=5, home_prob=0.0),
        Degree(name='NA', mean_earnings=2200, stdev=8000, experience_growth=0.01, years_to_complete=4, home_prob=0.8),
    ]
    
    # Set seniority structure
    total_debt = num_students * price_per_student
    senior_debt = total_debt * 0.7
    mezzanine_debt = total_debt * 0.2
    remainder_debt = total_debt * 0.1
    senior_debt_threshold = senior_debt * 1.5
    mezzanine_debt_threshold = mezzanine_debt * 2
    
    # Prepare containers for results
    total_payment = {}
    senior_payment = {}
    mezzanine_payment = {}
    remainder_payment = {}
    df_list = []
    
    # Run multiple simulations
    for trial in range(num_sims):
        # Initialize year class
        year = Year(
            initial_gdp_growth=initial_gdp_growth, 
            initial_inflation_rate=initial_inflation_rate,
            initial_unemployment_rate=initial_unemployment_rate,
            initial_isa_cap=initial_isa_cap,
            initial_isa_threshold=initial_isa_threshold,
            num_years=num_years,
            senior_debt_threshold=senior_debt_threshold, 
            mezzanine_debt_threshold=mezzanine_debt_threshold
        )
        
        # Assign degrees to each student
        test_array = np.array([np.random.multinomial(1, degree_probs) for j in range(num_students)])
        degree_labels = np.array(degrees)[test_array.argmax(axis=1)]
        students = []
        for i in range(num_students):
            students.append(Student(degree_labels[i], num_years))
        
        # Run the simulation and store results
        df_list.append(simulate(
            students=students,
            year=year,
            num_years=num_years,
            limit_years=limit_years,
            isa_percentage=isa_percentage,
            gamma=False
        ))
        
        # Extract and store payments
        total_payment[trial] = np.sum(pd.DataFrame(df_list[trial]['Real_Payments']), axis=0)
        senior_payment[trial] = df_list[trial]['Cohort_Senior_Real_Payments']
        mezzanine_payment[trial] = df_list[trial]['Cohort_Mezzanine_Real_Payments']
        remainder_payment[trial] = df_list[trial]['Cohort_Remainder_Real_Payments']
    
    # Calculate summary statistics
    payments_df = pd.DataFrame(total_payment)
    average_total_payment = np.sum(payments_df, axis=0).mean()
    average_duration = np.dot((payments_df.index + 1), payments_df / np.sum(payments_df, axis=0)).mean()
    
    # Handle potential negative values in IRR calculation safely
    if average_total_payment > 0:
        IRR = np.log(max(1, average_total_payment) / total_debt) / average_duration
    else:
        IRR = -0.1  # Default negative return for cases with no payment
    
    payments_df_senior = pd.DataFrame(senior_payment)
    average_total_payment_senior = np.sum(payments_df_senior, axis=0).mean()
    average_duration_senior = np.dot((payments_df_senior.index + 1), payments_df_senior / np.sum(payments_df_senior, axis=0)).mean()
    if average_total_payment_senior > 0:
        IRR_senior = np.log(max(1, average_total_payment_senior) / senior_debt) / average_duration_senior + initial_inflation_rate
    else:
        IRR_senior = -0.1 + initial_inflation_rate
    
    min_total_payment_senior = np.sum(payments_df_senior, axis=0).min()
    if min_total_payment_senior > 0:
        IRR_senior_min = np.log(max(1, min_total_payment_senior) / senior_debt) / average_duration_senior + initial_inflation_rate
    else:
        IRR_senior_min = -0.15 + initial_inflation_rate
    
    fifth_total_payment_senior = np.sum(payments_df_senior, axis=0).quantile(.05)
    if fifth_total_payment_senior > 0:
        IRR_senior_fifth = np.log(max(1, fifth_total_payment_senior) / senior_debt) / average_duration_senior + initial_inflation_rate
    else:
        IRR_senior_fifth = -0.12 + initial_inflation_rate
    
    payments_df_mezzanine = pd.DataFrame(mezzanine_payment) + 1
    average_total_payment_mezzanine = np.sum(payments_df_mezzanine, axis=0).mean()
    average_duration_mezzanine = np.dot((payments_df_mezzanine.index + 1), payments_df_mezzanine / np.sum(payments_df_mezzanine, axis=0)).mean()
    if average_total_payment_mezzanine > 0:
        IRR_mezzanine = np.log(max(1, average_total_payment_mezzanine) / mezzanine_debt) / average_duration_mezzanine + initial_inflation_rate
    else:
        IRR_mezzanine = -0.2 + initial_inflation_rate
    
    payments_df_remainder = pd.DataFrame(remainder_payment) + 1
    average_total_payment_remainder = np.sum(payments_df_remainder, axis=0).mean()
    average_duration_remainder = np.dot((payments_df_remainder.index + 1), payments_df_remainder / np.sum(payments_df_remainder, axis=0)).mean()
    if average_total_payment_remainder > 0:
        IRR_remainder = np.log(max(1, average_total_payment_remainder) / remainder_debt) / average_duration_remainder + initial_inflation_rate
    else:
        IRR_remainder = -0.25 + initial_inflation_rate
    
    # Calculate quantile metrics with safe handling
    quantile_total_payment_75 = np.sum(payments_df, axis=0).quantile(.75)
    if quantile_total_payment_75 > 0:
        IRR_quantile_75 = np.log(max(1, quantile_total_payment_75) / total_debt) / average_duration
    else:
        IRR_quantile_75 = -0.1
    
    quantile_total_payment_25 = np.sum(payments_df, axis=0).quantile(.25)
    if quantile_total_payment_25 > 0:
        IRR_quantile_25 = np.log(max(1, quantile_total_payment_25) / total_debt) / average_duration
    else:
        IRR_quantile_25 = -0.15
    
    quantile_total_payment_0 = np.sum(payments_df, axis=0).quantile(.0)
    if quantile_total_payment_0 > 0:
        IRR_quantile_0 = np.log(max(1, quantile_total_payment_0) / total_debt) / average_duration
    else:
        IRR_quantile_0 = -0.2
    
    quantile_total_payment_100 = np.sum(payments_df, axis=0).quantile(1)
    if quantile_total_payment_100 > 0:
        IRR_quantile_100 = np.log(max(1, quantile_total_payment_100) / total_debt) / average_duration
    else:
        IRR_quantile_100 = -0.05
    
    # Prepare payment data for plotting
    payment_by_year = payments_df.mean(axis=1)
    
    return {
        'IRR': IRR,
        'IRR_senior': IRR_senior,
        'IRR_mezzanine': IRR_mezzanine,
        'IRR_remainder': IRR_remainder,
        'IRR_quantile_75': IRR_quantile_75,
        'IRR_quantile_25': IRR_quantile_25,
        'IRR_quantile_0': IRR_quantile_0,
        'IRR_quantile_100': IRR_quantile_100,
        'average_total_payment': average_total_payment,
        'average_duration': average_duration,
        'total_debt': total_debt,
        'senior_debt': senior_debt,
        'mezzanine_debt': mezzanine_debt,
        'remainder_debt': remainder_debt,
        'payment_by_year': payment_by_year,
        'payments_df': payments_df,
        'payments_df_senior': payments_df_senior,
        'payments_df_mezzanine': payments_df_mezzanine,
        'payments_df_remainder': payments_df_remainder,
    } 