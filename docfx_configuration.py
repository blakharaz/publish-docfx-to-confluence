import json
import yaml
from pathlib import Path


class DocfxChapter:
    base_path: Path
    title: str
    href: str
    documents: dict[str, str]
    subchapters: dict

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.title = ''
        self.href = ''
        self.documents = {}
        self.subchapters = {}

    def add_document(self, title: str, href: str):
        self.documents[href] = title

    def add_subchapter(self, title: str, href: str):
        href = href.replace('/toc.yml', '')
        subchapter = DocfxChapter(base_path=self.base_path.joinpath(href))
        subchapter.title = title
        subchapter.href = href
        self.subchapters[href] = subchapter

    def get_subchapters(self):
        return self.subchapters.values()

    def update_subchapter(self, href, chapter):
        self.subchapters[href] = chapter


class DocfxConfiguration:
    base_path: Path
    destination_directory: Path
    root: DocfxChapter

    def read_configuration(self, docfx_json):
        self.base_path = Path(docfx_json).parent
        with open(docfx_json, 'r') as f:
            config = json.load(f)
            self.destination_directory = self.base_path.joinpath(config['build']['dest'])

    def read_table_of_contents(self, toc_yaml, title_prefix: str = ""):
        self.root = self.__do_read_table_of_contents(toc_yaml=toc_yaml,
                                                     path_prefix=Path(toc_yaml).parent.relative_to(self.base_path),
                                                     title_prefix=title_prefix)

    def __do_read_table_of_contents(self, toc_yaml, path_prefix: Path, title_prefix: str):
        config = self.__parse_table_of_contents(toc_yaml, path_prefix, title_prefix=title_prefix)

        for subchapter in list(config.get_subchapters()):
            subchapter_path = subchapter.base_path
            if not subchapter_path.is_absolute():
                subchapter_path = self.base_path.joinpath(subchapter_path)
            if subchapter_path.is_dir():
                subchapter_path = subchapter_path.joinpath('toc.yml')
            chapter = self.__do_read_table_of_contents(toc_yaml=subchapter_path,
                                                       path_prefix=path_prefix.joinpath(subchapter.href),
                                                       title_prefix=title_prefix)
            chapter.title = subchapter.title
            config.update_subchapter(subchapter.href, chapter)

        return config

    @staticmethod
    def __parse_table_of_contents(toc_yaml, path_prefix: Path, title_prefix: str):
        with open(toc_yaml, 'r', encoding='utf-8') as f:
            chapter = DocfxChapter(base_path=path_prefix)
            chapter_config = yaml.load(f)
            for index, config_entry in enumerate(chapter_config):
                if index == 0:
                    chapter.href = config_entry['href']
                else:
                    if config_entry['href'].endswith('.md'):
                        chapter.add_document(title=f'{title_prefix}{config_entry["name"]}', href=config_entry['href'])
                    else:
                        chapter.add_subchapter(title=f'{title_prefix}{config_entry["name"]}', href=config_entry['href'])
            return chapter
