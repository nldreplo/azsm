"""
Main entry point for Azure Save Money (azsm).
"""

import argparse
import sys
from rich.console import Console

from azsm.analyzer import AzureCostAnalyzer
from azsm.pricing_client import PricingClient

console = Console()

def main():
    """Main entrypoint function."""
    parser = argparse.ArgumentParser(description="Azure Save Money | azsm")
    parser.add_argument("--subscription-id", "-s", help="Azure subscription ID")
    parser.add_argument("--output", "-o", default="azure_resources.json", 
                        help="Output file for resources data (default: azure_resources.json)")
    parser.add_argument("--debug", action="store_true", 
                        help="Enable debug mode to print API queries and responses")
    parser.add_argument("--currency", default="EUR", choices=list(PricingClient.SUPPORTED_CURRENCIES.keys()),
                        help="Currency for pricing (default: EUR)")
    parser.add_argument("--format", choices=["console", "csv", "html"], default="console",
                        help="Output format: console (default), csv, or html")
    parser.add_argument("--format-output", default=None,
                        help="File to save the formatted output (required for csv and html formats)")
    
    args = parser.parse_args()
    
    # Validate format arguments
    if args.format in ["csv", "html"] and not args.format_output:
        console.print("[bold red]Error:[/bold red] --format-output is required when using --format=csv or --format=html")
        sys.exit(1)
    
    try:
        analyzer = AzureCostAnalyzer(
            subscription_id=args.subscription_id,
            output_file=args.output,
            debug=args.debug,
            currency=args.currency,
            output_format=args.format,
            format_output_path=args.format_output
        )
        success = analyzer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if args.debug:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
