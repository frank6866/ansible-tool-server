#!/usr/bin/env python

import os
import subprocess
import uuid

# global config
tests_count = 3
ip_info_file_name = "ip_info.txt"
cpu_test_file_name = "cpu_test.txt"
memory_test_file_name = "memory_test.txt"
io_test_rootfs_4k_rand_write_file_name = "io_test_rootfs_4k_rand_write.txt"
io_test_rootfs_4k_rand_read_file_name = "io_test_rootfs_4k_rand_read.txt"
io_test_rootfs_64k_seq_write_file_name = "io_test_rootfs_64k_seq_write.txt"
io_test_rootfs_64k_seq_read_file_name = "io_test_rootfs_64k_seq_read.txt"

# cpu tests arguments
cpu_num_threads = 64
cpu_max_prime = 2000

# memory tests arguments
memory_block_size = 4096
memory_total_size = "4G"

# io tests arguments
io_size = "100M"

def write_str_to_file(file_name, string):
    with open(file_name, 'wt') as f:
        f.write(string)


def write_ip_to_file(file_name):
    # output ip info to file
    ip_output = subprocess.check_output(["ip a"], shell=True)
    print ip_output
    write_str_to_file(file_name, ip_output)


def install_packages(packages):
    for package in packages:
        output = subprocess.check_output(["yum -y install %s" % (package)], shell=True)
        print output


def cpu_test(file_name):
    # cpu benchmark
    cpu_output = subprocess.check_output(
        ["sysbench  --num-threads=%d --test=cpu --cpu-max-prime=%d run" % (cpu_num_threads, cpu_max_prime)], shell=True)
    print cpu_output
    write_str_to_file(file_name, cpu_output)


def memory_test(file_name):
    # memory benchmark
    memory_output = subprocess.check_output([
        "sysbench --test=memory --num-threads=1 --memory-block-size=%d --memory-total-size=%s run" % (
            memory_block_size, memory_total_size)], shell=True)
    print memory_output
    write_str_to_file(file_name, memory_output)


def io_test_rootfs_4k_rand_write(file_name):
    subprocess.check_output([
        "fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=4k --iodepth=64 --size=%s --readwrite=randwrite > %s" % (io_size, file_name)],
        shell=True)


def io_test_rootfs_4k_rand_read(file_name):
    subprocess.check_output([
        "fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=4k --iodepth=64 --size=%s --readwrite=randread > %s" % (io_size, file_name)],
        shell=True)


def io_test_rootfs_64k_seq_write(file_name):
    subprocess.check_output([
        "fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=4k --iodepth=64 --size=%s --readwrite=write > %s" % (io_size, file_name)],
        shell=True)


def io_test_rootfs_64k_seq_read(file_name):
    subprocess.check_output([
        "fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=4k --iodepth=64 --size=%s --readwrite=read > %s" % (io_size, file_name)],
        shell=True)


if __name__ == '__main__':
    packages = ['epel-release', 'sysbench', 'fio', 'iperf']
    install_packages(packages)

    path = "/tmp/%s" % uuid.uuid4()
    os.mkdir(path)
    print "create path: %s" % path

    write_ip_to_file("%s/%s" % (path, ip_info_file_name))

    for i in xrange(tests_count):
        sub_dir = "%s/%d" % (path, i)
        os.mkdir(sub_dir)
        cpu_test("%s/%s" % (sub_dir, cpu_test_file_name))
        memory_test("%s/%s" % (sub_dir, memory_test_file_name))
        io_test_rootfs_4k_rand_write("%s/%s" % (sub_dir, io_test_rootfs_4k_rand_write_file_name))
        io_test_rootfs_4k_rand_read("%s/%s" % (sub_dir, io_test_rootfs_4k_rand_read_file_name))
        io_test_rootfs_64k_seq_write("%s/%s" % (sub_dir, io_test_rootfs_64k_seq_write_file_name))
        io_test_rootfs_64k_seq_read("%s/%s" % (sub_dir, io_test_rootfs_64k_seq_read_file_name))

    # todo tar the dir and send them to server
    # todo get hardware info and write to file

