
import os
import sys
import json
from xml.etree import ElementTree


NAMESPACE = "http://schemas.microsoft.com/developer/msbuild/2003"
INDENT_UNIT = "  "


def indent(elem, level=0):
    """Copied from http://effbot.org/zone/element-lib.htm#prettyprint"""
    i = "\n" + level * INDENT_UNIT
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + INDENT_UNIT
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def search(element, path, search_tag, text, level=0):
    changes = 0
    tag = element.tag.rpartition('}')[-1]
    # print("%s%s" % (" " * 4 * level, tag))
    if level < len(path):
        if path[level] == tag:
            for child in element:
                changes += search(child, path, search_tag, text, level + 1)
    else:
        # print("Tag: %s" % tag)
        if tag == search_tag and element.text != text:
            print("<%s/%s> '%s' => '%s'" % ('/'.join(path), tag, element.text,
                                            text))
            element.text = text
            changes += 1
    return changes


def run_script(file_path, target_elements):
    ElementTree.register_namespace('', NAMESPACE)
    project_tree = ElementTree.parse(file_path)
    root = project_tree.getroot()

    total = 0

    for tag, properties in target_elements.items():
        total += search(root, properties["path"], tag, properties["default"])

    if total:
        print("\n%d elements changed for committing." % (total,))
    else:
        print("No element changes to make.")

    print("Writing formatted XML...")
    indent(root)
    project_tree.write(file_path, encoding="UTF-8", xml_declaration=True)


def main():
    try:
        file_path = sys.argv[1]
    except IndexError:
        print("ERROR: Script requires an XML filepath to parse and clean.")
        return 1

    try:
        with open(sys.argv[2]) as handle:
            target_elements = json.load(handle)
    except IndexError:
        print("ERROR: Script requires a JSON file defining what to clean out.")
        return 1
    except FileNotFoundError:
        print("ERROR: Could not find file '%s'" % (sys.argv[2]))
        return 1

    script_name = os.path.basename(__file__)
    first_line = "Beginning script '%s'" % (script_name,)
    print(first_line)
    print("-" * len(first_line))
    run_script(file_path, target_elements)
    print("-" * len(first_line))
    print("Script '%s' finished" % (script_name,))
    return 0


if __name__ == '__main__':
    exit(main())
