"""
Main analyzer module that orchestrates the Azure Save Money (azsm) functionality.
"""

import sys
from typing import Dict, Any, Optional, List
from rich.console import Console

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient

from .resource_collector import ResourceCollector
from .pricing_client import PricingClient
from .cost_calculator import CostCalculator
from .report_generator import ReportGenerator
from .utils import display_banner

console = Console()

class AzureCostAnalyzer:
    """Main class for Azure Save Money | azsm functionality."""
    
    def __init__(self, subscription_id: Optional[str] = None, output_file: str = "azure_resources.json", 
                 debug: bool = False, currency: str = "USD", output_format: str = "console",
                 format_output_path: Optional[str] = None):
        """Initialize the Azure Save Money | azsm.
        
        Args:
            subscription_id: Azure subscription ID (optional, will use current context if not provided)
            output_file: Path to the output JSON file
            debug: Enable debug mode to print API queries
            currency: Currency code for pricing (default: USD)
            output_format: Output format (console, csv, or html)
            format_output_path: Path to save the formatted output file (for csv and html formats)
        """
        self.credential = DefaultAzureCredential()
        self.subscription_id = subscription_id
        self.output_file = output_file
        self.resources_data = {}
        self.pricing_data = {}
        self.debug = debug
        self.currency = currency
        self.output_format = output_format
        self.format_output_path = format_output_path
        
        # If no subscription ID provided, get it from current context
        if not self.subscription_id:
            self._get_default_subscription()
            
        # Initialize our components
        self.resource_collector = ResourceCollector(self.credential, self.subscription_id)
        self.pricing_client = PricingClient(debug=self.debug, currency=self.currency)
        self.cost_calculator = CostCalculator()
        self.report_generator = ReportGenerator()
    
    def _get_default_subscription(self):
        """Get the default subscription ID from the current context."""
        subscription_client = SubscriptionClient(self.credential)
        subscriptions = list(subscription_client.subscriptions.list())
        if not subscriptions:
            console.print("[bold red]Error:[/bold red] No Azure subscriptions found in current context.")
            sys.exit(1)
        self.subscription_id = subscriptions[0].subscription_id
        console.print(f"Using subscription: [bold]{subscriptions[0].display_name}[/bold] ({self.subscription_id})")
    
    def run(self) -> None:
        """Run the Azure Save Money | azsm."""
        try:
            # Display banner
            display_banner()
            
            # 1. Gather resource data
            self.resources_data = self.resource_collector.collect_resources()
            self.resource_collector.save_data(self.resources_data, self.output_file)
            
            # 2. Get pricing data
            self.pricing_data = self.pricing_client.get_pricing_data(self.resources_data)
            
            # 3. Calculate costs and savings
            cost_data = self.cost_calculator.calculate_costs(self.resources_data, self.pricing_data)
            # Add currency to cost data
            cost_data["currency"] = self.currency
            
            # 4. Display results
            if self.output_format == "console":
                self.report_generator.display_savings_table(cost_data)
            elif self.output_format == "csv":
                self.report_generator.export_to_csv(cost_data, self.format_output_path)
                console.print(f"[bold green]CSV report saved to:[/bold green] {self.format_output_path}")
            elif self.output_format == "html":
                self.report_generator.export_to_html(cost_data, self.format_output_path)
                console.print(f"[bold green]HTML report saved to:[/bold green] {self.format_output_path}")
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return False
