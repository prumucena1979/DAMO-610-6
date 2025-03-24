from ortools.linear_solver import pywraplp
import numpy as np

def solve_route():
    # --------------------------------------------------------
    # SMALL-SCALE PROTOTYPE: ORIGINAL LINEAR PROGRAMMING MODEL
    # --------------------------------------------------------
    # This model implements a simplified version of the original LP model
    # proposed by Berhan et al. (2014), using a subset of 8 routes and 4 shifts.
    # It serves as a test to validate the mathematical logic and solvability
    # of the base model before scaling it to all 93 routes.
    #
    # Objective: Minimize the total number of bus trips (using two types of buses)
    # while satisfying demand, fleet, and shift-level constraints.
    # --------------------------------------------------------

    # Create a linear solver using the GLOP backend (for LP problems)
    solver = pywraplp.Solver.CreateSolver("GLOP")

    # -------------------------------
    # Define basic model input values
    # -------------------------------
    n_routes = 8   # Number of routes considered in the prototype
    n_shifts = 4   # Number of daily time shifts

    bus_capacity_I = 60   # Capacity of Bus Type I
    bus_capacity_II = 90  # Capacity of Bus Type II

    fleet_size_I = 600    # Total available buses of Type I
    fleet_size_II = 90    # Total available buses of Type II

    # Trip factor matrix T[i,j] representing the number of trips possible per route per shift
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

    # Proportion of total trips (P_i) assigned to each route, approximating relative importance
    P = [0.014, 0.012, 0.038, 0.010, 0.016, 0.040, 0.013, 0.007]

    # Demand matrix D[i,j] representing passenger demand per route per shift
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

    # Minimum number of trips required per shift, used in Constraint 5
    w = {7, 12, 8, 3}  # Corresponds to shift frequency requirements

    # --------------------------
    # Declare decision variables
    # --------------------------
    # x[i,j] = number of trips on route i during shift j using Bus Type I
    # y[i,j] = number of trips on route i during shift j using Bus Type II
    x = {}
    y = {}
    for i in range(n_routes):
        for j in range(n_shifts):
            x[i, j] = solver.NumVar(0, solver.infinity(), f"x_{i}_{j}")
            y[i, j] = solver.NumVar(0, solver.infinity(), f"y_{i}_{j}")

    # -----------------------------
    # Objective Function - Equation 1
    # -----------------------------
    # Minimize the total number of trips across all routes and shifts
    solver.Minimize(
        sum(x[i, j] + y[i, j] for i in range(n_routes) for j in range(n_shifts))
    )

    # --------------------------------------
    # Constraints to ensure model feasibility
    # --------------------------------------

    # Equation 2: Satisfy demand for each route and shift using total passenger capacity
    for i in range(n_routes):
        for j in range(n_shifts):
            solver.Add(
                x[i, j] * bus_capacity_I + y[i, j] * bus_capacity_II >= demand[i, j]
            )

    # Equation 3: Total Bus Type I trips across all routes and shifts must respect fleet capacity
    solver.Add(
        sum(x[i, j] for i in range(n_routes) for j in range(n_shifts)) <=
        sum(fleet_size_I * trip_factors[i, j] for i in range(n_routes) for j in range(n_shifts))
    )

    # Equation 4: Total Bus Type II trips must respect its fleet capacity
    solver.Add(
        sum(y[i, j] for i in range(n_routes) for j in range(n_shifts)) <=
        sum(fleet_size_II * trip_factors[i, j] for i in range(n_routes) for j in range(n_shifts))
    )

    # Equation 5: Ensure total number of trips respects shift-level minimum frequency requirement
    solver.Add(
        sum(x[i, j] + y[i, j] for i in range(n_routes) for j in range(n_shifts)) <= 93 * sum(w)
    )

    # Equation 6 & 7: Route-shift level capacity limits based on trip factors and proportions
    for i in range(n_routes):
        for j in range(n_shifts):
            solver.Add(x[i, j] <= trip_factors[i, j] * fleet_size_I * P[i])
            solver.Add(y[i, j] <= trip_factors[i, j] * fleet_size_II * P[i])

    # Equation 8: Ensure the total of all trip proportions (P_i) does not exceed 100%
    solver.Add(sum(P[i] for i in range(n_routes)) <= 1)

    # Equation 9: Ensure all trips are non-negative
    for i in range(n_routes):
        for j in range(n_shifts):
            solver.Add(x[i, j] >= 0)
            solver.Add(y[i, j] >= 0)

    # --------------------
    # Solve the LP model
    # --------------------
    status = solver.Solve()

    # ----------------------------------
    # Display results if solution exists
    # ----------------------------------
    if status == pywraplp.Solver.OPTIMAL:
        print("✅ Optimal solution found!")
        for i in range(n_routes):
            for j in range(n_shifts):
                print(f"Route {i + 1}, Shift {j + 1}:")
                print(f"  Bus Type I Trips (x): {round(x[i, j].solution_value(), 2)}")
                print(f"  Bus Type II Trips (y): {round(y[i, j].solution_value(), 2)}")
    else:
        print("❌ No optimal solution found.")

# Run the model
solve_route()
