import json
import os
import psutil
import subprocess
import time
from typing import List, Set

# TODO: instantiate json on disk that just stores a map of partition_id to update_timestamps

class ConnectedStorageDriveInfo():
    def __init__(self, partition_id: str, drive_path: str, drive_name: str):
        self.partition_id: str = partition_id
        self.drive_path: str = drive_path
        self.drive_name: str = drive_name
        self.connection_time: int = int(time.time())
        self.update_timestamps: List[str] = [] # TODO: load from disk

    def to_json(self):
        return {
            "partition_id": self.partition_id,
            "drive_path": self.drive_path,
            "drive_name": self.drive_name,
            "connection_time": self.connection_time,
            "update_timestamps": self.update_timestamps
        }

def is_external_drive(mountpoint):
    try:
        # Check if the drive is writable and not the main system drive
        return (os.access(mountpoint, os.W_OK) and 
                not mountpoint.endswith('Data') and 
                not mountpoint.endswith('System/Volumes/Data'))
    except Exception:
        return False
        
def get_connected_drives() -> List[ConnectedStorageDriveInfo]:
    drives: Set[ConnectedStorageDriveInfo] = set()

    # Add user's home directory
    drives.add(driveinfo_from_mountpoint(os.path.expanduser('~')))

    # Get all partitions
    partitions = psutil.disk_partitions(all=True)
    
    for partition in partitions:
        try:
            if partition.mountpoint.startswith('/System/Volumes/') or partition.mountpoint.startswith('/Volumes/'):
                # Check if it's an external drive
                if is_external_drive(partition.mountpoint):
                    driveinfo_obj = driveinfo_from_mountpoint(partition.mountpoint)
                    if driveinfo_obj:
                        drives.add(driveinfo_obj)
        except Exception:
            # Skip if we can't access the drive
            continue

    # Sort drives from most recently to least recently connected
    return sorted(drives, key=lambda x: x.connection_time, reverse=True)

def get_drive_free_space(drive_path: str):
    try:
        return psutil.disk_usage(drive_path).free / (1024 * 1024 * 1024)  # Convert to GB
    except Exception:
        return 0  # Return 0 if we can't access the drive
    
def get_partition_id_from_mountpoint(mountpoint: str) -> str:
    if mountpoint.startswith('/Users/'):
        return 'MACOS_USER'
    command = f'diskutil info "{mountpoint}" | grep "Volume UUID"'
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    uuid_line = result.stdout.strip().split(':')
    if len(uuid_line) > 1:
        return uuid_line[1].strip()
    else:
        return None
        
def driveinfo_from_mountpoint(mountpoint: str):
    partition_id = get_partition_id_from_mountpoint(mountpoint)
    drive_path = mountpoint
    # drive_name = mountpoint.split('/')[-1] if os.name != 'nt' else mountpoint.split('\\')[-1] # WINDOWS IS UNTESTED!
    drive_name = mountpoint.split('/')[-1]
    return ConnectedStorageDriveInfo(partition_id, drive_path, drive_name)