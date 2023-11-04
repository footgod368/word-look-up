# -*- coding: utf-8 -*-
# @Time    : 2023/11/3
# @Author  : boleli@umich.edu
# @简介    : 有道词典命令行python版
import requests
from colorama import Fore, Back, Style, init
import sys

init(autoreset=True)
URL = "http://dict.youdao.com/jsonapi"
USAGE = "python3 dictionary.py <word>"


class Word:
    def __init__(self, word: str):
        self.word = word
        self.ukphone = ""
        self.usphone = ""
        self.translations = []
        self.word_forms = []
        self.etymologies = []
        self.eg_sentences = []
        self._make_request()

    def _make_request(self):
        try:
            response = requests.get(f"{URL}?q={self.word}")
            if response.status_code == 200:
                data = response.json()
                if (
                    "ec" in data
                    and "word" in data["ec"]
                    and len(data["ec"]["word"]) > 0
                ):
                    word_data = data["ec"]["word"][0]
                    self.ukphone = word_data.get("ukphone", "")
                    self.usphone = word_data.get("usphone", "")
                    self.translations = word_data.get("trs", [])
                    self.word_forms = word_data.get("wfs", [])
                if "etym" in data and "etyms" in data["etym"]:
                    self.etymologies = data["etym"]["etyms"].get("zh", [])
                if "blng_sents_part" in data:
                    self.eg_sentences = data["blng_sents_part"].get(
                        "sentence-pair", []
                    )
            else:
                print(
                    f"Request to {URL} failed with status code {response.status_code}."
                )
        except requests.RequestException as e:
            print(f"Request to {URL} failed: {str(e)}")

    def print(self):
        print(self.word)
        print(self._str_ukphone())
        print(self._str_usphone())
        print(Fore.RED + self._str_translations())
        print(self._str_word_forms())
        print(Fore.GREEN + self._str_etymologies())
        print(self._str_eg_sentences())

    def _str_ukphone(self):
        return f"英音 [{self.ukphone}]"

    def _str_usphone(self):
        return f"美音 [{self.usphone}]"

    def _str_translations(self):
        return "\n".join(
            [item["tr"][0]["l"]["i"][0] for item in self.translations]
        )

    def _str_word_forms(self):
        return (
            "("
            + ", ".join(
                [
                    item["wf"]["name"] + item["wf"]["value"]
                    for item in self.word_forms
                ]
            )
            + ")"
        )

    def _str_etymologies(self):
        etymologies = [
            item["value"] + "\n" + item["desc"] for item in self.etymologies
        ]
        return "词源:\n" + "\n".join(
            [f"{i+1}. {item}" for i, item in enumerate(etymologies)]
        )

    def _str_eg_sentences(self):
        eg_sentences = [
            item["sentence-eng"].replace("<b>", "*").replace("</b>", "*")
            + "\n"
            + item["sentence-translation"]
            for item in self.eg_sentences
        ]
        return "例句：\n" + "\n".join(
            [f"{i+1}. {item}" for i, item in enumerate(eg_sentences)]
        )


if __name__ == "__main__":
    if len(sys.argv) == 2:
        word = Word(sys.argv[1])
        word.print()
    else:
        print(USAGE)
