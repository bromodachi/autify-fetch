from urllib.parse import urlparse


# Not a perfect validator. But we get rid of urls that might not be correct right away
from src.model.HtmlRequestor import RequestInfo


class ValidateUrls:
    @staticmethod
    def __is_valid(url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            print(url + " is not a valid url. Will remove this from the list")
            return False

    @staticmethod
    def get_all_valid_urls(urls):
        list = []
        for url in urls:
            if ValidateUrls.__is_valid(url):
                result = urlparse(url)
                list.append(RequestInfo(url, result.netloc, 60))
            else:
                print('%r is not a valid url' % url)
        return list
