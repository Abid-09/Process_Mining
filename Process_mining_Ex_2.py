import xml.etree.ElementTree as ELT
from datetime import datetime
from collections import defaultdict

#1st function to log as dictionary from (csv like logs)
def log_as_dictionary(log):
    log_dict_list=defaultdict(list)
    for entry in log.strip().splitlines():
        if len(entry.split(';')) !=4:
            continue
        job, event_id, username, timestamp = entry.split(';')
        event = {
            'job': job,
            'user': username,
            'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
            'org:resource':'N/A',
            'cost':'n/a',
            
        }
        log_dict_list[event_id].append(event)
    return log_dict_list
def dependency_graph_inline(log):
    dg =defaultdict(lambda:defaultdict(int))
    for case_id,entry in log.items():
        for i in range(len(entry)-1):
            source_task = entry[i]['job']
            target_task = entry[i+1]['job']
            dg[source_task][target_task]+=1
    return dg
""" def read_from_file(filename):
    log_tree= ELT.parse(filename)
    root= log_tree.getroot()
   
    log_dictionary= defaultdict(list)
    namespace="{http://www.xes-standard.org/}"
    for index in root.findall(f'{namespace}index'):
        case_id=None
        entry=[]
        for entry in index:
            if entry.tag==f'{namespace}string' and entry.attrib['key']=='concept:name':
                case_id = entry.attrib['value']
            elif entry.tag == f'{namespace}entry':
                entry_data={}
                for prop in entry:
                    if prop.tag==f'{namespace}string':
                        entry_data[prop.attrib['key']]==prop.attrib['value']
                    elif prop.tag==f'{namespace}date':
                        date_as_string=prop.attrib['value']
                    try:
                        entry_data=[prop.attrib['key']]=datetime.strptime(date_as_string,'%Y-%m-%dT%H:%M:%S%z')
                    except ValueError:
                        entry_data[prop.attrib['key']]==datetime.strptime(date_as_string,'%Y-%m-%dT%H:%M:%S.%f%z')
                entry.append(entry_data)
        if case_id:
            log_as_dictionary[case_id].append(entry)
    return log_dictionary  """

def read_from_file(filename):
    log_tree = ELT.parse(filename)
    root = log_tree.getroot()
    namespace = "{http://www.xes-standard.org/}"
    log_dictionary = defaultdict(list)
    for trace in root.findall(f'{namespace}trace'):
        case_id = None
        events = []
        resource=None
        for event in trace.findall(f'{namespace}event'):
            
            event_data = {}
            for prop in event:
                if prop.tag == f'{namespace}string' and prop.attrib['key'] == 'concept:name':
                    event_data['concept:name'] = prop.attrib['value']
                elif prop.tag == f'{namespace}string' and prop.attrib['key'] == 'org:resource':
                    event_data['org:resource'] = prop.attrib['value']
                elif prop.attrib['key'] == 'cost':
                    event_data['cost'] = int(prop.attrib['value'])
                elif prop.tag == f'{namespace}date' and prop.attrib['key'] == 'time:timestamp':
                    event_data['time:timestamp'] =  datetime.strptime(prop.attrib['value'] , '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)   
                
                
                """ elif prop.tag == f'{namespace}date':
                    date_as_string = prop.attrib['value']
                    try:
                        event_data['timestamp'] = datetime.strptime(date_as_string, '%Y-%m-%dT%H:%M:%S%z')
                    except ValueError:
                        event_data['timestamp'] = datetime.strptime(date_as_string, '%Y-%m-%dT%H:%M:%S.%f%z') """
            
            if 'concept:name' in event_data:
                events.append(event_data)
                
        for prop in trace.findall(f'{namespace}string'):
            if prop.attrib['key'] == 'concept:name':
                case_id = prop.attrib['value']

        if case_id and events:
            log_dictionary[case_id].extend(events)

    return log_dictionary 
def dependency_graph_file(log):
    dependency_graph_id = defaultdict(lambda: defaultdict(int))
    for case_id, entry in log.items():
        for index in range(len(entry) - 1):
            source = entry[index]['concept:name']
            target = entry[index+1]['concept:name']
            dependency_graph_id[source][target] += 1
    return dependency_graph_id

def main():
    f = """
    Task_A;case_1;user_1;2019-09-09 17:36:47
    Task_B;case_1;user_3;2019-09-11 09:11:13
    Task_D;case_1;user_6;2019-09-12 10:00:12
    Task_E;case_1;user_7;2019-09-12 18:21:32
    Task_F;case_1;user_8;2019-09-13 13:27:41
    Task_A;case_2;user_2;2019-09-14 08:56:09
    Task_B;case_2;user_3;2019-09-14 09:36:02
    Task_D;case_2;user_5;2019-09-15 10:16:40
    Task_G;case_1;user_6;2019-09-18 19:14:14
    Task_G;case_2;user_6;2019-09-19 15:39:15
    Task_H;case_1;user_2;2019-09-19 16:48:16
    Task_E;case_2;user_7;2019-09-20 14:39:45
    Task_F;case_2;user_8;2019-09-22 09:16:16
    Task_A;case_3;user_2;2019-09-25 08:39:24
    Task_H;case_2;user_1;2019-09-26 12:19:46
    Task_B;case_3;user_4;2019-09-29 10:56:14
    Task_C;case_3;user_1;2019-09-30 15:41:22
    """

    log = log_as_dictionary(f)
    dg = dependency_graph_inline(log)

    for ai in sorted(dg.keys()):
        for aj in sorted(dg[ai].keys()):
            print (ai, '->', aj, ':', dg[ai][aj])
    
    
    log = read_from_file("extension-log.xes")
    for case_id in sorted(log):
        print((case_id, len(log[case_id])))
    case_id = "case_123"
    event_no = 0
    print((log[case_id][event_no]["concept:name"], log[case_id][event_no]["org:resource"], log[case_id][event_no]["time:timestamp"],  log[case_id][event_no]["cost"]))
if __name__ == "__main__":
    main()