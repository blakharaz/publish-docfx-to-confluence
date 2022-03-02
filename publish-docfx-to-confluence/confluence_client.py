from urllib.parse import quote
from pathlib import Path
from atlassian import Confluence


def create_placeholder_content(title: str):
    return f'<h1>{title}</h1><p>This is a placeholder</p>'


class ConfluenceClient:
    def __init__(self, url, token, space):
        self.confluence = Confluence(url=url, token=token)
        self.space = space

    def find_page(self, title):
        page = self.confluence.get_page_by_title(space=self.space, title=title)
        return page

    def get_direct_children(self, page_id):
        return self.confluence.get_child_pages(page_id=page_id)

    def get_all_children(self, page_id):
        pages = self.confluence.get_child_pages(page_id=page_id)
        for child in pages:
            pages += self.get_all_children(child['id'])
        return pages

    def create_placeholder_page(self, parent_id, title):
        return self.confluence.create_page(space=self.space, parent_id=parent_id, title=title, representation='storage',
                                           body=create_placeholder_content(quote(title)))

    def replace_page(self, page_id, title, html_content):
        self.confluence.update_page(page_id=page_id, title=title, body=html_content, representation='storage')

    def upload_image(self, page_id: str, file_to_upload: Path, name: str):
        return self.confluence.attach_file(filename=str(file_to_upload.resolve()),
                                           page_id=page_id,
                                           name=name,
                                           space=self.space)

    def delete_all_children_of_page(self, page_id: str):
        children = self.get_direct_children(page_id=page_id)
        for child in children:
            self.delete_all_children_of_page(child["id"])
            self.confluence.remove_page(child["id"])
