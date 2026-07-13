import matplotlib.pyplot as plt
import numpy as np
import pybamm


NUMBER_OF_AGING_CYCLES = 20
PARAMETER_SET = "OKane2022"


options = {
    # SEI growth on the original particle surface
    "SEI": "solvent-diffusion limited",
    "SEI porosity change": "true", # SEI occupies pore volume

    # Lithium plating
    "lithium plating": "partially reversible",
    # Plated lithium occupies pore volume
    "lithium plating porosity change": "true",

    # Particle swelling and cracking
    # First entry  -> negative electrode
    # Second entry -> positive electrode
    "particle mechanics": (
        "swelling and cracking",
        "swelling only",
    ),

    # SEI can grow on newly created crack surfaces
    "SEI on cracks": "true",

    # Stress and cracking can deactivate active material
    "loss of active material": "stress-driven",
}

model = pybamm.lithium_ion.DFN(options=options,
    name="Coupled degradation DFN",
)

parameter_values = pybamm.ParameterValues(PARAMETER_SET)


# Increase particle mesh resolution

var_pts = {
    "x_n": 5, 
    "x_s": 5, 
    "x_p": 5,
    # Cracking can require a finer particle mesh
    "r_n": 30,
    "r_p": 30,
}


# Define the cycling experiment

initial_capacity_check = [
    "Hold at 4.2 V until C/100",
    "Rest for 4 hours",
    "Discharge at 0.1C until 2.5 V",
    "Charge at 0.3C until 4.2 V",
    "Hold at 4.2 V until C/100",
]


aging_cycle = (
    "Discharge at 1C until 2.5 V",
    "Charge at 0.3C until 4.2 V",
    "Hold at 4.2 V until C/100",
)


final_capacity_check = [
    "Discharge at 0.1C until 2.5 V",
]


experiment = pybamm.Experiment(
    initial_capacity_check
    + [aging_cycle] * NUMBER_OF_AGING_CYCLES
    + final_capacity_check,
    period="60 seconds",
)

solver = pybamm.IDAKLUSolver()
simulation = pybamm.Simulation(
    model=model,
    parameter_values=parameter_values,
    experiment=experiment,
    solver=solver,
    var_pts=var_pts,
)

print("Solving coupled degradation model...")

solution = simulation.solve(
    calc_esoh=False,
    showprogress=False,
)

print("Simulation completed successfully.")

# Extract the common x-axis
throughput_capacity_ah = solution[
    "Throughput capacity [A.h]"].entries
time_h = (solution["Time [s]"].entries/ 3600)

# SEI-related capacity losses
capacity_loss_sei_ah = solution[
    "Loss of capacity to negative SEI [A.h]"].entries
capacity_loss_sei_cracks_ah = solution[
    "Loss of capacity to negative SEI on cracks [A.h]"].entries

# Lithium-plating capacity loss
capacity_loss_plating_ah = solution[
    "Loss of capacity to negative lithium plating [A.h]"].entries

# Total loss caused by side reactions
total_side_reaction_loss_ah = solution[
    "Total capacity lost to side reactions [A.h]"].entries

# Degradation modes
lli_percent = solution[
    "Loss of lithium inventory [%]"].entries
lam_negative_percent = solution[
    "Loss of active material in negative electrode [%]"].entries
lam_positive_percent = solution[
    "Loss of active material in positive electrode [%]"].entries

# Porosity
negative_porosity = solution[
    "X-averaged negative electrode porosity"].entries
positive_porosity = solution[
    "X-averaged positive electrode porosity"].entries

# Particle crack lengths
negative_crack_length_m = solution[
    "X-averaged negative particle crack length [m]"].entries
positive_crack_length_m = solution[
    "X-averaged positive particle crack length [m]"].entries


# Convert crack length from m to micrometers
negative_crack_length_um = (negative_crack_length_m * 1e6)
positive_crack_length_um = (positive_crack_length_m * 1e6)


# Helper for spatial mechanical variables

def convert_to_time_series(entries, number_of_time_points):
    """
    Average a spatial PyBaMM variable over all spatial axes.
    The function keeps the axis corresponding to time.
    """

    values = np.asarray(entries)

    if values.ndim == 1:
        return values

    for axis, axis_size in enumerate(values.shape):

        if axis_size == number_of_time_points:

            spatial_axes = tuple(
                index
                for index in range(values.ndim)
                if index != axis
            )

            return np.mean(
                values,
                axis=spatial_axes,
            )

    raise ValueError(
        "Could not identify the time axis."
    )


# Swelling-related mechanical response

negative_surface_stress_raw = solution[
    "Negative particle surface tangential stress [Pa]"
    ].entries

negative_surface_stress_pa = convert_to_time_series(
    negative_surface_stress_raw,
    number_of_time_points=len(time_h),
)

negative_surface_stress_mpa = (
    negative_surface_stress_pa / 1e6
)

# Plot capacity-loss contributions

plt.figure(figsize=(9, 5))

plt.plot(
    throughput_capacity_ah,
    capacity_loss_sei_ah,
    label="SEI",
)

plt.plot(
    throughput_capacity_ah,
    capacity_loss_sei_cracks_ah,
    label="SEI on cracks",
)

plt.plot(
    throughput_capacity_ah,
    capacity_loss_plating_ah,
    label="Lithium plating",
)

plt.plot(
    throughput_capacity_ah,
    total_side_reaction_loss_ah,
    linestyle="--",
    label="All side reactions",
)

plt.xlabel("Throughput capacity [A.h]")
plt.ylabel("Capacity loss [A.h]")

plt.title(
    "Contributions of degradation mechanisms"
)

plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# Plot degradation modes

plt.figure(figsize=(9, 5))

plt.plot(
    throughput_capacity_ah,
    lli_percent,
    label="LLI",
)

plt.plot(
    throughput_capacity_ah,
    lam_negative_percent,
    label="LAM negative",
)

plt.plot(
    throughput_capacity_ah,
    lam_positive_percent,
    label="LAM positive",
)

plt.xlabel("Throughput capacity [A.h]")
plt.ylabel("Degradation mode [%]")

plt.title(
    "Loss of lithium inventory and active material"
)

plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# Plot porosity evolution

plt.figure(figsize=(9, 5))

plt.plot(
    throughput_capacity_ah,
    negative_porosity,
    label="Negative electrode",
)

plt.plot(
    throughput_capacity_ah,
    positive_porosity,
    label="Positive electrode",
)

plt.xlabel("Throughput capacity [A.h]")
plt.ylabel("Electrode porosity")
plt.title("Porosity evolution")

plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# Plot crack growth

plt.figure(figsize=(9, 5))

plt.plot(
    throughput_capacity_ah,
    negative_crack_length_um,
    label="Negative particle crack",
)

plt.plot(
    throughput_capacity_ah,
    positive_crack_length_um,
    label="Positive particle crack",
)

plt.xlabel("Throughput capacity [A.h]")
plt.ylabel("Crack length [micrometer]")

plt.title("Particle crack growth")

plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# Plot swelling-induced mechanical stress

plt.figure(figsize=(9, 5))

plt.plot(
    time_h,
    negative_surface_stress_mpa,
)

plt.xlabel("Time [h]")
plt.ylabel(
    "Average negative-particle "
    "surface tangential stress [MPa]"
)

plt.title(
    "Mechanical response caused by particle swelling"
)

plt.grid(True)
plt.tight_layout()
plt.show()