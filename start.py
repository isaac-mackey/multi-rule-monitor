from monitor import *
from rule_parser import *
from event_parser import *
from sys import argv

if __name__ == "__main__":
    
    log_file = argv[1]
    print("Processing log file: {}".format(log_file))
    
    rule_file_name = argv[2]
    rules = parse_rule_file(rule_file_name)
    for rule in rules:
        print("Monitoring rule: {}".format(rule))

    monitor = Monitor(rules=rules)

    batch_processing_times = monitor.process_log_file(log_file)
    average = sum(batch_processing_times) / len(batch_processing_times)
    print("Average processing time: {}".format(average))
    print("Completed processing log file")