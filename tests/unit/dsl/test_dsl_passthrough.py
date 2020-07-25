from strictdoc.backend.dsl.models import Document
from strictdoc.backend.dsl.reader import SDReader
from strictdoc.backend.dsl.writer import SDWriter


def test_01_basic_test():
    input = """
<DOCUMENT>

<SECTION>
LEVEL: 0

<REQUIREMENT>
STATEMENT: System shall do X

<REQUIREMENT>
TITLE: Optional title B
STATEMENT: System shall do Y
COMMENT: This requirement is very important
""".lstrip()

    reader = SDReader()

    document = reader.read(input)
    assert isinstance(document, Document)

    writer = SDWriter()
    output = writer.write(document)

    print(output)
    assert input == output
