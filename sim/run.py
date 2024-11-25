import os
import sys
import traci
import csv
from datetime import datetime
import numpy as np
from collections import defaultdict

# Add SUMO_HOME to path if not already there
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare SUMO_HOME environment variable")

class AutonomousVehicle:
    def __init__(self, vehicle_id):
        self.vehicle_id = vehicle_id
        traci.vehicle.setType(self.vehicle_id, "autonomous_passenger")

    def perform_behavior(self):
        # Implement specific behaviors for autonomous vehicles
        pass

class MixedTrafficSimulation:
    def __init__(self, config_file, av_penetration_rate):
        self.config_file = config_file
        self.av_penetration_rate = av_penetration_rate
        self.metrics = defaultdict(list)
        self.adaptation_count = 0  # Track infrastructure adaptations
        self.emergency_brake_threshold = -7.5  # Threshold acceleration for emergency braking
        self.autonomous_vehicles = set()
        # Initialize emergency braking counters
        self.metrics["emergency_braking_total"] = 0
        self.metrics["emergency_braking_av"] = 0
        self.metrics["emergency_braking_human"] = 0

    def start_simulation(self):
        # Start SUMO with TraCI
        sumo_cmd = ["sumo", "-c", self.config_file]
        traci.start(sumo_cmd)

    def setup_vehicle_types(self):
        # Ensure autonomous vehicle type is defined
        # Assuming 'autonomous_passenger' is defined in vtypes.add.xml
        pass  # No action needed if vehicle types are correctly defined

    def adapt_traffic_lights(self):
        """Dynamic traffic light adaptation based on current traffic conditions"""
        for tls_id in traci.trafficlight.getIDList():
            waiting_time = self._get_total_waiting_time(tls_id)
            if waiting_time > 120:  # Threshold for adaptation
                self._optimize_traffic_light(tls_id)

    def _get_total_waiting_time(self, tls_id):
        """Calculate total waiting time for vehicles at a traffic light"""
        total_waiting_time = 0
        for lane_id in traci.trafficlight.getControlledLanes(tls_id):
            vehicles = traci.lane.getLastStepVehicleIDs(lane_id)
            for veh_id in vehicles:
                total_waiting_time += traci.vehicle.getWaitingTime(veh_id)
        return total_waiting_time

    def _optimize_traffic_light(self, tls_id):
        """Simple traffic light optimization logic"""
        current_phase = traci.trafficlight.getPhase(tls_id)
        traci.trafficlight.setPhaseDuration(tls_id, 10)  # Extend green time
        self.adaptation_count += 1  # Increment adaptation count

    def detect_emergency_braking(self):
        """Detect emergency braking events and log them."""
        vehicles = traci.vehicle.getIDList()
        for veh_id in vehicles:
            accel = traci.vehicle.getAcceleration(veh_id)
            if accel <= self.emergency_brake_threshold:
                if veh_id in self.autonomous_vehicles:
                    veh_type = 'Autonomous Vehicle'
                    self.metrics["emergency_braking_av"] += 1
                else:
                    veh_type = 'Human-Driven Vehicle'
                    self.metrics["emergency_braking_human"] += 1
                self.metrics["emergency_braking_total"] += 1
                print(f"Emergency braking detected: Vehicle ID {veh_id} ({veh_type}) at time {traci.simulation.getTime()}")

    def collect_metrics(self):
        """Collect basic metrics like number of stops and fuel consumption"""
        vehicles = traci.vehicle.getIDList()
        if not vehicles:
            self.metrics["number_of_stops"].append(0)
            self.metrics["fuel_consumption"].append(0)
            self.metrics["mean_speed"].append(0)
            return

        stops = sum(1 for v in vehicles if traci.vehicle.getStopState(v))
        fuel_consumption = sum(traci.vehicle.getFuelConsumption(v) for v in vehicles)
        speeds = [traci.vehicle.getSpeed(v) for v in vehicles]

        self.metrics["number_of_stops"].append(stops)
        self.metrics["fuel_consumption"].append(fuel_consumption)
        self.metrics["mean_speed"].append(sum(speeds) / len(vehicles))  # Fixed mean speed calculation

    def collect_additional_metrics(self):
        """Collect additional metrics like average travel time, traffic flow rate, and congestion levels"""
        vehicles = traci.vehicle.getIDList()
        if not vehicles:
            self.metrics["average_travel_time"].append(0)
            self.metrics["traffic_flow_rate"].append(0)
            self.metrics["congestion_levels"].append(0)
            return

        # Average travel time
        travel_times = [traci.vehicle.getAccumulatedWaitingTime(v) for v in vehicles]
        average_travel_time = sum(travel_times) / len(travel_times)
        self.metrics["average_travel_time"].append(average_travel_time)

        # Traffic flow rate
        traffic_flow_rate = len(vehicles) / max(1, traci.simulation.getTime())  # Prevent division by zero
        self.metrics["traffic_flow_rate"].append(traffic_flow_rate)

        # Congestion levels (e.g., number of vehicles with speed < threshold)
        congestion_threshold = 5  # Speed threshold for congestion
        congested_vehicles = sum(1 for v in vehicles if traci.vehicle.getSpeed(v) < congestion_threshold)
        self.metrics["congestion_levels"].append(congested_vehicles)

    def run(self, steps=3600):
        """Main simulation loop"""
        self.start_simulation()
        self.setup_vehicle_types()

        step = 0
        while step < steps:
            traci.simulationStep()

            # Convert some new vehicles to autonomous vehicles
            for vehicle_id in traci.simulation.getDepartedIDList():
                if np.random.random() < self.av_penetration_rate:
                    av = AutonomousVehicle(vehicle_id)
                    self.autonomous_vehicles.add(vehicle_id)
                    av.perform_behavior()

            # Adapt infrastructure periodically
            if step % 30 == 0:  # Check every 30 simulation steps
                self.adapt_traffic_lights()

            # Collect metrics at each step
            self.collect_metrics()
            self.collect_additional_metrics()
            self.detect_emergency_braking()

            step += 1

        traci.close()
        # Store total number of adaptations
        self.metrics["adaptation_frequency"] = self.adaptation_count
        return self.metrics

    def analyze_results(self, all_metrics):
        """Analyze and visualize the collected metrics"""
        import matplotlib.pyplot as plt

        metrics_to_analyze = [
            ('number_of_stops', 'Number of Stops'),
            ('fuel_consumption', 'Fuel Consumption'),
            ('mean_speed', 'Mean Speed (m/s)'),
            ('average_travel_time', 'Average Travel Time (s)'),
            ('traffic_flow_rate', 'Traffic Flow Rate (vehicles/s)'),
            ('congestion_levels', 'Congested Vehicles Count')
        ]

        # Create output directory for plots
        output_dir = "../results/plots"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for metric, ylabel in metrics_to_analyze:
            plt.figure(figsize=(10, 6))
            for rate in sorted(all_metrics.keys()):
                values = all_metrics[rate][metric]
                plt.plot(values, label=f'AV Rate {int(rate*100)}%')

            plt.xlabel('Simulation Step')
            plt.ylabel(ylabel)
            plt.title(f'{ylabel} Over Time')
            plt.legend()
            plt.grid(True)

            plt.savefig(os.path.join(output_dir, f"{metric}_{timestamp}.png"))
            plt.close()

    def save_metrics_to_csv(self, all_metrics, output_dir="../results"):
        """Save metrics in a structured format"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"simulation_metrics_{timestamp}.csv")

        metrics_to_analyze = [
            ('number_of_stops', 'Number of Stops'),
            ('fuel_consumption', 'Fuel Consumption'),
            ('mean_speed', 'Mean Speed (m/s)'),
            ('average_travel_time', 'Average Travel Time (s)'),
            ('traffic_flow_rate', 'Traffic Flow Rate (vehicles/s)'),
            ('congestion_levels', 'Congested Vehicles Count')
        ]

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(['Mixed Traffic Simulation Results'])
            writer.writerow(['Timestamp:', timestamp])
            writer.writerow([])

            # Metrics statistics
            for metric, metric_name in metrics_to_analyze:
                writer.writerow([f'\n{metric_name} Statistics'])
                writer.writerow(['AV Rate (%)', 'Average', 'Maximum', 'Minimum', 'Final Value'])

                for rate in sorted(all_metrics.keys()):
                    values = all_metrics[rate][metric]
                    writer.writerow([
                        int(rate*100),
                        f'{np.mean(values):.2f}',
                        f'{np.max(values):.2f}',
                        f'{np.min(values):.2f}',
                        f'{values[-1]:.2f}'
                    ])
                writer.writerow([])

            # Infrastructure adaptations
            writer.writerow(['\nInfrastructure Adaptations'])
            writer.writerow(['AV Rate (%)', 'Total Adaptations'])
            for rate in sorted(all_metrics.keys()):
                writer.writerow([
                    int(rate*100),
                    all_metrics[rate]['adaptation_frequency']
                ])

            # Emergency braking statistics
            writer.writerow(['\nEmergency Braking Statistics'])
            writer.writerow(['AV Rate (%)', 'Total Emergency Brakings', 'AV Emergency Brakings', 'Human-Driven Emergency Brakings'])
            for rate in sorted(all_metrics.keys()):
                writer.writerow([
                    int(rate*100),
                    all_metrics[rate]['emergency_braking_total'],
                    all_metrics[rate]['emergency_braking_av'],
                    all_metrics[rate]['emergency_braking_human']
                ])

def main():
    # av_rates = [0.0, 0.25, 0.5, 0.75, 1.0]  # Full range
    av_rates = [0.0, 0.5, 1.0]  # Reduced for faster execution
    all_metrics = {}

    for rate in av_rates:
        print(f"Running simulation with AV penetration rate: {rate*100}%")
        sim = MixedTrafficSimulation(
            config_file="due.actuated.sumocfg",
            av_penetration_rate=rate
        )
        metrics = sim.run()
        all_metrics[rate] = metrics
        print(f"Simulation completed for AV rate: {rate*100}%")

    sim.save_metrics_to_csv(all_metrics)
    sim.analyze_results(all_metrics)

if __name__ == "__main__":
    main()
