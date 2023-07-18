from monitor import *
from language import *
from rule_parser import *
from event_parser import *
import datetime
import pandas as pd

if __name__ == "__main__":
    
    log_file_groups = {
        "test": [
            "a-e=975----c=10----b=10.txt",
            "a-e=975----c=10----b=50.txt",
            "a-e=975----c=10----b=100.txt",
            "a-e=975----c=10----b=500.txt",
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
                "num=2--overlap=4": [ "rules/num=2--overlap=4" ], 
                "num=3--overlap=0": [ "rules/num=3--overlap=0" ], 
                "num=3--overlap=1": [ "rules/num=3--overlap=1" ], 
                "num=3--overlap=2": [ "rules/num=3--overlap=2" ], 
                "num=3--overlap=3": [ "rules/num=3--overlap=3" ], 
                "num=4--overlap=0": [ "rules/num=4--overlap=0" ], 
                "num=4--overlap=1": [ "rules/num=4--overlap=1" ], 
                "num=4--overlap=2": [ "rules/num=4--overlap=2" ], 
                "num=4--overlap=3": [ "rules/num=4--overlap=3" ], 
    }

    test_rule_group = [ "medium" ]

    dimension_analysis = [ "small" ]

    number_rules = ["one_rule", "two_rule", "three_rule", "four_rule", "five_rule"]

    overlap = [ "shared-atoms-1", "shared-atoms-2", "shared-atoms-3" ]
    overlap = [ 
                "num=1--overlap=0",
                "num=1--overlap=0",
                "num=2--overlap=1",
                "num=2--overlap=2",
                "num=2--overlap=4",
                "num=3--overlap=0",
                "num=3--overlap=1",
                "num=3--overlap=2",
                "num=3--overlap=3",
                "num=4--overlap=0",
                "num=4--overlap=1",
                "num=4--overlap=2",
                "num=4--overlap=3",
    ]
    
    df = pd.DataFrame([], columns=["log-file", "rule-set", "batch-size", "conc", "ave-time"])

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
        log_group = "one_log"
        rule_sets = overlap
    else:
        print("Invalid experiment number")
        exit()
    
    batch_size_values = []
    concurrency_values = []

    try:
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

                head_to_body_overlap = 0
                for r1 in parsed_rules:
                    for r2 in parsed_rules:
                        for b in r1.body:
                            for h in r2.head:
                                if isinstance(b, EventAtom) and isinstance(h, EventAtom):
                                    if b.predicate == h.predicate:
                                        head_to_body_overlap += 1

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
                rule_set += '('+str(len(rule_set_names[rule_set]))+')'

                new_row = {"log-file": log, "rule-set": rule_set, "num-events": num_events, "conc": concurrency, "batch-size": monitor.batch_size, "overlap": head_to_body_overlap, "ave-time": average}
                batch_size_values.append(monitor.batch_size)
                concurrency_values.append(concurrency) 
                
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                print(df)
    except Exception as e:
        print("Exception: {}".format(e))

    print()
    print("Date and time: {}".format(datetime.datetime.now()))
    print(df)

    result = ""
    result += "Batch Size & "
    concurrency_values = sorted(list(set(concurrency_values)))
    batch_size_values = sorted(list(set(batch_size_values)))
    for concurrency in concurrency_values:
        result += "C="+str(concurrency)+" & "
    result = result[:-3] + "\n"
    for batch_size in batch_size_values:
        result += str(batch_size)+" & "
        for concurrency in concurrency_values:
            filtered_df = df[(df['batch-size'] == batch_size) & (df['conc'] == concurrency)]
            average_value = 0
            for index, row in filtered_df.iterrows():
                average_value += row['ave-time']
            if len(filtered_df.index):
                average_value /= len(filtered_df.index)
                result += str(average_value) + " & "
            else:
                result += "X & "
        result = result[:-3] + "\n"

    print(result)

'''
Experiment 1: Dimension Analysis
                                            log-file   rule-set batch-size conc  ave-time  num-events
0  ../LogGenerator/output/a-e=975----c=10----b=10...  medium(3)         10   10  0.060877       970.0
1  ../LogGenerator/output/a-e=975----c=10----b=50...  medium(3)         50   10  0.194898       950.0
2  ../LogGenerator/output/a-e=975----c=10----b=10...  medium(3)        100   10  0.373640       900.0
3  ../LogGenerator/output/a-e=975----c=10----b=50...  medium(3)        500   10  1.255612       500.0

0  ../LogGenerator/output/a-e=765----c=43---b=10.txt  medium(3)         10   43  0.046098       760.0
1  ../LogGenerator/output/a-e=765----c=43---b=50.txt  medium(3)         50   43  0.169014       750.0
2  ../LogGenerator/output/a-e=765----c=43---b=100...  medium(3)        100   43  0.328009       700.0
3  ../LogGenerator/output/a-e=765----c=43---b=500...  medium(3)        500   43  1.851411       500.0

0  ../LogGenerator/output/a-e=731----c=100---b=10...  medium(3)         10  100  0.293608       730.0
1  ../LogGenerator/output/a-e=731----c=100---b=50...  medium(3)         50  100  0.403104       700.0
2  ../LogGenerator/output/a-e=731----c=100---b=10...  medium(3)        100  100  0.552624       700.0
3  ../LogGenerator/output/a-e=731----c=100---b=50...  medium(3)        500  100  1.326460       500.0

0  ../LogGenerator/output/a-e=5000---c=1000---b=1...  medium(3)         10  1000  3.030983      5000.0
1  ../LogGenerator/output/a-e=5000---c=1000---b=5...  medium(3)         50  1000  3.269044      5000.0
2  ../LogGenerator/output/a-e=5000---c=1000---b=1...  medium(3)        100  1000  3.482907      5000.0
3  ../LogGenerator/output/a-e=5000---c=1000---b=5...  medium(3)        500  1000  5.278982      5000.0
4  ../LogGenerator/output/a-e=5000---c=1000---b=1...  medium(3)       1000  1000  7.690818      5000.0



Experiment 2: Number of Rules
Date and time: 2023-07-13 11:27:02.927605
                                             log_file     rule_set batch_size concurrency  average_processing_time  number events
0   ../LogGenerator/output/a-e=975----c=10----b=10...    one_rule1         10          10                 0.393889          975.0
10  ../LogGenerator/output/a-e=975----c=100---b=10...    one_rule1         10         100                 0.602938          975.0
5   ../LogGenerator/output/a-e=975----c=10----b=10...    one_rule1        100          10                 0.998220          975.0
15  ../LogGenerator/output/a-e=975----c=100---b=10...    one_rule1        100         100                 1.008815          975.0

1   ../LogGenerator/output/a-e=975----c=10----b=10...    two_rule2         10          10                 0.810125          975.0
11  ../LogGenerator/output/a-e=975----c=100---b=10...    two_rule2         10         100                 1.304450          975.0
6   ../LogGenerator/output/a-e=975----c=10----b=10...    two_rule2        100          10                 2.065917          975.0
16  ../LogGenerator/output/a-e=975----c=100---b=10...    two_rule2        100         100                 2.179334          975.0

2   ../LogGenerator/output/a-e=975----c=10----b=10...  three_rule3         10          10                 1.239180          975.0
12  ../LogGenerator/output/a-e=975----c=100---b=10...  three_rule3         10         100                 1.997940          975.0
7   ../LogGenerator/output/a-e=975----c=10----b=10...  three_rule3        100          10                 3.117692          975.0
17  ../LogGenerator/output/a-e=975----c=100---b=10...  three_rule3        100         100                 3.354450          975.0

3   ../LogGenerator/output/a-e=975----c=10----b=10...   four_rule4         10          10                 1.647203          975.0
13  ../LogGenerator/output/a-e=975----c=100---b=10...   four_rule4         10         100                 2.609007          975.0
8   ../LogGenerator/output/a-e=975----c=10----b=10...   four_rule4        100          10                 4.106302          975.0
18  ../LogGenerator/output/a-e=975----c=100---b=10...   four_rule4        100         100                 4.353116          975.0

4   ../LogGenerator/output/a-e=975----c=10----b=10...   five_rule5         10          10                 2.070799          975.0
14  ../LogGenerator/output/a-e=975----c=100---b=10...   five_rule5         10         100                 3.155237          975.0
9   ../LogGenerator/output/a-e=975----c=10----b=10...   five_rule5        100          10                 5.099725          975.0
19  ../LogGenerator/output/a-e=975----c=100---b=10...   five_rule5        100         100                 5.261761          975.0


Experiment 3: Overlapping Rules
Date and time: 2023-07-13 14:37:10.153668
                                             log_file            rule_set batch_size concurrency  average_processing_time  number events
0   ../LogGenerator/output/a-e=975----c=10----b=10...    one_shared_atom2         10          10                 0.431946          975.0
8   ../LogGenerator/output/a-e=975----c=100---b=10...    one_shared_atom2         10         100                 1.257681          975.0
4   ../LogGenerator/output/a-e=975----c=10----b=10...    one_shared_atom2        100          10                 1.241121          975.0
12  ../LogGenerator/output/a-e=975----c=100---b=10...    one_shared_atom2        100         100                 1.790256          975.0

1   ../LogGenerator/output/a-e=975----c=10----b=10...    two_shared_atom2         10          10                 1.189278          975.0
9   ../LogGenerator/output/a-e=975----c=100---b=10...    two_shared_atom2         10         100                 2.879041          975.0
5   ../LogGenerator/output/a-e=975----c=10----b=10...    two_shared_atom2        100          10                 3.509819          975.0
13  ../LogGenerator/output/a-e=975----c=100---b=10...    two_shared_atom2        100         100                 4.536579          975.0

2   ../LogGenerator/output/a-e=975----c=10----b=10...  three_shared_atom2         10          10                 1.194229          975.0
6   ../LogGenerator/output/a-e=975----c=10----b=10...  three_shared_atom2        100          10                 3.389745          975.0
10  ../LogGenerator/output/a-e=975----c=100---b=10...  three_shared_atom2         10         100                 2.231228          975.0
14  ../LogGenerator/output/a-e=975----c=100---b=10...  three_shared_atom2        100         100                 3.737768          975.0

3   ../LogGenerator/output/a-e=975----c=10----b=10...   four_shared_atom2         10          10                 0.514962          975.0
11  ../LogGenerator/output/a-e=975----c=100---b=10...   four_shared_atom2         10         100                 1.103682          975.0
7   ../LogGenerator/output/a-e=975----c=10----b=10...   four_shared_atom2        100          10                 1.965417          975.0
15  ../LogGenerator/output/a-e=975----c=100---b=10...   four_shared_atom2        100         100                 2.051071          975.0


Date and time: 2023-07-14 10:22:15.236396
                                            log_file           rule_set batch_size concurrency  average_processing_time  number events
0  ../LogGenerator/output/a-e=975----c=100---b=10...  shared-atoms-1(1)         10         100                 1.219294          975.0
1  ../LogGenerator/output/a-e=975----c=100---b=10...  shared-atoms-2(1)         10         100                 2.170418          975.0
2  ../LogGenerator/output/a-e=975----c=100---b=10...  shared-atoms-3(1)         10         100                 9.288008          975.0
Batch Size & C=10 & C=43 & C=100
10 & 1.219293620488415 & 2.1704175635559917 & 9.288008418801713 & 1.219293620488415 & 2.1704175635559917 & 9.288008418801713 & 1.219293620488415 & 2.1704175635559917 & 9.288008418801713
10 & 1.219293620488415 & 2.1704175635559917 & 9.288008418801713 & 1.219293620488415 & 2.1704175635559917 & 9.288008418801713 & 1.219293620488415 & 2.1704175635559917 & 9.288008418801713
10 & 1.219293620488415 & 2.1704175635559917 & 9.288008418801713 & 1.219293620488415 & 2.1704175635559917 & 9.288008418801713 & 1.219293620488415 & 2.1704175635559917 & 9.288008418801713

'''
