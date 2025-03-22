from ortools.linear_solver import pywraplp
import numpy as np

def solve_route():
    # Create solver using the Linear Programming solver (GLOP)
    solver = pywraplp.Solver.CreateSolver("GLOP")

    if not solver:
        print("❌ Solver not created. Please check your OR-Tools installation.")
        return

    # --------------------------
    # Define Input Data
    # --------------------------
    n_routes = 8  # Number of routes used for testing
    n_shifts = 4  # Number of daily shifts
    bus_capacity_I = 60  # Capacity of bus type I
    bus_capacity_II = 90  # Capacity of bus type II
    fleet_size_I = 600  # Total available buses of type I
    fleet_size_II = 90   # Total available buses of type II

    # Trip factors T[i][j] - number of trips per route per shift (extracted from Table 2)
    trip_factors = np.array([
        [7, 12, 8, 3],
        [4, 7, 5, 2],
        [4, 7, 5, 2],
        [3, 5, 3, 1],
        [4, 6, 7, 3],
        [4, 6, 7, 3],
        [4, 8, 5, 2],
        [5, 9, 6, 2]
    ])

    # Proportion of total demand per route (P[i])
    P = [0.014, 0.012, 0.038, 0.010, 0.016, 0.040, 0.013, 0.007]

    # Passenger demand D[i][j] per route and shift
    demand = np.array([
        [1650, 825, 1444, 206],
        [1399, 699, 1224, 175],
        [4412, 2206, 3860, 551],
        [1212, 606, 1060, 151],
        [1399, 699, 1224, 175],
        [400,  900,  200, 560],
        [1534, 767, 1342, 192],
        [812,  406,  710, 101]
    ])

    # Minimum required number of trips per shift (based on Table 1)
    w = {7, 12, 8, 3}

    # --------------------------
    # Define Decision Variables
    # --------------------------
    x = {}  # Trips by bus type I (x[i,j])
    y = {}  # Trips by bus type II (y[i,j])

    for i in range(n_routes):
        for j in range(n_shifts):
            x[i, j] = solver.NumVar(0, solver.infinity(), f"x_{i}_{j}")
            y[i, j] = solver.NumVar(0, solver.infinity(), f"y_{i}_{j}")

    # --------------------------
    # Objective Function: Minimize total number of trips
    # --------------------------
    solver.Minimize(sum(x[i, j] + y[i, j] for i in range(n_routes) for j in range(n_shifts)))

    # --------------------------
    # Constraints
    # --------------------------

    # (1) Demand Satisfaction Constraint
    for i in range(n_routes):
        for j in range(n_shifts):
            solver.Add(x[i, j] * bus_capacity_I + y[i, j] * bus_capacity_II >= demand[i, j])

    # (2 & 3) Fleet Capacity Constraints
    solver.Add(sum(x[i, j] for i in range(n_routes) for j in range(n_shifts)) <=
               sum(fleet_size_I * trip_factors[i, j] for i in range(n_routes) for j in range(n_shifts)))

    solver.Add(sum(y[i, j] for i in range(n_routes) for j in range(n_shifts)) <=
               sum(fleet_size_II * trip_factors[i, j] for i in range(n_routes) for j in range(n_shifts)))

    # (4) Minimum Required Trips Per Shift
    solver.Add(sum(x[i, j] + y[i, j] for i in range(n_routes) for j in range(n_shifts)) <= 93 * sum(w))

    # (5 & 6) Trips per Route and Shift should not exceed fleet limits based on P[i]
    for i in range(n_routes):
        for j in range(n_shifts):
            solver.Add(x[i, j] <= trip_factors[i, j] * fleet_size_I * P[i])
            solver.Add(y[i, j] <= trip_factors[i, j] * fleet_size_II * P[i])

    # (7) Sum of Proportions Constraint
    solver.Add(sum(P[i] for i in range(n_routes)) <= 1)

    # --------------------------
    # Solve the Model
    # --------------------------
    status = solver.Solve()

    # --------------------------
    # Analyze and Report Status
    # --------------------------
    if status == pywraplp.Solver.OPTIMAL:
        print("✅ OPTIMAL solution found.")
        print("This means the solver was able to minimize total trips while satisfying all constraints.")
        print("Below is the optimal trip assignment:\n")
        for i in range(n_routes):
            for j in range(n_shifts):
                print(f"Route {i + 1}, Shift {j + 1}:")
                print(f"  Bus Type I Trips (x) = {round(x[i, j].solution_value(), 2)}")
                print(f"  Bus Type II Trips (y) = {round(y[i, j].solution_value(), 2)}")

    elif status == pywraplp.Solver.FEASIBLE:
        print("🟡 A FEASIBLE solution was found, but it is not guaranteed to be optimal.")
        print("This may indicate solver stopped early due to time/resource limits.")
        print("You may consider increasing time limits or improving model flexibility.")

    elif status == pywraplp.Solver.INFEASIBLE:
        print("⚠️ No feasible solution exists for the current model and data.")
        print("This suggests that constraints are too restrictive, or the demand exceeds capacity.")
        print("Consider reviewing fleet size, trip caps, or allowing flexibility in constraints.")

    elif status == pywraplp.Solver.UNBOUNDED:
        print("⚠️ The model is unbounded. The objective function can decrease indefinitely.")
        print("This typically means a key constraint is missing (e.g., upper bounds on trips).")

    else:
        print("❌ Solver finished with an UNKNOWN or ERROR status.")
        print("Please check the input data and constraints for any inconsistencies.")

# Execute the model
solve_route()
