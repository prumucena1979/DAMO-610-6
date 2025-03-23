from ortools.linear_solver import pywraplp
import numpy as np


def solve_route():
    # Create solver
    solver = pywraplp.Solver.CreateSolver("SCIP")
    # Define data (example values; replace with actual data)
    n_routes = 6  # Number of routes
    n_shifts = 4  # Number of shifts
    bus_capacity_I = 60  # Capacity of bus type I
    bus_capacity_II = 90  # Capacity of bus type II
    bus_capacity_III = 160  # Capacity of bus type II
    fleet_size_I = 600  # Total available buses type I
    fleet_size_II = 90  # Total available buses type II
    fleet_size_III = 10  # Total available buses type III
    D = {
        1: 4126,
        2: 3497,
        3: 11030,
        4: 3029,
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
    # Extracted from Table 2
    trip_factors = np.array([
        [7, 12, 8, 3],
        [4, 7, 5, 2],
        [4, 7, 5, 2],
        [3, 5, 3, 1],


        [4, 8, 5, 2],
        [5, 9, 6, 2]
    ])

    P = [
        0.014,
        0.012,
        0.038,
        0.010,

        0.013,
        0.007,
    ]
    demand=np.array([
        [1650,825,1444,206],
        [1399,699,1224,175],
        [4412,2206,3860,551],
        [1212,606,1060,151],

        [1534,767,1342,192],
        [812,406,710,101]
    ])

    w = {
         7,  # Morning Peak
         12,  # First Off-Peak
         8,  # Evening Peak
         3  # Second Off-Peak
    }

    # Decision variables
    x = {}  # Trips by bus type I
    y = {}  # Trips by bus type II
    z = {}  # Trips by bus type III
    for i in range(n_routes):
        for j in range(n_shifts):
            x[i, j] = solver.NumVar(0, solver.infinity(), f"x_{i}_{j}")
            y[i, j] = solver.NumVar(0, solver.infinity(), f"y_{i}_{j}")
            z[i, j] = solver.NumVar(0, solver.infinity(), f"y_{i}_{j}")

    # Equation 1: Objective function - Minimize total trips
    solver.Minimize(sum(x[i, j] + y[i, j]+z[i, j] for i in range(n_routes)  for j in range(n_shifts)))

    # Equation 2: Demand satisfaction constraint
    # Constraints
    for i in range(n_routes):
        for j in range(n_shifts):
            # Equation 2: Demand satisfaction constraint
            solver.Add(x[i, j] * bus_capacity_I + y[i, j] * bus_capacity_II +z[i, j] * bus_capacity_III >= demand[i, j])


    # Equation 3,4 & 10: Total trips must not exceed available fleet trips
    solver.Add(sum(x[i, j] for i in range(n_routes) for j in range(n_shifts)) <= sum(fleet_size_I * trip_factors[i, j]for i in range(n_routes) for j in range(n_shifts)))
    solver.Add(sum(y[i, j] for i in range(n_routes) for j in range(n_shifts)) <= sum(fleet_size_II * trip_factors[i, j] for i in range(n_routes) for j in range(n_shifts)))
    solver.Add(sum(z[i, j] for i in range(n_routes) for j in range(n_shifts)) <= sum(fleet_size_III * trip_factors[i, j] for i in range(n_routes) for j in range(n_shifts)))

    # Equation 5: Minimum required trips per shift
    solver.Add(sum(x[i,j]+y[i,j]+z[i,j] for i in range(n_routes) for j in range(n_shifts))<=93*sum(w))

    # Equation 6, 7 & 11: Trips assigned should not exceed available trips for route i in shift j
    for i in range(n_routes):
        for j in range(n_shifts):
            solver.Add(x[i, j] <= trip_factors[i, j] * fleet_size_I * P[i])
            solver.Add(y[i, j] <= trip_factors[i, j] * fleet_size_II * P[i])
            solver.Add(z[i, j] <= trip_factors[i, j] * fleet_size_III * P[i])

    # Equation 8: Sum of trip proportions must be 1
    solver.Add(sum(P[i] for i in range(n_routes)) <= 1)

    # Equation 9: Non-negativity constraint
    for i in range(n_routes):
        for j in range(n_shifts):
            solver.Add(x[i, j] >= 0)
            solver.Add(y[i, j] >= 0)
            solver.Add(z[i, j] >= 0)

    # Solve the LP model
    status = solver.Solve()

    # Print results
    if status == pywraplp.Solver.OPTIMAL:
        print("Optimal solution found!")
        for i in range(n_routes):
            for j in range(n_shifts):
                print(f"Route {i + 1}, Shift {j + 1}:")
                print(f"Bus Type I Trips(x) = {round(x[i, j].solution_value(),2)}")
                print(f"Bus Type II Trips(y) = {round(y[i, j].solution_value(),2)}")
                print(f"Bus Type III Trips(z) = {round(z[i, j].solution_value(), 2)}")
    else:
        print("No optimal solution found.")

solve_route()