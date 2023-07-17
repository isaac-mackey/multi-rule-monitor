import ast

def get_names(c):
    return list(set([ node.id for node in ast.walk(ast.parse(c)) if isinstance(node, ast.Name)
    ]))

class Rule:
    def __init__(self, rule_id, body, head):
        self.rule_id = rule_id
        self.body = body
        self.head = head

    def __str__(self):
        return str(self.head) + " :- " + str(self.body)

    def __repr__(self):
        return str(self.head) + " :- " + str(self.body)
    
class EventAtom:
    def __init__(self, predicate, terms, timestamp_variable):
        self.predicate = predicate
        for x in terms+[timestamp_variable]:
            if "_" in x:
                raise Exception("EventAtom terms cannot contain underscores")
        self.terms = terms
        self.timestamp_variable = timestamp_variable

    def __repr__(self):
        return self.predicate + "(" + ", ".join(self.terms) + ")" + self.timestamp_variable

class ArithmeticAtom:
    def __init__(self, expression=True, operator=[], terms=[]):
        self.expression = expression
        self.operator = operator
        self.terms = get_names(str(expression))

    def __repr__(self):
        return str(self.expression)
    
    def __str__(self):
        return str(self.expression)

'''define a Class for aggregation expressions with a operator, a window, and a source'''
class AggregationRule:
    def __init__(self, head, operator, agg_attribute, window, source):
        self.head = head
        self.operator = operator
        self.agg_attribute = agg_attribute
        self.window = window
        self.source = source

    def __str__(self):
        return self.head + " :- " + self.operator + " " + self.agg_attribute + " " + self.window + " " + self.source

    def __repr__(self):
        return self.head + " :- " + self.operator + " " + self.agg_attribute + " " + self.window + " " + self.source

'''write a parser for aggregation rule heads that takes a string of the form, e.g.:
- event_name(X, max(amount), t)
and returns 
- event_name, [X, max_amount, t], max, amount'''
def parse_aggregation_head(atom_string):
    
    '''check for two left parentheses'''
    if atom_string.count("(") < 2:
        raise Exception("No aggregated attribute found in head of rule")

    head_event_name, remaining = atom_string.split("(", 1)
    attributes = remaining.strip('(').strip(')').split(",")
    operator = None
    for i in range(len(attributes)):
        attr = attributes[i]
        if "max" in attr:
            operator = "max"
            agg_attribute = attr.strip("max").strip("(").strip(")")
            continue
        elif "min" in attr:
            operator = "min"
            agg_attribute = attr.strip("min").strip("(").strip(")")
            continue
        elif "avg" in attr:
            operator = "avg"
            agg_attribute = attr.strip("avg").strip("(").strip(")")
            continue
        elif "sum" in attr:
            operator = "sum"
            agg_attribute = attr.strip("sum").strip("(").strip(")")
            continue
        else:
            pass
    if operator is None:
        raise Exception("No aggregation operator found in head of rule")
    head_event = EventAtom(head_event_name, attributes)
    return head_event, attributes, operator, agg_attribute

'''write a parser that takes a string of the form:
OVER TUMBLING(s, s+10) FROM event_name(amount, s)
and returns an aggregation expression'''
def parse_aggregation_body(expression_string):
    over, remaining = expression_string.split('OVER')
    window, source = remaining.split('FROM')
    return window, source

'''write a parser that takes a string of the form, e.g.:
maxAmount(X, max(amount), s, s+10) :- OVER TUMBLING(s, s+10) FROM event_name(X, amount, t)
and returns a rule
'''
def parse_aggregation_rule(rule_string):
    head_string, body = rule_string.split(":-")
    head_event, attributes, operator, agg_attribute = parse_aggregation_head(head_string)
    window, source = parse_aggregation_body(body)
    return AggregationRule(head_event, operator, agg_attribute, window, source)

test = "maxAmount(X, max(amount), s, s+10) :- OVER TUMBLING(s, s+10) FROM event_name(X, amount, t)"