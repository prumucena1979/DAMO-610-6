from ortools.linear_solver import pywraplp
import random

def create_bus_scheduling_model():
    """
    Creates and returns a bus scheduling optimization model.
    """

    solver = pywraplp.Solver.CreateSolver('SCIP')  # You can choose a different solver

    # ---- Define Data ----
    num_routes = 93
    num_shifts = 4

    # Passenger Demand Data (D)
    # Extracted from Table 2
    # Demand data for all 93 routes
    D = {
        1: 4126,
        2: 3497,
        3: 11030,
        4: 3029,
        5: 4133,
        6: 4221,
        7: 4616,
        8: 4734,
        9: 4282,
        10: 4443,
        11: 4596,
        12: 4376,
        13: 4786,
        14: 4475,
        15: 4479,
        16: 4434,
        17: 4522,
        18: 4565,
        19: 4704,
        20: 4452,
        21: 4402,
        22: 4539,
        23: 4640,
        24: 4488,
        25: 4554,
        26: 4526,
        27: 4615,
        28: 4725,
        29: 4697,
        30: 4441,
        31: 4516,
        32: 4486,
        33: 4600,
        34: 4637,
        35: 4633,
        36: 4426,
        37: 4386,
        38: 4543,
        39: 4473,
        40: 4683,
        41: 4656,
        42: 4504,
        43: 4627,
        44: 4410,
        45: 4400,
        46: 4626,
        47: 4560,
        48: 4467,
        49: 4689,
        50: 4594,
        51: 4710,
        52: 4668,
        53: 4513,
        54: 4454,
        55: 4380,
        56: 4438,
        57: 4562,
        58: 4586,
        59: 4571,
        60: 4496,
        61: 4404,
        62: 4547,
        63: 4660,
        64: 4708,
        65: 4575,
        66: 4390,
        67: 4428,
        68: 4537,
        69: 4500,
        70: 4608,
        71: 4675,
        72: 4647,
        73: 4432,
        74: 4465,
        75: 4492,
        76: 4550,
        77: 4581,
        78: 4667,
        79: 4557,
        80: 4417,
        81: 4397,
        82: 4511,
        83: 4532,
        84: 4604,
        85: 4671,
        86: 4643,
        87: 4421,
        88: 4458,
        89: 4484,
        90: 4541,
        91: 4611,
        92: 3836,
        93: 2029
    }

    # Demand proportions for each shift
    demand_proportions = {
        1: 0.40,  # Morning Peak
        2: 0.20,  # First Off-Peak
        3: 0.35,  # Evening Peak
        4: 0.05  # Second Off-Peak
    }

    # Calculate D[i,j] values
    D_ij = {}
    for i in D:
        #D_ij[i] = {}
        for j in demand_proportions:
            D_ij[i,j] = round(D[i] * demand_proportions[j],0)  # Calculate and store D[i,j]

    # Print the D[i,j] values for all routes
    for i in range(1, 94):
        print(f"Route {i}:")
        for j in range(1, 5):
            print(f"  D[{i},{j}]: {D_ij[i,j]}")


    # Trip Factor (T)
    # Calculated using Equation 11
    # Tij values from Table 2
    # Tij values from Table 2
    Tij_partial = {
        1: {'T_1': 7, 'T_2': 12, 'T_3': 8, 'T_4': 3},
        2: {'T_1': 4, 'T_2': 7, 'T_3': 5, 'T_4': 2},
        3: {'T_1': 4, 'T_2': 7, 'T_3': 5, 'T_4': 2},
        4: {'T_1': 3, 'T_2': 5, 'T_3': 3, 'T_4': 1},
        92: {'T_1': 4, 'T_2': 8, 'T_3': 5, 'T_4': 2},
        93: {'T_1': 5, 'T_2': 9, 'T_3': 6, 'T_4': 2}
    }

    # Create Tij dictionary for all routes
    T = {}
    for i in range(1, 94):
        #T[i] = {}  # Initialize the dictionary for route i
        for j in range(1, 5):  # Shifts are 1 to 4
            if i in Tij_partial:
                T[i,j] = Tij_partial[i][f'T_{j}']  # Assign value from Tij_partial
            else:
                T[i,j] = random.randint(1, 12) # Assign 0 for other routes

    # Print the T[i,j] values for all routes
    for i in range(1, 94):
        print(f"Route {i}:")
        for j in range(1, 5):
            print(f"  T[{i},{j}]: {T[i,j]}")

    shift_durations = {
        1: 195,  # Morning Peak
        2: 360,  # First Off-Peak
        3: 240,  # Evening Peak
        4: 90  # Second Off-Peak
    }

    # Trip Proportion (P)
    # Calculated using Equation 12
    # Initial Pi values from Table 2
    initial_Pi_values = {
        1: 0.014,
        2: 0.012,
        3: 0.038,
        4: 0.010,
        92: 0.013,
        93: 0.007
    }

    # Calculate the number of routes to adjust
    routes_to_adjust = 93 - len(initial_Pi_values)

    # Calculate the sum of the initial Pi values
    initial_Pi_sum = sum(initial_Pi_values.values())

    # Calculate the remaining proportion to be distributed
    remaining_proportion = 1 - initial_Pi_sum

    # Calculate the proportion for each of the remaining routes
    proportion_per_route = remaining_proportion / routes_to_adjust

    # Create the Pi dictionary
    Pi = {}

    # Assign the initial Pi values
    for route, value in initial_Pi_values.items():
        Pi[route] = value

    # Assign the calculated proportion to the remaining routes
    for route in range(5, 92):  # Loop from 5 to 91 (inclusive)
        if route not in initial_Pi_values:
            Pi[route] = proportion_per_route

    # Assign the value for route 93
    Pi[93] = initial_Pi_values[93]

    # Verify the total sum of Pi values
    total_Pi_sum = sum(Pi.values())
    print("Total sum of Pi:", total_Pi_sum)

    # Print the Pi values for all routes
    for i in range(1, 94):
        print(f"Route {i}: {Pi[i]}")

    # Minimum Trips per Shift (w)
    # Calculated from Table 1 and Equation 10
    w = {
        1: 7,  # Morning Peak
        2: 12,  # First Off-Peak
        3: 8,  # Evening Peak
        4: 3  # Second Off-Peak
    }

    # Decision Variables
    x = {}  # trips by bus type-1
    y = {}  # trips by bus type-2
    z = {}  # trips by bus type-3
    for i in range(1, num_routes + 1):
        for j in range(1, num_shifts + 1):
            x[i, j] = solver.NumVar(0, solver.infinity(), f'x_{i}_{j}')
            y[i, j] = solver.NumVar(0, solver.infinity(), f'y_{i}_{j}')
            z[i, j] = solver.NumVar(0, solver.infinity(), f'y_{i}_{j}')

    # Objective Function
    solver.Minimize(sum(x[i, j] + y[i, j] + z[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)))


    # Constraint 2
    for i in range(1, num_routes + 1):
        for j in range(1, num_shifts + 1):
            solver.Add(60 * x[i, j] + 90 * y[i, j] + 120*z[i,j] >= D_ij[i, j])

    # Constraint 3
    solver.Add(sum(x[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)) <=
                sum(600*T[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)))

    # Constraint 4
    solver.Add(solver.Sum(y[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)) <=
                sum(90*T[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)))

    # Constraint extension Z
    solver.Add(solver.Sum(z[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)) <=
               sum(10 * T[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)))

    # Constraint 5
    solver.Add(solver.Sum(x[i, j] + y[i, j] +z[i,j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1))
               <= 93 * sum(w))



    # Constraint 6
    for i in range(1, num_routes + 1):
        for j in range(1, num_shifts + 1):
            solver.Add(x[i, j] <= 600 * Pi[i] * T[i, j])

    # Constraint 7
    for i in range(1, num_routes + 1):
        for j in range(1, num_shifts + 1):
            solver.Add(y[i, j] <= 90 * Pi[i] * T[i, j])

    # Constraint extension
    for i in range(1, num_routes + 1):
        for j in range(1, num_shifts + 1):
            solver.Add(z[i, j] <= 10 * Pi[i] * T[i, j])

    # Constraint 8
    solver.Add(solver.Sum(Pi[i] for i in range(1, num_routes + 1)) <= 1)

    return solver, x, y, num_routes, num_shifts, D, w



# Create the model
solver, x, y, num_routes, num_shifts, D, w = create_bus_scheduling_model()

# Solve the model
status = solver.Solve()

# Check the solution status
if status == pywraplp.Solver.OPTIMAL:
    print("Solution is OPTIMAL")
    # Get the results
    for i in range(1, num_routes + 1):
        for j in range(1, num_shifts + 1):
            print(f"Route {i}, Shift {j}:")
            print(f"  Bus Type-I Trips (x): {x[i, j].solution_value()} .2f")
            print(f"  Bus Type-II Trips (y): {y[i, j].solution_value()} .2f")
            print(f"  Bus Type-III Trips (z): {z[i, j].solution_value()} .2f")
else:
    print("Solution is not OPTIMAL")