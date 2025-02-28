import io

from docutils.core import publish_parts


class RstToHtmlFragmentWriter:
    @staticmethod
    def write(rst_fragment):
        # How do I convert a docutils document tree into an HTML string?
        # https://stackoverflow.com/a/32168938/598057
        # Use a io.StringIO as the warning stream to prevent warnings from
        # being printed to sys.stderr.
        # https://www.programcreek.com/python/example/88126/docutils.core.publish_parts
        warning_stream = io.StringIO()
        settings = {"warning_stream": warning_stream}

        output = publish_parts(
            rst_fragment, writer_name="html", settings_overrides=settings
        )

        if warning_stream.tell() > 0:
            warnings = warning_stream.getvalue().rstrip("\n")
            print("error: problems when converting RST to HTML:")
            print(warnings)
            print("RST fragment: >>>")
            print(rst_fragment)
            print("<<<")
            exit(1)

        html = output["html_body"]
        return html
