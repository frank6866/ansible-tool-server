#
#
# def get_all_results():
#     pass
#     return []
#
#
# def process_one_result(path):
#     dir = decompress(path)
#     process_cpu(dir)
#     process_memory(dir)
#     process_io(dir)
#
#
# def decompress(path):
#     pass
#     return "decompressed dir"
#
#
# def process_cpu(dir):
#     if result_existed(dir):
#         return
#     # todo: get value
#     # todo: put value in mongo
#     pass
#
#
# def process_memory(dir):
#     if result_existed(dir):
#         return
#     # todo: get value
#     # todo: put value in mongo
#     pass
#
#
# def process_io(dir):
#     if result_existed(dir):
#         return
#     # todo: get value
#     # todo: put value in mongo
#     pass
#
#
# def result_existed(dir):
#     # query mongodb check if result existed
#     return False


import benchmark.utils.process_util as process_util


if __name__ == '__main__':
    result_tars = process_util.get_all_tar_files()
    for result_tar in result_tars:
        process_util.process_one_result(result_tar)
