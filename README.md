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
python -m azsm --subscription-id <subscription-id> --output resources.json --currency EUR --debug
```

### Options

- `--subscription-id`, `-s`: Azure subscription ID (optional, uses default if not specified)
- `--output`, `-o`: Output file for resource data (default: azure_resources.json)
- `--currency`: Currency for pricing (default: USD)
- `--debug`: Enable debug mode to print API queries and responses

## Authentication

The tool uses you context from the Azure CLI. Ensure you are logged in using:

```bash
az login
```

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

## Disk Size Reference

### Premium SSD Sizes (P-series)

| Disk Type | Disk Size (GiB) |
|-----------|----------------|
| P1        | 4              |
| P2        | 8              |
| P3        | 16             |
| P4        | 32             |
| P6        | 64             |
| P10       | 128            |
| P15       | 256            |
| P20       | 512            |
| P30       | 1,024          |
| P40       | 2,048          |
| P50       | 4,096          |
| P60       | 8,192          |
| P70       | 16,384         |
| P80       | 32,767         |

### Standard SSD Sizes (E-series)

| Disk Type | Disk Size (GiB) |
|-----------|----------------|
| E1        | 4              |
| E2        | 8              |
| E3        | 16             |
| E4        | 32             |
| E6        | 64             |
| E10       | 128            |
| E15       | 256            |
| E20       | 512            |
| E30       | 1,024          |
| E40       | 2,048          |
| E50       | 4,096          |
| E60       | 8,192          |
| E70       | 16,384         |
| E80       | 32,767         |

### Standard Disk Types (S-series)

| Disk Type | Disk Size (GiB) |
|-----------|----------------|
| S4        | 32             |
| S6        | 64             |
| S10       | 128            |
| S15       | 256            |
| S20       | 512            |
| S30       | 1,024          |
| S40       | 2,048          |
| S50       | 4,096          |
| S60       | 8,192          |
| S70       | 16,384         |
| S80       | 32,767         |

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
Garantie tot de deur