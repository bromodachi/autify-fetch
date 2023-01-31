import json
import os


class JsonUtil(object):
    def __init__(self):
        folder = os.path.join(os.curdir, "__metadata")
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.metadata_path = os.path.join(folder, "__metadata.json")

    def load_json_to_dict(self):
        metadata = {}
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path) as file:
                metadata = json.load(file)
        return metadata

    def write_to_json(self, metadata):
        if len(metadata) != 0:
            with open(self.metadata_path, "w+") as file:
                file.write(json.dumps(metadata))
