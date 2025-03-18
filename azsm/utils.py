"""
Utility functions for the Azure Save Money | azsm.
"""

from typing import Dict, Optional, Tuple, Any
from rich.console import Console

console = Console()

# Disk size mappings
PREMIUM_DISK_SIZES = {
    4: "P1",
    8: "P2",
    16: "P3",
    32: "P4",
    64: "P6",
    128: "P10",
    256: "P15",
    512: "P20",
    1024: "P30",
    2048: "P40",
    4096: "P50",
    8192: "P60",
    16384: "P70",
    32767: "P80"
}

STANDARD_SSD_SIZES = {
    4: "E1",
    8: "E2",
    16: "E3",
    32: "E4",
    64: "E6",
    128: "E10",
    256: "E15",
    512: "E20",
    1024: "E30",
    2048: "E40",
    4096: "E50",
    8192: "E60",
    16384: "E70",
    32767: "E80"
}

STANDARD_HDD_SIZES = {
    32: "S4",
    64: "S6",
    128: "S10",
    256: "S15",
    512: "S20",
    1024: "S30",
    2048: "S40",
    4096: "S50",
    8192: "S60",
    16384: "S70",
    32767: "S80"
}

CURRENCY_SYMBOLS = {
    "AUD": "A$",
    "BRL": "R$",
    "GBP": "£",
    "CAD": "C$",
    "CNY": "¥",
    "DKK": "kr",
    "EUR": "€",
    "INR": "₹",
    "JPY": "¥",
    "KRW": "₩",
    "NZD": "NZ$",
    "NOK": "kr",
    "RUB": "₽",
    "SEK": "kr",
    "CHF": "Fr",
    "TWD": "NT$",
    "USD": "$"
}

class DiskMapper:
    """Helper class for mapping disk sizes to SKUs and vice versa."""
    
    @staticmethod
    def get_disk_tiers(size_gb: int) -> Dict[str, str]:
        """Get all possible disk tiers for a given size.
        
        Args:
            size_gb: Size of the disk in GB
            
        Returns:
            Dictionary mapping disk types to their SKU names
        """
        tiers = {}
        
        # Round up to nearest available size
        available_sizes = sorted(PREMIUM_DISK_SIZES.keys())
        target_size = next((s for s in available_sizes if s >= size_gb), available_sizes[-1])
        
        if target_size in PREMIUM_DISK_SIZES:
            tiers["Premium_LRS"] = PREMIUM_DISK_SIZES[target_size]
        if target_size in STANDARD_SSD_SIZES:
            tiers["StandardSSD_LRS"] = STANDARD_SSD_SIZES[target_size]
        if target_size in STANDARD_HDD_SIZES:
            tiers["Standard_LRS"] = STANDARD_HDD_SIZES[target_size]
            
        return tiers
    
    @staticmethod
    def get_tier_from_size(size_gb: int, disk_type: str) -> Optional[str]:
        """Get the tier name for a specific disk size and type.
        
        Args:
            size_gb: Size of the disk in GB
            disk_type: Type of disk (Premium_LRS, StandardSSD_LRS, Standard_LRS, Premium_ZRS, or Standard_ZRS)
            
        Returns:
            Tier name or None if not found
        """
        # Map ZRS types to LRS types for lookup
        disk_type = disk_type.replace("_ZRS", "_LRS")
        if disk_type == "Premium_LRS":
            sizes = PREMIUM_DISK_SIZES
        elif disk_type == "StandardSSD_LRS":
            sizes = STANDARD_SSD_SIZES
        elif disk_type == "Standard_LRS":
            sizes = STANDARD_HDD_SIZES
        else:
            return None
            
        available_sizes = sorted(sizes.keys())
        target_size = next((s for s in available_sizes if s >= size_gb), available_sizes[-1])
        
        return sizes.get(target_size)

def display_banner():
    """Display the application banner."""
    console.print("""
[bold cyan]
  ______   ________         ______   __       __ 
 /      \ /        |       /      \ /  \     /  |
/$$$$$$  |$$$$$$$$/       /$$$$$$  |$$  \   /$$ |
$$ |__$$ |    /$$/        $$ \__$$/ $$$  \ /$$$ |
$$    $$ |   /$$/         $$      \ $$$$  /$$$$ |
$$$$$$$$ |  /$$/           $$$$$$  |$$ $$ $$/$$ |
$$ |  $$ | /$$/____       /  \__$$ |$$ |$$$/ $$ |
$$ |  $$ |/$$      |      $$    $$/ $$ | $/  $$ |
$$/   $$/ $$$$$$$$/        $$$$$$/  $$/      $$/ 
                                                 
[bold green]Azure Save Money[/bold green]
[/bold cyan]
    """)

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format a number as a currency amount.
    
    Args:
        amount: The amount to format
        currency: The currency code (default: USD)
        
    Returns:
        Formatted currency string
    """
    symbol = CURRENCY_SYMBOLS.get(currency, "$")
    
    # Special handling for currencies that go after the number
    if currency in ["DKK", "NOK", "SEK"]:
        return f"{amount:.2f} {symbol}"
    
    # Handle JPY and KRW which don't use decimal places
    if currency in ["JPY", "KRW"]:
        return f"{symbol}{int(amount)}"
        
    return f"{symbol}{amount:.2f}"

def format_percentage(percent: float) -> str:
    """Format a number as a percentage.
    
    Args:
        percent: The percentage value to format
        
    Returns:
        Formatted percentage string
    """
    return f"{percent:.2f}%"

def debug_print(message: str, data: Any = None, enabled: bool = False) -> None:
    """Print debug information if debug mode is enabled.
    
    Args:
        message: Debug message to print
        data: Optional data to print
        enabled: Whether debug mode is enabled
    """
    if not enabled:
        return
        
    console.print(f"\n[bold yellow]DEBUG: {message}[/bold yellow]")
    if data is not None:
        if isinstance(data, dict) or isinstance(data, list):
            import json
            console.print(json.dumps(data, indent=2))
        else:
            console.print(str(data))
