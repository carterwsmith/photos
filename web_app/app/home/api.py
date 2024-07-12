import json

if __name__ == '__main__':
    from utils import get_connected_drives
else:
    from .utils import get_connected_drives

def drives_json():
    return json.dumps([drive.to_json() for drive in get_connected_drives()])