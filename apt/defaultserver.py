from flask import Flask, request, abort
from flask import send_file
import apt.services.security as apt_security
import apt.services.dataset as apt_dataset
import apt.services.registry as apt_registry
import apt.services.reporting as apt_reporting
import apt.services.config as CONFIG

def create_server(server_name, port):

    app = Flask(server_name)

    registry = apt_registry.Registry()
    reporting = apt_reporting.Reporting(registry)

    @app.route('/', methods=['GET'])
    def home():
        return send_file("apt/resources/home.html")

    @app.route('/dataset', methods=['GET'])
    def list_datasets():
        # Retrieve gbif attribute if set
        args = request.args
        include_gbif = args.get("gbif", default="").lower() in ('true', 'on')
        # Retrieve dataset list
        datasets = apt_dataset.list_all()
        enhanced_datasets = []
        for id in datasets:
            dataset = {}
            dataset["id"] = id
            # Enhance result with APT URL of the dataset
            dataset["url"] = CONFIG.APT_PUBLIC_URL + "/dataset/"+id
            # If gbif attribute set, enhance result with GBIF registration information
            if include_gbif:
                if registry.check_already_registered(id):
                    dataset["gbif_key"] = registry.get_gbif_key(id)
                    dataset["registered"] = True
                else:
                    dataset["gbif_key"] = None
                    dataset["registered"] = False
            enhanced_datasets.append(dataset)
        # Return enhanced dataset list
        return enhanced_datasets

    @app.route('/dataset/<string:id>', methods=['GET'])
    def get_dataset(id):
        # Get server path for dataset
        dataset_path = apt_dataset.get_path(id)
        if not dataset_path:
            abort(400)
        # If dataset exists, return file
        if apt_dataset.check_file_exist(dataset_path):
            return send_file(dataset_path)
        # Else return 404 error
        else:
            abort(404)

    @app.route('/report/registered', methods=['GET'])
    def list_registered_datasets():
        datasets = []
        for url in registry.gbif_published_datasets:
            dataset = {}
            dataset["url"] = url
            dataset["key"] = registry.gbif_published_datasets[url]
            datasets.append(dataset)
        return datasets

    @app.route('/report/deleted', methods=['GET'])
    def list_deleted_datasets():
        datasets = []
        for url in registry.gbif_deleted_datasets:
            dataset = {}
            dataset["url"] = url
            dataset["key"] = registry.gbif_deleted_datasets[url]
            datasets.append(dataset)
        return datasets

    @app.route('/dataset/<string:id>', methods=['POST'])
    def post_dataset(id):
        # Secured endpoint
        apt_security.verify(request)
        # Get server path for dataset
        dataset_path = apt_dataset.get_path(id)
        if not dataset_path:
            print(f"Dataset path not correct "+dataset_path, flush=True)
            abort(400)
        apt_dataset.init_path(id)
        # Save uploaded file to correct server path
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            print(f"Missing dataset file in POST", flush=True)
            abort(400)
        uploaded_file.save(dataset_path)
        # Update GBIF registry (register or crawl)
        gbif_key = registry.update(id)
        if not gbif_key:
            abort(500)
        # Return success message
        success = {}
        success["id"] = id
        success["url"] = CONFIG.APT_PUBLIC_URL + "/dataset/"+id
        success["gbif_key"] = gbif_key
        success["registered"] = True
        return success

    @app.route('/dataset/<string:id>', methods=['DELETE'])
    def delete_dataset(id):
        # Secured endpoint
        apt_security.verify(request)
        # Get server path for dataset
        dataset_path = apt_dataset.get_path(id)
        if not dataset_path:
            print(f"Dataset path not correct "+dataset_path, flush=True)
            abort(400)
        # If dataset exists, delete file and update registry
        if apt_dataset.check_file_exist(dataset_path):
            apt_dataset.delete_file(dataset_path)
            registry.delete(id)
        # Else return 404 error
        else:
            abort(404)
        # Return success message
        success = {}
        success["id"] = id
        success["deleted"] = "done"
        return success

    app.run(port=port, host="0.0.0.0", debug=False)
