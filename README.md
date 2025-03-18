# Azure Save Money (azsm)

A Python tool for analyzing Azure resources and identifying cost-saving opportunities.

## Features

- 🔍 Analyzes VMs and managed disks across your Azure subscription
- 💰 Calculates potential savings using:
  - Spot instances
  - Low-priority VMs
  - Azure Savings Plans (1-year and 3-year terms)
  - Azure Hybrid Benefit
  - Alternative disk tiers
- 📊 Provides detailed cost breakdowns
- 💵 Supports multiple currencies
- 📋 Exports resource data to JSON for further analysis

## Installation

```bash
git clone https://github.com/yourusername/azsm.git
cd azsm
pip install -e .
```

## Prerequisites

- Python 3.8+
- Azure subscription
- Azure CLI (logged in) or environment variables for authentication

## Usage

Basic usage:
```bash
python -m azsm
```

With options:
```bash
python -m azsm --subscription-id <subscription-id> --output resources.json --debug
```

### Options

- `--subscription-id`, `-s`: Azure subscription ID (optional, uses default if not specified)
- `--output`, `-o`: Output file for resource data (default: azure_resources.json)
- `--debug`: Enable debug mode to print API queries and responses

## Authentication

The tool uses DefaultAzureCredential for authentication, which tries these methods in order:
1. Environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
2. Azure CLI credentials
3. Managed Identity
4. Visual Studio Code credentials

## Example Output

```
Cost Analysis Results
╭──────────────────────────────────────╮
│ Current Monthly Cost: $1,234.56      │
╰──────────────────────────────────────╯

Flexible Consumption Options
┌─────────────────────┬──────────────┬────────────────┬────────────┐
│ Option              │ Monthly Cost │ Monthly Savings│ Savings %  │
├─────────────────────┼──────────────┼────────────────┼────────────┤
│ Pay-as-you-go       │ $1,234.56    │ -             │ -          │
│ Spot Instances      │ $370.37      │ $864.19       │ 70.00%     │
│ Low Priority VMs    │ $493.82      │ $740.74       │ 60.00%     │
└─────────────────────┴──────────────┴────────────────┴────────────┘

Commitment-Based Options
┌─────────────────────┬──────────────┬────────────────┬────────────┐
│ Option              │ Monthly Cost │ Monthly Savings│ Savings %  │
├─────────────────────┼──────────────┼────────────────┼────────────┤
│ Savings Plan (1 Yr) │ $987.65      │ $246.91       │ 20.00%     │
│ Savings Plan (3 Yr) │ $864.19      │ $370.37       │ 30.00%     │
└─────────────────────┴──────────────┴────────────────┴────────────┘
```

## Supported Currencies

- USD (US Dollar)
- EUR (Euro)
- GBP (British Pound)
- AUD (Australian Dollar)
- CAD (Canadian Dollar)
- And many more...

## Development

### Project Structure

```
azsm/
├── __init__.py
├── __main__.py
├── analyzer.py        # Main orchestration
├── cost_calculator.py # Cost calculations
├── pricing_client.py  # Azure pricing API client
├── report_generator.py# Output formatting
├── resource_collector.py # Azure resource collection
└── utils.py          # Helper functions
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Disclaimer

This tool is not officially associated with Microsoft Azure. Always verify pricing calculations and recommendations against the official Azure pricing calculator and documentation.
Garantie tot aan de deur.