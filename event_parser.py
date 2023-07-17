from stream import *

def parse_event(event_string):

    # Example: 5 11 2 read support=0 Value=50

    event_string_list = event_string.split(" ")
    event_timestamp = int(event_string_list[0])
    enactment_id = int(event_string_list[1])
    # enactment_process_id = int(event_string_list[2])
    event_name = event_string_list[3].strip()
    
    if event_name == "START" or event_name == "END":
        event_instance = Event(event_name, [enactment_id], event_timestamp)
        return event_instance
    else:
        event_args = event_string_list[4:]
        event_data = [x[x.index('=')+1:].strip() for x in event_args]
        event_data = [enactment_id] + event_data
        event_instance = Event(event_name, event_data, event_timestamp)
        return event_instance
    return None

if __name__ == "__main__":
    # Example usage
    event_string = '5 11 2 read support=0 Value=50'
    event_string_2 = '5 12 2 START'
    event_string_3 = '5 13 2 END'
    event_string_4 = '5 7 3 check_faq support=0'

    event_strings = [event_string, event_string_2, event_string_3, event_string_4]

    for event_string in event_strings:
        parsed_event = parse_event(event_string)
        
        print("Event Name:", parsed_event.event_name)
        print("Data:", parsed_event.data)
        print("Timestamp:", parsed_event.timestamp)
        print()
