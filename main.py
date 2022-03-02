import argparse
from pathlib import Path

from confluence_client import ConfluenceClient
from confluence_content import ConfluenceContent
from confluence_page_map import find_or_create_pages
from docfx_configuration import DocfxConfiguration


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Publish DocFx documentation to Confluence.')
    parser.add_argument('--docfx_configuration', type=Path, required=True,
                        help='Path to the json configuration for DocFx')
    parser.add_argument('--table_of_contents', type=Path, required=True,
                        help='Path to the root table of contents file')
    parser.add_argument('--title_prefix', type=str, default='',
                        help='Prefix for all pages, to avoid clashes with existing page titles')
    parser.add_argument('--confluence_server', type=str, required=True, help='Confluence server URL')
    parser.add_argument('--confluence_space', type=str, required=True, help='Confluence space')
    parser.add_argument('--confluence_token', type=str, required=True, help='Access token for Confluence')
    parser.add_argument('--root_page_id', type=str, required=True, help='Confluence page ID of the root page')
    parser.add_argument('--update_mode', type=str, choices=['update_existing', 'delete_existing'],
                        default='update_existing')

    args = parser.parse_args()

    configuration = DocfxConfiguration()
    configuration.read_configuration(args.docfx_configuration)
    configuration.read_table_of_contents(args.table_of_contents, title_prefix=args.title_prefix)

    confluence = ConfluenceClient(url=args.confluence_server,
                                  token=args.confluence_token,
                                  space=args.confluence_space)

    if args.update_mode == 'delete_existing':
        confluence.delete_all_children_of_page(args.root_page_id)

    page_map = find_or_create_pages(configuration.root, confluence, args.root_page_id)

    for path, page in page_map.items():
        html_path = configuration.destination_directory.joinpath(path).with_suffix(".html")
        html = open(html_path, encoding='utf-8').read()

        content = ConfluenceContent(html)
        content.process_images(page_html_path=html_path,
                               confluence_page_id=page['id'],
                               confluence=confluence)
        content.process_links(page_html_path=html_path,
                              html_root=configuration.destination_directory,
                              page_map=page_map)

        confluence.replace_page(page_id=page['id'], html_content=content.get_html(), title=page['title'])

    print("done")
