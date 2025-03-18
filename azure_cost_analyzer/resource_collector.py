"""
Module for collecting Azure resource information.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

from azure.core.credentials import TokenCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from rich.console import Console

console = Console()

class ResourceCollector:
    """Class for collecting Azure resource information."""
    
    def __init__(self, credential: TokenCredential, subscription_id: str):
        """Initialize the ResourceCollector.
        
        Args:
            credential: Azure credential for authentication
            subscription_id: Azure subscription ID
        """
        self.credential = credential
        self.subscription_id = subscription_id
        
        # Initialize Azure clients
        self.compute_client = ComputeManagementClient(self.credential, self.subscription_id)
        self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)
    
    def collect_resources(self) -> Dict[str, Any]:
        """Collect information about Azure resources.
        
        Returns:
            Dictionary containing collected resource data
        """
        resources_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "subscription_id": self.subscription_id
            },
            "virtual_machines": [],
            "disks": []
        }
        
        self._gather_virtual_machines(resources_data)
        self._gather_disks(resources_data)
        
        return resources_data
    
    def _gather_virtual_machines(self, resources_data: Dict[str, Any]) -> None:
        """Gather information about all virtual machines in the subscription."""
        console.print("\n[bold blue]Gathering Virtual Machines...[/bold blue]")
        
        with console.status("[bold green]Fetching VM data...[/bold green]"):
            vms = list(self.compute_client.virtual_machines.list_all())
            console.print(f"Found [bold]{len(vms)}[/bold] virtual machines")
            
            for vm in vms:
                # Get VM details
                resource_group = vm.id.split('/')[4]
                vm_details = self.compute_client.virtual_machines.get(
                    resource_group_name=resource_group,
                    vm_name=vm.name,
                    expand='instanceView'
                )
                
                # Get OS information
                os_type = "Unknown"
                os_info = "Unknown"
                
                if vm.storage_profile.os_disk.os_type:
                    os_type = vm.storage_profile.os_disk.os_type
                    
                    if os_type == 'Windows':
                        if vm.storage_profile.image_reference:
                            os_info = f"{vm.storage_profile.image_reference.offer} {vm.storage_profile.image_reference.sku}"
                    elif os_type == 'Linux':
                        if vm.storage_profile.image_reference:
                            os_info = f"{vm.storage_profile.image_reference.offer} {vm.storage_profile.image_reference.sku}"
                
                # Build VM data
                vm_data = {
                    "id": vm.id,
                    "name": vm.name,
                    "resource_group": resource_group,
                    "location": vm.location,
                    "vm_size": vm.hardware_profile.vm_size,
                    "os_type": os_type,
                    "os_info": os_info,
                    "provisioning_state": vm.provisioning_state,
                    "power_state": self._get_vm_power_state(vm_details.instance_view),
                    "tags": vm.tags if vm.tags else {},
                    "attached_disks": []
                }
                
                # Add disk information
                if vm.storage_profile.os_disk:
                    vm_data["attached_disks"].append({
                        "name": vm.storage_profile.os_disk.name,
                        "is_os_disk": True,
                        "disk_size_gb": vm.storage_profile.os_disk.disk_size_gb,
                        "storage_account_type": vm.storage_profile.os_disk.managed_disk.storage_account_type if vm.storage_profile.os_disk.managed_disk else None
                    })
                
                if vm.storage_profile.data_disks:
                    for disk in vm.storage_profile.data_disks:
                        vm_data["attached_disks"].append({
                            "name": disk.name,
                            "is_os_disk": False,
                            "disk_size_gb": disk.disk_size_gb,
                            "storage_account_type": disk.managed_disk.storage_account_type if disk.managed_disk else None
                        })
                
                resources_data["virtual_machines"].append(vm_data)
                console.print(f"  - Processed VM: [bold]{vm.name}[/bold]")

    def _gather_disks(self, resources_data: Dict[str, Any]) -> None:
        """Gather information about all managed disks in the subscription."""
        console.print("\n[bold blue]Gathering Managed Disks...[/bold blue]")
        
        with console.status("[bold green]Fetching disk data...[/bold green]"):
            disks = list(self.compute_client.disks.list())
            console.print(f"Found [bold]{len(disks)}[/bold] managed disks")
            
            for disk in disks:
                disk_data = {
                    "id": disk.id,
                    "name": disk.name,
                    "resource_group": disk.id.split('/')[4],
                    "location": disk.location,
                    "disk_size_gb": disk.disk_size_gb,
                    "sku": disk.sku.name if disk.sku else None,
                    "os_type": self._safe_get_value(disk.os_type),
                    "disk_state": self._safe_get_value(disk.disk_state),
                    "tags": disk.tags if disk.tags else {},
                    "creation_data": {
                        "create_option": self._safe_get_value(disk.creation_data.create_option) if disk.creation_data.create_option else None,
                        "source_uri": disk.creation_data.source_uri if hasattr(disk.creation_data, 'source_uri') else None
                    }
                }
                
                resources_data["disks"].append(disk_data)
                console.print(f"  - Processed Disk: [bold]{disk.name}[/bold]")
    
    def _get_vm_power_state(self, instance_view):
        """Helper method to get the power state of a VM."""
        if instance_view and instance_view.statuses:
            for status in instance_view.statuses:
                if status.code.startswith('PowerState/'):
                    return status.code.split('/')[1]
        return "Unknown"
    
    def _safe_get_value(self, attr):
        """Helper function to safely get value from attribute that could be string or enum."""
        if attr is None:
            return None
        return attr.value if hasattr(attr, 'value') else attr
    
    def save_data(self, resources_data: Dict[str, Any], output_file: str) -> None:
        """Save gathered resource data to a JSON file."""
        with open(output_file, 'w') as f:
            json.dump(resources_data, f, indent=2)
        console.print(f"\n[bold green]Resource data saved to:[/bold green] {os.path.abspath(output_file)}")
