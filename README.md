# Mixed Traffic Simulation with Autonomous Vehicles

A traffic simulation framework built on SUMO (Simulation of Urban MObility) to study the impact of autonomous vehicles in mixed traffic conditions.

## Features

- Variable autonomous vehicle penetration rates (0-100%)
- Dynamic traffic light adaptation
- Comprehensive metrics collection:
  - Average travel time
  - Traffic flow rate
  - Congestion levels
  - Fuel consumption
  - Vehicle stops
- Automated result analysis and visualization
- CSV export of simulation metrics

## Installation

1. Install SUMO traffic simulator
2. Set the SUMO_HOME environment variable
3. Create and activate python env
4. Install Python dependencies:
```
pip install -r requirements.txt

```

## Usage

Run the simulation:
```
cd sim && python run.py

```

## Simulation Details

The simulation uses the Luxembourg SUMO Traffic (LuST) Scenario as its base network and traffic patterns. It implements autonomous vehicle behavior and infrastructure adaptation strategies to study mixed traffic dynamics.

## Disclaimer

This simulation is a research prototype and has not been peer-reviewed. The results and predictions may not accurately reflect real-world autonomous vehicle behavior or traffic patterns. Use for research and experimental purposes only.

## References
L. Codeca, R. Frank, and T. Engel, "Luxembourg SUMO Traffic (LuST) Scenario: 24 Hours of Mobility for Vehicular Networking Research" in Proceedings of the 7th IEEE Vehicular Networking Conference (VNC15), December 2015.
https://github.com/lcodeca/LuSTScenario

## Acknowledgments

- Based on the LuST Scenario developed by Lara Codecá et al.
- Built using SUMO (Simulation of Urban MObility) framework
