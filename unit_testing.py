'''test functions'''

'''import libraries'''
from stream import *
from monitor import *
from language import *
from event_parser import *

'''test the find_assignment function'''
def test_find_assignment():
    # create a random stream schema
    stream_schema = generate_random_stream_schema(num_event_schemas=1, min_num_attributes=1, max_num_attributes=1)

    # create a set of atoms for the stream schema
    atom = None
    for event_schema in stream_schema.event_schemas:
        terms = []
        for i,attribute in enumerate(event_schema.attributes):
            terms.append("v" + str(i))
        atom = EventAtom(event_schema.event_name, terms, 't')

    # create a random set of events
    event = None
    for event_schema in stream_schema.event_schemas:
        e = generate_random_event(event_schema, 0)
        e.data = [3]
        event = e

    # find an assignment from a set of atoms to a set of events
    assignment = find_assignment([atom], [event])

    log = []
    log.append(str(atom))
    log.append(str(event))
    log.append(str(assignment))

    return log, is_atom_mapped_to_event(atom, event, assignment)

'''test the update_assignment_table function'''
def update_test_1():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", ["v1"], "x"),
                EventAtom("E3", ["v3"], "y")],
        head=[  EventAtom("E1", ["v2"], "z"),
                EventAtom("E2", ["v3"], "w")],
    )
    events = [
        Event("E1", [43], 0),
        Event("E2", [51], 2),
        Event("E3", [51], 3),
    ]
    r0 = RuleTables(rule_0)
    r0.update(events)
    # r0.print_tables()
    
    log = []
    if len(r0.body_table.rows) != 3:
        log.append("body table failure")
        return log, False
    if len(r0.head_table.rows) != 3:
        log.append("head table failure")
        return log, False
    if len(r0.extension_table.rows) != 12:
        log.append("extension table failure")
        return log, False
    return log, True

def update_test_2():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", ["v1"], "x"),
                EventAtom("E1", ["v2"], "z"),
                EventAtom("E3", ["v3"], "y")],
        head=[  EventAtom("E2", ["v4"], "w")],
    )
    events = [  Event("E1", [43], 0),
                Event("E2", [51], 2),
                Event("E2", [63], 4),
                Event("E3", [70], 3) ]
    
    r0 = RuleTables(rule_0)
    r0.update(events)
    # r0.print_tables()

    log = []
    if len(r0.body_table.rows) != 7:
        log.append("body table failure")
        return log, False
    
    if len(r0.head_table.rows) != 2:
        log.append("head table failure")
        return log, False

    if len(r0.extension_table.rows) != 21:
        log.append("extension table failure")
        return log, False

    return log, True

def update_test_3():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", ["v1"], "x"),
                EventAtom("E2", ["v3"], "z")],
        head=[  EventAtom("E3", ["v1"], "z")]
    )
    events = [  Event("E3", [44], 2),
                Event("E2", [22], 2), #
                Event("E1", [44], 0), #
                Event("E3", [55], 2),
                Event("E3", [44], 7) ]
    r0 = RuleTables(rule_0)
    r0.update(events)
    # r0.print_tables()
    
    log = []
    if len(r0.body_table.rows) != 3:
        log.append("body table failure")
        return log, False
    
    if len(r0.head_table.rows) != 3:
        log.append("head table failure")
        return log, False

    if len(r0.extension_table.rows) != 8:
        log.append("extension table failure")
        return log, False

    return log, True

def update_test_4():
    # create a set of atoms for the stream schema
    body_atoms = [
        EventAtom("E1", ["v1"], "x"),
        EventAtom("E2", ["v3"], "y")
    ]
    
    head_atoms = [
        EventAtom("E3", ["v1"], "x")
    ]
    
    events = [
        Event("E1", [43], 0),
        Event("E2", [51], 4)
    ]
    rule_0 = Rule(
        rule_id=0,
        body=body_atoms,
        head=head_atoms)
    r0 = RuleTables(rule_0)
    r0.update(events)
    # r0.print_tables()
    
    log = []

    if len(r0.body_table.rows) != 3:
        log.append("body table failure")
        return log, False
    
    if len(r0.head_table.rows) != 0:
        log.append("head table failure")
        return log, False

    if len(r0.extension_table.rows) != 3:
        log.append("extension table failure")
        return log, False

    return "success", True

def update_test_5():
    rule_0 = Rule(
        rule_id=0,
        body=[EventAtom("E1", ["v1", "v2"], "x")],
        head=[  EventAtom("E2", ["v1"], "y"),
                EventAtom("E3", ["v3"], "z")]
        )

    events = [Event("E1", [43, 55], 0)]
    
    r0 = RuleTables(rule_0)
    r0.update(events)
    r0.chase()
    # r0.print_tables()
    
    if len(r0.body_table.rows) != 1:
        return ["body table error"], False

    if len(r0.head_table.rows) != 3:
        return ["head table error"], False
    
    return "passed", True

def chase_test_1():
    # create a set of atoms for the stream schema
    body_atoms = []
    body_atoms.append(EventAtom("E1", ["v1"], "x"))
    body_atoms.append(EventAtom("E2", ["v3"], "y"))
    
    head_atoms = []
    head_atoms.append(EventAtom("E3", ["v1"], "x"))
    
    events = []
    events.append(Event("E1", [43], 0))
    events.append(Event("E2", [51], 4))
    
    rule_0 = Rule(
        rule_id=0,
        body=body_atoms,
        head=head_atoms)
    r0 = RuleTables(rule_0)
    r0.update(events)
    r0.chase()

    if len(r0.extension_table.rows) != 6:
        return ["extension table error"], False

    return "success", True

def chase_test_2():
    # create a set of atoms for the stream schema
    body_atoms = []
    body_atoms.append(EventAtom("E1", ["v1"], "x"))
    body_atoms.append(EventAtom("E2", ["v2"], "y"))
    
    head_atoms = []
    head_atoms.append(EventAtom("E3", ["v2"], "z"))
    head_atoms.append(EventAtom("E4", ["v4"], "w"))
    # head_atoms.append(EventAtom("E4", ["v4"], "w"))
    
    events = []
    events.append(Event("E1", [43], 0))
    events.append(Event("E2", [51], 4))
    rule_0 = Rule(
        rule_id=0,
        body=body_atoms,
        head=head_atoms)
    r0 = RuleTables(rule_0)
    r0.update(events)
    r0.chase()
    # # r0.print_tables()

    if len(r0.head_table.rows) != 3:
        return ["head table error"], False
    
    if len(r0.extension_table.rows) != 12:
        return ["extension table error"], False

    return "passed", True

def chase_test_3():
    rule_0 = Rule(
        rule_id=0,
        body=[EventAtom("E1", ["v1"], "x")],
        head=[EventAtom("E2", ["v2"], "y")]
    )
    
    rule_1 = Rule(
        rule_id=1,
        body=[EventAtom("E2", ["v3"], "z")],
        head=[EventAtom("E3", ["v4"], "w")]
    )
    
    events = [Event("E1", [43], 1)]

    # create a body, head, and extension tables
    r0 = RuleTables(rule_0)
    r0.update(events)
    r1 = RuleTables(rule_1)
    r1.update(events)
    expected_events = r0.chase()
    r1.update(expected_events)
    r1.chase()

    # # r0.print_tables()
    # # r1.print_tables()

    if len(r1.head_table.rows) != 1:
        return ["head table error"], False

    return "passed", True

def constraint_test_1():
    rule_0 = Rule(
        rule_id=0,
        body=[EventAtom("E1", ["v1"], "x1")],
        head=[EventAtom("E2", ["v2"], "x2"),
              ArithmeticAtom("x1 + 1 == x2")
        ]
    )

    events = [Event("E1", [43], 1),
              Event("E2", [52], 2)
    ]

    r0 = RuleTables(rule_0)
    r0.update(events)
    # # r0.print_tables()

    if len(r0.extension_table.rows) != 2:
        return ["extension table error"], False
    
    return "passed", True

def constraint_test_2():
    rule_0 = Rule(
        rule_id=0,
        body=[EventAtom("E1", ["v1"], "x1")],
        head=[EventAtom("E2", ["v2"], "x2"),
              ArithmeticAtom("x1 + 1 != x2")
        ]
    )

    events = [Event("E1", [43], 1),
              Event("E2", [52], 2)
    ]

    r0 = RuleTables(rule_0)
    r0.update(events)
    # r0.print_tables()

    if len(r0.extension_table.rows) != 1:
        return ["extension table error"], False
    
    return "passed", True

def constraint_test_3():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", ["v1"], "x1"),
                EventAtom("E2", ["v2"], "x2"),
                ArithmeticAtom("x1 + 1 <= x2")],
        head=[  EventAtom("E3", ["v3"], "x3"),
                EventAtom("E4", ["v4"], "x4"),
                ArithmeticAtom("v2 + 1 < v3"),
                ArithmeticAtom("x3 + 1 == x4")
        ]
    )
    events = [Event("E1", [50], 1),
              Event("E2", [50], 1),
              Event("E3", [50], 1),
              Event("E4", [50], 1)]

    r0 = RuleTables(rule_0)
    r0.update(events)
    # r0.print_tables()

    if len(r0.body_table.rows) != 2:
        return ["body table error"], False
    if len(r0.head_table.rows) != 2:
        return ["head table error"], False
    if len(r0.extension_table.rows) != 5:
        return ["extension table error"], False
    return "passed", True

def constraint_test_4():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", ["v1"], "x1"),
                EventAtom("E2", ["v2"], "x2"),
                ArithmeticAtom("x1 + 1 <= x2")],
        head=[  EventAtom("E3", ["v3"], "x3"),
                EventAtom("E4", ["v4"], "x4"),
                ArithmeticAtom("v2 + 1 < v3"),
                ArithmeticAtom("x3 + 1 == x4")
        ]
    )
    events = [Event("E1", [50], 1),
              Event("E2", [50], 2),
              Event("E3", [52], 1),
              Event("E4", [52], 2)]

    r0 = RuleTables(rule_0)
    r0.update(events)
    # # r0.print_tables()

    if len(r0.body_table.rows) != 3:
        return ["body table error"], False
    if len(r0.head_table.rows) != 3:
        return ["head table error"], False
    if len(list(filter(lambda x: x.body_table_row.complete and x.head_table_row.complete, r0.extension_table.rows))) != 1:
        return ["extension table error"], False
    return "passed", True

def constraint_test_5():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", ["v1", "v6", "v3"], "x1"),
                EventAtom("E2", ["v2", "v4"], "x2"),
                ArithmeticAtom("x1 + 1 <= x2"),
                ArithmeticAtom("v1 == v3"),
                ArithmeticAtom("x2 == v4")],
        head=[  EventAtom("E3", ["v5", "x1"], "x3"),
                ArithmeticAtom("v1 + 5 == v5"),
                ArithmeticAtom("v1 <= v3"),
        ]
    )
    events = [Event("E1", [50, 60, 50], 1),
              Event("E2", [50, 2], 2),
              Event("E3", [55, 1], 1)]

    r0 = RuleTables(rule_0)
    r0.update(events)
    # # r0.print_tables()

    if len(r0.body_table.rows) != 3:
        return ["body table error"], False
    if len(r0.head_table.rows) != 1:
        return ["head table error"], False
    if len(list(filter(lambda x: x.body_table_row.complete and x.head_table_row.complete, r0.extension_table.rows))) != 1:
        return ["extension table error"], False
    return "passed", True

def chase_constraints_test_1():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", ["v1"], "x1") ],
        head=[  EventAtom("E2", ["v2"], "x2"),
                ArithmeticAtom("v1 + 5 == v2"),
        ]
    )
    rule_1 = Rule(
        rule_id=1,
        body=[  EventAtom("E1", ["v1"], "x1"),
                EventAtom("E2", ["v2"], "x2"),
                ArithmeticAtom("v1 + 5 == v2"),
              ],
        head=[EventAtom("E3", ["v3"], "x3")]
    )
    events = [Event("E1", [50], 1)]

    r0 = RuleTables(rule_0)
    r1 = RuleTables(rule_1)
    r0.update(events)
    r1.update(events)
    expected_events = r0.chase()
    r1.update(expected_events)

    r1.chase()
    # r0.print_tables()
    # r1.print_tables()

    if len(r0.body_table.rows) != 1:
        return ["r0 body table error"], False
    if len(r0.head_table.rows) != 1:
        return ["r0 head table error"], False
    if len(list(filter(lambda x: x.body_table_row.complete and x.head_table_row.complete and not x.head_table_row.ground, r0.extension_table.rows))) != 1:
        return ["r0 extension table error"], False
    
    if len(r1.body_table.rows) != 3:
        return ["r1 body table error"], False
    if len(r1.head_table.rows) != 1:
        return ["r1 head table error"], False
    if len(list(filter(lambda x: x.body_table_row.complete and x.head_table_row.complete and not x.head_table_row.ground, r1.extension_table.rows))) != 1:
        return ["r1 extension table error"], False
    return "passed", True

def chase_constraints_test_2():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", ["v1"], "x1") ],
        head=[  EventAtom("E2", ["v2"], "x2"),
                ArithmeticAtom("v1 + 10 <= v2"),
        ]
    )
    rule_1 = Rule(
        rule_id=1,
        body=[  EventAtom("E1", ["v1"], "x1"),
                EventAtom("E2", ["v2"], "x2"),
                ArithmeticAtom("v1 + 5 <= v2"),
              ],
        head=[EventAtom("E3", ["v3"], "x3")]
    )
    events = [Event("E1", [50], 1)]

    r0 = RuleTables(rule_0)
    r1 = RuleTables(rule_1)
    r0.update(events)
    r1.update(events)
    expected_events = r0.chase()
    r1.update(expected_events)

    r1.chase()
    # r0.print_tables()
    # r1.print_tables()

    if len(r0.body_table.rows) != 1:
        return ["r0 body table error"], False
    if len(r0.head_table.rows) != 1:
        return ["r0 head table error"], False
    if len(list(filter(lambda x: x.body_table_row.complete and x.head_table_row.complete and not x.head_table_row.ground, r0.extension_table.rows))) != 1:
        return ["r0 extension table error"], False
    
    if len(r1.body_table.rows) != 3:
        return ["r1 body table error"], False
    if len(r1.head_table.rows) != 1:
        return ["r1 head table error"], False
    if len(list(filter(lambda x: x.body_table_row.complete and x.head_table_row.complete and not x.head_table_row.ground, r1.extension_table.rows))) != 1:
        return ["r1 extension table error"], False
    return "passed", True

def build_test_1():
    
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", ["v1"], "x1") ],
        head=[  EventAtom("E2", ["v2"], "x2"),
                ArithmeticAtom("x1 + 10 >= x2"),
        ]
    )
    
    events = [Event("E1", [0], 50)]

    r0 = RuleTables(rule_0)
    r0.update(events)
    # expected_events = r0.chase()
    # r0.print_tables()

    theta = build(r0.extension_table, 65)

    # check if a violation exists
    if sat_test(theta) != True:
        print("violation exists")
    else:
        print("no violation")
        raise Exception("incorrect: violation exists")
    return "passed", True


def build_test_2():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", ["v1"], "x1") ],
        head=[  EventAtom("E2", ["v2"], "x2"),
                ArithmeticAtom("x1 + 10 >= x2"),
        ]
    )
    events = [Event("E1", [0], 50)]

    r0 = RuleTables(rule_0)
    r0.update(events)
    # expected_events = r0.chase()
    # r0.print_tables()
    theta = build(r0.extension_table, 55)

    # check if a violation exists
    if sat_test(theta) != True:
        print("violation exists")
        raise Exception("incorrect: no violation exists")
    else:
        print("no violation")
    return "passed", True

def build_test_3():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", ["v1"], "x1") ],
        head=[  EventAtom("E2", ["v2"], "x2"),
                ArithmeticAtom("x1 + 10 >= x2"),
        ]
    )
    events = [Event("E1", [0], 50)]

    r0 = RuleTables(rule_0)
    r0.update(events)
    # expected_events = r0.chase()
    # r0.print_tables()
    theta = build(r0.extension_table, 55)

    # check if a violation exists
    if sat_test(theta) != True:
        raise Exception("incorrect: no violation exists")
    else:
        pass
    return "passed", True

def build_test_4():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", [], "x1") ],
        head=[  EventAtom("E2", [], "x2"),
                ArithmeticAtom("x1 + 10 >= x2"),
        ]
    )
    events = [Event("E1", [], 50)]

    r0 = RuleTables(rule_0)
    r0.update(events)
    expected_events = r0.chase()
    r0.update(expected_events)
    # r0.print_tables()
    theta = build(r0.extension_table, 55)

    # check if a violation exists
    if sat_test(theta):
        pass
    else:
        raise Exception("incorrect: no violation exists")
    return "passed", True

def build_test_5():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", [], "x1") ],
        head=[  EventAtom("E2", [], "x2") ]
    )
    rule_1 = Rule(
        rule_id=1,
        body=[  EventAtom("E1", [], "x1"), 
                EventAtom("E2", [], "x2"),
                ArithmeticAtom("x1 + 10 <= x2"),
                ],
        head=[  EventAtom("E3", [], "x3"),
                ArithmeticAtom("x1 == x3"),
        ]
    )
    events = [  Event("E1", [], 50) ]

    r0 = RuleTables(rule_0)
    r1 = RuleTables(rule_1)
    r0.update(events)
    r1.update(events)
    expected_events_0 = r0.chase()
    r0.update(expected_events_0)
    r1.update(expected_events_0)
    expected_events_1 = r1.chase()
    r0.update(expected_events_1)
    r1.update(expected_events_1)
    # r0.print_tables()
    theta_0 = build(r0.extension_table, 65)
    # r1.print_tables()
    theta_1 = build(r1.extension_table, 65)

    # check if a violation exists
    if sat_test(And(theta_0, theta_1)):
        raise Exception("incorrect: violation exists")
    else:
        pass
    return "passed", True

def build_test_6():
    rule_0 = Rule(
        rule_id=0,
        body=[  EventAtom("E1", [], "x1") ],
        head=[  EventAtom("E2", [], "x2") ]
    )
    rule_1 = Rule(
        rule_id=1,
        body=[  EventAtom("E1", [], "x1"), 
                EventAtom("E2", [], "x2"),
                ArithmeticAtom("x1 + 10 <= x2"),
                ],
        head=[  EventAtom("E3", [], "x3"),
                ArithmeticAtom("x1 == x3"),
        ]
    )
    events = [  Event("E1", [], 50) ]

    r0 = RuleTables(rule_0)
    r1 = RuleTables(rule_1)
    r0.update(events)
    r1.update(events)
    expected_events_0 = r0.chase()
    r0.update(expected_events_0)
    r1.update(expected_events_0)
    expected_events_1 = r1.chase()
    r0.update(expected_events_1)
    r1.update(expected_events_1)
    # r0.print_tables()
    theta_0 = build(r0.extension_table, 55)
    # r1.print_tables()
    theta_1 = build(r1.extension_table, 55)

    # check if a violation exists
    if sat_test(And(theta_0, theta_1)):
        pass
    else:
        raise Exception("incorrect: no violation exists")
    return "passed", True

def unit_test_suite(test):
    log, passed = test()
    if passed:
        print("passed "+test.__name__)
    else:
        print("\n".join(log)+"\n\n")
        raise Exception("failed "+test.__name__)

def update_test_suite():
    update_tests = [update_test_1, update_test_2, update_test_3, update_test_4, update_test_5]
    for test in update_tests:
        log, passed = test()
        if passed:
            print("passed "+test.__name__)
        else:
            print("\n".join(log)+"\n\n")
            raise Exception("failed "+test.__name__)
    print("passed "+str(len(update_tests))+" tests in update_test_suite")

def chase_test_suite():
    chase_tests = [chase_test_1, chase_test_2]
    for test in chase_tests:
        log, passed = test()
        if passed:
            print("passed "+test.__name__)
        else:
            print("\n".join(log)+"\n\n")
            raise Exception("failed "+test.__name__)
    print("passed "+str(len(chase_tests))+" tests in chase_test_suite")

def constraint_test_suite():
    constraint_tests = [constraint_test_1, constraint_test_2, constraint_test_3, constraint_test_4, constraint_test_5]
    for test in constraint_tests:
        log, passed = test()
        if passed:
            print("passed "+test.__name__)
        else:
            print("\n".join(log)+"\n\n")
            raise Exception("failed "+test.__name__)
    print("passed "+str(len(constraint_tests))+" tests in constraint_test_suite")

def chase_constraints_test_suite():
    chase_constraints_tests = [chase_constraints_test_1, chase_constraints_test_2]
    for test in chase_constraints_tests:
        log, passed = test()
        if passed:
            print("passed "+test.__name__)
        else:
            print("\n".join(log)+"\n\n")
            raise Exception("failed "+test.__name__)
    print("passed "+str(len(chase_constraints_tests))+" tests in chase_constraints_test_suite")

def build_test_suite():
    build_tests = [build_test_1, build_test_2, build_test_3, build_test_4, build_test_5, build_test_6]
    for test in build_tests:
        log, passed = test()
        if passed:
            print("passed "+test.__name__)
        else:
            print("\n".join(log)+"\n\n")
            raise Exception("failed "+test.__name__)
    print("passed "+str(len(build_tests))+" tests in build_test_suite")

if __name__ == "__main__":
    
    unit_test_mode = False

    if unit_test_mode:

        unit_test = constraint_test_3

        log, passed = unit_test()
        if passed:
            print("passed "+unit_test.__name__)
        else:
            print("\n".join(log)+"\n\n")
            raise Exception("failed "+unit_test.__name__)
        print("finished "+unit_test.__name__)
    else:
        test_suites = [
            update_test_suite,
            chase_test_suite,
            constraint_test_suite,
            build_test_suite,
        ]
        for test_suite in test_suites:
            test_suite()
        print()
        print("passed "+str(len(test_suites))+" test suites")