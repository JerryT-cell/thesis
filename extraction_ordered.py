import xml.etree.ElementTree as ET
import random
import copy
import os


def get_namespaces(file_path):
    namespaces = dict([node for _, node in ET.iterparse(file_path, events=['start-ns'])])
    return namespaces


class XMIOperations:
    def __init__(self, namespaces):
        self.namespaces = namespaces

    def parse_xmi(self, file_path):
        """
Returns the root element for this tree.
:param file_path: the file path to the XMI file
:return: the root
"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        print(root.tag)
        return root

    def get_classes(self, root):
        return root.findall(".//*[@xsi:type='uml:Class']", namespaces=self.namespaces)

    def get_class_attributes(self, class_elem):
        return class_elem.findall("ownedAttribute")

    def remove_random_attributes(self, class_elem, removal_probability=0.5):
        attributes = self.get_class_attributes(class_elem)
        attributes_removed = []
        for attr in attributes:
            if random.random() < removal_probability:
                print(attr.attrib)
                attributes_removed.append(attr)
                class_elem.remove(attr)

    def remove_elements_with_matching_attribute_value(self, root, class_id):
        elements_to_remove = []
        elements_to_return = []
        print(class_id)

        def find_elements_to_remove(elem, parent=None):
            if class_id in elem.attrib.values():
                elements_to_remove.append((parent, elem))
                elements_to_return.append(elem)
            for child in elem:
                find_elements_to_remove(child, elem)

        find_elements_to_remove(root)
        for parent, elem in elements_to_remove:
            if parent is not None:
                parent.remove(elem)
        return elements_to_return

    def create_modified_xmi_2(self, root):
        modified_root = copy.deepcopy(root)
        classes = self.get_classes(modified_root)

        for class_elem in classes:
            r = random.random()
            if r < 0.7:
                print("attribute")
                self.remove_random_attributes(class_elem)
            else:
                print("class")
                self.remove_elements_with_matching_attribute_value(modified_root,
                                                                   class_elem.attrib[f"{{{self.namespaces['xmi']}}}id"])
        return modified_root

    def create_xmi_from_elements(self, element_trees, filepath):
        root = ET.Element("XMI")
        self.register_namespaces()

        for tree in element_trees:
            root.append(tree)

        input_file_path = os.path.join(filepath, "test")
        xml_string = ET.tostring(root, encoding='unicode', method='xml')
        with open(input_file_path + ".xmi", "w") as file:
            file.write(xml_string)

    def remove_a_class(self, root):
        modified_root = copy.deepcopy(root)
        classes = self.get_classes(modified_root)
        class_elem = random.choice(classes)
        elements = self.remove_elements_with_matching_attribute_value(modified_root,
                                                                      class_elem.attrib[f"{{{self.namespaces['xmi']}}}id"])
        return elements

    def test(self, input_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        root = self.parse_xmi(input_folder)
        namespaces = get_namespaces(input_folder)
        elements = self.remove_a_class(root)
        self.create_xmi_from_elements(elements, output_folder)

    def register_namespaces(self):
        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)