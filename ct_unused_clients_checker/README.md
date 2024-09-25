# Commercetools Unused API Clients Script

This script identifies and reports unused API clients in Commercetools projects. It can process multiple projects defined in the environment variables and generate reports for each project.

## Requirements

- Python 3.6+
- pip (Python package installer)

## Installation

1. Clone this repository or download the script files.

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

3. Copy the `.env.example` file to `.env` and fill in your Commercetools credentials:

   ```
   cp .env.example .env
   ```

   Then edit the `.env` file with your actual credentials for each project.

## Usage

Run the script using Python:

```
python commercetools_unused_clients_script.py [project_key]
```

If `project_key` is not provided, the script will process all available projects defined in the `PROJECTS` dictionary within the script.

Available project keys are: 'dev', 'stage', 'preprod', 'prod', 'diy'.

Example:
```
python commercetools_unused_clients_script.py dev
```

## Output

The script generates two types of output:

1. Log file: `commercetools_api_client_check.log`
2. Report file: `unused_api_clients_report_{project}.txt` for each processed project

## Environment Variables

For each project, the following environment variables should be set in the `.env` file:

```
{PROJECT_PREFIX}_CTP_PROJECT_KEY
{PROJECT_PREFIX}_CTP_CLIENT_SECRET
{PROJECT_PREFIX}_CTP_CLIENT_ID
{PROJECT_PREFIX}_CTP_AUTH_URL
{PROJECT_PREFIX}_CTP_API_URL
{PROJECT_PREFIX}_CTP_SCOPES
```

Where `{PROJECT_PREFIX}` is one of the keys defined in the `PROJECTS` dictionary in the script.

## Security Considerations

1. Protect your `.env` file:
   - Never commit the `.env` file to version control
   - Restrict file permissions: `chmod 600 .env`
   - Consider using a secrets management system for production environments

2. Secure the log and report files:
   - Restrict access to the directory containing these files
   - Regularly rotate and archive old log files

3. Use least-privilege principles when setting up Commercetools API clients for this script

4. Regularly audit who has access to run this script and review its outputs

## Customization

You can modify the `DAYS_THRESHOLD` constant in the script to change the number of days after which a client is considered unused.

## Troubleshooting

If you encounter any issues, please check the log file `commercetools_api_client_check.log` for error messages and details.
