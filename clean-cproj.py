
import os
import sys
import json
from xml.etree import ElementTree


NAMESPACE = "http://schemas.microsoft.com/developer/msbuild/2003"
INDENT_UNIT = "  "


def sort_group(parent_element, sort_rules):
    sortable = []
    unsortable = []
    parent_tag = parent_element.tag.partition('}')[-1]
    for element in parent_element:
        tag = element.tag.partition('}')[-1]
        if tag in sort_rules["children"]:
            if sort_rules["sortby"] == "attribute":
                attr_key = sort_rules["attribute"]
                key = element.attrib[attr_key]
            elif sort_rules["sortby"] == "value":
                key = element.text
            else:
                print("Warning: Could not sort '%s' element, invalid rules"
                      % (parent_tag,))
                return 0, len(parent_element)

            if key in [x[0] for x in sortable]:
                print("Ignoring duplicate value %s" % (key,))
            else:
                sortable.append((key, element))
        else:
            unsortable.append(element)
            print("Warning: Unexpected item '%s' as child of '%s'" %
                  (tag, parent_tag))
    count_sorted = len(sortable)
    count_not_sorted = len(unsortable)
    # print("  Group '%s': total=%d sorted=%d  unsorted=%d" %
    #       (parent_tag, len(parent_element), count_sorted, count_not_sorted))
    sortable.sort()
    unsortable.extend(sortable)
    parent_element[:] = [item[-1] for item in unsortable]
    return count_sorted, count_not_sorted


def sort_all_groups(root, sortable_items):
    count_groups = 0
    count_sorted = 0
    count_not_sorted = 0
    for element in root.iter():
        tag = element.tag.partition('}')[-1]
        # print("Debug: Current tag %s" % tag)
        if tag in sortable_items:
            sorted_cnt, unsorted_cnt = sort_group(element, sortable_items[tag])
            count_groups += 1
            count_sorted += sorted_cnt
            count_not_sorted += unsorted_cnt
    print("  Sorted %d elements in %d groups (skipped %d)"
          % (count_sorted, count_groups, count_not_sorted))


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


def substitue(root, target_elements):
    total = 0

    for tag, properties in target_elements.items():
        total += search(root, properties["path"], tag, properties["default"])

    if total:
        print("\n  %d elements changed for committing." % (total,))
    else:
        print("  No element changes to make.")


def run_script(file_path, config):
    ElementTree.register_namespace('', NAMESPACE)
    project_tree = ElementTree.parse(file_path)
    root = project_tree.getroot()

    print("Making Element substitutions...")
    substitue(root, config["substitutions"])

    print("Sorting list elements...")
    sort_all_groups(root, config["sorts"])

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
