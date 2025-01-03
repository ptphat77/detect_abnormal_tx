import pandas as pd
import requests
import time
import threading
import csv

# Đọc file Excel
data = pd.read_excel("./dataset/Table02-Transaction.xlsx")

# cell_value = data.loc[1, 'Event Name']

# for index, row in data.iterrows():
#     print("Chỉ số hàng:", index)
#     print("Dữ liệu của hàng:", row)
#     print("-------------------------------------")

# for row in data.itertuples():
#     print("Dữ liệu của hàng:", row)
#     print("-------------------------------------")


def http_request(url):
    try:
        # Send a GET request to the Etherscan API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            return data["result"]
        else:
            print(
                "Request to API failed. Please check your network connection or try again later."
            )
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # handle exceeded limit request
        time.sleep(7000)
        http_request(url)


network = {
    "ethereum": {
        "key": "SIHIX7SCIYTGBS54GTVQQA2W5GXDISD9XU",
        "api": "api.etherscan.io",
    },
    "bsc": {"key": "M6IIKGI25H3QFNWECXFBHU1E9SBS2NRAVX", "api": "api.bscscan.com"},
    "polygon": {
        "key": "4H4QFF99X2JMYXZ64ZH4M7ECAUEBFUPKPE",
        "api": "api.polygonscan.com",
    },
    "arbitrum": {"key": "7NMGU8SMIGX5F43H4IV8HEGIIS2FQ2SGGR", "api": "api.arbiscan.io"},
    "fantom": {"key": "DJC4CSP6T74DYA4Z53B9WD3YM6HA9AJYXS", "api": "api.ftmscan.com"},
    "moonriver": {
        "key": "4PF7HCWI4BDBSEP8E2DM3CP6298S1F6FJ1",
        "api": "api-moonriver.moonscan.io",
    },
}

check_exists_contract = []

# Init Data Frame empty
transaction_columns = [
    "hash",
    "from_address",
    "to_address",
    "network_name",
    "from_exploit",
    "to_exploit",
    "exploit",
    # "from_is_contract",
    # "to_is_contract",
    "value",
    "block_timestamp",
    "gas_price",
]
transaction_raw_df = pd.DataFrame(columns=transaction_columns)

address_columns = ["address", "network_name", "label"]
abnormal_address_df = pd.DataFrame(columns=address_columns)
normal_address_df = pd.DataFrame(columns=address_columns)


def is_contract(address, network_name):
    get_code_url = f"https://{network[network_name]['api']}/api?module=proxy&action=eth_getCode&address={address}&tag=latest&apikey={network[network_name]['key']}"

    bytecode = http_request(get_code_url)
    # if bytecode == "0x":
    #     print("address: ", address)
    #     print("bytecode: ", bytecode)
    # exit()

    return 1 if bytecode != "0x" else 0


def collect_abnormal_address():
    global abnormal_address_df

    for _, transaction in data.iterrows():
        if transaction["from_exploit"] == 1:
            new_row = list(
                [transaction["from_address"], transaction["network_name"], 1]
            )
            exists = (
                abnormal_address_df["address"].isin([transaction["from_address"]]).any()
            )
            if not exists:
                abnormal_address_df.loc[len(abnormal_address_df)] = new_row
        if transaction["to_exploit"] == 1:
            new_row = list([transaction["to_address"], transaction["network_name"], 1])
            exists = (
                abnormal_address_df["address"].isin([transaction["to_address"]]).any()
            )
            if not exists:
                abnormal_address_df.loc[len(abnormal_address_df)] = new_row


def collect_normal_address():
    global transaction_raw_df

    for _, transaction in transaction_raw_df.iterrows():
        if transaction["from_exploit"] == 0:
            new_row = list(
                [transaction["from_address"], transaction["network_name"], 0]
            )
            exists = (
                normal_address_df["address"].isin([transaction["from_address"]]).any()
            )
            if not exists:
                normal_address_df.loc[len(normal_address_df)] = new_row
        if transaction["to_exploit"] == 0:
            new_row = list([transaction["to_address"], transaction["network_name"], 0])
            exists = (
                normal_address_df["address"].isin([transaction["to_address"]]).any()
            )
            if not exists:
                normal_address_df.loc[len(normal_address_df)] = new_row

    # print(normal_address_df.shape)
    # print(normal_address_df.head(3))


def collect_abnormal_transaction():
    global abnormal_address_df
    global transaction_raw_df

    # url = f"https://api.etherscan.io/api?module=account&action=txlist&address=0x148426fDC4C8a51b96b4BEd827907b5FA6491aD0&startblock=0&endblock=99999999&page=1&offset=10000&sort=asc&apikey=SIHIX7SCIYTGBS54GTVQQA2W5GXDISD9XU"

    # data = http_request(url)

    # print("len(data): ", type(data))
    # print("len(data): ", len(data))
    # print("data: ", data[0])

    for _, address in abnormal_address_df.iterrows():
        print("##############################")
        contract_list = []
        network_name = address["network_name"]

        if network_name == "c-chain":
            continue

        url = f"https://{network[network_name]['api']}/api?module=account&action=txlist&address={address['address']}&startblock=0&endblock=99999999&page=1&offset=10000&sort=asc&apikey={network[network_name]['key']}"
        transantion_data = http_request(url)

        print(address)
        print(len(transantion_data))
        # print(transantion_data[0])

        for item in transantion_data:
            # Debug/Search transaction by hash
            # if (
            #     item["hash"].lower()
            #     == "0xa1b0e0765db4caa7a5e3d54e61fd76435f3ab358448a6da07098144646714116".lower()
            # ):
            #     print(item)
            #     exit()

            # Check tx exists
            # print(item["hash"])
            network_names = transaction_raw_df.loc[
                transaction_raw_df["hash"] == item["hash"], "network_name"
            ].tolist()
            # print(network_names)

            if network_name in network_names:
                continue

            # Add item to transaction_raw_df
            new_row = {
                "hash": item["hash"],
                "from_address": "",
                "to_address": "",
                "network_name": network_name,
                "from_exploit": 0,
                "to_exploit": 0,
                "exploit": 1,
                # "from_is_contract": 0,
                # "to_is_contract": 0,
                "value": item["value"],
                "block_timestamp": item["timeStamp"],
                "gas_price": item["gasPrice"],
            }
            if item["from"] != "":
                new_row["from_address"] = item["from"]
            if item["to"] != "":
                new_row["to_address"] = item["to"]

            if item["from"] == "":
                new_row["from_address"] = item["contractAddress"]
            if item["to"] == "":
                new_row["to_address"] = item["contractAddress"]

            # if item['to'] == '' or item['from'] == '':
            #     print('Address empty!!!')

            if item["from"] == address["address"] and item["to"] == address["address"]:
                print("Dulicate!!!")
                continue

            if (
                abnormal_address_df["address"]
                .str.lower()
                .isin([new_row["from_address"].lower()])
                .any()
            ):
                new_row["from_exploit"] = 1
            if (
                abnormal_address_df["address"]
                .str.lower()
                .isin([new_row["to_address"].lower()])
                .any()
            ):
                new_row["to_exploit"] = 1

            # if new_row["from_address"] in contract_list:
            #     new_row["from_is_contract"] = 1
            # elif is_contract(new_row["from_address"], network_name):
            #     new_row["from_is_contract"] = 1
            #     contract_list.append(new_row["from_address"])
            # if new_row["to_address"] in contract_list:
            #     new_row["to_is_contract"] = 1
            # elif is_contract(new_row["to_address"], network_name):
            #     new_row["to_is_contract"] = 1
            #     contract_list.append(new_row["to_address"])

            # print('contract_list: ', contract_list)

            transaction_raw_df = pd.concat(
                [transaction_raw_df, pd.DataFrame([new_row])], ignore_index=True
            )

        # Stop after collect all transactions of first address
        # break

    # print(transaction_raw_df.shape)
    # print(transaction_raw_df.iloc[0])
    # print(transaction_raw_df.iloc[0]['hash'])


def collect_normal_transaction():
    global normal_address_df
    global transaction_raw_df
    global normal_address_index
    normal_address_df_length = normal_address_df.shape[0]

    # url = f"https://api.etherscan.io/api?module=account&action=txlist&address=0x148426fDC4C8a51b96b4BEd827907b5FA6491aD0&startblock=0&endblock=99999999&page=1&offset=10000&sort=asc&apikey=SIHIX7SCIYTGBS54GTVQQA2W5GXDISD9XU"

    # data = http_request(url)

    # print("len(data): ", type(data))
    # print("len(data): ", len(data))
    # print("data: ", data[0])

    while True:
        normal_address_index_lock.acquire()
        try:
            if normal_address_index + 1 > normal_address_df_length:
                return

            normal_address_index += 1
            address = normal_address_df.iloc[normal_address_index]
        finally:
            normal_address_index_lock.release()

        print("##############################")
        contract_list = []
        network_name = address["network_name"]

        if network_name == "c-chain":
            continue

        url = f"https://{network[network_name]['api']}/api?module=account&action=txlist&address={address['address']}&startblock=0&endblock=99999999&page=1&offset=10000&sort=asc&apikey={network[network_name]['key']}"
        transantion_data = http_request(url)

        print(address)
        print(len(transantion_data))
        # print(transantion_data[0])

        transaction_thread = pd.DataFrame(columns=transaction_columns)

        for item in transantion_data:
            # Debug/Search transaction by hash
            # if (
            #     item["hash"].lower()
            #     == "0xa1b0e0765db4caa7a5e3d54e61fd76435f3ab358448a6da07098144646714116".lower()
            # ):
            #     print(item)
            #     exit()

            # Check tx exists
            # print(item["hash"])
            # if type(item["hash"]) != str:
            #     print("Checking tx failed")
            #     exit()

            # network_names = transaction_raw_df.loc[
            #     transaction_raw_df["hash"] == item["hash"], "network_name"
            # ].tolist()
            # print(network_names)

            # if network_name in network_names:
            #     continue

            # Add item to transaction_raw_df
            new_row = {
                "hash": item["hash"],
                "from_address": "",
                "to_address": "",
                "network_name": network_name,
                "from_exploit": 0,
                "to_exploit": 0,
                "exploit": 0,
                # "from_is_contract": 0,
                # "to_is_contract": 0,
                "value": item["value"],
                "block_timestamp": item["timeStamp"],
                "gas_price": item["gasPrice"],
            }
            if item["from"] != "":
                new_row["from_address"] = item["from"]
            if item["to"] != "":
                new_row["to_address"] = item["to"]

            if item["from"] == "":
                new_row["from_address"] = item["contractAddress"]
            if item["to"] == "":
                new_row["to_address"] = item["contractAddress"]

            # if item['to'] == '' or item['from'] == '':
            #     print('Address empty!!!')

            if item["from"] == address["address"] and item["to"] == address["address"]:
                print("Dulicate!!!")
                continue

            transaction_raw_df = pd.concat(
                [transaction_raw_df, pd.DataFrame([new_row])], ignore_index=True
            )

            transaction_thread = pd.concat(
                [transaction_thread, pd.DataFrame([new_row])], ignore_index=True
            )


        transaction_raw_lock.acquire()
        try:
            transaction_thread.to_csv('Transaction_raw.csv', mode='a', header=False, index=False)
        finally:
            transaction_raw_lock.release()    
        
        normal_adress_lock.acquire()
        try:
            remove_normal_address(address["address"], address["network_name"])
        finally:
            normal_adress_lock.release()


def merge_network_name():
    global transaction_raw_df

    # Add prefix 'network_name' to column 'hash'
    transaction_raw_df["hash"] = (
        transaction_raw_df["hash"] + "-" + transaction_raw_df["network_name"]
    )
    transaction_raw_df["from_address"] = (
        transaction_raw_df["from_address"] + "-" + transaction_raw_df["network_name"]
    )
    transaction_raw_df["to_address"] = (
        transaction_raw_df["to_address"] + "-" + transaction_raw_df["network_name"]
    )

    # Delete 'network_name'
    # transaction_raw_df = transaction_raw_df.drop("network_name", axis=1)

def remove_normal_address(address_to_remove, network_to_remove):
    # read csv
    with open('Normal_address_raw.csv', 'r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    # remove row
    filtered_rows = [row for row in rows if row['address'] != address_to_remove or row['network_name'] != network_to_remove]

    # Write into csv file
    with open('Normal_address_raw.csv', 'w', newline='') as file:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_rows)

# Main code
#############################################################
######################## PART 1 #############################
# start_time = time.time()

# collect_abnormal_address()
# abnormal_address_df.to_csv("Abnormal_address_raw.csv", index=False)
# collect_abnormal_transaction()

# # Save transaction_raw_df
# transaction_raw_df.to_csv("Transaction_raw_checkpoint.csv", index=False)

# collect_normal_address()
# normal_address_df.to_csv("Normal_address_raw.csv", index=False)
# end_time = time.time()
# execution_time = end_time - start_time
# print(f"Execution time: {execution_time:.6f} seconds")

#############################################################
######################## PART 2 #############################

normal_address_df = pd.read_csv("Normal_address_raw.csv")
transaction_raw_df = pd.read_csv("Transaction_raw.csv")

transaction_raw_lock = threading.Lock()
normal_adress_lock = threading.Lock()
normal_address_index_lock = threading.Lock()
start_time = time.time()
normal_address_index = -1
threadNumber = 10
threads = []
for threadNo in range(threadNumber):
    thread = threading.Thread(target=collect_normal_transaction)
    threads.append(thread)
    thread.start()
    time.sleep(3)
# collect_normal_transaction()
# Waiting for all threads
for thread in threads:
    thread.join()


# merge_network_name()

end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.6f} seconds")

transaction_raw_df.to_csv("Transaction_raw.csv", index=False)
