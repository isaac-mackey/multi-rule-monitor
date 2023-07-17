from language import *
from stream import *
from event_parser import *
import ast
import re
import time
from z3 import *
import copy

class Monitor:
    def __init__(self, rules):
        self.rules = rules
        self.rule_tables = [RuleTables(rule) for rule in rules]
        self.current_timestamp = 0
        self.batch_size = 1

    def process_log_file(self, log_file):

        print("Processing log file: {}".format(log_file))
        matches = re.findall(r'e=(\d+)', log_file)
        num_events = int(matches[0])
        matches = re.findall(r'c=(\d+)', log_file)
        concurrency = int(matches[0])
        matches = re.findall(r'b=(\d+)', log_file)
        batch_size = int(matches[0])
        self.batch_size = batch_size

        batch_processing_times = []
        batch_counter = 0

        f = open(log_file)
        for line in f:
            batch = []
            batch.append(parse_event(line))
            while len(batch) < batch_size:
                line = f.readline()
                if not line:
                    break
                batch.append(parse_event(line))

            if len(batch) == batch_size:
                start_time = time.time()
                self.process(batch)
                end_time = time.time()

                print("Batch {} out of {} processed in {}".format(batch_counter, num_events // batch_size, end_time - start_time))
                batch_processing_times.append(end_time - start_time)
                batch_counter += 1
                
        f.close()

        return batch_processing_times
            
    def add_rule(self, rule):
        self.rules.append(rule)
        self.rule_tables.append(RuleTables(rule))

    def process(self, new_events):
        last_time = self.current_timestamp
        self.current_timestamp = new_events[0].timestamp
        expected_events = []
        before_update_and_chase = time.time()
        for rule_table in self.rule_tables:
            rule_table.update(new_events)
            expected_events.append(rule_table.chase())
        # print("update/chase:  "+str(time.time()-before_update_and_chase))
        
        result = ""
        # result += 'Current time: ' + str(self.current_timestamp) + '\n'
        # result += 'Number of body rows: ' + str(sum([len(rule_table.body_table.rows) for rule_table in self.rule_tables])) + '\n'
        # result += 'Number of head rows: ' + str(sum([len(rule_table.body_table.rows) for rule_table in self.rule_tables])) + '\n'
        # result += 'Number of extension rows: ' + str(sum([len(rule_table.extension_table.rows) for rule_table in self.rule_tables])) + '\n'

        # if self.current_timestamp % self.batch_size == 0 and self.current_timestamp != last_time:
        theta_list = []
        test = False
        before_build = time.time()
        for rule_table in self.rule_tables:
            formula = build(rule_table.extension_table, current_timestamp=self.current_timestamp)
            theta_list.append(formula)
        # print("build time: "+" "*3+str(time.time()-before_build))
        sat_test_time = time.time()
        satisfiable = sat_test(And(theta_list))
        # print("sat test time: "+str(time.time()-sat_test_time))
        if not satisfiable:
            result += 'Rule ' + str(rule_table.rule_id) + ' violated at time ' + str(self.current_timestamp) + '\n'
        else:
            result += "Rule " + str(rule_table.rule_id) + " satisfied at time " + str(self.current_timestamp) + '\n'
    
        # remove data from events that have ended
        for e in new_events:
            if e.event_name == 'END':
                self.remove_enactment_data(e.data[0])
    
    def chase(self):
        new_events = []
        continue_chasing = True
        while continue_chasing:
            chase_events = []
            for rule_table in self.rule_tables:
                chase_events.extend(rule_table.chase())
            for rule_table in self.rule_tables:
                rule_body_event_names = [event.event_name for event in rule_table.body_event_atoms]
                rule_table.update([e for e in chase_events if e.event_name in rule_body_event_names])
            new_events.extend(chase_events)
            continue_chasing = len(chase_events) > 0
        return new_events
    
    def remove_enactment_data(self, enactment_id):
        for rule_table in self.rule_tables:
            rule_table.body_table.remove_enactment_data(enactment_id)
            rule_table.head_table.remove_enactment_data(enactment_id)
            rule_table.extension_table.remove_enactment_data(enactment_id)

class RuleTables:
    def __init__(self, rule):
        self.rule_id = rule.rule_id
        self.body_event_atoms = list(filter(lambda x: isinstance(x, EventAtom), rule.body))
        self.body_constraints = list(filter(lambda x: not isinstance(x, EventAtom), rule.body))
        self.body_table = BodyTable(rule.rule_id, self.body_event_atoms, self.body_constraints)
        self.head_event_atoms = list(filter(lambda x: isinstance(x, EventAtom), rule.head))
        self.head_constraints = list(filter(lambda x: not isinstance(x, EventAtom), rule.head))
        self.head_table = HeadTable(rule.rule_id, self.head_event_atoms, self.head_constraints)
        self.extension_table = ExtensionTable(rule.rule_id, self.body_table, self.head_table)
    
    def update(self, events):
        update_assignment_table(table=self.body_table, batch=events)
        update_assignment_table(table=self.head_table, batch=events)
        update_extension_table(body_table=self.body_table, head_table=self.head_table, extension_table=self.extension_table)

    def chase(self):
        return chase(body_table=self.body_table, head_table=self.head_table, extension_table=self.extension_table)

    def print_tables(self):
        pretty_print_table(self.body_table)
        pretty_print_table(self.head_table)
        pretty_print_extension_table(self.extension_table)

class BodyTable:
    def __init__(self, rule_id="", atoms=[], constraints=[]):
        self.rule_id = rule_id
        self.atoms = atoms
        self.constraints = constraints
        self.rows = []
        self.ids = [-1]
        self.row_type = BodyTableRow

    def __repr__(self):
        atom_string = ", ".join([str(atom) for atom in self.atoms])
        result = "Body Table for r" + str(self.rule_id) + " body:" + atom_string + ": " + "\n"
        for i, row in enumerate(self.rows):
            result += "b" + str(i) + ": " + str(row) + " " + "\n"
        return result
    
    def new_id(self):
        new_id = max(self.ids)+1
        self.ids.append(new_id)
        return new_id
    
    def remove_enactment_data(self, enactment_id):
        # Iterate over the list in reverse order
        for i in range(len(self.rows) - 1, -1, -1):
            try:
                if self.rows[i].assignment['eid'] == enactment_id:
                    del self.rows[i]
            except KeyError:
                pass
            
class BodyTableRow:
    def __init__(self, id, assignment, atoms, atoms_covered, events_covered, constraints):
        self.id = id
        self.assignment = assignment
        self.atoms = atoms
        self.atoms_covered = atoms_covered
        self.complete = is_assignment_complete(assignment, atoms, atoms_covered, constraints)
        self.events_covered = events_covered
        self.ground = is_row_ground(assignment, events_covered) 
        self.chased = False
        self.constraints = constraints

    def __repr__(self):
        result = []
        result.append('id:'+str(self.id))
        result.append("assignment:"+str(self.assignment))
        result.append("atoms:"+str(self.atoms))
        result.append("complete" if self.complete else "incomplete")
        result.append("ground" if self.ground else "not ground")
        result.append("chased" if self.chased else "not chased")
        result.append("atoms_covered:"+ str(self.atoms_covered))
        result.append("events_covered"+str(self.events_covered))
        result.append("constraints:" + ", ".join([str(constraint) for constraint in self.constraints]))
        return str(result)

    def __eq__(self, other):
        return self.assignment == other.assignment and self.atoms == other.atoms and self.atoms_covered == other.atoms_covered and self.chased == other.chased and self.constraints == other.constraints and self.events_covered == other.events_covered

class HeadTable:
    def __init__(self, rule_id="", atoms=[], constraints=[]):
        self.rule_id = rule_id
        self.atoms = atoms
        self.constraints = constraints
        self.rows = []
        self.ids = [-1]
        self.row_type = HeadTableRow

    def __repr__(self):
        atom_string = ", ".join([str(atom) for atom in self.atoms])
        result = "Head Table for " + atom_string + ": " + "\n"
        for row in self.rows:
            result += "h-id" + str(row.id) + ": " + str(row) + " " + "\n"
        return result
    
    def new_id(self):
        new_id = max(self.ids)+1
        self.ids.append(new_id)
        return new_id

    def remove_enactment_data(self, enactment_id):
        # Iterate over the list in reverse order
        for i in range(len(self.rows) - 1, -1, -1):
            try:
                if self.rows[i].assignment['eid'] == enactment_id:
                    del self.rows[i]
            except KeyError:
                pass

class HeadTableRow:
    def __init__(self, id, assignment, atoms, atoms_covered, events_covered, constraints):
        self.id = id
        self.assignment = assignment
        self.atoms = atoms
        self.atoms_covered = atoms_covered
        self.events_covered = events_covered
        self.chased = "n/a"
        self.complete = is_assignment_complete(assignment, atoms, atoms_covered, constraints)
        self.ground = is_row_ground(assignment, events_covered)
        self.constraints = constraints

    def __repr__(self):
        result = []
        result.append('id:'+str(self.id))
        result.append("assignment:"+str(self.assignment))
        result.append("atoms:"+str(self.atoms))
        result.append("complete" if self.complete else "incomplete")
        result.append("ground" if self.ground else "not ground")
        
        result.append("atoms_covered:"+ str(self.atoms_covered))
        result.append("events_covered"+str(self.events_covered))
        result.append("constraints:" + ", ".join([str(constraint) for constraint in self.constraints]))
        return str(result)

# used by both head and body tables
def pretty_print_table(table):
    result = "\n"
    table_type = "Body Table " if isinstance(table, BodyTable) else "Head Table "
    rule_name = "for r"+str(table.rule_id)
    atom_string = ": " + ", ".join([str(atom) for atom in table.atoms])
    result += (table_type + rule_name + atom_string + "\n")
    result += (str(len(table.rows))+" entries\n")
    rows = table.rows
    max_cell_width = {}
    max_cell_width['id'] = len("row.id")
    max_cell_width['assignment'] = len("assignment")
    max_cell_width['complete'] = len('complete')
    max_cell_width['ground'] = len('not ground')
    max_cell_width['chased'] = len('not chased')
    max_cell_width['events_covered'] = len('events_covered')
    max_cell_width['constraints'] = len("constraints")
    
    for x in rows:
        max_cell_width['id'] = max(max_cell_width['id'], len(str(x.id)))
        max_cell_width['assignment'] = max(max_cell_width['assignment'], len(str(x.assignment)))
        max_cell_width['constraints'] = max(max_cell_width['constraints'], len(str(x.constraints)))
        max_cell_width['events_covered'] = max(max_cell_width['events_covered'], len(str(x.events_covered)))

    result += "| " + "row.id"+' '*(max_cell_width['id']-len(str("row.id")))
    result += " | " + "assignment"+' '*(max_cell_width['assignment']-len("assignment"))
    result += " | " + "events_covered"+' '*(max_cell_width['events_covered']-len(str("events_covered")))
    result += " | " + "complete"+' '*(max_cell_width['complete']-len(str("complete")))
    result += " | " + str("ground")+' '*(max_cell_width['ground']-len(str("ground")))
    result += " | " + str("chased")+' '*(max_cell_width['chased']-len(str("chased")))
    result += " | " + str("constraints")+' '*(max_cell_width['constraints']-len(str("constraints")))+" | \n"
    for row in rows:
        result += "| " + str(row.id)+' '*(max_cell_width['id']-len(str(row.id)))
        result += " | " + str(row.assignment)+' '*(max_cell_width['assignment']-len(str(row.assignment)))
        result += " | " + str(row.events_covered)+' '*(max_cell_width['events_covered']-len(str(row.events_covered)))
        result += " | " + str(row.complete)+' '*(max_cell_width['complete']-len(str(row.complete)))
        result += " | " + str(row.ground)+' '*(max_cell_width['ground']-len(str(row.ground)))
        result += " | " + str(row.chased)+' '*(max_cell_width['chased']-len(str(row.chased)))
        result += " | " + str(row.constraints)+' '*(max_cell_width['constraints']-len(str(row.constraints)))+" | "
        result += "\n"
    print(result)

class ExtensionTableRow:
    def __init__(self, body_table_row, head_table_row, constraints):
        self.body_table_row = body_table_row
        self.head_table_row = head_table_row
        self.chased = False
        self.matched = False
        self.constraints = constraints

    def __repr__(self):
        result = []
        result.append("body complete" if self.body_table_row.complete else "body incomplete")
        result.append("body ground" if self.body_table_row.ground else "body not ground")
        result.append("chased" if self.chased else "not chased")
        result.append("head complete" if self.head_table_row.complete else "head incomplete")
        result.append("head ground" if self.body_table_row.ground else "head not ground")
        result.append("matched" if self.matched else "not matched")
        result.append("constraints: " + ", ".join([str(constraint) for constraint in self.constraints]))
        return str(self.body_table_row.assignment) + " -> " + str(self.head_table_row.assignment) + ", " +  ", ".join(result)

class ExtensionTable:
    def __init__(self, rule_id, body_table, head_table):
        self.rule_id = rule_id
        self.body_table = body_table
        self.head_table = head_table
        self.rows = []
        self.body_head_ids = {}
        self.matched_body_ids = []
        self.null_count = 0

    def __repr__(self):
        atom_string = ""
        atom_string += ", ".join([str(atom) for atom in self.body_table.atoms])
        atom_string += " -> "
        atom_string += ", ".join([str(atom) for atom in self.head_table.atoms])
        result = "Extension Table for: " + atom_string + ": " + "\n"
        for row in self.rows:
            result += str(row) + "\n"
        return result[:-1]

    def new_null(self):
        self.null_count += 1
        new_null = str(self.rule_id) + str(self.null_count)
        return new_null
    
    def remove_enactment_data(self, enactment_id):
        # Iterate over the list in reverse order
        for i in range(len(self.rows) - 1, -1, -1):
            try:
                if self.rows[i].body_table_row.assignment['eid'] == enactment_id or self.rows[i].head_table_row.assignment['eid'] == enactment_id:
                    del self.rows[i]
                
            except KeyError:
                pass

def pretty_print_extension_table(table):
    
    name = "Extension Table for: "
    body_atom_string = ", ".join([str(atom) for atom in table.body_table.atoms])
    head_atom_string = ", ".join([str(atom) for atom in table.head_table.atoms])
    result = (name + body_atom_string + " -> " + head_atom_string)
    result += (": "+str(len(table.rows))+" entries\n")
    rows = table.rows
    max_cell_width = {}
    max_cell_width['body_id'] = len("b_id")
    max_cell_width['body_assignment'] = len("b_assmt")
    max_cell_width['body_events'] = len("b_events")
    max_cell_width['body_complete'] = len('b_compl')
    max_cell_width['body_ground'] = len('b_gro')
    max_cell_width['head_id'] = len("h_id")
    max_cell_width['head_assignment'] = len("h_assmt")
    max_cell_width['head_events'] = len("h_events")
    max_cell_width['head_complete'] = len('h_compl')
    max_cell_width['head_ground'] = len('h_gro')
    max_cell_width['chased'] = len('chased')
    max_cell_width['matched'] = len('matched')
    max_cell_width['constraints'] = len("constr")
    
    for row in rows:
        max_cell_width['body_id'] = max(max_cell_width['body_id'], len(str(row.body_table_row.id)))
        max_cell_width['body_assignment'] = max(max_cell_width['body_assignment'], len(str(row.body_table_row.assignment)))
        max_cell_width['body_events'] = max(max_cell_width['body_events'], len(str(row.body_table_row.events_covered)))
        max_cell_width['head_id'] = max(max_cell_width['body_id'], len(str(row.head_table_row.id)))
        max_cell_width['head_assignment'] = max(max_cell_width['head_assignment'], len(str(row.head_table_row.assignment)))
        max_cell_width['head_events'] = max(max_cell_width['head_events'], len(str(row.head_table_row.events_covered)))
        max_cell_width['constraints'] = max(max_cell_width['constraints'], len(str(row.constraints)))

    result += ("| " + "b_id"+' '*(max_cell_width['body_id']-len(str("b_id"))))
    result += (" | " + "b_assmt"+' '*(max_cell_width['body_assignment']-len("b_assmt")))
    result += (" | " + "b_events"+' '*(max_cell_width['body_events']-len("b_events")))
    result += (" | " + "b_compl"+' '*(max_cell_width['body_complete']-len("b_compl")))
    result += (" | " + "b_gro"+' '*(max_cell_width['body_ground']-len("b_gro")))
    
    result += (" | " + "h_id"+' '*(max_cell_width['head_id']-len(str("h_id"))))
    result += (" | " + "h_assm"+' '*(max_cell_width['head_assignment']-len("h_assm")))
    result += (" | " + "h_events"+' '*(max_cell_width['head_events']-len("h_events")))
    result += (" | " + "h_compl"+' '*(max_cell_width['head_complete']-len("h_compl")))
    result += (" | " + "h_gro"+' '*(max_cell_width['head_ground']-len("h_gro")))

    result += (" | " + str("constr")+' '*(max_cell_width['constraints']-len(str("constr")))+" | " + "\n")

    for row in rows:
        result += "| " + str(row.body_table_row.id)+' '*(max_cell_width['body_id']-len(str(row.body_table_row.id)))
        result += " | " + str(row.body_table_row.assignment)+' '*(max_cell_width['body_assignment']-len(str(row.body_table_row.assignment)))
        result += " | " + str(row.body_table_row.events_covered)+' '*(max_cell_width['body_events']-len(str(row.body_table_row.events_covered)))
        result += " | " + str(True if row.body_table_row.complete else False)+' '*(max_cell_width['body_complete']-len(str(True if row.body_table_row.complete else False)))
        result += " | " + str(True if row.body_table_row.ground else False)+' '*(max_cell_width['body_ground']-len(str(True if row.body_table_row.ground else False)))

        result += " | " + str(row.head_table_row.id)+' '*(max_cell_width['head_id']-len(str(row.head_table_row.id)))
        result += " | " + str(row.head_table_row.assignment)+' '*(max_cell_width['head_assignment']-len(str(row.head_table_row.assignment)))
        result += " | " + str(row.head_table_row.events_covered)+' '*(max_cell_width['head_events']-len(str(row.head_table_row.events_covered)))
        result += " | " + str(True if row.head_table_row.complete else False)+' '*(max_cell_width['head_complete']-len(str(True if row.head_table_row.complete else False)))
        result += " | " + str(True if row.head_table_row.ground else False)+' '*(max_cell_width['head_ground']-len(str(True if row.head_table_row.ground else False)))

        result += " | " + str(row.constraints)+' '*(max_cell_width['constraints']-len(str(row.constraints)))+" | "
        result += "\n"
    
    print(result)
    print(table.body_head_ids)

# merge with other assignments in the same table
def update_assignment_table(table, batch):
    new_rows = []
    for event in batch:
        for atom in table.atoms:
            if atom.predicate == event.event_name:
                new_assignment = find_assignment([atom], [event])
                skip = False
                for row in table.rows:
                    if row.assignment == new_assignment and row.atoms_covered == set([atom]):
                        skip = True
                simplified_constraints = generous_eval(new_assignment, new_assignment, table.constraints+event.constraints)
                for c in simplified_constraints:
                    if str(c.expression) == "False":
                        skip = True
                if skip:
                    continue
                if not do_assignments_agree(assignment1=new_assignment, assignment2=new_assignment, constraints=simplified_constraints):
                    continue
                new_row = table.row_type(table.new_id(), new_assignment, table.atoms, set([atom]), set([event]), simplified_constraints)
                table.rows.append(new_row)
                new_rows.append(new_row)

    changes = len(new_rows) > 0
    while changes:
        changes = False
        next_rows = []
        for row1 in new_rows:
            for row2 in table.rows:
                if do_assignments_agree(row1.assignment, row2.assignment, row1.constraints+row2.constraints):
                    if row1.assignment == row2.assignment and row1.atoms_covered == row2.atoms_covered and row1.events_covered == row2.events_covered:
                        continue
                    merged_assignment = merge_assignments(row1.assignment, row2.assignment)
                    merged_atoms_covered = row1.atoms_covered.union(row2.atoms_covered)
                    merged_events_covered = row1.events_covered.union(row2.events_covered)
                    skip = False
                    for row3 in table.rows + next_rows:
                        if row3.assignment == merged_assignment and row3.atoms_covered == merged_atoms_covered and row3.events_covered == merged_events_covered:
                            skip = True
                    if skip:
                        continue
                    simplified_constraints = generous_eval(row1.assignment, row2.assignment, row1.constraints+row2.constraints)
                    for c in simplified_constraints:
                        if c.expression == "False":
                            skip = True
                    if skip:
                        continue
                    new_row = table.row_type(table.new_id(), merged_assignment, table.atoms, merged_atoms_covered, merged_events_covered, simplified_constraints)
                    next_rows.append(new_row)
        
        new_rows = []
        for row in next_rows:
            table.rows.append(row)
            new_rows.append(row)
            changes = True

# match assignments between body and head tables
def update_extension_table(body_table, head_table, extension_table):

    for body_row in body_table.rows:
        body_assignment = body_row.assignment
        body_id = body_row.id
        if not body_id in extension_table.body_head_ids.keys():
            blank_head_row = HeadTableRow(head_table.new_id(), {}, atoms=head_table.atoms, atoms_covered=set(), events_covered=set(), constraints=head_table.constraints)
            skip = False
            simplified_constraints = generous_eval(assignment1=body_assignment, assignment2=body_assignment, constraints=body_row.constraints+blank_head_row.constraints)
            for c in simplified_constraints:
                if c.expression == "False":
                    skip = True
            if skip:
                continue
            new_row = ExtensionTableRow(body_row, blank_head_row, simplified_constraints)
            extension_table.body_head_ids[body_id] = [blank_head_row.id]
            extension_table.rows.append(new_row)

        for head_row in head_table.rows:
            if head_row.id in extension_table.body_head_ids[body_id]:
                continue
            head_assignment = head_row.assignment
            head_id = head_row.id
            if do_assignments_agree(assignment1=body_assignment, assignment2=head_assignment, constraints=body_row.constraints+head_row.constraints):
                skip = False
                simplified_constraints = generous_eval(assignment1=body_assignment, assignment2=head_assignment, constraints=body_row.constraints+head_row.constraints)
                for c in simplified_constraints:
                    if c.expression == "False":
                        skip = True
                if skip:
                    continue
                new_row = ExtensionTableRow(body_row, head_row, simplified_constraints)
                if body_row.complete and head_row.complete and head_row.ground:
                    new_row.matched = True
                    extension_table.matched_body_ids.append(body_id)
                extension_table.rows.append(new_row)
                extension_table.body_head_ids[body_id].append(head_id)


def chase(body_table, head_table, extension_table):

    # check if extension table has a complete, unmatched, unchased body assignment
    rows_to_chase = [row for row in extension_table.rows if row.body_table_row.complete and not row.head_table_row.complete and not row.matched and not row.chased]
    
    expected_events = []
    
    while len(rows_to_chase) > 0:

        new_events = []

        for row in rows_to_chase:
            # don't chase the same assignment again 
            skip = False
            for row2 in extension_table.rows:
                if row.body_table_row.assignment == row2.body_table_row.assignment and row2.chased:
                    row.chased = True
                    skip = True
            if skip:
                continue

            missing_atoms = set(head_table.atoms).difference(row.body_table_row.atoms_covered)

            # create head data with fresh constants
            new_head_assignment = {}
            for atom in missing_atoms:
                for term in atom.terms:
                    if term in row.body_table_row.assignment.keys():
                        new_head_assignment[term] = row.body_table_row.assignment[term]
                    elif term in row.head_table_row.assignment.keys():
                        new_head_assignment[term] = row.head_table_row.assignment[term]
                    else:
                        # instantiate a new constant
                        new_head_assignment[term] = term+"_f"+extension_table.new_null()
                        
                if atom.timestamp_variable in row.body_table_row.assignment.keys():
                    new_head_assignment[atom.timestamp_variable] = row.body_table_row.assignment[atom.timestamp_variable]
                elif atom.timestamp_variable in row.head_table_row.assignment.keys():
                    new_head_assignment[atom.timestamp_variable] = row.head_table_row.assignment[atom.timestamp_variable]
                else:
                    # instantiate a new timestamp
                    new_head_assignment[atom.timestamp_variable]=atom.timestamp_variable+"_f"+extension_table.new_null()
            
            for atom in missing_atoms:
                head_data = [new_head_assignment[t] for t in atom.terms]
                constraints = generous_eval(new_head_assignment, new_head_assignment, row.constraints)
                new_event = Event(atom.predicate, head_data, new_head_assignment[atom.timestamp_variable], expected=True, constraints=constraints)
                expected_events.append(new_event)
                new_events.append(new_event)

            row.chased = True
            row.matched = True
            for row2 in extension_table.rows:
                if row.body_table_row.assignment == row2.body_table_row.assignment and row.body_table_row.atoms_covered == row2.body_table_row.atoms_covered:
                    row2.chased = True
                    row2.matched = True
            for row3 in body_table.rows:
                if row.body_table_row.assignment == row3.assignment:
                    row3.chased = True
        
        update_assignment_table(body_table, new_events)
        update_assignment_table(head_table, new_events)
        update_extension_table(body_table, head_table, extension_table)
   
        # collect complete, unmatched, unchased body assignments
        assignments_to_chase_2 = [row for row in extension_table.rows if row.body_table_row.complete and not row.head_table_row.complete and not row.matched and not row.chased]

        rows_to_chase = []
        for row1 in assignments_to_chase_2:
            add = True
            for row2 in rows_to_chase:
                if row1.body_table_row.assignment == row2.body_table_row.assignment and row1.body_table_row.atoms_covered == row2.body_table_row.atoms_covered:
                    add = False
                    break
            for row3 in extension_table.rows:
                if row1.body_table_row.assignment == row3.body_table_row.assignment and row3.chased:
                    row1.chased = True
                    row1.matched = True
                    add = False
                    break
            if add:
                rows_to_chase.append(row1)
    
    return expected_events

def build(extension_table, current_timestamp):

    theta = z3.BoolVal(True)
    all_variables = []
    for row in extension_table.rows:
        for c in row.body_table_row.constraints:
            all_variables += c.terms
        for c in row.head_table_row.constraints:
            all_variables += c.terms
        for c in row.constraints:
            all_variables += get_names(c)
        for c in row.body_table_row.atoms:
            all_variables.extend(c.terms)
            all_variables.append(c.timestamp_variable)
        for c in row.head_table_row.atoms:
            all_variables.extend(c.terms)
            all_variables.append(c.timestamp_variable)
        for c in row.body_table_row.assignment.values():
            if not isinstance(c, int):
                all_variables.append(c)
        for c in row.head_table_row.assignment.values():
            if not isinstance(c, int):
                all_variables.append(c)
    all_variables = list(set(all_variables))
    z3_vars = {name:Int(name) for name in all_variables}

    b_time = time.time()
    theta_list = []
    for row in filter(lambda x: x.body_table_row.complete, extension_table.rows):
        already_matched = False
        row_list = []
        for row2 in extension_table.rows:
            if row2.head_table_row.id in extension_table.body_head_ids[row.body_table_row.id]:
                x_time = time.time()
                row_row2_list = [z3.BoolVal(True)]
                if row2.head_table_row.ground and row2.head_table_row.complete:
                    already_matched = True
                    row_list = [z3.BoolVal(True)]
                    break

                if row.body_table_row.constraints:
                    a = And(list(set((list(map(lambda c: atom_to_z3_inequality(z3_vars, c), row.body_table_row.constraints))))))
                    b = And(list(set(list(map(lambda c: atom_to_z3_inequality(z3_vars, c), row2.constraints)))))
                    c = z3.BoolVal(True)
                    row_row2_list = [If(a=a, b=b, c=c)]
                else:
                    if row2.constraints:
                        row_row2_list.append(And(list(set(list(map(lambda c: atom_to_z3_inequality(z3_vars, c), row2.constraints))))))
                # print("x_time", time.time()-x_time)

                d_time = time.time()
                # enforce unresolved timestamp variables greater than current time
                timestamp_variables = []
                for atom in list(set.difference(set(row2.head_table_row.atoms), set(row2.head_table_row.atoms_covered))):
                    if atom.timestamp_variable not in timestamp_variables:
                        timestamp_variables.append(atom.timestamp_variable)
                for event in list(row.body_table_row.events_covered):
                    if event.timestamp not in timestamp_variables and ("_f" in event.timestamp if isinstance(event.timestamp, str) else False):
                        timestamp_variables.append(event.timestamp)
                for event in list(row2.head_table_row.events_covered):
                    if event.timestamp not in timestamp_variables and ("_f" in event.timestamp if isinstance(event.timestamp, str) else False):
                        timestamp_variables.append(event.timestamp)
                for x in row.body_table_row.assignment.values():
                    if isinstance(x, str) and "_f" in x and x not in timestamp_variables:
                        timestamp_variables.append(x)
                for x in row2.body_table_row.assignment.values():
                    if isinstance(x, str) and "_f" in x and x not in timestamp_variables:
                        timestamp_variables.append(x)
                # print("d_time", time.time()-d_time)

                e_time = time.time()
                for timestamp_variable in timestamp_variables:
                    row_row2_list.append(z3_vars[timestamp_variable] >= current_timestamp)

                row_row2_theta = (And(row_row2_list))
                row_list.append(row_row2_theta)
                # print("e_time", time.time()-e_time)

        if already_matched:
            row_list = [z3.BoolVal(True)]

        row_theta = (Or(row_list))
        theta_list.append(row_theta)

    theta = (And(theta_list))
    # print("b_time", time.time()-b_time)
    return theta

def is_assignment_complete(assignment, atoms, atoms_covered, constraints):
    for atom in atoms:
        for term in atom.terms:
            if term not in assignment.keys():
                return False
        if atom.timestamp_variable not in assignment.keys():
            return False
    if len(atoms_covered) != len(atoms):
        return False
    if not do_assignments_agree(assignment1=assignment, assignment2=assignment, constraints=constraints):
        return False
    return True
    
def is_row_ground(assignment, events_covered):
    test = "_f" not in str(assignment) and all(map(lambda x: not x.expected, events_covered))
    return test

def is_atom_mapped_to_event(atom, event, assignment):
    result = True
    for i,term in enumerate(atom.terms):
        if assignment[term] != event.data[i]:
            return False
    if assignment[atom.timestamp_variable] != event.timestamp:
        return False
    return result
                
def merge_assignments(assignment1, assignment2):
    mapping = {}
    common_keys = set(assignment1.keys()).intersection(set(assignment2.keys()))
    for key in common_keys:
        if assignment1[key] != assignment2[key]:
            raise Exception("Assignments do not agree")
    for key in assignment1.keys():
        mapping[key] = assignment1[key]
    for key in assignment2.keys():
        mapping[key] = assignment2[key]
    return mapping

def generous_eval(assignment1, assignment2, constraints):
    assignment = merge_assignments(assignment1, assignment2)
    constraints = [copy.deepcopy(c) for c in constraints]

    upper_bounds = {}
    lower_bounds = {}
    exacts = {}
    variables = list(assignment.keys())+list(assignment.values())
    
    for constraint in constraints:
        c = str(constraint.expression)
        for var in assignment.keys():
            #c = c.replace(var, str(assignment[var]))
            pattern = re.compile(r'{}(?!_)'.format(var))
            constraint.expression = pattern.sub(str(assignment[var]), c)
            c = str(constraint.expression)
        if "==" in c:
            c = c.split("==")
            l = c[0].strip()
            r = c[1].strip()
            if l in variables:
                try:
                    exacts[l] = eval(r)
                    upper_bounds[l] = eval(r)
                    lower_bounds[l] = eval(r)
                except (NameError, SyntaxError):
                    pass
            if r in variables:
                try:
                    exacts[r] = eval(l)
                    upper_bounds[r] = eval(l)
                    lower_bounds[r] = eval(l)
                except:
                    pass
        elif "<=" in c:
            c = c.split("<=")
            l = c[0].strip()
            r = c[1].strip()
            if l in variables:
                try:
                    upper_bounds[l] = eval(r)
                except (NameError, SyntaxError):
                    pass
            if r in variables:
                try:
                    lower_bounds[r] = eval(l)
                except (NameError, SyntaxError):
                    pass
        elif ">=" in c:
            c = c.split(">=")
            l = c[0].strip()
            r = c[1].strip()
            if l in variables:
                try:
                    lower_bounds[l] = eval(r)
                except (NameError, SyntaxError):
                    pass
            if r in variables:
                try:
                    upper_bounds[r] = eval(l)
                except (NameError, SyntaxError):
                    pass
        else:
            pass

    for var in exacts.keys():
        if var in assignment.keys():
            if assignment[var] != exacts[var]:
                return ArithmeticAtom(expression=False)
            assignment[var] = exacts[var]
        if var in assignment.values():
            for key in assignment.keys():
                if assignment[key] == var:
                    assignment[key] = exacts[var]

    evaluated_constraints = []
    for c in constraints:
        c = str(c.expression)
        for var in assignment.keys():
            #c = c.replace(var, str(assignment[var]))
            pattern = re.compile(r'{}(?!_)'.format(var))
            c = pattern.sub(str(assignment[var]), c)
        for op in ["==", "!=", "<", ">", "<=", ">="]:
            if op in c:
                if op == "<" and "<=" in c:
                    continue
                if op == ">" and ">=" in c:
                    continue
                c = c.split(op)
                for i in range(len(c)):
                    try:
                        c[i] = str(eval(c[i]))
                    except (NameError, SyntaxError, TypeError):
                        pass
                c = op.join(c)
                try:
                    evaluated_constraints.append(eval(c))
                except (NameError, SyntaxError, TypeError):
                    evaluated_constraints.append(c)
    
    evaluated_constraints = list(filter(lambda x: x != True, evaluated_constraints))
    evaluated_constraints = list(set(evaluated_constraints))
    evaluated_constraints = list(map(lambda x: ArithmeticAtom(expression=x), evaluated_constraints))

    return evaluated_constraints

def do_assignments_agree(assignment1, assignment2, constraints):
  
    for key in assignment1.keys():
        if key in assignment2.keys():
            if assignment1[key] != assignment2[key]:
                return False
    evaluated_constraints = []
    for c in constraints:
        c = str(c.expression)
        for var in assignment1.keys():
            c = c.replace(var, str(assignment1[var]))
        for var in assignment2.keys():
            c = c.replace(var, str(assignment2[var]))
        try:
            evaluated_constraints.append(eval(c))
        except (NameError, SyntaxError, TypeError):
            continue
        
    return all(evaluated_constraints)

def find_assignment(atoms, events):
    # check if the atoms and events have the same predicate names
    for atom in atoms:
        if atom.predicate not in [event.event_name for event in events]:
            return None

    # match atoms to events by predicate name
    predicate_matching = {}
    for atom in atoms:
        predicate_matching[atom] = []
        for event in events:
            if atom.predicate == event.event_name:
                predicate_matching[atom].append(event)

    # create a mapping from terms to values, if possible
    mapping = {}
    for atom in predicate_matching.keys():
        event = predicate_matching[atom][0] # is this [0] okay?
        for term in atom.terms:
            if term not in mapping.keys():
                mapping[term] = event.data[atom.terms.index(term)]
            else:
                if event.data[atom.terms.index(term)] is not mapping[term]:
                    return None
        if atom.timestamp_variable not in mapping.keys():
            mapping[atom.timestamp_variable] = event.timestamp
        else:
            if event.timestamp is not mapping[atom.timestamp_variable]:
                return None

    return mapping

def get_names(c):
    c = str(c.expression)
    return list(set([ node.id for node in ast.walk(ast.parse(c)) if isinstance(node, ast.Name)
    ]))

def atom_to_z3_inequality(variables, constraint):
    constraint = str(constraint).strip()
    elements = re.split('([<>]=?|==)', constraint)
    operator = elements[1]
    
    left = str(elements[0]).strip()
    if not left.isdigit():
        if left not in variables.keys():
            variables[left] = Int(left)
        left = variables[left]
    
    right = str(elements[2]).strip()
    if not right.isdigit():
        if right not in variables.keys():
            variables[right] = Int(right)
        right = variables[right]

    # Add the constraint to the solver based on the operator
    if operator == "<":
        return left < right
    elif operator == ">":
        return left > right
    elif operator == "<=":
        return left <= right
    elif operator == ">=":
        return left >= right
    elif operator == "==":
        return left == right

def sat_test(theta):
    s = Solver()
    s.add(theta)
    result = s.check()
    if result == z3.sat:
        return True
    else:
        return False

def example_z3_sat():
    x, y = Int('x'), Int('y')
    s = Solver()
    print(s)
    s.add(x > 10, y < x + 2)
    s.add(x < 9)
    print(s)
    print("Solving constraints in the solver s ...")
    print(s.check())
    return s.check() == "sat"