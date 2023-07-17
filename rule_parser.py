import re
from language import *

def extract_text_from_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read().replace('\n', '')
    return text

def parse_rule_file(rule_file_path):
    rule_syntax = extract_text_from_file(rule_file_path)
    rules = parse_rule_syntax(rule_syntax)
    return rules

def parse_rule_syntax(rule_syntax):

    rules = []

    pattern = r"Rule\(\s*rule_id=([^\s,]+),\s*body=\[(.*?)\],\s*head=\[(.*?)\]\s*\)"
    matches = re.findall(pattern, rule_syntax, re.DOTALL)
    for match in matches:
        rule_id = match[0]
        body_str = match[1]
        head_str = match[2]
        # Parse the body and head into EventAtoms
        body = parse_atoms(body_str)
        head = parse_atoms(head_str)
        rules.append(Rule(rule_id, body, head))
    
    return rules

def parse_atoms(atoms_str):
    event_atoms = []
    arithmetic_atoms = []

    atom_regex = r'EventAtom\("([^"]+)", \[(.*?)\], "([^"]+)"\)'
    matches = re.findall(atom_regex, atoms_str)
    for match in matches:
        event_name = match[0]
        variables = match[1].split(',')
        variables = [variable.replace("'","").replace('"','') for variable in variables]
        variables = ['eid'] + variables
        timestamp_variable = match[2]

        event_atom = EventAtom(event_name, variables, timestamp_variable)
        event_atoms.append(event_atom)
    
    atom_regex= r'ArithmeticAtom\((.*?)\)'

    matches = re.findall(atom_regex, atoms_str)
    for match in matches:
        arithmetic_atom = ArithmeticAtom(match)
        arithmetic_atoms.append(arithmetic_atom)

    return event_atoms+arithmetic_atoms

if __name__ == "__main__":
    # Example usage
    rule_syntax = 'rule_0 = Rule(rule_id=0, body=[EventAtom("E1", ["v1"], "x"), EventAtom("E3", ["v3"], "y")], head=[EventAtom("E1", ["v2"], "z"), EventAtom("E2", ["v3"], "w")])'

    parsed_rule = parse_rule_syntax(rule_syntax)
    print(parsed_rule.rule_id)
    print(parsed_rule.body)
    print(parsed_rule.head)