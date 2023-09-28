import requests
from requests.auth import HTTPBasicAuth
import apt.services.config as CONFIG

class Registry:

    def __init__(self):
        self.gbif_published_datasets = {}
        self.gbif_deleted_datasets = {}
        self.init_gbif_published_datasets()
        self.init_gbif_deleted_datasets()

    #
    # Entry point for the registry update:
    # Register, update or revive, according to current state of the dataset
    #
    def update(self, id):
        if self.check_already_registered(id):
            gbif_key = self.get_gbif_key(id)
            print(f"Dataset {id} already registered with key {gbif_key}. Trigger crawl...", flush=True)
            return self.update_dataset(id, gbif_key)
        elif self.check_deleted(id):
            gbif_key = self.get_gbif_deleted_key(id)
            print(f"Dataset {id} was registered and deleted with key {gbif_key}. Trigger registration...", flush=True)
            return self.revive_dataset(id, gbif_key)
        else:
            print(f"Dataset {id} not yet registered. Trigger registration...", flush=True)
            return self.register_new_dataset(id)

    #
    # Entry point for the registry deletion
    #
    def delete(self, id):
        if self.check_already_registered(id):
            gbif_key = self.get_gbif_key(id)
            print(f"Dataset {id} registered with key {gbif_key}. Trigger deletion...", flush=True)
            self.delete_dataset(id, gbif_key)

    #
    # Check if the dataset URL (built from its id)
    # is in GBIF published datasets map
    #
    def check_already_registered(self, id):
        # Look for dataset URL in the GBIF published datasets map
        gbif_key = self.get_gbif_key(id)
        return gbif_key != None

    def get_gbif_key(self, id):
        return self.gbif_published_datasets.get(dataset_url(id), None)

    #
    # Check if the dataset URL (built from its id)
    # is in GBIF deleted datasets map
    #
    def check_deleted(self, id):
        # Look for dataset URL in the GBIF deleted datasets map
        gbif_key = self.get_gbif_deleted_key(id)
        return gbif_key != None

    def get_gbif_deleted_key(self, id):
        return self.gbif_deleted_datasets.get(dataset_url(id), None)

    #
    # Call GBIF published datasets URL (page by page)
    # to retrieve all datasets of the configured publisher
    #
    # Filter the datasets using the endpoint URL, to keep only datasets
    # hosted on this APT
    #
    # Store the GBIF key / endpoint URL results
    # in GBIF published datasets map
    #
    def init_gbif_published_datasets(self):
        print("Initializing GBIF published datsets list...", flush=True)
        local_gbif_published_datasets = {}

        offset = 0
        limit = 1000

        while True:
            url = published_dataset_url(offset, limit)
            print(url, flush=True)
            response = requests.get(url)
            data = response.json()

            for r in data['results']:
                key = r['key']
                endpoints = r['endpoints']
                for endpoint in endpoints:
                    endpoint_url = endpoint['url']
                    if endpoint_url.startswith(CONFIG.APT_PUBLIC_URL):
                        if endpoint_url in local_gbif_published_datasets:
                            print("ERROR - endpoint already registered "+endpoint_url, flush=True)
                        else:
                            local_gbif_published_datasets[endpoint_url] = key

            if data['endOfRecords']:
                break
            else:
                offset = offset + limit

        self.gbif_published_datasets = local_gbif_published_datasets
        print(f"{str(len(self.gbif_published_datasets))} GBIF published datasets found", flush=True)

    #
    # Call GBIF deleted datasets URL (page by page)
    # to retrieve all deleted datasets from all publishers
    #
    # Filter the datasets using the endpoint URL, to keep only datasets
    # that were hosted on this APT
    #
    # Store the GBIF key / endpoint URL results
    # in GBIF deleted datasets map
    #
    def init_gbif_deleted_datasets(self):
        print("Initializing GBIF deleted datsets list...", flush=True)
        local_gbif_deleted_datasets = {}

        offset = 0
        limit = 1000

        while True:
            url = deleted_dataset_url(offset, limit)
            print(url, flush=True)
            response = requests.get(url)
            data = response.json()

            for r in data['results']:
                publisher_key = r['publishingOrganizationKey']
                key = r['key']
                endpoints = r['endpoints']

                if publisher_key == CONFIG.PUBLISHER_KEY:
                    for endpoint in endpoints:
                        endpoint_url = endpoint['url']
                        if endpoint_url.startswith(CONFIG.APT_PUBLIC_URL):
                            if endpoint_url in local_gbif_deleted_datasets:
                                print("ERROR - endpoint already exists in deleted datasets "+endpoint_url, flush=True)
                            else:
                                local_gbif_deleted_datasets[endpoint_url] = key

            if data['endOfRecords']:
                break
            else:
                offset = offset + limit

        self.gbif_deleted_datasets = local_gbif_deleted_datasets
        print(f"{str(len(self.gbif_deleted_datasets))} GBIF deleted datasets found", flush=True)

    #
    # Register a new dataset
    #
    def register_new_dataset(self, id):
        register_dataset_body = {
            "publishingOrganizationKey": CONFIG.PUBLISHER_KEY,
            "installationKey": CONFIG.INSTALLATION_KEY,
            "type": "OCCURRENCE",
            "title": "Dataset "+id,
            "description": "Dataset "+id,
            "language": CONFIG.PUBLICATION_LANGUAGE,
            "license": CONFIG.PUBLICATION_LICENSE
        }

        url = registry_dataset_url()
        print(f"Calling {url} with body: {register_dataset_body}", flush=True)
        response = requests.post(url, json = register_dataset_body, auth = HTTPBasicAuth(CONFIG.GBIF_REGISTRY_LOGIN, CONFIG.GBIF_REGISTRY_PASSWORD))
        gbif_key = response.json()
        print(f"Dataset {id} registered with GBIF ID {gbif_key}", flush=True)

        apt_endpoint_url = dataset_url(id)
        apt_endpoint = {
            "type": "DWC_ARCHIVE",
            "url": apt_endpoint_url
        }
        url = registry_dataset_endpoint_url(gbif_key)
        print(f"Calling POST {url} with body: {apt_endpoint}", flush=True)
        response = requests.post(url, json = apt_endpoint, auth = HTTPBasicAuth(CONFIG.GBIF_REGISTRY_LOGIN, CONFIG.GBIF_REGISTRY_PASSWORD))
        print(f"Endpoint {apt_endpoint_url} added for dataset {id}", flush=True)

        # Update local GBIF Registry
        self.gbif_published_datasets[apt_endpoint_url] = gbif_key

        return gbif_key

    #
    # Update an existing dataset - trigger the GBIF crawl
    #
    def update_dataset(self, id, gbif_key):
        crawl_url = registry_dataset_crawl_url(gbif_key)
        print(f"Calling {crawl_url}", flush=True)
        response = requests.post(crawl_url, auth = HTTPBasicAuth(CONFIG.GBIF_REGISTRY_LOGIN, CONFIG.GBIF_REGISTRY_PASSWORD))

        print(f"Dataset {id} updated with GBIF ID {gbif_key}", flush=True)

        return gbif_key

    #
    # Revive a previously deleted dataset
    #
    def revive_dataset(self, id, gbif_key):
        # Get current dataset
        url = registry_dataset_revive_url(gbif_key)
        response = requests.get(url)
        dataset_json = response.json()
        del dataset_json["deleted"]

        apt_endpoint_url = dataset_url(id)

        # Update installation
        url = registry_dataset_revive_url(gbif_key)
        print(f"Calling PUT {url}", flush=True)
        response = requests.put(url, json = dataset_json, auth = HTTPBasicAuth(CONFIG.GBIF_REGISTRY_LOGIN, CONFIG.GBIF_REGISTRY_PASSWORD))

        # Update local GBIF Registry
        self.gbif_published_datasets[apt_endpoint_url] = gbif_key
        del self.gbif_deleted_datasets[apt_endpoint_url]

        print(f"Dataset {id} revived with GBIF ID {gbif_key}", flush=True)

        return gbif_key

    #
    # Delete dataset from the GBIF registry
    #
    def delete_dataset(self, id, gbif_key):
        delete_url = registry_dataset_delete_url(gbif_key)
        print(f"Calling {delete_url}", flush=True)
        response = requests.delete(delete_url, auth = HTTPBasicAuth(CONFIG.GBIF_REGISTRY_LOGIN, CONFIG.GBIF_REGISTRY_PASSWORD))

        apt_endpoint_url = dataset_url(id)

        # Update local GBIF Registry
        del self.gbif_published_datasets[apt_endpoint_url]
        self.gbif_deleted_datasets[apt_endpoint_url] = gbif_key

        print(f"Dataset {id} deleted with GBIF ID {gbif_key}", flush=True)

        return gbif_key

###################################
#
#   Internal Functions
#
###################################

def dataset_url(id):
    return CONFIG.APT_PUBLIC_URL + "/dataset/"+id

def registry_dataset_url():
    return CONFIG.GBIF_REGISTRY_URL + "/v1/dataset"

def registry_dataset_delete_url(gbif_key):
    return CONFIG.GBIF_REGISTRY_URL + "/v1/dataset/" + gbif_key

def registry_dataset_revive_url(gbif_key):
    return CONFIG.GBIF_REGISTRY_URL + "/v1/dataset/" + gbif_key

def registry_dataset_endpoint_url(gbif_key):
    return CONFIG.GBIF_REGISTRY_URL + "/v1/dataset/" + gbif_key + "/endpoint"

def registry_dataset_crawl_url(gbif_key):
    return CONFIG.GBIF_REGISTRY_URL + "/v1/dataset/" + gbif_key + "/crawl"

def published_dataset_url(offset, limit):
    return CONFIG.GBIF_REGISTRY_URL + "/v1/organization/" + CONFIG.PUBLISHER_KEY + "/publishedDataset?offset=" + str(offset) + "&limit=" + str(limit)

def deleted_dataset_url(offset, limit):
    return CONFIG.GBIF_REGISTRY_URL + "/v1/dataset/deleted?offset=" + str(offset) + "&limit=" + str(limit)
