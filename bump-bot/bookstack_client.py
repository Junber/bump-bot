import json
import os
from typing import Any
import requests

from utils import get_logger


class Bookstack:
    valid = False
    config = {}
    book_cache = {}
    chapter_cache = {}
    page_cache = {}

    def __init__(self) -> None:
        if not os.path.exists("config/bookstack.json"):
            return

        self.valid = True
        with open("config/bookstack.json", "r", encoding="utf-8") as config_file:
            self.config = json.loads(config_file.read())

        self.rebuild_book_cache()
        self.rebuild_chapter_cache()
        self.rebuild_page_cache()

    # Generic
    def get_url(self, endpoint: str) -> str:
        return self.config["url"].rstrip("/") + "/api/" + endpoint.lstrip("/")

    def get_header(self) -> dict:
        return {
            "Authorization": "Token {}:{}".format(
                self.config["token id"], self.config["token secret"]
            )
        }

    def post(self, endpoint: str, data: dict) -> dict:
        response = requests.post(self.get_url(endpoint), headers=self.get_header(), json=data)
        try:
            response.raise_for_status()
        except:
            get_logger().error(
                "Invalid response from POST to {} with {}:\n{}".format(
                    endpoint, data, response.text
                )
            )
            raise
        return response.json()

    def get(self, endpoint: str) -> dict:
        response = requests.get(self.get_url(endpoint), headers=self.get_header())
        try:
            response.raise_for_status()
        except:
            get_logger().error(
                "Invalid response from GET to {}:\n{}".format(endpoint, response.text)
            )
            raise
        return response.json()

    def delete(self, endpoint: str):
        response = requests.delete(self.get_url(endpoint), headers=self.get_header())
        try:
            response.raise_for_status()
        except:
            get_logger().error(
                "Invalid response from DELETE to {}:\n{}".format(endpoint, response.text)
            )
            raise

    # Helpers
    def rebuild_book_cache(self):
        self.book_cache = self.get("books")

    def rebuild_chapter_cache(self):
        self.chapter_cache = self.get("chapters")

    def rebuild_page_cache(self):
        self.page_cache = self.get("pages")

    def find_book_id(self, name: str) -> int:
        for book in self.book_cache["data"]:
            if book["name"] == name:
                return book["id"]
        return -1

    def find_chapter_id(self, book_id: int, name: str) -> int:
        for chapter in self.chapter_cache["data"]:
            if chapter["name"] == name and chapter["book_id"] == book_id:
                return chapter["id"]
        return -1

    def find_page_id(self, book_id: int, chapter_id: int, name: str) -> int:
        for page in self.page_cache["data"]:
            if (
                page["name"] == name
                and page["book_id"] == book_id
                and (chapter_id < 0 or page["chapter_id"] == chapter_id)
            ):
                return page["id"]
        return -1

    def find_page_id_safe(self, book: str, chapter: str, name: str) -> int:
        book_id = self.find_book_id(book)
        if book_id < 0:
            self.rebuild_book_cache()
            book_id = self.find_book_id(book)
            if book_id < 0:
                return -1

        page_id = self.find_page_id(book_id, self.find_chapter_id(book_id, chapter), name)
        if page_id < 0:
            self.rebuild_chapter_cache()
            self.rebuild_page_cache()
            page_id = self.find_page_id(book_id, self.find_chapter_id(book_id, chapter), name)
        return page_id

    def create_book(self, name: str) -> int:
        return self.post("books", {"name": name})["id"]

    def create_chapter(self, book_id: int, name: str) -> int:
        return self.post("chapters", {"name": name, "book_id": book_id})["id"]

    def find_or_create_book(self, book: str) -> int:
        book_id = self.find_book_id(book)
        if book_id < 0:
            self.rebuild_book_cache()
            book_id = self.find_book_id(book)
            if book_id < 0:
                book_id = self.create_book(book)
                self.rebuild_book_cache()
        return book_id

    def find_or_create_chapter(self, book: str, chapter: str) -> int:
        book_id = self.find_or_create_book(book)

        chapter_id = self.find_chapter_id(book_id, chapter)
        if chapter_id < 0:
            self.rebuild_chapter_cache()
            chapter_id = self.find_chapter_id(book_id, chapter)
            if chapter_id < 0:
                chapter_id = self.create_chapter(book_id, chapter)
                self.rebuild_chapter_cache()
        return chapter_id

    # Use cases
    def create_page(self, name: str, markdown: str, chapter: tuple[str, str]) -> None:
        if not self.valid:
            return

        data: dict[str, Any] = {"name": name, "markdown": markdown}

        if len(chapter[1]):
            data["chapter_id"] = self.find_or_create_chapter(chapter[0], chapter[1])
        else:
            data["book_id"] = self.find_or_create_book(chapter[0])

        self.post("pages", data)
        self.rebuild_page_cache()

    def delete_page(self, name: str, chapter: tuple[str, str]) -> None:
        if not self.valid:
            return

        page_id = self.find_page_id_safe(chapter[0], chapter[1], name)
        if page_id >= 0:
            self.delete("pages/{}".format(page_id))


bookstack = Bookstack()
