import apt.services.dataset as apt_dataset
import apt.services.registry as apt_registry

class Reporting:

    def __init__(self, registry):
        self.registry = registry

    #
    #
    #
    def build_apt_list():
        dataset_list = {}
        datasets = apt_dataset.list_all()
        for id in datasets:
            dataset_path = apt_dataset.get_path(id)
            dataset_url = apt_registry.dataset_url(id)
            modification_date = apt_dataset.get_modification_date(dataset_path)
            dataset = {}
            dataset["id"] = id
            dataset["url"] = dataset_url
            dataset["apt_modification_date"] = modification_date

    #
    #
    #
    def build_gbif_list():       
        
        responseCount = requests.get('http://api.gbif.org/v1/occurrence/count?datasetKey='+key)
        recordCount = responseCount.text