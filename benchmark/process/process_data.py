import os

import benchmark.settings as settings
import benchmark.utils.tar_util as tar_util



def process_one_result(path):
    dir_name = tar_util.extract_to_dir(path)
    process_cpu(dir_name)
    process_memory(dir_name)
    process_io(dir_name)


def process_cpu(dir):
    if result_existed(dir):
        return
    # todo: get value
    # todo: put value in mongo
    pass


def process_memory(dir):
    if result_existed(dir):
        return
    # todo: get value
    # todo: put value in mongo
    pass


def process_io(dir):
    if result_existed(dir):
        return
    # todo: get value
    # todo: put value in mongo
    pass


def result_existed(dir):
    # query mongodb check if result existed
    return False





