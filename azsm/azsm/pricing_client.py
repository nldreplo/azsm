"""
Module for retrieving pricing information from Azure Price Calculator API.
"""

import requests
import json
import urllib.parse
from typing import Dict, Any, List
from rich.console import Console
from azsm.utils import DiskMapper, PREMIUM_DISK_SIZES, STANDARD_SSD_SIZES, STANDARD_HDD_SIZES
from .utils import format_currency  # Add this import at the top

console = Console()

class PricingClient:
    """Client for Azure Pricing API."""
    
    SUPPORTED_CURRENCIES = {
        "AUD": "Australian Dollar",
        "BRL": "Brazilian Real",
        "GBP": "British Pound",
        "CAD": "Canadian Dollar",
        "CNY": "Chinese Yuan",
        "DKK": "Danish Krone",
        "EUR": "Euro",
        "INR": "Indian Rupee",
        "JPY": "Japanese Yen",
        "KRW": "Korean Won",
        "NZD": "New Zealand Dollar",
        "NOK": "Norwegian Krone",
        "RUB": "Russian Ruble",
        "SEK": "Swedish Krona",
        "CHF": "Swiss Franc",
        "TWD": "Taiwan Dollar",
        "USD": "US Dollar"
    }
    
    def __init__(self, debug=False, currency="USD"):
        """Initialize the Azure Pricing Client."""
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}. Supported currencies: {', '.join(self.SUPPORTED_CURRENCIES.keys())}")
            
        self.api_url = "https://prices.azure.com/api/retail/prices"
        self.api_params = {
            "api-version": "2023-01-01-preview",
            "currencyCode": f"'{currency}'"
        }
        self.debug = debug
        self.currency = currency
        
        # Windows VM license cost per core - this is added to Linux savings plan prices
        self.windows_license_cost = {
            "Standard_D4as_v5": 0.184  # $0.184/hour for Windows Server license for D4as_v5 (4 cores)
        }
    
    def get_pricing_data(self, resources_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get pricing data from Azure Price Calculator API.
        
        Args:
            resources_data: Dictionary containing resource data
            
        Returns:
            Dictionary containing pricing data
        """
        console.print("\n[bold blue]Fetching Azure Pricing Data...[/bold blue]")
        
        pricing_data = {
            "currency": self.currency,  # Add this line
            "virtual_machines": {},
            "disks": {}
        }
        
        with console.status("[bold green]Querying Azure Price API...[/bold green]"):
            pricing_data["virtual_machines"] = self._get_vm_pricing(resources_data)
            pricing_data["disks"] = self._get_disk_pricing(resources_data)
            
        return pricing_data
    
    def _get_vm_pricing(self, resources_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get pricing for virtual machines."""
        vm_pricing = {}
        
        vm_regions = set(vm["location"] for vm in resources_data["virtual_machines"])
        vm_sizes = set(vm["vm_size"] for vm in resources_data["virtual_machines"])
        
        for region in vm_regions:
            vm_pricing[region] = {}
            
            for vm_size in vm_sizes:
                filter_query = f"armRegionName eq '{region}' and armSkuName eq '{vm_size}'"
                params = {**self.api_params, "$filter": filter_query}
                
                try:
                    vm_pricing_data = self._fetch_all_pricing_data(params)
                    
                    pricing_result = {
                        # Base prices
                        "windows": {
                            "pay_as_you_go": None,
                            "low_priority": None,
                            "spot": None,
                            "savings_plan_1yr": None,
                            "savings_plan_3yr": None,
                            "hybrid_benefit": None,
                            "hybrid_savings_plan_1yr": None,
                            "hybrid_savings_plan_3yr": None
                        },
                        "linux": {
                            "pay_as_you_go": None,
                            "low_priority": None,
                            "spot": None,
                            "savings_plan_1yr": None,
                            "savings_plan_3yr": None
                        }
                    }
                    
                    # Track base prices to calculate hybrid benefit costs
                    linux_base_price = None
                    windows_base_price = None
                    
                    for item in vm_pricing_data:
                        os_type = "windows" if "Windows" in item.get("productName", "") else "linux"
                        
                        # Skip DevTestConsumption type prices
                        if item.get("type") == "DevTestConsumption":
                            continue
                            
                        # Handle regular consumption prices
                        if item.get("type") == "Consumption":
                            if "Spot" in item.get("meterName", ""):
                                pricing_result[os_type]["spot"] = item.get("retailPrice")
                            elif "Low Priority" in item.get("meterName", ""):
                                pricing_result[os_type]["low_priority"] = item.get("retailPrice")
                            else:
                                price = item.get("retailPrice")
                                pricing_result[os_type]["pay_as_you_go"] = price
                                if os_type == "linux":
                                    linux_base_price = price
                                else:
                                    windows_base_price = price
                        
                        # Handle savings plan prices
                        if "savingsPlan" in item:
                            if os_type == "linux":
                                # Store Linux savings plan prices
                                for plan in item["savingsPlan"]:
                                    if plan.get("term") == "1 Year":
                                        linux_1yr_price = plan.get("retailPrice")
                                        pricing_result["linux"]["savings_plan_1yr"] = linux_1yr_price
                                        # Add Windows license cost for Windows savings plan
                                        windows_license = self.windows_license_cost.get(vm_size, 0)
                                        pricing_result["windows"]["savings_plan_1yr"] = linux_1yr_price + windows_license
                                    elif plan.get("term") == "3 Years":
                                        linux_3yr_price = plan.get("retailPrice")
                                        pricing_result["linux"]["savings_plan_3yr"] = linux_3yr_price
                                        # Add Windows license cost for Windows savings plan
                                        windows_license = self.windows_license_cost.get(vm_size, 0)
                                        pricing_result["windows"]["savings_plan_3yr"] = linux_3yr_price + windows_license
                    
                    # Calculate hybrid benefit prices for Windows VMs (base Windows price - base Linux price)
                    if windows_base_price and linux_base_price:
                        license_cost = windows_base_price - linux_base_price
                        # Hybrid benefit removes the Windows license cost
                        pricing_result["windows"]["hybrid_benefit"] = linux_base_price
                        
                        # Hybrid benefit + savings plans (Linux savings plan prices)
                        if pricing_result["linux"]["savings_plan_1yr"]:
                            pricing_result["windows"]["hybrid_savings_plan_1yr"] = pricing_result["linux"]["savings_plan_1yr"]
                        if pricing_result["linux"]["savings_plan_3yr"]:
                            pricing_result["windows"]["hybrid_savings_plan_3yr"] = pricing_result["linux"]["savings_plan_3yr"]
                    
                    vm_pricing[region][vm_size] = pricing_result
                    console.print(f"  - Got pricing for VM: [bold]{vm_size}[/bold] in [bold]{region}[/bold]")
                
                except Exception as e:
                    console.print(f"[bold red]Error fetching pricing for VM size {vm_size} in region {region}:[/bold red] {str(e)}")
        
        return vm_pricing

    def _get_disk_pricing(self, resources_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get pricing for managed disks."""
        disk_pricing = {}
        
        # Get unique regions and SKUs from the resources
        disk_regions = set(disk["location"] for disk in resources_data["disks"])
        disk_skus = set(disk["sku"] for disk in resources_data["disks"] if disk["sku"])
        
        # Get unique disk sizes to match with appropriate tiers
        disk_sizes = {(disk["sku"], disk["disk_size_gb"]) for disk in resources_data["disks"] 
                      if disk["sku"] and disk["disk_size_gb"]}
        
        # Debug printing
        if self.debug:
            console.print("\n[bold yellow]Debug: Found SKUs and sizes[/bold yellow]")
            console.print(f"SKUs in resources: {disk_skus}")
            console.print(f"Disk sizes (SKU, GB): {disk_sizes}")
        
        # Create a mapping of actual disk sizes to tier names for each SKU type
        size_tier_mapping = {
            "Premium_LRS": {},
            "StandardSSD_LRS": {},
            "Standard_LRS": {}
        }
        
        # Fill in the mappings based on our disk size constants
        for size, tier in PREMIUM_DISK_SIZES.items():
            size_tier_mapping["Premium_LRS"][size] = tier
        for size, tier in STANDARD_SSD_SIZES.items():
            size_tier_mapping["StandardSSD_LRS"][size] = tier
        for size, tier in STANDARD_HDD_SIZES.items():
            size_tier_mapping["Standard_LRS"][size] = tier
        
        for region in disk_regions:
            disk_pricing[region] = {}
            
            # Initialize the pricing structure for the region
            for sku_type in disk_skus:
                disk_pricing[region][sku_type] = {
                    "pay_as_you_go": {},
                    "reserved": {},
                    "tier_mapping": {},  # Maps disk size to tier name and pricing
                    "alternatives": {}   # Alternative tiers for each size
                }
            
            # Iterate through each SKU and size combination
            for disk_sku, disk_size in disk_sizes:
                # Determine the appropriate tier name based on size and SKU
                tier_name = DiskMapper.get_tier_from_size(disk_size, disk_sku)
                if not tier_name:
                    console.print(f"[bold yellow]Warning: No tier found for size {disk_size}GB and SKU {disk_sku} in disk mapper[/bold yellow]")
                    continue
                
                # Extract redundancy type (LRS or ZRS)
                redundancy = "ZRS" if "ZRS" in disk_sku else "LRS"
                
                # Construct the filter query
                if "Premium" in disk_sku:
                    sku_name = f"{tier_name} {redundancy}"
                    product_name = "Premium SSD Managed Disks"
                elif "StandardSSD" in disk_sku:
                    sku_name = f"{tier_name} {redundancy}"
                    product_name = "Standard SSD Managed Disks"
                elif "Standard" in disk_sku:
                    sku_name = f"{tier_name} {redundancy}"
                    product_name = "Standard HDD Managed Disks"
                else:
                    sku_name = tier_name
                    product_name = "Ultra Disks"  # Assuming default to Ultra Disks if no other match

                query = (
                    f"armRegionName eq '{region}' and "
                    f"serviceFamily eq 'Storage' and "
                    f"skuName eq '{sku_name}' and "
                    f"productName eq '{product_name}' and "
                    f"meterName eq '{tier_name} {redundancy} Disk'"
                )
                
                params = {**self.api_params, "$filter": query}
                
                try:
                    disk_pricing_data = self._fetch_all_pricing_data(params)
                    if self.debug:
                        console.print(f"\nFound {len(disk_pricing_data)} pricing records for {disk_sku} {disk_size}GB in {region}")
                    
                    # Process the pricing data
                    for item in disk_pricing_data:
                        price_type = item.get("type")
                        retail_price = item.get("retailPrice")
                        
                        if price_type == "Consumption":
                            disk_pricing[region][disk_sku]["pay_as_you_go"][disk_size] = retail_price
                            if self.debug:
                                console.print(f"  - Pay-as-you-go price: {format_currency(retail_price, self.currency)}")
                        elif price_type == "Reservation" and item.get("reservationTerm") == "1 Year":
                            disk_pricing[region][disk_sku]["reserved"][disk_size] = retail_price
                            if self.debug:
                                console.print(f"  - Reserved price (1 year): {format_currency(retail_price, self.currency)}")
                
                except Exception as e:
                    console.print(f"[bold red]Error fetching pricing for {disk_sku} {disk_size}GB in region {region}:[/bold red] {str(e)}")
                    import traceback
                    console.print(traceback.format_exc())
                
                # For Premium disks, add Standard alternatives with matching size
                if disk_sku == "Premium_LRS":
                    disk_pricing[region][disk_sku]["alternatives"][disk_size] = {}
                    
                    # Find matching Standard SSD tier
                    if "StandardSSD_LRS" in disk_pricing[region]:
                        disk_pricing[region][disk_sku]["alternatives"][disk_size]["StandardSSD_LRS"] = {
                            "pay_as_you_go": disk_pricing[region]["StandardSSD_LRS"]["pay_as_you_go"].get(disk_size),
                            "reserved": disk_pricing[region]["StandardSSD_LRS"]["reserved"].get(disk_size)
                        }
                    
                    # Find matching Standard HDD tier
                    if "Standard_LRS" in disk_pricing[region]:
                        disk_pricing[region][disk_sku]["alternatives"][disk_size]["Standard_LRS"] = {
                            "pay_as_you_go": disk_pricing[region]["Standard_LRS"]["pay_as_you_go"].get(disk_size),
                            "reserved": disk_pricing[region]["Standard_LRS"]["reserved"].get(disk_size)
                        }
        
        # Debug - show mapped SKUs for each disk size
        if self.debug:
            console.print(f"\n[bold green]Mapped Disk Pricing for {region}:[/bold green]")
            for sku_type, sku_data in disk_pricing[region].items():
                if self.debug:
                    console.print(f"\n[bold blue]SKU Type: {sku_type}[/bold blue]")
                else:
                    
                    console.print(f"\nSKU Type: {sku_type}")
                console.print(f"  SKU: {sku_type}")
                
                for size, pay_as_you_go in sku_data["pay_as_you_go"].items():
                    reserved = sku_data["reserved"].get(size)
                    console.print(f"    Size {size}GB: Pay-as-you-go={format_currency(pay_as_you_go, self.currency)}, Reserved={format_currency(reserved, self.currency) if reserved else 'N/A'}")
                
                for size, alt_data in sku_data.get("alternatives", {}).items():
                    console.print(f"    Alternatives for {size}GB:")
                    for alt_sku, alt_prices in alt_data.items():
                        pay_go = alt_prices.get('pay_as_you_go')
                        res = alt_prices.get('reserved')
                        console.print(f"      {alt_sku}: Pay-as-you-go={format_currency(pay_go, self.currency) if pay_go else 'N/A'}, Reserved={format_currency(res, self.currency) if res else 'N/A'}")
        
        return disk_pricing
    
    def _fetch_all_pricing_data(self, params: Dict) -> List[Dict]:
        """Fetch all pages of pricing data from the Azure Pricing API.
        
        Args:
            params: Query parameters
            
        Returns:
            List of pricing items from all pages
        """
        all_items = []
        next_page = True
        current_url = self.api_url
        current_params = params
        page_count = 1
        
        while (next_page):
            # Build the full URL with query parameters for debug output
            if self.debug:
                if current_params:
                    # Properly encode each parameter and join with ampersands
                    query_string = "&".join(
                        f"{urllib.parse.quote(str(k))}={urllib.parse.quote(str(v))}" 
                        for k, v in current_params.items()
                    )
                    full_url = f"{current_url}?{query_string}"
                else:
                    full_url = current_url
                console.print(f"\n[bold yellow]DEBUG: API Request (Page {page_count})[/bold yellow]")
                console.print(f"URL: {full_url}")
            
            # Make the request
            response = requests.get(current_url, params=current_params)
            response.raise_for_status()
            data = response.json()
            
            # Print debug info if enabled
            if self.debug:
                console.print(f"Response Status: {response.status_code}")
                console.print(f"Items count: {len(data.get('Items', []))}")
                if data.get('Count'):
                    console.print(f"Total count: {data.get('Count')}")
                if data.get('Items') and len(data.get('Items')) > 0:
                    console.print(f"Sample item:")
                    console.print(json.dumps(data['Items'][0], indent=2))
            
            if "Items" in data and data["Items"]:
                all_items.extend(data["Items"])
            
            # Check if there's a next page
            if "NextPageLink" in data and data["NextPageLink"]:
                # The next page link contains all parameters, so we don't need to pass params again
                current_url = data["NextPageLink"]
                current_params = None  # Parameters are in the URL
                page_count += 1
            else:
                next_page = False
                
        if self.debug:
            console.print(f"\n[bold green]DEBUG: API Query Complete[/bold green]")
            console.print(f"Total items retrieved: {len(all_items)}")
            
        return all_items
