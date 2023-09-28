import re
import os
import apt.services.config as CONFIG

#
# List all datasets from file system
#
def list_all():
    datasets = []
    for root,d_names,f_names in os.walk(CONFIG.RESOURCES_PATH):
        for f in f_names:
            datasets.append(os.path.splitext(f)[0])
    return datasets

#
# Compute dataset path from id
#
def get_path(id):
    # Check forbidden characters in ID
    if not checkAuthorizedChars(id) or len(id) < 3:
        return None

    return CONFIG.RESOURCES_PATH + id[0] + "/" + id[1] + "/" + id[2] + "/" + id + ".zip"

#
# Compute dataset path from id and version
#
def get_path_with_version(id, version):
    # Check forbidden characters in ID
    if not checkAuthorizedChars(id) or len(id) < 3:
        return None

    # Check forbidden characters in version
    if not checkAuthorizedChars(version) or len(version) < 1:
        return None

    return CONFIG.RESOURCES_PATH + id[0] + "/" + id[1] + "/" + id[2] + "/" + id + ".zip." + version

#
# Create dataset path on file system
#
def init_path(id):
    os.makedirs(CONFIG.RESOURCES_PATH + id[0] + "/" + id[1] + "/" + id[2], exist_ok=True)

#
# Check if path exists on file system
#
def check_file_exist(path):
    return os.path.exists(path)

#
# Delete path on file system
#
def delete_file(path):
    return os.remove(path)

#
# Get the dataset modification date
#
def get_modification_date(path):
    return os.path.getmtime(path)

#
# Check if text contains only authorized characters
#
def checkAuthorizedChars(text):
    return re.match("^[A-Za-z0-9-_.]*$", text)