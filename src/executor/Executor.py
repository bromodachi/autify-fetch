import concurrent.futures
from pathlib import Path
import requests
import os
import re
from src.model.HtmlRequestor import RequestInfo
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timezone

import traceback


class Executor(object):

    def __init__(self, workers: int = 10):
        self.workers = workers

    # handles if the src is something like /folder/to/path
    def handle_path_like_src(self, src, url, folder, session):
        sources = src.split(',')
        replace_types = []
        for src in sources:
            src = src.strip()
            url_to_request = '{}{}'.format(url, src).split(' ')[0]
            path = re.search('^[\w+\/]+\/', src)
            if path is not None:
                if src[0] == "/":
                    new_file_path = path.group(0)[1:]
                else:
                    new_file_path = path.group(0)
                path_create = Path(os.path.join(os.curdir, folder, new_file_path))
                may_contain_space = os.path.basename(src).split(" ")
                basename = may_contain_space[0]
                other_info = None
                if len(may_contain_space) > 1:
                    other_info = may_contain_space[1]
                path_create.mkdir(parents=True, exist_ok=True)
                full_path = "/".join(path_create.parts) + "/" + basename
                if other_info is not None:
                    replace_types.append(full_path + " " + other_info)
                else:
                    replace_types.append(full_path)
                if not os.path.isfile(full_path):
                    with open(full_path, 'wb') as file:
                        response = session.get(url_to_request)
                        file.write(response.content)
            else:
                # treat as a regular asset
                replace_types.append(self.save_asset(src, url, folder, session))
        return replace_types

    # attempts to save the asset. May failure as there are many edge cases.
    def save_asset(self, src, url, folder, session):
        if len(src.strip()) == 0:
            return src
        basename = os.path.basename(src)
        if 'https://' in src or 'http://' in src:
            url_to_request = src
        else:
            url_to_request = '{}{}'.format(url, src)
        filepath = os.path.join(folder, basename)
        if not os.path.isfile(filepath):
            with open(filepath, 'wb') as file:
                response = session.get(url_to_request)
                file.write(response.content)
        return filepath

    def add_slash_if_needed(self, src):
        if len(src) == 0 or 'https://' in src or 'http://' in src or src[0] == '/' or "base64," in src:
            return src
        return '/' + src


    def save_assets(self, soup, folder, session, url, tag_to_look_for, elements_to_focus):
        if not os.path.exists(folder):
            os.mkdir(folder)
        for tag in soup.findAll(tag_to_look_for):
            for type in elements_to_focus:
                if tag.has_attr(type):
                    try:
                        src = self.add_slash_if_needed(tag[type])
                        # regex for path related
                        path = re.search('^[\w+\/]+\/', src)
                        # if it's a directory format, we need to do something special
                        if path is not None:
                            tag[type] = ", ".join(self.handle_path_like_src(src, url, folder, session))
                        else:
                            # TODO: use regex instead
                            if "base64," in src:
                                string = src.split("base64,")
                                if len(string) > 0:
                                    matches = re.search("model:(.*?);base64", src)
                                    if matches is not None:
                                        from base64 import b64decode
                                        base64_str = string[1]
                                        path_create = Path(
                                            os.path.join(
                                                os.curdir,
                                                folder,
                                                base64_str[0:50].replace("/", "_") + "." +
                                                matches.group(1).split("/")[1]
                                            )
                                        )
                                        tag[type] = path_create
                                        with open(path_create, 'wb') as file:
                                            from base64 import b64decode
                                            data = string[1]
                                            file.write(b64decode(data))
                            else:
                                tag[type] = self.save_asset(src, url, folder, session)

                    except Exception as e:
                        # TODO: do not ignore
                        print(traceback.format_exception(None, e, e.__traceback__))
                        pass

    def create_metadata(self, url, soup, show_metadata, metadata):
        links = soup.findAll('a')
        images = soup.findAll('img')
        num_of_links = str(len(links))
        num_of_images = str(len(images))
        if show_metadata:
            print("site: " + url)
            print("num_links: " + num_of_links)
            print("images: " + num_of_images)
            if url in metadata:
                print("last_fetch: " + metadata[url]['last_fetch'])
        metadata.update(
            {
                url: {
                    'num_links': num_of_links,
                    'images': num_of_images,
                    'last_fetch': datetime.now(timezone.utc).strftime("%a %b %d %Y %H:%M %Z")
                }
            }
        )

    def load_url_html_to_soup(self, session, request: RequestInfo):
        try:
            response = session.get(request.url, timeout=request.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                return soup
            # TODO: create custom exception
            raise Exception("Can't reach specified url: " + str(request.url))
        except Exception:
            # TODO: catching general exception isn't ideal
            raise Exception("Can't reach specified url: " + str(request.url))

    # Retrieve a single page, creates metadata, save its assets, and then finally write it to an HTML file
    def load_url(self, request: RequestInfo, show_metadata, metadata):
        s = requests.Session()
        soup = self.load_url_html_to_soup(s, request)
        self.create_metadata(request.base_url, soup, show_metadata, metadata)
        # save assets...not perfect
        self.save_assets(soup, request.file_name + "_assets", s, request.url, "source", ["srcset"])
        self.save_assets(soup, request.file_name + "_assets", s, request.url, "img",
                         ["model-srcset", "model-src", "model-fallback-src", "src", "srcset"])
        self.save_assets(soup, request.file_name + "_assets", s, request.url, "style", ["model-href", "href", "data-href"])
        self.save_assets(soup, request.file_name + "_assets", s, request.url, "script",
                         ["src"])
        self.save_assets(soup, request.file_name + "_assets", s, request.url, "link",
                         ["href"])
        with open(os.path.join(os.curdir, request.file_name), "w+", encoding='utf-8') as file:
            file.write(str(soup))

    def load_urls(self, urls, show_metadata, metadata):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_url = {executor.submit(self.load_url, request_info, show_metadata, metadata): request_info for
                             request_info in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                request_info = future_to_url[future]
                try:
                    future.result()
                except Exception as exc:
                    print('%s generated an exception: %s' % (request_info.url, exc))
