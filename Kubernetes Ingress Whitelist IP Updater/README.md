# Kubernetes Ingress Whitelist IP Updater

A Python script for managing IP whitelists in Kubernetes Ingress configurations across different environments. This tool allows for safe and controlled updates to `whitelist-source-range` in ingress configurations while preserving existing settings and file formatting.

## Features

- Support for multiple environments (DEV, STAGE, PREPROD, PROD)
- Environment-specific IP configurations
- Selective file processing
- Preservation of existing IP addresses
- Detailed execution logging
- No external dependencies

## Prerequisites

- Python 3.6 or higher
- Access to Kubernetes ingress configuration files

## Installation

1. Clone the repository or download the script:
```bash
git clone <repository-url>
# or
wget <script-url>/whitelist_update.py
```

2. Make the script executable:
```bash
chmod +x whitelist_update.py
```

## Usage

### Basic Command Structure

```bash
./whitelist_update.py --env <environment> [--files file1.yaml,file2.yaml]
```

### Parameters

- `--env`: Required. Specifies the target environment
  - Allowed values: `dev`, `stage`, `preprod`, `prod`
- `--files`: Optional. Comma-separated list of files to process
  - If not specified, uses default file list

### Default Files

If no files are specified, the script processes these files:
```
- your-ingress-frontend-pro360.yaml
- your-ingress-frontend.yaml
- your-ingress-price-api-service.yaml
- your-ingress-stock-service.yaml
- your-ingress-tax-service.yaml
```

### Environment-Specific IP Configurations

Each environment has its predefined set of IPs:

#### Production (prod)
- 0.0.0.0 (Description)
- 1.1.1.1 (Description)

#### Pre-Production (preprod)
- 3.3.3.3 (Description)
- 4.4.4.4 (Description)

#### Staging (stage)
- 5.5.5.5 (Description)
- 6.6.6.6 (Description)

#### Development (dev)
- 7.7.7.7 (Description)
- 8.8.8.8 (Description)
- 9.9.9.9 (Description)

### Examples

1. Update all default files in DEV environment:
```bash
./whitelist_update.py --env dev
```

2. Update specific files in PROD environment:
```bash
./whitelist_update.py --env prod --files "your-ingress-frontend.yaml,your-ingress-price-api-service.yaml"
```

3. Update single file in STAGE environment:
```bash
./whitelist_update.py --env stage --files your-ingress-frontend.yaml
```


## Output Example

```
=== Whitelist Update Configuration ===
Environment: DEV
Working directory: pt-bdo-tp-qa/b2c-eshop-dev

Target IPs:
  • 4.180.46.227 (Dev AKS outbound)
  • 108.142.221.81 (Sandbox AKS outbound)
  • 20.103.137.206 (PRO360 VPN)

Target files:
  • your-ingress-frontend.yaml
  • your-ingress-price-api-service.yaml

=== Starting Update Process ===
Processing: your-ingress-frontend.yaml
Added IP: 3.3.3.3 (Dev AKS outbound)
✓ Successfully updated your-ingress-frontend.yaml

=== Update Summary ===
Files processed: 2
Successfully updated: 2
Failed/Skipped: 0
```

## Error Handling

The script includes error handling for common scenarios:
- File not found
- Permission issues
- Invalid file format
- Invalid IP addresses

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

Free to use. Have fun

## Authors

ASKoshelenko 

## Version History

- 1.0.0
  - Initial Release
  - Basic functionality for updating whitelist IPs
  - Support for all environments
  - File selection support