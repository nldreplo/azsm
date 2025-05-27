#!/usr/bin/env python3
"""
Azure Save Money | azsm - A CLI tool to analyze Azure resources and calculate potential cost savings.
"""

import argparse
import sys
from azsm.analyzer import AzureCostAnalyzer
from azsm.pricing_client import PricingClient

def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(description="Azure Save Money | azsm - A tool to analyze Azure resources and calculate potential cost savings")
    
    parser.add_argument("-s", "--subscription-id", 
                        help="Azure subscription ID (uses current context if not provided)")
    
    parser.add_argument("-o", "--output", default="azure_resources.json",
                        help="Output JSON file path (default: azure_resources.json)")
    
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode to print API queries and responses")
    
    parser.add_argument("--currency", default="EUR", choices=list(PricingClient.SUPPORTED_CURRENCIES.keys()),
                        help="Currency for pricing (default: EUR)")
    
    args = parser.parse_args()
    
    analyzer = AzureCostAnalyzer(
        subscription_id=args.subscription_id, 
        output_file=args.output,
        debug=args.debug,
        currency=args.currency
    )
    analyzer.run()
    
if __name__ == "__main__":
    main()
