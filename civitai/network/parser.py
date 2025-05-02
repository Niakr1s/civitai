import lxml.html


def extract_mantine_class(html):
    tree = lxml.html.fromstring(html)
    mantine_elements = tree.cssselect(".mantine-lrbwmi")
    return [element.attrib["poster"] for element in mantine_elements]


if __name__ == "__main__":
    html_content = """
    <html>
        <body>
            <div class="mantine-lrbwmi" poster="poster1">Element 1</div>
            <div class="mantine-lrbwmi" poster="poster2">Element 2</div>
        </body>
    </html>
    """
    mantine_classes = extract_mantine_class(html_content)
    print(mantine_classes)
