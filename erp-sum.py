import os
import csv
import argparse
import matplotlib.pyplot as plt

def parse_log_file(file_path):
    initial_coil_length = None
    final_coil_length = None
    total_component_length = 0.0
    total_waste = 0.0

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 14:
                try:
                    current_coil_length = float(row[5])
                    if initial_coil_length is None:
                        initial_coil_length = current_coil_length
                    final_coil_length = current_coil_length
                    total_component_length += float(row[11]) / 1000
                    total_waste += float(row[12]) / 1000
                except ValueError:
                    continue

    if initial_coil_length is not None and final_coil_length is not None:
        coil_length_decrease = initial_coil_length - final_coil_length
    else:
        coil_length_decrease = 0.0

    return coil_length_decrease, total_component_length, total_waste

def summarize_logs(directory):
    total_coil_length_decrease = 0.0
    total_component_length = 0.0
    total_waste = 0.0

    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            coil_length_decrease, component_length, waste = parse_log_file(file_path)
            total_coil_length_decrease += coil_length_decrease
            total_component_length += component_length
            total_waste += waste

    return total_coil_length_decrease, total_component_length, total_waste

def create_graph(coil_decrease, component_length, waste):
    labels = ['Coil Length Decrease', 'Component Length', 'Waste']
    values = [coil_decrease, component_length, waste]

    plt.figure(figsize=(10, 6))
    plt.plot(labels, values, marker='o')
    plt.title('Summary of Coil Usage')
    plt.ylabel('Length (meters)')
    plt.grid(True, linestyle='--', alpha=0.7)

    for i, v in enumerate(values):
        plt.text(i, v, f'{v:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('coil_usage_summary.png')
    plt.close()

def main(directory):
    total_coil_length_decrease, total_component_length, total_waste = summarize_logs(directory)

    print(f"Total Coil Length Decrease: {total_coil_length_decrease:.3f} meters")
    print(f"Total Component Length: {total_component_length:.3f} meters")
    print(f"Total Waste: {total_waste:.3f} meters")
    print(f"Total Component Length + Waste: {total_component_length + total_waste:.3f} meters")

    create_graph(total_coil_length_decrease, total_component_length, total_waste)
    print("Graph saved as 'coil_usage_summary.png'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process log files to summarize coil length decrease, component length, and waste.')
    parser.add_argument('directory', type=str, help='The directory containing the log files')
    args = parser.parse_args()
    main(args.directory)