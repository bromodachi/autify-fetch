from argparse import ArgumentParser
from src.executor.Executor import Executor
from src.utils.JsonUtil import JsonUtil
from src.utils.ValidateUrls import ValidateUrls

if __name__ == '__main__':
    # cli arguments
    cli = ArgumentParser()
    cli.add_argument("--metadata", action="store_true", help="If we should store the metadata or not")
    args_specified, un_validated_url = cli.parse_known_args()
    jsonutil = JsonUtil()
    metadata = jsonutil.load_json_to_dict()
    # validate urls
    request_info_list = ValidateUrls.get_all_valid_urls(un_validated_url)
    # load urls. If metadata is true, we will print out the metadata
    Executor().load_urls(request_info_list, args_specified.metadata, metadata)
    # finally, save all metadata into a json
    jsonutil.write_to_json(metadata)
