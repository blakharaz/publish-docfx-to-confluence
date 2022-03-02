from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from confluence_client import ConfluenceClient


class ConfluenceContent:
    def __init__(self, html):
        self.html_soup = BeautifulSoup(html, 'lxml')

    def process_images(self, page_html_path: Path, confluence_page_id: str, confluence: ConfluenceClient):
        images = self.html_soup.select('img')
        for image in images:
            src = image.attrs['src']
            if urlparse(src).netloc == '':
                source_file_path = page_html_path.parent.joinpath(src).resolve()
                attachment = confluence.upload_image(page_id=confluence_page_id,
                                                     file_to_upload=source_file_path,
                                                     name=source_file_path.name)
                if 'results' in attachment:
                    attachment_name = attachment['results'][0]['title']
                else:
                    attachment_name = attachment['title']
                confluence_image = self.html_soup.new_tag(nsprefix="ac", name="image")
                confluence_image_attachment = self.html_soup.new_tag(nsprefix="ri", name="attachment")
                confluence_image_attachment.attrs["ri:filename"] = attachment_name
                confluence_image.append(confluence_image_attachment)
                image.replace_with(confluence_image)

    def process_links(self, page_html_path: Path, html_root: Path, page_map: dict):
        anchors = self.html_soup.select('a[href]')
        for anchor in anchors:
            href = anchor.attrs['href']
            if urlparse(href).netloc == '':
                target_path = page_html_path.parent.joinpath(href).resolve()
                source_file_path = target_path.with_suffix('.md').relative_to(html_root)
                if source_file_path in page_map:
                    mapped_page = page_map[source_file_path]
                    anchor.attrs['href'] = f'https://docs.osi.dataport.de{mapped_page["_links"]["webui"]}'

    def get_html(self):
        return str(self.html_soup)
