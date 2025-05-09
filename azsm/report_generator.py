"""
Module for generating reports and displaying results.
"""

import os
import csv
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

    def export_to_csv(self, cost_data: Dict[str, Any], output_path: str) -> None:
        """Export cost data to a CSV file.
        
        Args:
            cost_data: Cost data to export
            output_path: Path to save the CSV file
        """
        self.currency = cost_data.get("currency", "USD")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Write summary section
            summary_writer = csv.writer(csvfile)
            summary_writer.writerow(['Azure Save Money (azsm) - Cost Analysis Results'])
            summary_writer.writerow([])
            summary_writer.writerow(['Current Monthly Cost', format_currency(cost_data['current_monthly_cost'], self.currency)])
            summary_writer.writerow([])
            
            # Write flexible consumption options
            summary_writer.writerow(['Flexible Consumption Options'])
            summary_writer.writerow(['Option', 'Monthly Cost', 'Monthly Savings', 'Savings %'])
            summary_writer.writerow([
                'Pay-as-you-go', 
                format_currency(cost_data['current_monthly_cost'], self.currency),
                '-',
                '-'
            ])
            summary_writer.writerow([
                'Spot Instances (variable availability)', 
                format_currency(cost_data['spot_monthly_cost'], self.currency),
                format_currency(cost_data['current_monthly_cost'] - cost_data['spot_monthly_cost'], self.currency),
                format_percentage(cost_data['savings_spot_percent'])
            ])
            summary_writer.writerow([
                'Low Priority VMs (can be evicted)', 
                format_currency(cost_data['low_priority_monthly_cost'], self.currency),
                format_currency(cost_data['current_monthly_cost'] - cost_data['low_priority_monthly_cost'], self.currency),
                format_percentage(cost_data['savings_low_priority_percent'])
            ])
            summary_writer.writerow([])
            
            # Write commitment-based options
            summary_writer.writerow(['Commitment-Based Options'])
            summary_writer.writerow(['Option', 'Monthly Cost', 'Monthly Savings', 'Savings %'])
            summary_writer.writerow([
                'Savings Plan (1 Year)', 
                format_currency(cost_data['savings_plan_1yr_monthly_cost'], self.currency),
                format_currency(cost_data['current_monthly_cost'] - cost_data['savings_plan_1yr_monthly_cost'], self.currency),
                format_percentage(cost_data['savings_plan_1yr_percent'])
            ])
            summary_writer.writerow([
                'Savings Plan (3 Years)', 
                format_currency(cost_data['savings_plan_3yr_monthly_cost'], self.currency),
                format_currency(cost_data['current_monthly_cost'] - cost_data['savings_plan_3yr_monthly_cost'], self.currency),
                format_percentage(cost_data['savings_plan_3yr_percent'])
            ])
            
            # Add hybrid benefit options if applicable
            if cost_data['hybrid_monthly_cost'] > 0:
                summary_writer.writerow([
                    'Azure Hybrid Benefit', 
                    format_currency(cost_data['hybrid_monthly_cost'], self.currency),
                    format_currency(cost_data['current_monthly_cost'] - cost_data['hybrid_monthly_cost'], self.currency),
                    format_percentage(cost_data['hybrid_savings_percent'])
                ])
                summary_writer.writerow([
                    'Hybrid + Savings Plan (1 Year)', 
                    format_currency(cost_data['hybrid_savings_plan_1yr'], self.currency),
                    format_currency(cost_data['current_monthly_cost'] - cost_data['hybrid_savings_plan_1yr'], self.currency),
                    format_percentage(cost_data['hybrid_savings_plan_1yr_percent'])
                ])
                summary_writer.writerow([
                    'Hybrid + Savings Plan (3 Years)', 
                    format_currency(cost_data['hybrid_savings_plan_3yr'], self.currency),
                    format_currency(cost_data['current_monthly_cost'] - cost_data['hybrid_savings_plan_3yr'], self.currency),
                    format_percentage(cost_data['hybrid_savings_plan_3yr_percent'])
                ])
            
            summary_writer.writerow([])
            
            # Write VM details
            if cost_data["detailed"]["virtual_machines"]:
                summary_writer.writerow(['Virtual Machine Details'])
                summary_writer.writerow([
                    'Name', 'Size', 'OS', 'Region', 'Current', 'Spot', 
                    'Low Priority', '1Y Plan', '3Y Plan'
                ])
                
                for vm in cost_data["detailed"]["virtual_machines"]:
                    summary_writer.writerow([
                        vm["name"],
                        vm["size"],
                        vm["os_type"],
                        vm["region"],
                        format_currency(vm["current_monthly_cost"], self.currency),
                        format_currency(vm["spot_monthly_cost"], self.currency),
                        format_currency(vm["low_priority_monthly_cost"], self.currency),
                        format_currency(vm["savings_plan_1yr_monthly_cost"], self.currency),
                        format_currency(vm["savings_plan_3yr_monthly_cost"], self.currency)
                    ])
                
                summary_writer.writerow([])
            
            # Write disk details
            if cost_data["detailed"]["disks"]:
                summary_writer.writerow(['Managed Disk Details'])
                summary_writer.writerow([
                    'Name', 'SKU', 'Tier', 'Size (GB)', 'Region', 'Current Cost',
                    'Reserved Cost', 'Reserved Savings', 'Alternative Options'
                ])
                
                for disk in cost_data["detailed"]["disks"]:
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
                                f"{alt['type'].replace('_LRS', '')} ({alt['tier_name']}): "
                                f"{format_currency(alt['cost'], self.currency)} "
                                f"Save: {format_currency(alt['savings'], self.currency)} "
                                f"({format_percentage(alt['savings_percent'])})"
                            )
                            alt_options.append(alt_text)
                    alt_options_text = ", ".join(alt_options) if alt_options else ""
                    
                    summary_writer.writerow([
                        disk["name"],
                        disk["sku"] or "Unknown",
                        disk.get("tier_name", "N/A"),
                        str(disk["size_gb"]),
                        disk["region"],
                        format_currency(disk["current_monthly_cost"], self.currency),
                        reserved_cost_text,
                        reserved_savings_text,
                        alt_options_text
                    ])

    def export_to_html(self, cost_data: Dict[str, Any], output_path: str) -> None:
        """Export cost data to an HTML file with sortable tables.
        
        Args:
            cost_data: Cost data to export
            output_path: Path to save the HTML file
        """
        self.currency = cost_data.get("currency", "USD")
        
        # CSS for styling
        css = """
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
                line-height: 1.5;
            }
            h1 {
                color: #0078d4;
                margin: 20px 0;
            }
            h2 {
                color: #0078d4;
                margin: 20px 0 10px 0;
            }
            .panel {
                background-color: #f0f8ff;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 20px;
                display: inline-block;
            }
            .panel-title {
                color: #0078d4;
                font-weight: bold;
                margin-bottom: 5px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
                box-shadow: 0 2px 3px rgba(0,0,0,0.1);
            }
            thead {
                background-color: #0078d4;
                color: white;
            }
            th {
                padding: 12px 15px;
                text-align: left;
                cursor: pointer;
                position: relative;
            }
            th:after {
                content: '';
                margin-left: 5px;
                display: inline-block;
            }
            th.sort-asc:after {
                content: '▲';
            }
            th.sort-desc:after {
                content: '▼';
            }
            td {
                padding: 8px 15px;
                border-bottom: 1px solid #ddd;
            }
            tr:nth-child(even) {
                background-color: #f5f5f5;
            }
            tr:hover {
                background-color: #e6f2ff;
            }
            .cost-value {
                text-align: right;
            }
            .savings-value {
                text-align: right;
                color: #287733;
            }
            .banner {
                color: #0078d4;
                font-weight: bold;
                margin-bottom: 30px;
                text-align: center;
                font-size: 24px;
            }
            .footnote {
                color: #999;
                font-size: 0.8em;
                margin-top: 20px;
            }
        </style>
        """
        
        # JavaScript for table sorting
        sorting_script = """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const tables = document.querySelectorAll('table');
                tables.forEach(table => {
                    const headerCells = table.querySelectorAll('th');
                    headerCells.forEach((th, i) => {
                        th.addEventListener('click', function() {
                            sortTable(table, i, th);
                        });
                    });
                });
            });

            function sortTable(table, colNum, th) {
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const headerCells = Array.from(table.querySelectorAll('th'));
                
                // Reset sort indicators
                headerCells.forEach(cell => {
                    cell.classList.remove('sort-asc', 'sort-desc');
                });

                // Determine sort direction
                const isAscending = !th.classList.contains('sort-asc');
                th.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
                
                // Sort the rows
                rows.sort((a, b) => {
                    let aValue = a.cells[colNum].textContent.trim();
                    let bValue = b.cells[colNum].textContent.trim();
                    
                    // Handle currency values by removing symbols
                    if (aValue.match(/[$€£¥]/)) {
                        aValue = aValue.replace(/[$€£¥,]/g, '');
                        bValue = bValue.replace(/[$€£¥,]/g, '');
                        return isAscending ? 
                            parseFloat(aValue) - parseFloat(bValue) : 
                            parseFloat(bValue) - parseFloat(aValue);
                    }
                    
                    // Handle percentage values
                    if (aValue.endsWith('%')) {
                        aValue = parseFloat(aValue.replace('%', ''));
                        bValue = parseFloat(bValue.replace('%', ''));
                        return isAscending ? aValue - bValue : bValue - aValue;
                    }
                    
                    // Handle N/A values
                    if (aValue === 'N/A') return isAscending ? 1 : -1;
                    if (bValue === 'N/A') return isAscending ? -1 : 1;
                    
                    // Try to convert to numbers
                    const aNum = parseFloat(aValue);
                    const bNum = parseFloat(bValue);
                    
                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        return isAscending ? aNum - bNum : bNum - aNum;
                    }
                    
                    // Default string comparison
                    return isAscending ? 
                        aValue.localeCompare(bValue) : 
                        bValue.localeCompare(aValue);
                });
                
                // Remove existing rows and append in new order
                rows.forEach(row => tbody.appendChild(row));
            }
        </script>
        """
        
        # Start building HTML content
        html_content = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Azure Save Money (azsm) - Cost Analysis</title>
            {css}
        </head>
        <body>
            <div class="banner">Azure Save Money (azsm) - Cost Analysis Results</div>
            
            <div class="panel">
                <div class="panel-title">Current Monthly Cost</div>
                <div>{format_currency(cost_data['current_monthly_cost'], self.currency)}</div>
            </div>
            
            <h2>Flexible Consumption Options</h2>
            <table>
                <thead>
                    <tr>
                        <th>Option</th>
                        <th>Monthly Cost</th>
                        <th>Monthly Savings</th>
                        <th>Savings %</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Pay-as-you-go</td>
                        <td class="cost-value">{format_currency(cost_data['current_monthly_cost'], self.currency)}</td>
                        <td class="savings-value">-</td>
                        <td>-</td>
                    </tr>
                    <tr>
                        <td>Spot Instances (variable availability)</td>
                        <td class="cost-value">{format_currency(cost_data['spot_monthly_cost'], self.currency)}</td>
                        <td class="savings-value">{format_currency(cost_data['current_monthly_cost'] - cost_data['spot_monthly_cost'], self.currency)}</td>
                        <td>{format_percentage(cost_data['savings_spot_percent'])}</td>
                    </tr>
                    <tr>
                        <td>Low Priority VMs (can be evicted)</td>
                        <td class="cost-value">{format_currency(cost_data['low_priority_monthly_cost'], self.currency)}</td>
                        <td class="savings-value">{format_currency(cost_data['current_monthly_cost'] - cost_data['low_priority_monthly_cost'], self.currency)}</td>
                        <td>{format_percentage(cost_data['savings_low_priority_percent'])}</td>
                    </tr>
                </tbody>
            </table>
            
            <h2>Commitment-Based Options</h2>
            <table>
                <thead>
                    <tr>
                        <th>Option</th>
                        <th>Monthly Cost</th>
                        <th>Monthly Savings</th>
                        <th>Savings %</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Savings Plan (1 Year)</td>
                        <td class="cost-value">{format_currency(cost_data['savings_plan_1yr_monthly_cost'], self.currency)}</td>
                        <td class="savings-value">{format_currency(cost_data['current_monthly_cost'] - cost_data['savings_plan_1yr_monthly_cost'], self.currency)}</td>
                        <td>{format_percentage(cost_data['savings_plan_1yr_percent'])}</td>
                    </tr>
                    <tr>
                        <td>Savings Plan (3 Years)</td>
                        <td class="cost-value">{format_currency(cost_data['savings_plan_3yr_monthly_cost'], self.currency)}</td>
                        <td class="savings-value">{format_currency(cost_data['current_monthly_cost'] - cost_data['savings_plan_3yr_monthly_cost'], self.currency)}</td>
                        <td>{format_percentage(cost_data['savings_plan_3yr_percent'])}</td>
                    </tr>
        """
        
        # Add hybrid benefit options if applicable
        if cost_data['hybrid_monthly_cost'] > 0:
            html_content += f"""
                    <tr>
                        <td>Azure Hybrid Benefit</td>
                        <td class="cost-value">{format_currency(cost_data['hybrid_monthly_cost'], self.currency)}</td>
                        <td class="savings-value">{format_currency(cost_data['current_monthly_cost'] - cost_data['hybrid_monthly_cost'], self.currency)}</td>
                        <td>{format_percentage(cost_data['hybrid_savings_percent'])}</td>
                    </tr>
                    <tr>
                        <td>Hybrid + Savings Plan (1 Year)</td>
                        <td class="cost-value">{format_currency(cost_data['hybrid_savings_plan_1yr'], self.currency)}</td>
                        <td class="savings-value">{format_currency(cost_data['current_monthly_cost'] - cost_data['hybrid_savings_plan_1yr'], self.currency)}</td>
                        <td>{format_percentage(cost_data['hybrid_savings_plan_1yr_percent'])}</td>
                    </tr>
                    <tr>
                        <td>Hybrid + Savings Plan (3 Years)</td>
                        <td class="cost-value">{format_currency(cost_data['hybrid_savings_plan_3yr'], self.currency)}</td>
                        <td class="savings-value">{format_currency(cost_data['current_monthly_cost'] - cost_data['hybrid_savings_plan_3yr'], self.currency)}</td>
                        <td>{format_percentage(cost_data['hybrid_savings_plan_3yr_percent'])}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        """
        
        # Add VM details table if data exists
        if cost_data["detailed"]["virtual_machines"]:
            html_content += """
            <h2>Virtual Machine Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Size</th>
                        <th>OS</th>
                        <th>Region</th>
                        <th>Current</th>
                        <th>Spot</th>
                        <th>Low Priority</th>
                        <th>1Y Plan</th>
                        <th>3Y Plan</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for vm in cost_data["detailed"]["virtual_machines"]:
                html_content += f"""
                    <tr>
                        <td>{vm["name"]}</td>
                        <td>{vm["size"]}</td>
                        <td>{vm["os_type"]}</td>
                        <td>{vm["region"]}</td>
                        <td class="cost-value">{format_currency(vm["current_monthly_cost"], self.currency)}</td>
                        <td class="cost-value">{format_currency(vm["spot_monthly_cost"], self.currency)}</td>
                        <td class="cost-value">{format_currency(vm["low_priority_monthly_cost"], self.currency)}</td>
                        <td class="cost-value">{format_currency(vm["savings_plan_1yr_monthly_cost"], self.currency)}</td>
                        <td class="cost-value">{format_currency(vm["savings_plan_3yr_monthly_cost"], self.currency)}</td>
                    </tr>
                """
            
            html_content += """
                </tbody>
            </table>
            """
        
        # Add disk details table if data exists
        if cost_data["detailed"]["disks"]:
            html_content += """
            <h2>Managed Disk Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>SKU</th>
                        <th>Tier</th>
                        <th>Size (GB)</th>
                        <th>Region</th>
                        <th>Current Cost</th>
                        <th>Reserved Cost</th>
                        <th>Reserved Savings</th>
                        <th>Alternative Options</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for disk in cost_data["detailed"]["disks"]:
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
                            f"{alt['type'].replace('_LRS', '')} ({alt['tier_name']}): "
                            f"{format_currency(alt['cost'], self.currency)} "
                            f"Save: {format_currency(alt['savings'], self.currency)} "
                            f"({format_percentage(alt['savings_percent'])})"
                        )
                        alt_options.append(alt_text)
                alt_options_text = "<br>".join(alt_options) if alt_options else ""
                
                html_content += f"""
                    <tr>
                        <td>{disk["name"]}</td>
                        <td>{disk["sku"] or "Unknown"}</td>
                        <td>{disk.get("tier_name", "N/A")}</td>
                        <td>{disk["size_gb"]}</td>
                        <td>{disk["region"]}</td>
                        <td class="cost-value">{format_currency(disk["current_monthly_cost"], self.currency)}</td>
                        <td class="cost-value">{reserved_cost_text}</td>
                        <td class="savings-value">{reserved_savings_text}</td>
                        <td>{alt_options_text}</td>
                    </tr>
                """
            
            html_content += """
                </tbody>
            </table>
            """
        
        # Complete the HTML document
        html_content += f"""
            <div class="footnote">Generated by Azure Save Money (azsm)</div>
            {sorting_script}
        </body>
        </html>
        """
        
        # Write the HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
