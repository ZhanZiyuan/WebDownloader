#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import platform
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import sleep, time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class WebDownloader(object):
    """
    ``WebDownloader``
    =================

    A class to download elements from a specified website.

    Attributes
    ----------
    website_url: string
        The URL of the website to be crawled.
    folder_path: string
        The directory to store the downloaded elements.
    element_tag: string
        The tag of elements to be filtered.
        Default is "image".
    requests_per_minute: integer
        The number of requests to the specified URL per minute.
        Default is 10.
    last_request_time: float
        The time of the last request made to the website.
    """

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
    }

    def __init__(self,
                 website_url: str,
                 folder_path: str,
                 element_tag: str = "image",
                 requests_per_minute: int = 10) -> None:
        """
        Initialize the WebDownloader object.
        """
        self.website_url = website_url
        self.folder_path = folder_path
        self.element_tag = element_tag
        self.requests_per_minute = requests_per_minute
        self.last_request_time = 0.0

    def _check_folder_path(self) -> Path:
        """
        Check if the directory to the input file exists.
        """
        if not Path(self.folder_path).exists():
            Path(self.folder_path).mkdir(
                parents=True,
                exist_ok=True
            )
        return Path(self.folder_path)

    def _rename_duplicate_files(self, file_name: str) -> str:
        """
        Rename files if their names are the same.

        Args
        ----
        file_name: str
            The original file name.
        """
        folder_path = self._check_folder_path()
        base_name = Path(file_name).stem
        extension = Path(file_name).suffix

        i = 1
        while (folder_path / file_name).exists():
            file_name = f"{base_name}_({i}){extension}"
            i += 1
        return file_name

    @staticmethod
    def _make_request(url: str) -> requests.Response:
        """
        Make a request to the specified URL.

        Args
        ----
        url: string
            The URL to make the request to.
        """
        return requests.get(
            url=url,
            headers=WebDownloader.headers,
            timeout=10
        )

    def download_single_element(self, url: str) -> None:
        """
        Download a single element from the specified URL.

        Args
        ----
        url: string
            The URL of the element to be downloaded.
        """
        current_time = time()

        if current_time - self.last_request_time < 60 / self.requests_per_minute:
            sleep(
                60/self.requests_per_minute
                - (current_time - self.last_request_time)
            )

        response = WebDownloader._make_request(url)

        if response.status_code == 200:
            updated_file_name = self._rename_duplicate_files(Path(url).name)
            full_file_path = self._check_folder_path() / updated_file_name
            with open(full_file_path, "wb") as file_object:
                file_object.write(response.content)
                print(f"Downloaded: {updated_file_name}")
            self.last_request_time = time()

    def download_multi_threaded(self, urls: list) -> None:
        """
        Download multiple elements from the specified list of URLs.

        Args
        ----
        urls: list
            A list of URLs to download elements from.
        """
        with ThreadPoolExecutor() as executor:
            executor.map(self.download_single_element, urls)

    def download_all_elements(self) -> None:
        """
        Download all elements from the specified website.
        """
        response = WebDownloader._make_request(self.website_url)

        if response.status_code == 200:
            print(
                f"Downloading {self.element_tag}s "
                f"from: {self.website_url}"
            )
            soup = BeautifulSoup(response.text, "html.parser")
            element_tags = soup.find_all(
                name="img" if self.element_tag == "image" else self.element_tag,
                src=True
            )
            elem_urls = [
                urljoin(
                    self.website_url,
                    elem_tag.get("src")
                )
                for elem_tag in element_tags
            ]
            self.download_multi_threaded(elem_urls)
            print("All downloads completed.")


if __name__ == "__main__":

    print(
        "A script to download elements (e.g. images) "
        "from the specified website.\n"
    )

    website_url_input = input(
        "Please input the URL to be requested.\n"
        "For example: https://www.baidu.com/\n"
    )
    folder_path_input = input(
        "Please input the directory to store the downloaded elements.\n"
        "For example: C:/Users/user/Downloads\n"
    )
    element_tag_input = input(
        "Please input the tag of elements to be downloaded.\n"
        "For example: image\n"
    )
    requests_per_minute_input = int(
        input(
            "Please input the number of requests "
            "to the specified URL per minute.\n"
            "For example: 10\n"
        )
    )

    downloader = WebDownloader(
        website_url=website_url_input,
        folder_path=folder_path_input,
        element_tag=element_tag_input,
        requests_per_minute=requests_per_minute_input
    )

    downloader.download_all_elements()

    if platform.system() == "Windows":
        os.system("pause")
    else:
        os.system(
            "/bin/bash -c 'read -s -n 1 -p \"Press any key to exit.\"'"
        )
        print()
