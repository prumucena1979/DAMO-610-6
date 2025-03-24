from ortools.linear_solver import pywraplp
import random

def create_bus_scheduling_model_with_slack():
    # Create a solver instance using Google's OR-Tools with the SCIP backend
    solver = pywraplp.Solver.CreateSolver('SCIP')

    num_routes = 93     # Number of city routes
    num_shifts = 4      # Number of shifts per day

    # Generate synthetic passenger demand per route
    D = {i: random.randint(2000, 12000) for i in range(1, num_routes + 1)}

    # Define how the daily demand is split across the four shifts
    demand_proportions = {1: 0.4, 2: 0.2, 3: 0.35, 4: 0.05}

    # Calculate demand per route and shift (D_ij)
    D_ij = {(i, j): round(D[i] * demand_proportions[j]) for i in D for j in demand_proportions}

    # Create synthetic trip factors for each route and shift (e.g., how long trips take)
    T = {(i, j): random.randint(1, 12) for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)}

    # Assume uniform route proportions for simplicity (since historical data is incomplete)
    Pi = {i: 1 / num_routes for i in range(1, num_routes + 1)}

    # Minimum number of trips required per shift
    w = {1: 7, 2: 12, 3: 8, 4: 3}

    # Decision variables:
    # x, y, z = number of trips for each bus type
    # s = slack variable: unmet demand (we want to minimize this)
    x, y, z, s = {}, {}, {}, {}
    for i in range(1, num_routes + 1):
        for j in range(1, num_shifts + 1):
            x[i, j] = solver.NumVar(0, solver.infinity(), f'x_{i}_{j}')  # Bus type I (60 passengers)
            y[i, j] = solver.NumVar(0, solver.infinity(), f'y_{i}_{j}')  # Bus type II (90 passengers)
            z[i, j] = solver.NumVar(0, solver.infinity(), f'z_{i}_{j}')  # Bus type III (120 passengers)
            s[i, j] = solver.NumVar(0, solver.infinity(), f'slack_{i}_{j}')  # Slack (unserved demand)

    # Objective function:
    # Minimize total number of trips + penalty for unmet demand
    lambda_penalty = 10  # Penalty factor for each unit of unmet demand
    solver.Minimize(
        sum(x[i, j] + y[i, j] + z[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)) +
        lambda_penalty * sum(s[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1))
    )

    # Constraint: Meet demand (or track shortfall using slack)
    for i in range(1, num_routes + 1):
        for j in range(1, num_shifts + 1):
            solver.Add(60 * x[i, j] + 90 * y[i, j] + 120 * z[i, j] + s[i, j] >= D_ij[i, j])

    # Constraint: Fleet capacity limits
    solver.Add(sum(x[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)) <=
               sum(600 * T[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)))
    solver.Add(sum(y[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)) <=
               sum(90 * T[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)))
    solver.Add(sum(z[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)) <=
               sum(10 * T[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)))

    # Constraint: Limit on total trips in the system
    solver.Add(sum(x[i, j] + y[i, j] + z[i, j] for i in range(1, num_routes + 1) for j in range(1, num_shifts + 1)) <=
               num_routes * sum(w.values()))

    # Constraint: Cap trips per route/shift based on capacity and historical proportions
    for i in range(1, num_routes + 1):
        for j in range(1, num_shifts + 1):
            solver.Add(x[i, j] <= 600 * Pi[i] * T[i, j])
            solver.Add(y[i, j] <= 90 * Pi[i] * T[i, j])
            solver.Add(z[i, j] <= 10 * Pi[i] * T[i, j])

    return solver, x, y, z, s, num_routes, num_shifts

# Run the model
solver, x, y, z, s, num_routes, num_shifts = create_bus_scheduling_model_with_slack()
status = solver.Solve()

# Display results
if status == pywraplp.Solver.OPTIMAL:
    print("✅ Optimal solution found!\n")
    for i in range(1, num_routes + 1):
        for j in range(1, num_shifts + 1):
            print(f"Route {i}, Shift {j}: Type I = {x[i, j].solution_value():.0f}, "
                  f"Type II = {y[i, j].solution_value():.0f}, Type III = {z[i, j].solution_value():.0f}, "
                  f"Slack = {s[i, j].solution_value():.0f}")
else:
    print("❌ No optimal solution found.")
