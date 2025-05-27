"""
Module for calculating costs and potential savings.
"""

from typing import Dict, Any
from rich.console import Console

# Import DiskMapper from utils directly with absolute import
from azsm.utils import DiskMapper

console = Console()

class CostCalculator:
    """Calculator for costs and potential savings."""
    
    def calculate_costs(self, resources_data: Dict[str, Any], pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate current costs and potential savings.
        
        Args:
            resources_data: Dictionary containing resource data
            pricing_data: Dictionary containing pricing data
            
        Returns:
            Dictionary with cost analysis data
        """
        cost_data = {
            "currency": pricing_data.get("currency", "EUR"),  # Add this line
            "current_monthly_cost": 0.0,
            "spot_monthly_cost": 0.0,
            "low_priority_monthly_cost": 0.0,
            "savings_plan_1yr_monthly_cost": 0.0,
            "savings_plan_3yr_monthly_cost": 0.0,
            "hybrid_monthly_cost": 0.0,
            "hybrid_savings_plan_1yr": 0.0,
            "hybrid_savings_plan_3yr": 0.0,
            "savings_spot_percent": 0.0,
            "savings_low_priority_percent": 0.0,
            "savings_plan_1yr_percent": 0.0,
            "savings_plan_3yr_percent": 0.0,
            "reservations_1yr_monthly_cost": 0.0,
            "reservations_3yr_monthly_cost": 0.0,
            "reservations_low_priority_percent": 0.0,
            "hybrid_savings_percent": 0.0,
            "hybrid_savings_plan_1yr_percent": 0.0,
            "hybrid_savings_plan_3yr_percent": 0.0,
            "detailed": {
                "virtual_machines": [],
                "disks": []
            }
        }
        
        # Calculate VM costs
        for vm in resources_data["virtual_machines"]:
            self._calculate_vm_cost(vm, pricing_data, cost_data)
        
        # Calculate disk costs
        for disk in resources_data["disks"]:
            self._calculate_disk_cost(disk, pricing_data, cost_data)
        
        # Calculate overall savings percentages if there are costs
        if cost_data["current_monthly_cost"] > 0:
            cost_data["savings_spot_percent"] = ((cost_data["current_monthly_cost"] - cost_data["spot_monthly_cost"]) / 
                                               cost_data["current_monthly_cost"]) * 100
             cost_data["reservations_low_priority_percent"] = ((cost_data["current_monthly_cost"] - cost_data["low_priority_monthly_cost"]) / 
                                                       cost_data["current_monthly_cost"]) * 100
             cost_data["reservations_low_priority_percent"] = ((cost_data["current_monthly_cost"] - cost_data["low_priority_monthly_cost"]) / 
                                                       cost_data["current_monthly_cost"]) * 100
            
            cost_data["savings_low_priority_percent"] = ((cost_data["current_monthly_cost"] - cost_data["low_priority_monthly_cost"]) / 
                                                       cost_data["current_monthly_cost"]) * 100
            
            cost_data["savings_plan_1yr_percent"] = ((cost_data["current_monthly_cost"] - cost_data["savings_plan_1yr_monthly_cost"]) / 
                                                    cost_data["current_monthly_cost"]) * 100
            
            cost_data["savings_plan_3yr_percent"] = ((cost_data["current_monthly_cost"] - cost_data["savings_plan_3yr_monthly_cost"]) / 
                                                    cost_data["current_monthly_cost"]) * 100
            
            cost_data["hybrid_savings_percent"] = ((cost_data["current_monthly_cost"] - cost_data["hybrid_monthly_cost"]) /
                                                 cost_data["current_monthly_cost"]) * 100
            
            cost_data["hybrid_savings_plan_1yr_percent"] = ((cost_data["current_monthly_cost"] - cost_data["hybrid_savings_plan_1yr"]) /
                                                          cost_data["current_monthly_cost"]) * 100
            
            cost_data["hybrid_savings_plan_3yr_percent"] = ((cost_data["current_monthly_cost"] - cost_data["hybrid_savings_plan_3yr"]) /
                                                          cost_data["current_monthly_cost"]) * 100
        
        return cost_data
    
    def _calculate_vm_cost(self, vm: Dict[str, Any], pricing_data: Dict[str, Any], cost_data: Dict[str, Any]) -> None:
        """Calculate cost for a virtual machine."""
        region = vm["location"]
        vm_size = vm["vm_size"]
        is_windows = vm["os_type"] == "Windows"
        os_type = "windows" if is_windows else "linux"
        
        if (region in pricing_data["virtual_machines"] and 
            vm_size in pricing_data["virtual_machines"][region]):
            
            pricing = pricing_data["virtual_machines"][region][vm_size][os_type]
            
            # Azure pricing API returns hourly rates
            hours_per_month = 730  # Average number of hours in a month
            
            # Calculate all costs from hourly rates
            current_cost = pricing["pay_as_you_go"] * hours_per_month if pricing["pay_as_you_go"] else 0
            spot_cost = pricing["spot"] * hours_per_month if pricing["spot"] else current_cost
            low_priority_cost = pricing["low_priority"] * hours_per_month if pricing["low_priority"] else current_cost
            savings_plan_1yr_cost = pricing["savings_plan_1yr"] * hours_per_month if pricing["savings_plan_1yr"] else current_cost
            savings_plan_3yr_cost = pricing["savings_plan_3yr"] * hours_per_month if pricing["savings_plan_3yr"] else current_cost
            reservations_1yr_cost = pricing["reservations_1yr"] * hours_per_month if pricing["reservations_1yr"] else current_cost
            reservations_3yr_cost = pricing["reservations_3yr"] * hours_per_month if pricing["reservations_3yr"] else current_cost

            
            # Update total costs
            cost_data["current_monthly_cost"] += current_cost
            cost_data["spot_monthly_cost"] += spot_cost
            cost_data["low_priority_monthly_cost"] += low_priority_cost
            cost_data["savings_plan_1yr_monthly_cost"] += savings_plan_1yr_cost
            cost_data["savings_plan_3yr_monthly_cost"] += savings_plan_3yr_cost
            cost_data["reservations_1yr_monthly_cost"] += reservations_1yr_cost
            cost_data["reservations_3yr_monthly_cost"] += reservations_3yr_cost
            
            # Add to detailed breakdown
            vm_detail = {
                "name": vm["name"],
                "size": vm_size,
                "region": region,
                "os_type": vm["os_type"],
                "current_monthly_cost": current_cost,
                "spot_monthly_cost": spot_cost,
                "low_priority_monthly_cost": low_priority_cost,
                "savings_plan_1yr_monthly_cost": savings_plan_1yr_cost,
                "savings_plan_3yr_monthly_cost": savings_plan_3yr_cost,
                "reservations_1yr_monthly_cost": reservation_1yr_cost,
                "reservations_3yr_monthly_cost": reservation_3yr_cost
            }
            
            cost_data["detailed"]["virtual_machines"].append(vm_detail)
    
    def _calculate_disk_cost(self, disk: Dict[str, Any], pricing_data: Dict[str, Any], cost_data: Dict[str, Any]) -> None:
        """Calculate cost for a managed disk."""
        region = disk["location"]
        sku = disk["sku"]
        size_gb = disk["disk_size_gb"]
        
        if not size_gb or not sku:
            return
            
        if region not in pricing_data["disks"] or sku not in pricing_data["disks"][region]:
            return
        
        disk_pricing = pricing_data["disks"][region]
        original_sku_pricing = disk_pricing[sku]
        
        # Get the tier name for this disk size
        tier_name = DiskMapper.get_tier_from_size(size_gb, sku)
        
        # Find the nearest available size in the pricing data
        available_sizes = sorted(original_sku_pricing["pay_as_you_go"].keys())
        target_size = next((s for s in available_sizes if s >= size_gb), available_sizes[-1])
        
        # Find the pay-as-you-go price for the nearest size
        pay_as_you_go_price = original_sku_pricing["pay_as_you_go"].get(target_size)
        
        if pay_as_you_go_price is None:
            console.print(f"[bold yellow]Warning: No pay-as-you-go price found for {sku} {size_gb}GB (rounded to {target_size}GB) in {region}[/bold yellow]")
            return
        
        # Calculate current cost
        current_cost = pay_as_you_go_price
        
        # Check if reserved pricing is available
        reserved_price = original_sku_pricing["reserved"].get(target_size)
        
        # Calculate savings options for alternative tiers
        savings_options = []
        
        # Only calculate alternatives for Premium disks
        if sku.startswith("Premium"):
            alternatives = [
                ("StandardSSD_LRS", "Standard SSD"),
                ("Standard_LRS", "Standard HDD")
            ]
            
            for alt_sku, alt_name in alternatives:
                if alt_sku in disk_pricing:
                    alt_pricing = disk_pricing[alt_sku]
                    alt_price = alt_pricing["pay_as_you_go"].get(target_size)
                    
                    if alt_price is not None:
                        alt_reserved = alt_pricing["reserved"].get(target_size)
                        savings = current_cost - alt_price
                        savings_percent = (savings / current_cost * 100) if current_cost > 0 else 0
                        
                        alt_tier_name = DiskMapper.get_tier_from_size(size_gb, alt_sku)
                        
                        savings_options.append({
                            "type": alt_sku,
                            "name": alt_name,
                            "tier_name": alt_tier_name,
                            "cost": alt_price,
                            "reserved_cost": alt_reserved,
                            "savings": savings,
                            "savings_percent": savings_percent
                        })
        
        # Calculate reserved instance savings
        if reserved_price:
            reserved_cost = reserved_price
            savings = current_cost - reserved_cost
        else:
            reserved_cost = None
            savings = 0
        
        # Add to total costs
        cost_data["current_monthly_cost"] += current_cost
        
        # Add to savings plan cost
        if reserved_cost:
            cost_data["savings_plan_3yr_monthly_cost"] += reserved_cost
        else:
            cost_data["savings_plan_3yr_monthly_cost"] += current_cost
        
        # Add to detailed breakdown
        disk_detail = {
            "name": disk["name"],
            "sku": sku,
            "tier_name": tier_name,
            "size_gb": size_gb,
            "region": region,
            "current_monthly_cost": current_cost,
            "reserved_monthly_cost": reserved_cost,
            "reservation_eligible": reserved_cost is not None,
            "savings": savings,
            "alternative_tiers": savings_options
        }
        
        cost_data["detailed"]["disks"].append(disk_detail)
