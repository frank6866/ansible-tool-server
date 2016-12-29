from pymongo import MongoClient

import benchmark.settings as settings

client = MongoClient(settings.mongodb_host, settings.mongodb_port)
db = client[settings.mongodb_database]


def insert_test_result(test_result):
    ip = test_result["ip"]
    time_str = test_result["time_str"]
    collection = db[settings.mongodb_collection_results]
    collection.update({"ip": ip, "time_str": time_str}, test_result,
                      upsert=True)


def find_one_result(ip, time_str):
    collection = db[settings.mongodb_collection_results]
    result = collection.find_one({"ip": ip, "time_str": time_str})
    return result


def find_test_results(ip):
    collection = db[settings.mongodb_collection_results]
    results = collection.find({"ip": ip})
    return results


def result_existed(ip, time_str):
    result = find_one_result(ip, time_str)
    return True if result else False


def truncate_test_results():
    collection = db[settings.mongodb_collection_results]
    collection.delete_many({})


# servers
def insert_server(server):
    ip = server["ip"]
    collection = db[settings.mongodb_collection_servers]
    collection.update({"ip": ip}, server, upsert=True)


def insert_many_server(servers):
    for server in servers:
        insert_server(server)


def get_all_servers():
    collection = db[settings.mongodb_collection_servers]
    results = collection.find({})
    return results
