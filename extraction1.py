import xml.etree.ElementTree as ET
import random
import copy
import os


def parse_xmi(file_path):
    """
    Returns the root element for this tree.
    :param file_path: the file path to the XMI file
    :return: the root
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    print(root.tag)
    return root


def get_namespaces(file_path):
    """
    Returns the namespaces in the XMI file.
    :param file_path: the file path to the XMI file
    :return: the namespaces
    """
    namespaces = dict([node for _, node in ET.iterparse(file_path, events=['start-ns'])])
    return namespaces


def get_classes(root, namespaces):
    """
    Returns the UML classes in the XMI file.
    :param root: the root element
    :param namespaces: the namespaces
    :return: the UML classes
    """
    # Look for elements with xsi:type="uml:Class"
    return root.findall(".//*[@xsi:type='uml:Class']", namespaces=namespaces)


def get_class_attributes(class_elem):
    """
    Returns the attributes of a UML class.
    :param class_elem: the class element
    :return: the attributes of the class
    """
    # Look for ownedAttribute elements
    return class_elem.findall("ownedAttribute")


def remove_random_attributes(class_elem, removal_probability=0.5):
    """
    Removes random attributes from a UML class element.
    :param class_elem: the class element
    :param removal_probability: the probability of removing an attribute
    """
    attributes = get_class_attributes(class_elem)
    for attr in attributes:
        if random.random() < removal_probability:
            print(attr.attrib)
            class_elem.remove(attr)

def remove_element(root, element):
    """
    Removes an element from the tree.
    :param root:  the root element
    :param element:  the element to remove
    :return:  the modified tree
    """
    for parent in root.iter():
        for child in parent:
            if child == element:
                print(child.attrib)
                parent.remove(child)
                return



def remove_elements_with_matching_attribute_value(root, class_id):
    """
    Removes elements with any attribute value matching the specified class_id.

    :param root: The root element of the XML tree.
    :param class_id: The class ID to match against attribute values.
    """
    # Create a list to hold elements to be removed to avoid modifying the tree while iterating
    elements_to_remove = []
    print(class_id)

    # Use a recursive function to track parent elements
    def find_elements_to_remove(elem, parent=None):
        # Check each attribute of the element for a match with class_id
        if class_id in elem.attrib.values():
            elements_to_remove.append((parent, elem))
        # Recursively check all child elements
        for child in elem:
            find_elements_to_remove(child, elem)

    # Start the recursive search from the root
    find_elements_to_remove(root)

    # Remove the collected elements from their parents
    for parent, element in elements_to_remove:
        if parent is not None:
            parent.remove(element)


def create_modified_xmi(root, namespaces):
    modified_root = copy.deepcopy(root)
    classes = get_classes(modified_root, namespaces)

    for class_elem in classes:
        r = random.random()
        if r < 0.7:  # 70% chance to remove attributes, 30% to remove the entire class
            print("attribute")
            remove_random_attributes(class_elem)

        else:
            print("class")
            print(class_elem.attrib)

            # Check if the class element has an attribute ID
            class_id = class_elem.attrib.get(f"{{{namespaces['xmi']}}}id", None)
            if class_id:
                # If class_elem has an attribute ID, call remove_elements_with_matching_attribute_value
                remove_elements_with_matching_attribute_value(modified_root, class_id)
            else:
                # If class_elem does not have an attribute ID, call remove_element
                remove_element(modified_root, class_elem)



    return modified_root


def register_namespaces(namespaces):
    """
    Registers namespaces with their prefixes to ensure they are preserved in the output.
    :param namespaces: A dictionary of namespace prefixes to URIs.
    """
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)


def process_folder_to_file(input_folder, output_folder):
    """
    Processes all XMI files in the input folder and generates a single output file with removed parts.
    :param input_folder:  the input folder(contains the folder with complete XMI files)
    :param output_folder:  the output folder(contains the folder with modified XMI files)
    """
    # Create the output folder if it does not exist
    os.makedirs(output_folder, exist_ok=True)
    # Get all XMI files in the input folder
    # The xmi_files will be a list of strings, where each string represents the filename of a
    # .xmi file located in the input_folder.
    xmi_files = [f for f in os.listdir(input_folder) if f.endswith('.xmi')]

    # Process each XMI file
    for xmi_file in xmi_files:
        input_file_path = os.path.join(input_folder, xmi_file)
        root = parse_xmi(input_file_path)
        namespaces = get_namespaces(input_file_path)
        file_output = os.path.splitext(xmi_file)[0]

        # Register namespaces to preserve prefixes
        register_namespaces(namespaces)

        modified_root = create_modified_xmi(root, namespaces)
        output_file = os.path.join(output_folder, file_output + "_modified.xmi")
        tree = ET.ElementTree(modified_root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True, )

        print(f"Processed {xmi_file} and generated modified XMI file in {file_output}")


if __name__ == '__main__':
    input_folder = "modelset_extract/modelset/raw-data/repo-genmymodel-uml/data"
    output_folder = "output"
    process_folder_to_file(input_folder, output_folder)
