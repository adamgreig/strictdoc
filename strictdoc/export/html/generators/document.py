from jinja2 import Environment, PackageLoader, StrictUndefined

from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class DocumentHTMLGenerator:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates"),
        undefined=StrictUndefined,
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(
        config,
        document_tree,
        document,
        traceability_index,
        link_renderer,
        standalone=False,
    ):
        output = ""

        markup_renderer = MarkupRenderer()

        template = DocumentHTMLGenerator.env.get_template(
            "single_document/document.jinja.html"
        )

        root_path = document.meta.get_root_path_prefix()
        static_path = f"{root_path}/_static"
        document_iterator = traceability_index.get_document_iterator(document)

        output += template.render(
            config=config,
            document=document,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            renderer=markup_renderer,
            standalone=standalone,
            document_type=DocumentType.document(),
            root_path=root_path,
            static_path=static_path,
            document_iterator=document_iterator,
        )

        return output
