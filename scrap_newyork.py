import requests
import json
import csv
import time
from datetime import datetime ; import pickle

to = time.time()

event_code = 'm2022'
new_york_stats_file_name = f"NewYorkStats-{event_code}.csv"
new_york_stats_split_times_file_name = f"NewYorkStatsSplitTimes-{event_code}.csv"
event_runner_uri = 'https://rmsprodapi.nyrr.org/api/v2/runners/eventRunner'
result_details_uri = 'https://rmsprodapi.nyrr.org/api/v2/runners/resultDetails'

#finishers = []
#finishers_details = []
#athletes=[]

with open('NYC_2022_1-6978.pkl', 'rb') as f:
    athletes = pickle.load(f)




max_runners = 70000
first_bib_number = 6979
last_bib_number = first_bib_number + max_runners
bib_numbers = range(first_bib_number, last_bib_number + 1)

headers = {'Content-Type': 'application/json;charset=utf-8'}
event_runner_body = {
    'eventCode': event_code,
    'bib': ''
}
result_details_body = {
    'runnerId': ''
}

print(f"{datetime.now().strftime('%H:%M:%S')} - START OF EXTRACTION FROM BIB {first_bib_number} TO BIB {last_bib_number}")

for bib in bib_numbers:
    if bib % 200 == 1:
        print(f"{datetime.now().strftime('%H:%M:%S')} - Bib number {bib}..")
# =============================================================================
#         with open(new_york_stats_file_name, 'a', newline='', encoding='utf-8') as f:
#             writer = csv.writer(f, delimiter=';')
#             writer.writerows(finishers)
#         with open(new_york_stats_split_times_file_name, 'a', newline='', encoding='utf-8') as f:
#             writer = csv.writer(f, delimiter=';')
#             writer.writerows(finishers_details)
# =============================================================================
        finishers = []
        finishers_details = []

    event_runner_body['bib'] = bib
    event_runner_parameters = {
        'url': event_runner_uri,
        'headers': headers,
        'data': json.dumps(event_runner_body)
    }

    try:
        response = requests.post(**event_runner_parameters)
        finisher = response.json().get('finisher')
        if finisher:
            #finishers.append(finisher)
            name,age,gender = finisher['firstName']+' '+finisher['lastName'],finisher['age'],finisher['gender']
            result_details_body['runnerId'] = finisher['runnerId']
            result_details_parameters = {
                'url': result_details_uri,
                'headers': headers,
                'data': json.dumps(result_details_body)
            }
            response = requests.post(**result_details_parameters)
            finisher_details = response.json().get('details', {}).get('splitResults')
            if finisher_details:
                splits = [x['time'] for x in response.json().get('details', {}).get('splitResults')] 
            else:
                print(f"No split times for bib {bib}")
            athletes.append([name,age,gender,bib]+splits)
        else:
            print(f"No stats for bib {bib}")
        time.sleep(0.1)
    except Exception as e:
        if 'Just a moment..' in str(e):
            print(f"Just a moment to retrieve bib {bib}..")
            time.sleep(0.5)
            response = requests.post(**event_runner_parameters)
            finisher = response.json().get('finisher')
            if finisher:
                #finishers.append(finisher)
                name,age,gender = finisher['firstName']+' '+finisher['lastName'],finisher['age'],finisher['gender']
                result_details_body['runnerId'] = finisher['runnerId']
                response = requests.post(**result_details_parameters)
                finisher_details = response.json().get('details', {}).get('splitResults')
                if finisher_details:
                    for detail in finisher_details:
                        splits = [x['time'] for x in response.json().get('details', {}).get('splitResults')] 
                else:
                    print(f"No split times for bib {bib}")
                athletes.append([name,age,gender,bib]+splits)

        else:
            print(f"An error occurred when retrieving bib '{bib}' => {e}")

    if not bib%1000 : 
        # Save the athletes data to a pickle file
        with open(f"NYC_2022_1-{bib}.pkl", 'wb') as f:
            pickle.dump(athletes, f)
        print(f'{bib} bibs processed in {time.time()-to}')
# =============================================================================
# with open(new_york_stats_file_name, 'a', newline='', encoding='utf-8') as f:
#     writer = csv.writer(f, delimiter=';')
#     writer.writerows(finishers)
# with open(new_york_stats_split_times_file_name, 'a', newline='', encoding='utf-8') as f:
#     writer = csv.writer(f, delimiter=';')
#     writer.writerows(finishers_details)
# =============================================================================

print(f"{datetime.now().strftime('%H:%M:%S')} - THE END!")