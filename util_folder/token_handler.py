from transformers import AutoTokenizer
import os
from util_folder.extraction_xmi_remove_one_class_removed import parse_xmi, namespaces_org, get_classes, get_class_attributes, ET
import shutil
from util_folder.json_extraction_util import count_json_files_with_strings


def count_files_in_folder(folder_path: str) -> int:
    """
    Counts the number of files in a folder.

    :param folder_path: The path to the folder.
    :return: The number of files in the folder.
    """
    file_count = 0
    for _ in os.listdir(folder_path):
        file_count += 1
    return file_count


class TokenCounter:

    def __init__(self, model_id="google/gemma-2-2b"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

    def count_tokens(self, text: str) -> int:
        """
        Returns the number of tokens in a text string using the provided tokenizer.

        :param text: The input text to tokenize.
        :return: The number of tokens in the text.
        """
        encoded_tokens = self.tokenizer.encode(text)
        return len(encoded_tokens)

    def count_tokens_in_file(self, file_path: str) -> int:
        """
        Reads the content of the file and returns the number of tokens using the provided tokenizer.

        :param file_path: The path to the file.
        :return: The number of tokens in the file content.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return self.count_tokens(content)

    def count_tokens_in_xmi_folder(self, folder_path: str):
        """
        Counts the number of tokens for each file in a folder and categorizes them.

        :param folder_path: The path to the folder containing the files.
        """
        token_counts = {
            '<1000': 0,
            '<2000': 0,
            '<3000': 0,
            '<4000': 0,
            '<5000': 0,
            '<6000': 0,
            '<7000': 0,
            '<=8192': 0,
            '>8192': 0
        }

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                num_tokens = self.count_tokens_in_file(file_path)
                if num_tokens < 1000:
                    token_counts['<1000'] += 1
                elif num_tokens < 2000:
                    token_counts['<2000'] += 1
                elif num_tokens < 3000:
                    token_counts['<3000'] += 1
                elif num_tokens < 4000:
                    token_counts['<4000'] += 1
                elif num_tokens < 5000:
                    token_counts['<5000'] += 1
                elif num_tokens < 6000:
                    token_counts['<6000'] += 1
                elif num_tokens < 7000:
                    token_counts['<7000'] += 1
                elif num_tokens <= 8192:
                    token_counts['<=8192'] += 1
                elif num_tokens > 8192:
                    token_counts['>8192'] += 1

        for category, count in token_counts.items():
            print(f"Number of xmi files with tokens {category}: {count}")

    def read_until_first_xmi_class(self, file_path: str) -> str:
        """
        Reads the content of the file until it encounters the string 'packagedElement xsi:type="uml:Class"'.

        :param file_path: The path to the file.
        :return: The content read until the specified string is found.
        """
        content = []
        search_string = 'packagedElement xsi:type="uml:Class"'

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                content.append(line)
                if search_string in line:
                    break

        return ''.join(content)

    def count_tokens_before_first_class(self, folder_path: str):
        """
        Counts the number of tokens for each file in a folder before the first class.

        :param folder_path: The path to the folder containing the files.
        """
        token_counts = {
            '<100': 0,
            '<200': 0,
            '<300': 0,
            '<400': 0,
            '<500': 0,
            '<600': 0,
            '<700': 0,
            '<800': 0,
            '<900': 0,
            '>=900': 0,
        }

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                xmi_before_class = self.read_until_first_xmi_class(file_path)
                num_tokens = self.count_tokens(xmi_before_class)
                if num_tokens < 100:
                    token_counts['<100'] += 1
                elif num_tokens < 200:
                    token_counts['<200'] += 1
                elif num_tokens < 300:
                    token_counts['<300'] += 1
                elif num_tokens < 400:
                    token_counts['<400'] += 1
                elif num_tokens < 500:
                    token_counts['<500'] += 1
                elif num_tokens < 600:
                    token_counts['<600'] += 1
                elif num_tokens < 700:
                    token_counts['<700'] += 1
                elif num_tokens < 800:
                    token_counts['<800'] += 1
                elif num_tokens < 900:
                    token_counts['<900'] += 1
                elif num_tokens >= 900:
                    token_counts['>=900'] += 1

        for category, count in token_counts.items():
            print(f"Number of xmi files with tokens before first class {category}: {count}")

    def count_tokens_of_classes_with_att(self, folder_path: str):
        """
        Counts the number of tokens for each file in a folder before the first class.

        :param folder_path: The path to the folder containing the files.
        """
        token_sums = {
            'class_with_att_num_1': 0,
            'class_with_att_num_2': 0,
            'class_with_att_num_3': 0,
            'class_with_att_num_4': 0,
            'class_with_att_num_5': 0,
            'class_with_att_num_6': 0,
            'class_with_att_num_>=7': 0
        }

        class_counts = {
            'class_with_att_num_1': 0,
            'class_with_att_num_2': 0,
            'class_with_att_num_3': 0,
            'class_with_att_num_4': 0,
            'class_with_att_num_5': 0,
            'class_with_att_num_6': 0,
            'class_with_att_num_>=7': 0
        }

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            root = parse_xmi(file_path)
            classes = get_classes(root, namespaces_org)
            for class_elem in classes:
                attributes = get_class_attributes(class_elem)
                num_attributes = len(attributes)
                class_text = ET.tostring(class_elem, encoding='unicode')
                attributes_text = ''.join([ET.tostring(attr, encoding='unicode') for attr in attributes])
                combined_text = class_text + attributes_text
                num_tokens = self.count_tokens(combined_text)

                if num_attributes == 1:
                    token_sums['class_with_att_num_1'] += num_tokens
                    class_counts['class_with_att_num_1'] += 1
                elif num_attributes == 2:
                    token_sums['class_with_att_num_2'] += num_tokens
                    class_counts['class_with_att_num_2'] += 1
                elif num_attributes == 3:
                    token_sums['class_with_att_num_3'] += num_tokens
                    class_counts['class_with_att_num_3'] += 1
                elif num_attributes == 4:
                    token_sums['class_with_att_num_4'] += num_tokens
                    class_counts['class_with_att_num_4'] += 1
                elif num_attributes == 5:
                    token_sums['class_with_att_num_5'] += num_tokens
                    class_counts['class_with_att_num_5'] += 1
                elif num_attributes == 6:
                    token_sums['class_with_att_num_6'] += num_tokens
                    class_counts['class_with_att_num_6'] += 1
                else:
                    token_sums['class_with_att_num_>=7'] += num_tokens
                    class_counts['class_with_att_num_>=7'] += 1

        for category in token_sums:
            if class_counts[category] > 0:
                average_tokens = token_sums[category] / class_counts[category]
            else:
                average_tokens = 0
            print(f"Average number of tokens for {category}: {average_tokens}")

    def count_tokens_folder_in_folder(self, base_folder_path):
        """
        Counts the number of tokens in each folder in the base folder.
        :param base_folder_path: the base folder path
        :return: none
        """

        token_counts = {
            '<1000': 0,
            '<2000': 0,
            '<3000': 0,
            '<4000': 0,
            '<5000': 0,
            '<6000': 0,
            '<7000': 0,
            '<=8192': 0,
            '>8192': 0
        }

        for folder_name in os.listdir(base_folder_path):
            folder_path = os.path.join(base_folder_path, folder_name)
            if os.path.isdir(folder_path):
                new_file = f"{folder_name.replace('.xmi', '')}.json"
                json_file_path = os.path.join(folder_path, new_file)
                if os.path.isfile(json_file_path):
                    num_tokens = self.count_tokens_in_file(json_file_path)
                    if num_tokens < 1000:
                        token_counts['<1000'] += 1
                    elif num_tokens < 2000:
                        token_counts['<2000'] += 1
                    elif num_tokens < 3000:
                        token_counts['<3000'] += 1
                    elif num_tokens < 4000:
                        token_counts['<4000'] += 1
                    elif num_tokens < 5000:
                        token_counts['<5000'] += 1
                    elif num_tokens < 6000:
                        token_counts['<6000'] += 1
                    elif num_tokens < 7000:
                        token_counts['<7000'] += 1
                    elif num_tokens <= 8192:
                        token_counts['<=8192'] += 1
                    elif num_tokens > 8192:
                        token_counts['>8192'] += 1

        for category, count in token_counts.items():
            print(f"Number of json files with tokens {category}: {count}")

    def collect_json_files(self, base_folder_path: str, target_folder: str, collect_num_tokens):
        """
        Collects the json files from the base folder that have less than the specified number of tokens.
        :param base_folder_path: base folder path
        :param target_folder: target folder path
        :param collect_num_tokens: the number of tokens less than which the files will be collected
        :return: none
        """
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        for folder_name in os.listdir(base_folder_path):
            folder_path = os.path.join(base_folder_path, folder_name)
            if os.path.isdir(folder_path):
                new_file = f"{folder_name.replace('.xmi', '')}.json"
                json_file_path = os.path.join(folder_path, new_file)
                if os.path.isfile(json_file_path):
                    num_tokens = self.count_tokens_in_file(json_file_path)
                    if num_tokens < collect_num_tokens:
                        shutil.copy(json_file_path, target_folder)

    def max_tokens_in_files(self, base_folder_path: str):
        max_tokens = 0
        for file_name in os.listdir(base_folder_path):
            file_path = os.path.join(base_folder_path, file_name)
            num_tokens = self.count_tokens_in_file(file_path)
            if num_tokens > max_tokens:
                max_tokens = num_tokens
        print(f"Max number of tokens in json files: {max_tokens}")




if __name__ == "__main__":
    token = TokenCounter()

    base_json_folder = '../modelset/graph/repo-genmymodel-uml/data'
    folders = [
        'json_files/json_dataset/json2000',
        'json_files/json_dataset/json3000',
        'json_files/json_dataset/json4000',
        'json_files/json_dataset/json5000',
        'json_files/json_dataset/json6000',
        'json_files/json_dataset/json7000',
        'json_files/json_dataset/json8000',
        'json_files/json_dataset/json8500',
        'json_files/json_dataset/json9000',
        'json_files/json_dataset/json10000'
    ]

    for i, folder in enumerate(folders, start=2):
        token.collect_json_files(base_json_folder, folder, i * 1000)


    for folder in folders:
        print(f"max token {folder.split('/')[-1]}: ")
        token.max_tokens_in_files(folder)
        print(f"There are : {count_files_in_folder(folder)} files in {folder.split('/')[-1]}")
