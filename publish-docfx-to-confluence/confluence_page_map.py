from confluence_client import ConfluenceClient
from docfx_configuration import DocfxChapter


def find_or_create_pages(chapter: DocfxChapter, confluence: ConfluenceClient, root_page_id: str):
    confluence_page_map = {}

    page_children = confluence.get_direct_children(page_id=root_page_id)
    for document, title in chapter.documents.items():
        document_page = next((p for p in page_children if p['title'] == title), None)
        if document_page is None:
            document_page = confluence.create_placeholder_page(root_page_id, title=title)

        confluence_page_map[chapter.base_path.joinpath(document)] = document_page

    for name, subchapter in chapter.subchapters.items():
        chapter_page = next((p for p in page_children if p['title'] == subchapter.title), None)
        if chapter_page is None:
            chapter_page = confluence.create_placeholder_page(root_page_id, title=subchapter.title)

        confluence_page_map[subchapter.base_path.joinpath(subchapter.href)] = chapter_page
        confluence_page_map |= find_or_create_pages(subchapter, confluence, chapter_page['id'])

    return confluence_page_map
