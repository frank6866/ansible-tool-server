# -*- coding: utf-8 -*-
import benchmark.utils.mongo_util as mongo_util

# clean test_result collection

# server1 = {"company": "aliyun", "series": "系列1", "type": "高IO型1",
#            "root_disk_type": "local_ssd", "data_disk_type": "local_ssd",
#            "cpus": 8, "memory_gb": 16}


def init_servers():
    # qcloud
    servers = []
    server1 = {"ip": "10.0.246.150/24"}
    servers.append(server1)

    server2 = {"ip": "10.0.246.23/24"}
    servers.append(server2)

    server3 = {"ip": "10.0.246.132/24"}
    servers.append(server3)

    server4 = {"ip": "10.0.246.94/24"}
    servers.append(server4)

    server5 = {"ip": "10.0.246.90/24"}
    servers.append(server5)

    # aliyun
    server6 = {"ip": "10.100.5.6/24"}
    servers.append(server6)

    server7 = {"ip": "10.100.5.7/24"}
    servers.append(server7)

    server8 = {"ip": "10.100.5.8/24"}
    servers.append(server8)

    server9 = {"ip": "10.100.5.9/24"}
    servers.append(server9)

    server10 = {"ip": "10.100.5.10/24"}
    servers.append(server10)

    server11 = {"ip": "10.100.5.11/24"}
    servers.append(server11)

    # aws
    server12 = {"ip": "10.30.0.131/24"}
    servers.append(server12)

    server13 = {"ip": "10.30.0.28/24"}
    servers.append(server13)

    server14 = {"ip": "10.30.0.66/24"}
    servers.append(server14)

    server15 = {"ip": "10.30.0.86/24"}
    servers.append(server15)

    mongo_util.insert_many_server(servers)


if __name__ == '__main__':
    init_servers()


