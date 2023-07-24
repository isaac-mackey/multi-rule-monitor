from monitor import *
from language import *
from rule_parser import *
from event_parser import *
import datetime
import pandas as pd
from edit_rules import *

if __name__ == "__main__":
    
    log_file_groups = {
        "test": [
            "a-e=975----c=10----b=10.txt",
            # "a-e=975----c=10----b=50.txt",
            # "a-e=975----c=10----b=100.txt",
            # "a-e=975----c=10----b=500.txt",
            # "a-e=765----c=43---b=10.txt",
            # "a-e=765----c=43---b=50.txt",
            # "a-e=765----c=43---b=100.txt",
            # "a-e=765----c=43---b=500.txt",
            # "a-e=731----c=100---b=10.txt",
            # "a-e=731----c=100---b=50.txt",
            # "a-e=731----c=100---b=100.txt",
            # "a-e=731----c=100---b=500.txt",
            # "a-e=5000---c=500---b=10.txt",
            # "a-e=5000---c=500---b=50.txt",
            # "a-e=5000---c=500---b=100.txt",
            # "a-e=5000---c=500---b=500.txt",
            # "a-e=5000---c=500---b=1000.txt",
            # "a-e=5000---c=1000---b=10.txt",
            # "a-e=5000---c=1000---b=50.txt",
            # "a-e=5000---c=1000---b=100.txt",
            # "a-e=5000---c=1000---b=500.txt",
            # "a-e=5000---c=1000---b=1000.txt",

        ],
        "one_log": [
            "a-e=975----c=100---b=10.txt",
        ],
        "a": [
            "a-e=731----c=100---b=10.txt",
            "a-e=731----c=100---b=50.txt",
            "a-e=731----c=100---b=100.txt",
            "a-e=731----c=100---b=500.txt",
            "a-e=765----c=43---b=10.txt",
            "a-e=765----c=43---b=100.txt",
            "a-e=765----c=43---b=50.txt",
            "a-e=765----c=43---b=500.txt",
            "a-e=975----c=10----b=10.txt",
            "a-e=975----c=10----b=100.txt",
            "a-e=975----c=10----b=50.txt",
            "a-e=975----c=10----b=500.txt",
            "a-e=5000---c=500---b=10.txt",
            "a-e=5000---c=500---b=50.txt",
            "a-e=5000---c=500---b=100.txt",
            "a-e=5000---c=500---b=500.txt",
            "a-e=5000---c=500---b=1000.txt",
            "a-e=5000---c=1000---b=10.txt",
            "a-e=5000---c=1000---b=100.txt",
            "a-e=5000---c=1000---b=1000.txt",
            "a-e=5000---c=1000---b=50.txt",
            "a-e=5000---c=1000---b=500.txt",
            ],
        "b": [
            "b-e=9640---c=10---b=10-rupnhs.txt",
            "b-e=9640---c=10---b=100-rupnhs.txt",
            "b-e=9640---c=10---b=1000-rupnhs.txt",
            "b-e=9640---c=100---b=10-rupnhs.txt",
            "b-e=9640---c=100---b=100-rupnhs.txt",
            "b-e=9640---c=100---b=1000-rupnhs.txt",
            "b-e=9640---c=1000---b=10-rupnhs.txt",
            "b-e=9640---c=1000---b=100-rupnhs.txt",
            "b-e=9640---c=1000---b=1000-rupnhs.txt",   
        ],
        "d": [
            "d-e=5000---c=10---b=10.txt",
            "d-e=5000---c=10---b=50.txt",
            "d-e=5000---c=10---b=100.txt",
            "d-e=5000---c=10---b=500.txt",
            "d-e=5000---c=10---b=1000.txt",
            "d-e=5000---c=100---b=10.txt",
            "d-e=5000---c=100---b=50.txt",
            "d-e=5000---c=100---b=100.txt",
            "d-e=5000---c=100---b=500.txt",
            "d-e=5000---c=100---b=1000.txt",
            "d-e=5000---c=1000---b=10.txt",
            "d-e=5000---c=1000---b=50.txt",
            "d-e=5000---c=1000---b=100.txt",
            "d-e=5000---c=1000---b=500.txt"
            "d-e=5000---c=1000---b=1000.txt",
        ],

    }

    rule_set_names = {
                "small": ["rules/small-rule-1.txt", "rules/small-rule-2.txt", "rules/small-rule-3.txt"],
                "medium": ["rules/medium-rule-1.txt", "rules/medium-rule-2.txt", "rules/medium-rule-3.txt"],
                "large": ["rules/large-rule-1.txt", "rules/large-rule-2.txt", "rules/large-rule-3.txt"],
                
                "one_rule": ["rules/small-rule-1.txt"],
                "two_rule": ["rules/small-rule-1.txt", "rules/small-rule-2.txt"],
                "three_rule": ["rules/small-rule-1.txt", "rules/small-rule-2.txt", "rules/small-rule-3.txt"],
                "four_rule": ["rules/small-rule-1.txt", "rules/small-rule-2.txt", "rules/small-rule-3.txt", "rules/small-rule-4.txt"],
                "five_rule": ["rules/small-rule-1.txt", "rules/small-rule-2.txt", "rules/small-rule-3.txt", "rules/small-rule-4.txt", "rules/small-rule-5.txt"],

                "shared-atoms-1" : ["rules/shared-atoms-1.txt"],
                "shared-atoms-2" : ["rules/shared-atoms-2.txt"],
                "shared-atoms-3" : ["rules/shared-atoms-3.txt"],

                "num=1--overlap=0": [ "rules/num=1--overlap=0" ], 
                "num=2--overlap=1": [ "rules/num=2--overlap=1" ], 
                "num=2--overlap=2": [ "rules/num=2--overlap=2" ], 
                "num=2--overlap=3": [ "rules/num=2--overlap=3" ], 
                "num=2--overlap=4": [ "rules/num=2--overlap=4" ], 
                'num=2--overlap=4a': [ 'rules/num=2--overlap=4a' ],
                "num=3--overlap=0": [ "rules/num=3--overlap=0" ], 
                "num=3--overlap=1": [ "rules/num=3--overlap=1" ], 
                "num=3--overlap=2": [ "rules/num=3--overlap=2" ], 
                "num=3--overlap=3": [ "rules/num=3--overlap=3" ], 
                'num=3--overlap=3a': [ 'rules/num=3--overlap=3a' ],
                "num=3--overlap=4": [ "rules/num=3--overlap=4" ], 
                "num=4--overlap=0": [ "rules/num=4--overlap=0" ], 
                "num=4--overlap=1": [ "rules/num=4--overlap=1" ], 
                "num=4--overlap=2": [ "rules/num=4--overlap=2" ], 
                "num=4--overlap=3": [ "rules/num=4--overlap=3" ],
                'num=4--overlap=3a': [ 'rules/num=4--overlap=3a' ],
                'num=4--overlap=3b': [ 'rules/num=4--overlap=3b' ],
                "num=4--overlap=4": [ "rules/num=4--overlap=4" ], 
                "num=4--overlap=5": [ "rules/num=4--overlap=5" ],
    }

    test_rule_group = [ "medium" ]

    dimension_analysis = [ "small" ]

    number_rules = ["one_rule", "two_rule", "three_rule", "four_rule", "five_rule"]

    overlap = [ "shared-atoms-1", "shared-atoms-2", "shared-atoms-3" ]
    overlap = [ 
                # "num=1--overlap=0", 
                # "num=2--overlap=1", 
                # "num=2--overlap=2", 
                # "num=2--overlap=3", 
                # "num=2--overlap=4", 
                "num=3--overlap=0", 
                "num=3--overlap=1", 
                "num=3--overlap=2", 
                "num=3--overlap=3", 
                'num=3--overlap=3a',
                "num=3--overlap=4", 
                "num=4--overlap=0", 
                "num=4--overlap=1", 
                "num=4--overlap=2", 
                "num=4--overlap=3", 
                'num=4--overlap=3a',
                "num=4--overlap=4", 
                "num=4--overlap=5", 
    ]
    
    df = pd.DataFrame([], columns=["log-file", "num-events", "conc", "batch-size",  "rule-set", "num-rules", "overlap", "ave-time"])

    experiment_number = 3

    if experiment_number == 0:
        log_group = "test"
        rule_sets = test_rule_group
    elif experiment_number == 1:
        log_group = "a"
        rule_sets = dimension_analysis
    elif experiment_number == 2:
        log_group = "a"
        rule_sets = number_rules
    elif experiment_number == 3:
        log_group = "test"
        rule_sets = overlap
    else:
        print("Invalid experiment number")
        exit()

    for log in log_file_groups[log_group]:
        log = "../LogGenerator/output/"+log
        for rule_set in rule_sets:
            parsed_rules = []
            print(rule_set_names[rule_set])
            for rule_file in rule_set_names[rule_set]:
                rules = parse_rule_file(rule_file)
                for rule in rules:
                    # print("Parsed rule: {}".format(rule))
                    parsed_rules.append(rule)

            monitor = Monitor(rules=parsed_rules)

            # print date and time
            print("Date and time: {}".format(datetime.datetime.now()))
            print("Processing log file: {}".format(log))
            print("Rules: {}".format(rule_set))
            batch_processing_times = monitor.process_log_file(log)
            average = sum(batch_processing_times) / len(batch_processing_times)
            print("Average processing time: {}".format(average))
            print("Completed processing log file")

            matches = re.findall(r'=(\d+)', log)
            num_events = len(batch_processing_times) * monitor.batch_size
            concurrency = int(matches[1])
            batch_size = int(matches[2])
            num_rules = len(parsed_rules)
            new_row = {"log-file": log, "num-events": num_events, "conc": concurrency, "batch-size": monitor.batch_size, "rule-set": rule_set, "num-rules": num_rules, "overlap": compute_overlap_ruleset(parsed_rules), "ave-time": average}
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            print(df.to_string())

    # except Exception as e:
    #     print("Exception: {}".format(e))

    print()
    print("Date and time: {}".format(datetime.datetime.now()))
    print(df.to_string())