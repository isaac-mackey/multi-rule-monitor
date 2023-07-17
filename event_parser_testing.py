from stream import *
import ast

def parse_events(event_string):
    events = []
    event_list = event_string.split(",")
    for event_data in event_list:
        event_data = event_data.strip()
        event_parts = event_data.split("(")
        event_name = event_parts[0].strip()
        event_args = event_parts[1].split(")")[0]
        event_args = [arg.strip() for arg in event_args.split(",")]
        event_instance = Event(event_name, event_args[:-1], event_args[-1])
        events.append(event_instance)
    return events

def parse_event(event_string):
    event_parts = event_string.split("(")
    event_args = event_parts[1].split(")")[0]
    event_name = event_args.split(",")[0].replace('"', '').replace("'", '')
    event_timestamp = int(event_args.split(",")[-1])
    string_list = event_args.split(",")[1][1:]
    parsed_list = ast.literal_eval(string_list)
    event_instance = Event(event_name, parsed_list, event_timestamp)
    return event_instance

if __name__ == "__main__":
    # Example usage
    event_string = 'Event("E1", [43], 0), Event("E2", [51], 2), Event("E3", [51], 3)'

    parsed_events = parse_events(event_string)
    for event in parsed_events:
        print("Event Name:", event.event_name)
        print("Variables:", event.variables)
        print("Value:", event.value)
        print()
