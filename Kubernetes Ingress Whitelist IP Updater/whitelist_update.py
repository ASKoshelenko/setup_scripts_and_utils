#!/usr/bin/env python3
"""
Kubernetes Ingress Whitelist IP Updater

This script updates the whitelist-source-range in Kubernetes ingress configurations
for different environments. It allows adding specific IP addresses to the whitelist
while preserving the existing configuration and formatting.

Usage:
    ./whitelist_update.py --env [dev|stage|preprod|prod] [--files file1.yaml,file2.yaml]

Examples:
    # Update all default files in DEV environment
    ./whitelist_update.py --env dev

    # Update specific files in PROD environment
    ./whitelist_update.py --env prod --files "your-ingress-frontend.yaml,your-ingress-price-api-service.yaml"

Environment Configurations:
    - dev: Development environment (includes Dev and Sandbox IPs)
    - stage: Staging/QA environment
    - preprod: Pre-production environment
    - prod: Production environment

The script will:
1. Validate the environment and target files
2. Check for existing IP addresses to avoid duplicates
3. Update the whitelist while preserving file formatting
4. Provide detailed output of changes made

Author: ASKoshelenko
Version: 1.0.0
"""

import os
import argparse
from typing import List, Dict, Optional

# Environment configuration with paths and corresponding IPs
ENV_CONFIG: Dict[str, Dict[str, any]] = {
    'prod': {
        'path': 'relative-path/to-PROD-configuration',
        'ips': ['0.0.0.0', '1.1.1.1'],
        'description': {
            '0.0.0.0': 'Prod AKS outbound',
            '1.1.1.1': 'PRO360 VPN'
        }
    },
    'preprod': {
        'path': 'relative-path/to-PREPROD-configuration',
        'ips': ['0.0.0.0', '1.1.1.1'],
        'description': {
            '0.0.0.0': 'Prod AKS outbound',
            '1.1.1.1': 'PRO360 VPN'
        }
    },
    'stage': {
        'path': 'relative-path/to-STAGE-configuration',
        'ips': ['2.2.2.2', '1.1.1.1'],
        'description': {
            '2.2.2.2': 'Review AKS outbound',
            '1.1.1.1': 'PRO360 VPN'
        }
    },
    'dev': {
        'path': 'relative-path/to-DEV-configuration',
        'ips': ['3.3.3.3', '4.4.4.4', '1.1.1.1'],
        'description': {
            '3.3.3.3': 'Dev AKS outbound',
            '4.4.4.4': 'Sandbox AKS outbound',
            '1.1.1.1': 'PRO360 VPN'
        }
    }
}

# Default files to process if none specified
DEFAULT_FILES: List[str] = [
    'your-ingress-frontend-pro360.yaml',
    'your-ingress-frontend.yaml',
    'your-ingress-price-api-service.yaml',
    'your-ingress-stock-service.yaml',
    'your-ingress-tax-service.yaml'
]

def update_whitelist(file_path: str, new_ips: List[str], ip_descriptions: Dict[str, str]) -> bool:
    """
    Update the whitelist-source-range in a Kubernetes ingress configuration file.

    Args:
        file_path (str): Path to the ingress YAML file
        new_ips (List[str]): List of IP addresses to add to the whitelist
        ip_descriptions (Dict[str, str]): Descriptions for the IP addresses

    Returns:
        bool: True if update was successful, False otherwise

    Example:
        >>> update_whitelist('ingress.yaml', ['1.2.3.4'], {'1.2.3.4': 'Test IP'})
        True
    """
    try:
        # Read the file
        with open(file_path, 'r') as file:
            lines = file.readlines()

        modified = False
        # Process each line
        for i, line in enumerate(lines):
            if 'nginx.ingress.kubernetes.io/whitelist-source-range' in line:
                # Extract current IPs
                start = line.find('"') + 1
                end = line.rfind('"')
                if start > 0 and end > 0:
                    current_ips = line[start:end].split(',')
                    
                    # Add new IPs if they don't exist
                    added = []
                    for new_ip in new_ips:
                        if new_ip not in current_ips:
                            current_ips.append(new_ip)
                            added.append(new_ip)
                            modified = True
                    
                    if added:
                        # Preserve line formatting
                        prefix = line[:start]
                        suffix = line[end:]
                        
                        # Update the line
                        new_line = prefix + ','.join(current_ips) + suffix
                        lines[i] = new_line
                        
                        # Print added IPs with descriptions
                        for ip in added:
                            desc = ip_descriptions.get(ip, 'No description')
                            print(f"Added IP: {ip} ({desc})")
                    else:
                        print("All IPs already present")

        # Write updates back to file
        if modified:
            with open(file_path, 'w') as file:
                file.writelines(lines)

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

    return True

def main():
    """
    Main function to handle command line arguments and orchestrate the update process.
    
    Parses command line arguments, validates input, and executes the whitelist update
    for the specified environment and files.
    """
    parser = argparse.ArgumentParser(
        description='Update whitelist IPs in Kubernetes ingress configurations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--env',
        required=True,
        choices=['dev', 'stage', 'preprod', 'prod'],
        help='Target environment for the update'
    )
    parser.add_argument(
        '--files',
        help='Comma-separated list of files to process (optional, uses defaults if not specified)'
    )
    
    args = parser.parse_args()
    
    # Get environment configuration
    env_config = ENV_CONFIG[args.env]
    env_path = env_config['path']
    new_ips = env_config['ips']
    ip_descriptions = env_config['description']
    
    # Determine target files
    target_files = args.files.split(',') if args.files else DEFAULT_FILES
    
    # Print execution summary
    print("\n=== Whitelist Update Configuration ===")
    print(f"Environment: {args.env.upper()}")
    print(f"Working directory: {env_path}")
    print("\nTarget IPs:")
    for ip in new_ips:
        print(f"  • {ip} ({ip_descriptions[ip]})")
    print("\nTarget files:")
    for file in target_files:
        print(f"  • {file}")
    print("\n=== Starting Update Process ===")
    
    # Process each file
    success_count = 0
    for file_name in target_files:
        file_path = os.path.join(env_path, file_name)
        if os.path.exists(file_path):
            print(f"\nProcessing: {file_name}")
            if update_whitelist(file_path, new_ips, ip_descriptions):
                success_count += 1
                print(f"✓ Successfully updated {file_name}")
        else:
            print(f"× File not found: {file_path}")

    # Print summary
    print("\n=== Update Summary ===")
    print(f"Files processed: {len(target_files)}")
    print(f"Successfully updated: {success_count}")
    print(f"Failed/Skipped: {len(target_files) - success_count}")

if __name__ == "__main__":
    main()