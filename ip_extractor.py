#!/usr/bin/env python3

import os
import re
import csv
from ipaddress import ip_network
from typing import List, Set, Tuple

# Configuration variables
DIRECTORIES = [
    'pt-bdo-tp-qa/b2c-eshop-dev',
    'pt-bdo-tp-qa/b2c-eshop-qas',
    'pt-bdo-tp-prod/b2c-eshop-preprod',
    'pt-bdo-tp-prod/b2c-eshop-prod'
]

FILE_PREFIXES = ('deployment-jsdl-', 'ingress-jsdl-')
FILE_SUFFIX = '.yaml'

OUTPUT_FILE = 'unique_ip_addresses.csv'

IP_PATTERN = r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b'

def find_yaml_files(directories: List[str]) -> List[str]:
    """Find all YAML files in given directories matching the specified patterns."""
    yaml_files = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.startswith(FILE_PREFIXES) and file.endswith(FILE_SUFFIX):
                    yaml_files.append(os.path.join(root, file))
    return sorted(yaml_files)

def extract_ip_addresses(file_path: str) -> Set[str]:
    """Extract IP addresses from a given file."""
    with open(file_path, 'r') as file:
        content = file.read()
    return set(re.findall(IP_PATTERN, content))

def remove_duplicate_and_subset_ips(ip_addresses: Set[str]) -> Tuple[List[str], List[str]]:
    """Remove duplicate IP addresses, subsets, and overlapping networks."""
    networks = [ip_network(ip, strict=False) for ip in ip_addresses]
    networks.sort(key=lambda x: (x.num_addresses, x.network_address), reverse=True)
    
    unique_networks = []
    removed_networks = []
    
    for network in networks:
        is_unique = True
        for existing in unique_networks:
            if network.subnet_of(existing) or existing.subnet_of(network) or network.overlaps(existing):
                is_unique = False
                break
        
        if is_unique:
            unique_networks.append(network)
        else:
            removed_networks.append(network)
    
    return [str(net) for net in unique_networks], [str(net) for net in removed_networks]

def save_to_csv(ip_addresses: List[str], output_file: str):
    """Save IP addresses to a CSV file."""
    # Sort IP addresses
    sorted_ips = sorted(ip_addresses, key=lambda x: ip_network(x, strict=False))
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['IP Address/Range'])
        for ip in sorted_ips:
            writer.writerow([ip])

def main():
    """Main function to orchestrate the IP address extraction and deduplication process."""
    print("Step 1: Finding YAML files...")
    yaml_files = find_yaml_files(DIRECTORIES)
    print(f"Found {len(yaml_files)} YAML files.")

    print("\nStep 2: Extracting IP addresses...")
    all_ip_addresses = set()
    for file in yaml_files:
        ip_addresses = extract_ip_addresses(file)
        all_ip_addresses.update(ip_addresses)
        print(f"Extracted {len(ip_addresses)} IP addresses from {file}")

    print(f"\nTotal IP addresses extracted: {len(all_ip_addresses)}")

    print("\nStep 3: Removing duplicates, subsets, and overlapping networks...")
    unique_ip_addresses, removed_ips = remove_duplicate_and_subset_ips(all_ip_addresses)
    print(f"Unique IP addresses after removal: {len(unique_ip_addresses)}")
    print("Removed IP addresses:")
    for ip in removed_ips:
        print(f"  - {ip}")

    print(f"\nStep 4: Saving to {OUTPUT_FILE}...")
    save_to_csv(unique_ip_addresses, OUTPUT_FILE)
    print("Done!")

if __name__ == "__main__":
    main()
