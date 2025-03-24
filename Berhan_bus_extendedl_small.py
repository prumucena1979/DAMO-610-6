from ortools.linear_solver import pywraplp
import numpy as np

def solve_route():
    # Create solver using SCIP, which supports integer programming and is useful for extended models
    solver = pywraplp.Solver.CreateSolver("SCIP")

    # ---- Model Parameters ----

    n_routes = 6  # Number of selected bus routes (simplified prototype)
    n_shifts = 4  # Number of daily time shifts (e.g., morning peak, off-peak, etc.)

    # Capacities of the 3 bus types
    bus_capacity_I = 60
    bus_capacity_II = 90
    bus_capacity_III = 160

    # Total fleet sizes for each bus type
    fleet_size_I = 600
    fleet_size_II = 90
    fleet_size_III = 10

    # Total daily demand per route (aggregated)
    D = {
        1: 4126,
        2: 3497,
        3: 11030,
        4: 3029,
        92: 3836,
        93: 2029
    }

    # Proportions of daily demand split by shift
    demand_proportions = {
        1: 0.40,  # Morning Peak
        2: 0.20,  # First Off-Peak
        3: 0.35,  # Evening Peak
        4: 0.05   # Second Off-Peak
    }

    # Estimated average trip durations per route and shift (Tij)
    trip_factors = np.array([
        [7, 12, 8, 3],
        [4, 7, 5, 2],
        [4, 7, 5, 2],
        [3, 5, 3, 1],
        [4, 8, 5, 2],
        [5, 9, 6, 2]
    ])

    # Historical trip proportions by route (Pi)
    P = [
        0.014,
        0.012,
        0.038,
        0.010,
        0.013,
        0.007
    ]

    # Demand distributed by shift and route
    demand = np.array([
        [1650, 825, 1444, 206],
        [1399, 699, 1224, 175],
        [4412, 2206, 3860, 551],
        [1212, 606, 1060, 151],
        [1534, 767, 1342, 192],
        [812, 406, 710, 101]
    ])

    # Minimum number of trips per shift (from Berhan et al. assumptions)
    w = {
        1: 7,
        2: 12,
        3: 8,
        4: 3
    }

    # ---- Decision Variables ----

    x = {}  # Trips by bus type I
    y = {}  # Trips by bus type II
    z = {}  # Trips by bus type III

    for i in range(n_routes):
        for j in range(n_shifts):
            x[i, j] = solver.NumVar(0, solver.infinity(), f"x_{i}_{j}")
            y[i, j] = solver.NumVar(0, solver.infinity(), f"y_{i}_{j}")
            z[i, j] = solver.NumVar(0, solver.infinity(), f"z_{i}_{j}")

    # ---- Objective Function ----
    # Minimize total number of trips across all bus types and shifts
    solver.Minimize(sum(x[i, j] + y[i, j] + z[i, j] for i in range(n_routes) for j in range(n_shifts)))

    # ---- Constraints ----

    # (2) Demand satisfaction: Total capacity must meet or exceed demand for each route and shift
    for i in range(n_routes):
        for j in range(n_shifts):
            solver.Add(x[i, j] * bus_capacity_I +
                       y[i, j] * bus_capacity_II +
                       z[i, j] * bus_capacity_III >= demand[i, j])

    # (3,4,10) Total trips by fleet should not exceed the allowed fleet usage based on trip factors
    solver.Add(sum(x[i, j] for i in range(n_routes) for j in range(n_shifts)) <=
               sum(fleet_size_I * trip_factors[i, j] for i in range(n_routes) for j in range(n_shifts)))

    solver.Add(sum(y[i, j] for i in range(n_routes) for j in range(n_shifts)) <=
               sum(fleet_size_II * trip_factors[i, j] for i in range(n_routes) for j in range(n_shifts)))

    solver.Add(sum(z[i, j] for i in range(n_routes) for j in range(n_shifts)) <=
               sum(fleet_size_III * trip_factors[i, j] for i in range(n_routes) for j in range(n_shifts)))

    # (5) Global trip cap constraint: limits total trips based on shift minimums (service level constraint)
    solver.Add(sum(x[i, j] + y[i, j] + z[i, j] for i in range(n_routes) for j in range(n_shifts)) <=
               93 * sum(w.values()))

    # (6,7,11) Capacity constraints: trips per route/shift must not exceed available potential trips
    for i in range(n_routes):
        for j in range(n_shifts):
            solver.Add(x[i, j] <= trip_factors[i, j] * fleet_size_I * P[i])
            solver.Add(y[i, j] <= trip_factors[i, j] * fleet_size_II * P[i])
            solver.Add(z[i, j] <= trip_factors[i, j] * fleet_size_III * P[i])

    # (8) Ensure trip proportions across routes do not exceed 100% of the schedule
    solver.Add(sum(P[i] for i in range(n_routes)) <= 1)

    # (9) Non-negativity constraints (automatically satisfied, but explicitly declared for clarity)
    for i in range(n_routes):
        for j in range(n_shifts):
            solver.Add(x[i, j] >= 0)
            solver.Add(y[i, j] >= 0)
            solver.Add(z[i, j] >= 0)

    # ---- Solve Model ----

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print("Optimal solution found!")
        for i in range(n_routes):
            for j in range(n_shifts):
                print(f"Route {i + 1}, Shift {j + 1}:")
                print(f"  Bus Type I Trips (x) = {round(x[i, j].solution_value(), 2)}")
                print(f"  Bus Type II Trips (y) = {round(y[i, j].solution_value(), 2)}")
                print(f"  Bus Type III Trips (z) = {round(z[i, j].solution_value(), 2)}")
    else:
        print("No optimal solution found.")

solve_route()
