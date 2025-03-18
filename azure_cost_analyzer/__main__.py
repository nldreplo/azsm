"""
Main entry point for Azure Save Money | azsm.
"""

import argparse
import sys
from rich.console import Console

from azure_cost_analyzer.analyzer import AzureCostAnalyzer

console = Console()

def main():
    """Main entrypoint function."""
    parser = argparse.ArgumentParser(description="Azure Save Money | azsm")
    parser.add_argument("--subscription-id", "-s", help="Azure subscription ID")
    parser.add_argument("--output", "-o", default="azure_resources.json", 
                        help="Output file for resources data (default: azure_resources.json)")
    parser.add_argument("--debug", action="store_true", 
                        help="Enable debug mode to print API queries and responses")
    
    args = parser.parse_args()
    
    try:
        analyzer = AzureCostAnalyzer(
            subscription_id=args.subscription_id,
            output_file=args.output,
            debug=args.debug
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
