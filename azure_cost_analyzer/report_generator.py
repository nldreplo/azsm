"""
Module for generating reports and displaying results.
"""

from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .utils import format_currency, format_percentage

console = Console()

class ReportGenerator:
    """Generator for reports and displays."""
    
    def __init__(self, debug: bool = False):
        """Initialize the report generator.
        
        Args:
            debug: Whether to show debug information
        """
        self.debug = debug
        self.currency = "USD"  # Default currency

    def display_savings_table(self, cost_data: Dict[str, Any]) -> None:
        """Display a table showing current costs and potential savings."""
        console.print("\n[bold blue]Cost Analysis Results[/bold blue]")
        
        # Get currency from cost_data
        self.currency = cost_data.get("currency", "USD")
        
        # Debug: Print disk data
        if self.debug:
            console.print("\n[bold yellow]Debug: Currency:[/bold yellow]", self.currency)
            if "detailed" in cost_data and "disks" in cost_data["detailed"]:
                console.print(f"Number of disks in detailed data: {len(cost_data['detailed']['disks'])}")
                for disk in cost_data["detailed"]["disks"]:
                    console.print(f"Disk: {disk['name']}, SKU: {disk['sku']}, Cost: {disk['current_monthly_cost']}")
            else:
                console.print("No disk data found in cost_data['detailed']")
        
        # Current Cost Panel
        current_cost_panel = Panel(
            f"Current Monthly Cost: {format_currency(cost_data['current_monthly_cost'], self.currency)}",
            title="Current Cost",
            style="bold cyan"
        )
        console.print(current_cost_panel)
        
        # Savings Options Tables
        self._display_consumption_options_table(cost_data)
        self._display_commitment_options_table(cost_data)
        
        # VM details table
        if cost_data["detailed"]["virtual_machines"]:
            self._display_vm_details_table(cost_data["detailed"]["virtual_machines"])
        
        # Disk details table
        if cost_data["detailed"]["disks"]:
            self._display_disk_details_table(cost_data["detailed"]["disks"])
    
    def _display_consumption_options_table(self, cost_data: Dict[str, Any]) -> None:
        """Display a table with flexible consumption pricing options."""
        table = Table(title="Flexible Consumption Options")
        table.add_column("Option", style="cyan")
        table.add_column("Monthly Cost", style="green", justify="right")
        table.add_column("Monthly Savings", style="magenta", justify="right")
        table.add_column("Savings %", style="yellow", justify="right")
        
        # Current cost (baseline)
        table.add_row(
            "Pay-as-you-go",
            format_currency(cost_data['current_monthly_cost'], self.currency),
            "-",
            "-"
        )
        
        # Spot instances
        savings = cost_data['current_monthly_cost'] - cost_data['spot_monthly_cost']
        table.add_row(
            "Spot Instances [dim](variable availability)[/dim]",
            format_currency(cost_data['spot_monthly_cost'], self.currency),
            format_currency(savings, self.currency),
            format_percentage(cost_data['savings_spot_percent'])
        )
        
        # Low priority
        savings = cost_data['current_monthly_cost'] - cost_data['low_priority_monthly_cost']
        table.add_row(
            "Low Priority VMs [dim](can be evicted)[/dim]",
            format_currency(cost_data['low_priority_monthly_cost'], self.currency),
            format_currency(savings, self.currency),
            format_percentage(cost_data['savings_low_priority_percent'])
        )
        
        console.print()
        console.print(table)
    
    def _display_commitment_options_table(self, cost_data: Dict[str, Any]) -> None:
        """Display a table with commitment-based pricing options."""
        table = Table(title="Commitment-Based Options")
        table.add_column("Option", style="cyan")
        table.add_column("Monthly Cost", style="green", justify="right")
        table.add_column("Monthly Savings", style="magenta", justify="right")
        table.add_column("Savings %", style="yellow", justify="right")
        
        # Savings Plan options
        savings_1yr = cost_data['current_monthly_cost'] - cost_data['savings_plan_1yr_monthly_cost']
        savings_3yr = cost_data['current_monthly_cost'] - cost_data['savings_plan_3yr_monthly_cost']
        
        table.add_row(
            "Savings Plan (1 Year)",
            format_currency(cost_data['savings_plan_1yr_monthly_cost'], self.currency),
            format_currency(savings_1yr, self.currency),
            format_percentage(cost_data['savings_plan_1yr_percent'])
        )
        
        table.add_row(
            "Savings Plan (3 Years)",
            format_currency(cost_data['savings_plan_3yr_monthly_cost'], self.currency),
            format_currency(savings_3yr, self.currency),
            format_percentage(cost_data['savings_plan_3yr_percent'])
        )
        
        # Add hybrid benefit options if applicable
        if cost_data['hybrid_monthly_cost'] > 0:
            hybrid_savings = cost_data['current_monthly_cost'] - cost_data['hybrid_monthly_cost']
            hybrid_1yr_savings = cost_data['current_monthly_cost'] - cost_data['hybrid_savings_plan_1yr']
            hybrid_3yr_savings = cost_data['current_monthly_cost'] - cost_data['hybrid_savings_plan_3yr']
            
            table.add_row(
                "Azure Hybrid Benefit",
                format_currency(cost_data['hybrid_monthly_cost'], self.currency),
                format_currency(hybrid_savings, self.currency),
                format_percentage(cost_data['hybrid_savings_percent'])
            )
            
            table.add_row(
                "Hybrid + Savings Plan (1 Year)",
                format_currency(cost_data['hybrid_savings_plan_1yr'], self.currency),
                format_currency(hybrid_1yr_savings, self.currency),
                format_percentage(cost_data['hybrid_savings_plan_1yr_percent'])
            )
            
            table.add_row(
                "Hybrid + Savings Plan (3 Years)",
                format_currency(cost_data['hybrid_savings_plan_3yr'], self.currency),
                format_currency(hybrid_3yr_savings, self.currency),
                format_percentage(cost_data['hybrid_savings_plan_3yr_percent'])
            )
        
        console.print()
        console.print(table)
    
    def _display_vm_details_table(self, vm_details: List[Dict[str, Any]]) -> None:
        """Display a table with VM cost details."""
        table = Table(title="\nVirtual Machine Details")
        
        # Add columns
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Size", style="blue")
        table.add_column("OS", style="blue")
        table.add_column("Region", style="blue")
        table.add_column("Current", justify="right", style="green")
        table.add_column("Spot", justify="right", style="green")
        table.add_column("Low Priority", justify="right", style="green")
        table.add_column("1Y Plan", justify="right", style="green")
        table.add_column("3Y Plan", justify="right", style="green")
        
        # Add rows
        for vm in vm_details:
            table.add_row(
                vm["name"],
                vm["size"],
                vm["os_type"],
                vm["region"],
                format_currency(vm["current_monthly_cost"], self.currency),
                format_currency(vm["spot_monthly_cost"], self.currency),
                format_currency(vm["low_priority_monthly_cost"], self.currency),
                format_currency(vm["savings_plan_1yr_monthly_cost"], self.currency),
                format_currency(vm["savings_plan_3yr_monthly_cost"], self.currency)
            )
        
        console.print(table)
    
    def _display_disk_details_table(self, disk_details: List[Dict[str, Any]]) -> None:
        """Display a table with disk cost details."""
        table = Table(title="\nManaged Disk Details")
        
        # Add columns
        table.add_column("Name", style="cyan")
        table.add_column("SKU", style="blue")
        table.add_column("Tier", style="blue")
        table.add_column("Size (GB)", justify="right", style="blue")
        table.add_column("Region", style="blue")
        table.add_column("Current Cost", justify="right", style="green")
        table.add_column("Reserved Cost", justify="right", style="green")
        table.add_column("Reserved Savings", justify="right", style="magenta")
        table.add_column("Alternative Options", style="yellow")
        
        # Add rows
        for disk in disk_details:
            # Calculate reserved instance savings
            current_cost = disk["current_monthly_cost"]
            
            # Handle reservation eligibility
            if disk.get("reservation_eligible", False) and disk.get("reserved_monthly_cost"):
                reserved_cost = disk["reserved_monthly_cost"]
                reserved_savings = disk["savings"]
                reserved_savings_text = format_currency(reserved_savings, self.currency)
                reserved_cost_text = format_currency(reserved_cost, self.currency)
            else:
                reserved_cost_text = "N/A"
                reserved_savings_text = "N/A"
            
            # Format alternative options text
            alt_options = []
            if disk.get("alternative_tiers"):
                for alt in disk["alternative_tiers"]:
                    alt_text = (
                        f"{alt['type'].replace('_LRS', '')}"
                        f" ({alt['tier_name']}): "
                        f"{format_currency(alt['cost'], self.currency)} "
                        f"[dim]Save: {format_currency(alt['savings'], self.currency)} "
                        f"({format_percentage(alt['savings_percent'])})[/dim]"
                    )
                    alt_options.append(alt_text)
            alt_options_text = "\n".join(alt_options) if alt_options else ""
            
            table.add_row(
                disk["name"],
                disk["sku"] or "Unknown",
                disk.get("tier_name", "N/A"),
                str(disk["size_gb"]),
                disk["region"],
                format_currency(current_cost, self.currency),
                reserved_cost_text,
                reserved_savings_text,
                alt_options_text
            )
        
        console.print(table)
