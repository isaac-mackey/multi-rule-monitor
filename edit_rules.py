from language import *
from rule_parser import *

def compute_overlap_two_rules(rule1, rule2):
    
    head_to_body_overlap = 0
    for body_atom in rule1.body:
        for head_atom in rule2.head:
            if isinstance(body_atom, EventAtom) and isinstance(head_atom, EventAtom):
                if body_atom.predicate == head_atom.predicate:
                        head_to_body_overlap += 1
    for body_atom in rule2.body:
        for head_atom in rule1.head:
            if isinstance(body_atom, EventAtom) and isinstance(head_atom, EventAtom):
                if body_atom.predicate == head_atom.predicate:
                        head_to_body_overlap += 1
    # print("Rule 1: {}".format(rule1))
    # print("Rule 2: {}".format(rule2))
    # print("Overlap: {}".format(head_to_body_overlap))
    return head_to_body_overlap

def compute_overlap_ruleset(rules):
    overlap = 0
    if len(rules) <= 1:
        return 0
    for i in range(len(rules)):
        for j in range(i+1, len(rules)):
            overlap += compute_overlap_two_rules(rules[i], rules[j])
    return float(overlap)/(len(rules)*(len(rules)-1)/2)

if __name__ == "__main__":
     rulesets = [
        "num=4--overlap=0.5",
        "num=4--overlap=?b",
        "num=4--overlap=a?",
        "num=4--overlap=c?"
     ]

     for ruleset in rulesets:
        parsed_rules = []
        rules = parse_rule_file("rules/"+ruleset)
        for rule in rules:
            # print("Parsed rule: {}".format(rule))
            parsed_rules.append(rule)  
        print("Ruleset: {}".format(ruleset))
        print("Number of rules: {}".format(len(parsed_rules)))
        print("Ruleset overlap: {}".format(compute_overlap_ruleset(parsed_rules)))