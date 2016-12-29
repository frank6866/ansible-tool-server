import benchmark.utils.mongo_util as mongo_util


chart_demo = {"id": 4, "title": "数据盘吞吐测试(64k顺序读)",
          "servers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
          "sub_title": "fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=/dev/vdb --bs=64k --iodepth=64 --size=20G --readwrite=read --runtime=600",
          "x_axis": "", "y_axis": "数据盘吞吐速率(MB/s)",
          "key": "io/data_disk_64k_seq_read/bw_kb_per_sec",
          "x_axis_names": ["company", "series", "type", "core", "memory",
                           "data_disk_type"]
          }


def construct_char(chart_id):
    servers = mongo_util.get_all_servers()
    chart = mongo_util.get_chart(chart_id)
    pairs = []
    for server_id in chart["servers"]:
        name = get_name_of_server(servers, server_id, chart["x_axis_names"])
        value = get_value_of_server(servers, server_id, chart["key"])
        pair = {"name": name, "value": value}
        pairs.append(pair)
    chart["pairs"] = pairs
    return chart


def get_name_of_server(servers, server_id, name_keys):
    return ""


def get_value_of_server(servers, server_id, value_key):
    return ""



