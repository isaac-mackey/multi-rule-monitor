'''This file contains the following classes and functions:
- StreamSchema
- Stream
- EventSchema
- Event
- generate_random_stream_schema
- generate_random_stream
- generate_random_events
streams'''

'''import libraries'''
import random
import numpy as np

'''define a StreamSchema class with a list of event schemas'''
'''Example: StreamSchema([EventSchema("event0", ["attribute0", "attribute1"]), EventSchema("event1", ["attribute0", "attribute1"])])'''
class StreamSchema:
    def __init__(self, event_schemas):
        self.event_schemas = event_schemas

    def __str__(self):
        return str(self.event_schemas)

    def __repr__(self):
        return str(self.event_schemas)
    
'''define a Stream class with an event schema and a list of events'''
'''Example: Stream([Event("event0", {"attribute0":0, "attribute1":1}, 0), Event("event1", {"attribute0":0, "attribute1":1}, 0)], [EventSchema("event0", ["attribute0", "attribute1"]), EventSchema("event1", ["attribute0", "attribute1"])])'''
class Stream:
    def __init__(self, events, event_schemas):
        self.event_schemas = event_schemas 
        self.events = events
    
    def __str__(self):
        result = "Stream Schema: " + str(self.event_schemas) + "\n"
        for i in range(len(self.events)):
            result += "Time " + str(i) + ": " + str(self.events[i]) + "\n"
        return result

    def __repr__(self):
        return str(self.event_schemas) + " " + str(self.events)
    
'''define an EventSchema class with a name and a list of attributes'''
'''Example: EventSchema("event0", ["attribute0", "attribute1"])'''
class EventSchema:
    def __init__(self, event_name, attributes):
        self.event_name = event_name
        self.attributes = attributes

    def __str__(self):
        return self.event_name + " " + str(self.attributes)

    def __repr__(self):
        return self.event_name + " " + str(self.attributes)

'''define an Event (instance) class with a name, data, and a timestamp'''
'''Example: Event("event0", {"attribute0":0, "attribute1":1}, 0)'''
class Event:
    def __init__(self, event_name, data, timestamp, expected=False, constraints=[]):
        self.event_name = event_name
        self.data = data
        self.timestamp = timestamp
        self.expected = expected
        self.constraints = constraints
    
    def __repr__(self):
        return ('e' if self.expected else '') + self.event_name + str(self.data) + "@" + str(self.timestamp)+"("+ str(self.constraints) + ")"

    def __eq__(self, __value: object) -> bool:
        return self.event_name == __value.event_name and self.data == __value.data and self.timestamp == __value.timestamp and self.expected == __value.expected and self.constraints == __value.constraints
    
    def __hash__(self) -> int:
        return hash((self.event_name, str(self.data), self.timestamp, self.expected, str(self.constraints)))

'''define a function that generates events from a stream schema
each timestamp has a random subset of events from the stream schema'''
'''Example: generate_random_events(StreamSchema([EventSchema("event0", ["attribute0", "attribute1"]), EventSchema("event1", ["attribute0", "attribute1"])]), 10)'''
def generate_random_stream(stream_schema, length):
    events = []
    for timestamp in range(length):
        events.append([])
        for event_schema in stream_schema.event_schemas:
            if random.random() < 2:
                events[timestamp].append(generate_random_event(event_schema, timestamp))
            else:
                pass
    return Stream(events, stream_schema.event_schemas)

'''define a function that generates random stream schemas'''
def generate_random_stream_schema(num_event_schemas, min_num_attributes, max_num_attributes):
    event_schemas = []
    for i in range(num_event_schemas):
        event_name = "E" + str(i)
        attributes = ["attr" + str(j) for j in range(random.randint(min_num_attributes, max_num_attributes))]
        event_schemas.append(EventSchema(event_name, attributes))
    return StreamSchema(event_schemas)

'''define a function that generates random events'''
def generate_random_event(event_schema, timestamp):
    random_data = [random.randint(0, 100) for a in event_schema.attributes]
    return Event(event_schema.event_name, random_data, timestamp)

'''preprocess stream for an aggregate operator and selected attribute'''
def preprocess_stream(stream, event_name, aggregate_operator, selected_attribute):
    for timestamp in range(len(stream.events)):
        names = [event.event_name for event in stream.events[timestamp]]
        if event_name not in names:
            if aggregate_operator == "sum":
                stream.events[timestamp].append(Event(event_name, [0], timestamp))
            elif aggregate_operator == "count":
                stream.events[timestamp].append(Event(event_name, [0], timestamp))
            elif aggregate_operator == "max":
                stream.events[timestamp].append(Event(event_name, ['-infty'], timestamp))
            elif aggregate_operator == "min":
                stream.events[timestamp].append(Event(event_name, ['+infty'], timestamp))
            else:
                exception = "Invalid aggregate operator: " + aggregate_operator
                raise Exception(exception)
    return stream

'''main function'''
if __name__ == "__main__":
    
    '''generate a random stream schema'''
    print("generate a random stream schema")
    ss0 = generate_random_stream_schema(num_event_schemas=2, min_num_attributes=2, max_num_attributes=2)
    print(ss0)
    print()

    '''generate a random stream'''
    print("generate a random stream")
    stream = generate_random_stream(stream_schema=ss0, length=20)
    print(stream)
    print()

    '''preprocess the stream for an aggregate operator and selected attribute'''
    print("preprocess the stream for an aggregate operator and selected attribute")

    for i in range(len(stream.event_schemas)):
        for k in range(len(stream.event_schemas[i].attributes)):
            stream = preprocess_stream(stream, "E" + str(i), "sum", stream.event_schemas[i].attributes[k])
            print('preprocess_stream(stream, "E' + str(i) + '", "sum", "' + stream.event_schemas[i].attributes[k] + '")')

    # find the maximum length up to the first @ symbol
    max_length = 0

    # find the maximum length between the first and second @ symbols
    max_length2 = 0

    for i in range(len(stream.events)):
        max_length = max(max_length, len(str(stream.events[i]).split("@")[0]))
        max_length2 = max(max_length2, len(str(stream.events[i]).split("@")[1]))

    '''print the stream but pad it with spaces so that the timestamps line up'''
    print("print the stream but pad it with spaces so that the @ symbols line up")

    for i in range(len(stream.events)):
        print(str(stream.events[i]).split("@")[0].ljust(max_length) + "@" + str(stream.events[i]).split("@")[1].ljust(max_length2))