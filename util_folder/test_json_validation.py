import json
from io import StringIO
import sys

from util_folder.utils import fix_and_validate_json


def run_test(test_input, expected_output=None, expected_print=None):
    """
    Helper function to run a single test.
    Captures stdout and compares against expected_print if provided.
    Checks the returned value against expected_output if provided.
    """
    backup_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        result = fix_and_validate_json(test_input)
        printed = sys.stdout.getvalue()
    finally:
        sys.stdout = backup_stdout

    if expected_print is not None:
        # Strip to avoid newline mismatches
        printed = printed.strip()
        expected_print = expected_print.strip()
        assert printed == expected_print, f"Expected print: {expected_print}, Got: {printed}"

    if expected_output is not None:
        assert result == expected_output, f"Expected output: {expected_output}, Got: {result}"
    else:
        assert result is None, f"Expected None, got {result}"

    print("Test Passed!")


if __name__ == "__main__":
    # 1. Valid JSON with nodes
    # Description: Already valid JSON, should return the parsed dict.
    test_input_1 = '''
    {
      "nodes": [{"id": 1, "name": "NodeA"}],
      "links": [{"source": 1, "target": 1}]
    }'''
    expected_output_1 = {
        "nodes": [{"id": 1, "name": "NodeA"}],
        "links": [{"source": 1, "target": 1}]
    }
    run_test(test_input_1, expected_output=expected_output_1, expected_print="")

    # 2. No 'nodes' in JSON
    # Description: Should print a message and return None.
    test_input_2 = '{"links":[{"source":1,"target":2}]}'
    run_test(test_input_2, expected_output=None, expected_print="No 'nodes' found in the JSON.")

    # 3. Nodes present but malformed JSON
    # Description: The JSON ends abruptly, attempt to fix by appending ']}'
    test_input_3 = '{"nodes":[{"id":1,"name":"NodeA"},{"id":2,"name":"NodeB"}'
    # After fix:
    # It finds last '}', which is after NodeB's object: {"id":2,"name":"NodeB"}
    # and appends "]}". Final: {"nodes":[{"id":1,"name":"NodeA"},{"id":2,"name":"NodeB"}]}
    expected_output_3 = {
        "nodes": [{"id":1,"name":"NodeA"},{"id":2,"name":"NodeB"}]
    }
    run_test(test_input_3, expected_output=expected_output_3, expected_print="")

    # 4. JSON ends with ']}', but still malformed in another way
    # Description: If it ends with ']}', the code prints a specific message and returns None.
    test_input_4 = '{"nodes":[{"id":1,"name":"NodeA"}]]}'
    # It's already ending with ']}', but there's an extra ']' making it malformed.
    run_test(test_input_4, expected_output=None, expected_print="JSON is malformed in a different way, cannot fix easily.")

    # 5. No closing brace at all
    # Description: The JSON is incomplete and doesn't contain any '}' to fix from.
    test_input_5 = '''
    {
      "nodes": [{"id": 1, "name": "NodeA"}],
      "links": [{"source": 1, "target": 1},{"source": 1, "target": 3'''
    # There's no '}' at all after NodeA. The code should fail and print the message.
    expected_output_5 = {
        "nodes": [{"id":1,"name":"NodeA"}],
        "links": [{"source": 1, "target": 1}]
    }
    run_test(test_input_5, expected_output=expected_output_5, expected_print="")

    # 6. Cannot fix even after attempt
    # Description: After trying to fix, still invalid JSON.
    # For instance, truncated after id attribute, so even appending ']}'
    # won't create a valid JSON object.
    test_input_6 = '{"nodes":[{"id":1,"name":"NodeA"'
    # The fix step tries to find '}', it doesn't exist.
    # Same as test 5 actually, but let's try another scenario:
    # Include one brace but still broken.
    test_input_6_alt1 = '{"nodes":[{"id":1,"name":"NodeA"},'
    # last_brace_index should be the '}' of NodeA object,
    # after fix: {"nodes":[{"id":1,"name":"NodeA"}]} -> Missing quotes or something else?
    expected_output = {
        "nodes": [{"id":1,"name":"NodeA"}]
    }
    # Actually this would fix successfully, let's break differently:
    test_input_6_alt2 = '{"nodes":[{"id":1,"name":"NodeA","type":"Test"'
    # No closing '}' for the last node, fix would append after last '}', but there's none inside node.
    # Actually there's no '}' at all. It's same as test 5 scenario.
    # Let's add partial node so there's a '}', but something else breaks.
    test_input_6_alt3 = '{"nodes":[{"id":1,"name":"NodeA"}'  # Missing comma for next node or end
    # After fix: It finds '}' at NodeA, appends ']}':
    # becomes: {"nodes":[{"id":1,"name":"NodeA"}]}
    # This is actually valid. Let's force an error differently:
    # Introduce a weird character:
    test_input_6_alt4 = '{"nodes":[{"id":1,"name":"NodeA"}X'
    # last '}' is at NodeA, after fix: {"nodes":[{"id":1,"name":"NodeA"}]}X
    # Still invalid because extra 'X' at the end.
    # The fix approach doesn't remove chars after the last brace, just appends.
    # Let's assume it tries to fix and fails.
    run_test(test_input_6_alt1, expected_output=expected_output, expected_print="")
    run_test(test_input_6_alt2, expected_output=None, expected_print="No closing brace '}' found, cannot fix.")


    # 7. Nodes present but "nodes" is not a list
    # Description: Valid JSON but nodes is not a list, should print message and return None.
    test_input_7 = '{"nodes":{"id":1,"name":"NodeA"},"links":[]}'
    run_test(test_input_7, expected_output=None, expected_print="JSON does not contain a valid 'nodes' list.")

    # 8. After fixing, no 'nodes' list
    # Description: After append ']}', nodes might still not be a list.
    test_input_8 = '{"nodes":{"id":1,"name":"NodeA"}'
    # Fix: Finds last '}' for node object: that would be after "NodeA"}.
    # After fix: {"nodes":{"id":1,"name":"NodeA"}]} - still not valid nodes list
    run_test(test_input_8, expected_output=None, expected_print="Could not fix the JSON structure.")


    test_input_9 = '{"nodes":[{"visibility":"PUBLIC_LITERAL","id":1,"eClass":"PackageImport"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Deposit Cash/cheque","name":"Deposit Cash/cheque","id":8,"isLeaf":false,"isAbstract":false,"isFinalSpecialization":false,"eClass":"UseCase"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Withdraw Cash","name":"Withdraw Cash","id":9,"isLeaf":false,"isAbstract":false,"isFinalSpecialization":false,"eClass":"UseCase"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Transfer from other bank","name":"Transfer from other bank","id":10,"isLeaf":false,"isAbstract":false,"isFinalSpecialization":false,"eClass":"UseCase"},{"isDerived":false,"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Bank Customer_Display Menu","name":"Bank Customer_Display Menu","id":14,"isLeaf":false,"isAbstract":false,"isFinalSpecialization":false,"eClass":"Association"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::deposit cash/cheque ::ExtPoint","name":"ExtPoint","id":37,"isLeaf":false,"eClass":"ExtensionPoint"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":32,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":34,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":35,"value":0,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":36,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":37,"eClass":"Extend"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":42,"eClass":"Extend"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":47,"eClass":"Extend"}],"links":[{"source":0,"target":1},{"source":1,"target":0},{"source":4,"target":35},{"source":4,"target":36},{"source":5,"target":37},{"source":35,"target":4},{"source":36,"target":4},{"source":8,"target":32},{"source":8,"target":37},{"source":9,"target":37},{"source":37,"target":9},{"source":37,"target":8},{"source":10,"target":38},{"source":38,"target":10},{"source":14,"target":29},{"source":14,"target":30},{"source":14,"target":29},{"source":14,"target":30},{"source":14,"target":29},{"source":14,"target":30},{"source":29,"target":32},{"source":29,"target":14},{"source":29,"target":14},{"source":3'

    expected_output_9 = {
        "nodes": [{"visibility":"PUBLIC_LITERAL","id":1,"eClass":"PackageImport"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Deposit Cash/cheque","name":"Deposit Cash/cheque","id":8,"isLeaf":False,"isAbstract":False,"isFinalSpecialization":False,"eClass":"UseCase"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Withdraw Cash","name":"Withdraw Cash","id":9,"isLeaf":False,"isAbstract":False,"isFinalSpecialization":False,"eClass":"UseCase"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Transfer from other bank","name":"Transfer from other bank","id":10,"isLeaf":False,"isAbstract":False,"isFinalSpecialization":False,"eClass":"UseCase"},{"isDerived":False,"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Bank Customer_Display Menu","name":"Bank Customer_Display Menu","id":14,"isLeaf":False,"isAbstract":False,"isFinalSpecialization":False,"eClass":"Association"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::deposit cash/cheque ::ExtPoint","name":"ExtPoint","id":37,"isLeaf":False,"eClass":"ExtensionPoint"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":32,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":34,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":35,"value":0,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":36,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":37,"eClass":"Extend"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":42,"eClass":"Extend"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":47,"eClass":"Extend"}],
        "links": [{"source":0,"target":1},{"source":1,"target":0},{"source":4,"target":35},{"source":4,"target":36},{"source":5,"target":37},{"source":35,"target":4},{"source":36,"target":4},{"source":8,"target":32},{"source":8,"target":37},{"source":9,"target":37},{"source":37,"target":9},{"source":37,"target":8},{"source":10,"target":38},{"source":38,"target":10},{"source":14,"target":29},{"source":14,"target":30},{"source":14,"target":29},{"source":14,"target":30},{"source":14,"target":29},{"source":14,"target":30},{"source":29,"target":32},{"source":29,"target":14},{"source":29,"target":14}]
    }

    test_input_10 = '{"nodes":[{"visibility":"PUBLIC_LITERAL","id":1,"eClass":"PackageImport"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Deposit Cash/cheque","name":"Deposit Cash/cheque","id":8,"isLeaf":false,"isAbstract":false,"isFinalSpecialization":false,"eClass":"UseCase"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Withdraw Cash","name":"Withdraw Cash","id":9,"isLeaf":false,"isAbstract":false,"isFinalSpecialization":false,"eClass":"UseCase"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Transfer from other bank","name":"Transfer from other bank","id":10,"isLeaf":false,"isAbstract":false,"isFinalSpecialization":false,"eClass":"UseCase"},{"isDerived":false,"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Bank Customer_Display Menu","name":"Bank Customer_Display Menu","id":14,"isLeaf":false,"isAbstract":false,"isFinalSpecialization":false,"eClass":"Association"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::deposit cash/cheque ::ExtPoint","name":"ExtPoint","id":37,"isLeaf":false,"eClass":"ExtensionPoint"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":32,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":34,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":35,"value":0,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":36,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":37,"eClass":"Extend"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":42,"eClass":"Extend"},{"visibility":"PUBLIC_LITERAL","qualifiedName":null,"name":null,"id":47,"eClass":"Extend"}],"links":[{"source":0,"target":1},{"source":1,"target":0},{"source":4,"target":35},{"source":4,"target":36},{"source":5,"target":37},{"source":35,"target":4},{"source":36,"target":4},{"source":8,"target":32},{"source":8,"target":37},{"source":9,"target":37},{"source":37,"target":9},{"source":37,"target":8},{"source":10,"target":38},{"source":38,"target":10},{"source":14,"target":29},{"source":14,"target":30},{"source":14,"target":29},{"source":14,"target":30},{"source":14,"target":29},{"source":14,"target":30},{"source":29,"target":32},{"source":29,"target":14},{"source":29,"target":14},{"source":'

    run_test(test_input_9, expected_output=expected_output_9, expected_print="")

    expected_output_10 = {
        "nodes": [{"visibility":"PUBLIC_LITERAL","id":1,"eClass":"PackageImport"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Deposit Cash/cheque","name":"Deposit Cash/cheque","id":8,"isLeaf":False,"isAbstract":False,"isFinalSpecialization":False,"eClass":"UseCase"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Withdraw Cash","name":"Withdraw Cash","id":9,"isLeaf":False,"isAbstract":False,"isFinalSpecialization":False,"eClass":"UseCase"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Transfer from other bank","name":"Transfer from other bank","id":10,"isLeaf":False,"isAbstract":False,"isFinalSpecialization":False,"eClass":"UseCase"},{"isDerived":False,"visibility":"PUBLIC_LITERAL","qualifiedName":"model::Bank Customer_Display Menu","name":"Bank Customer_Display Menu","id":14,"isLeaf":False,"isAbstract":False,"isFinalSpecialization":False,"eClass":"Association"},{"visibility":"PUBLIC_LITERAL","qualifiedName":"model::deposit cash/cheque ::ExtPoint","name":"ExtPoint","id":37,"isLeaf":False,"eClass":"ExtensionPoint"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":32,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":34,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":35,"value":0,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":36,"value":1,"eClass":"LiteralInteger"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":37,"eClass":"Extend"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":42,"eClass":"Extend"},{"visibility":"PUBLIC_LITERAL","qualifiedName":None,"name":None,"id":47,"eClass":"Extend"}],
        "links": [{"source":0,"target":1},{"source":1,"target":0},{"source":4,"target":35},{"source":4,"target":36},{"source":5,"target":37},{"source":35,"target":4},{"source":36,"target":4},{"source":8,"target":32},{"source":8,"target":37},{"source":9,"target":37},{"source":37,"target":9},{"source":37,"target":8},{"source":10,"target":38},{"source":38,"target":10},{"source":14,"target":29},{"source":14,"target":30},{"source":14,"target":29},{"source":14,"target":30},{"source":14,"target":29},{"source":14,"target":30},{"source":29,"target":32},{"source":29,"target":14},{"source":29,"target":14}]
    }

    print(fix_and_validate_json(test_input_9))

    # After fix: {"nodes":{"id":1,"name":"NodeA"}]} - still not valid nodes list
    run_test(test_input_10, expected_output=expected_output_10, expected_print="")




    print("All tests passed successfully!")