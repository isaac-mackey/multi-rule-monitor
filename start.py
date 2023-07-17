from monitor import *
from rule_parser import *
from event_parser import *

if __name__ == "__main__":
    
    # define log file
    logs = [
        'logs/ab.txt',
        'logs/a_rup_num-events=975___ccrcy=10____batchsize=10.txt',
        'logs/a_rup_num-events=975___ccrcy=10____batchsize=100.txt',
        'logs/a_rup_num-events=975___ccrcy=10____batchsize=1000.txt',
    ]
    log_file = "logs/log_2.txt"

    log_selector = 0
    log_file = logs[log_selector]

    # define rule file and parse it
    rule_file_names = ["rules/rule_3.txt"]
    rules = []
    for rule_file_name in rule_file_names:
        rule = parse_rule_file(rule_file_name)
        print("Parsed rule: {}".format(rule))
        rules.append(rule)

    monitor = Monitor(rules=rules)

    print("Processing log file")
    results = monitor.process_log_file(log_file)
    
    print("Completed processing log file")
    print("Total number of events: {}".format(len(list(filter(lambda e: not e.expected, monitor.events)))))