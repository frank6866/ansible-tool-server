#!/usr/bin/env python

import os
import subprocess
import time
from datetime import datetime


# global config
tests_count = 3
tests_interval = 3  # unit: seconds, default value: 1200
ip_info_file_name = "ip_info.txt"
start_time_file_name = "start_time.txt"
end_time_file_name = "end_time.txt"
hardware_cpu_file_name = "hardware_cpu.txt"
hardware_memory_file_name = "hardware_memory.txt"
hardware_dmidecode_file_name = "hardware_dmidecode.txt"
hardware_lspci_file_name = "hardware_lspci.txt"
hardware_fdisk_file_name = "hardware_fdisk.txt"
hardware_df_file_name = "hardware_df.txt"

# test file location
cpu_test_file_name = "cpu_test.txt"
memory_test_file_name = "memory_test.txt"
io_test_rootfs_4k_rand_write_file_name = "io_test_rootfs_4k_rand_write.txt"
io_test_rootfs_4k_rand_read_file_name = "io_test_rootfs_4k_rand_read.txt"
io_test_rootfs_64k_seq_write_file_name = "io_test_rootfs_64k_seq_write.txt"
io_test_rootfs_64k_seq_read_file_name = "io_test_rootfs_64k_seq_read.txt"

# cpu tests arguments
cpu_num_threads = 64
cpu_max_prime = 2000  # default value: 200000(20w)

# memory tests arguments
memory_block_size = 4096
memory_total_size = "4G"

# io tests arguments
io_size = "100M"  # default value: 4G


def write_str_to_file(file_name, string):
    with open(file_name, 'wt') as f:
        f.write(string)


def get_ip_list_dir_name():
    ip_info_output = subprocess.check_output(
        ["ip a | awk '/inet /{print substr($2,0,20)}' | grep -v 127.0.0.1"],
        shell=True)
    ips = []
    for ip in ip_info_output.split('\n'):
        if "127.0.0.1" not in ip:
            replace_slash = ip.replace("/", "_")
            ips.append(replace_slash)
    time_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    return ("-".join(ips)) + time_str


def write_ip_to_file(file_name):
    # output ip info to file
    ip_output = subprocess.check_output(["ip a"], shell=True)
    print ip_output
    write_str_to_file(file_name, ip_output)


def write_time_to_file(file_name):
    # output ip info to file
    output = subprocess.check_output(["date -R"], shell=True)
    write_str_to_file(file_name, output)


def write_hardware_info_to_fine(dir_name):
    output = subprocess.check_output(["cat /proc/cpuinfo"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_cpu_file_name), output)

    output = subprocess.check_output(["free"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_memory_file_name), output)

    output = subprocess.check_output(["dmidecode"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_dmidecode_file_name),
                      output)

    output = subprocess.check_output(["lspci"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_lspci_file_name), output)

    output = subprocess.check_output(["fdisk -l"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_fdisk_file_name), output)

    output = subprocess.check_output(["df -lTh"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_df_file_name), output)


def install_packages(packages):
    for package in packages:
        output = subprocess.check_output(["sudo yum -y install %s" % (package)],
                                         shell=True)
        print output


def cpu_test(file_name):
    # cpu benchmark
    cpu_output = subprocess.check_output(
        ["sysbench  --num-threads=%d --test=cpu --cpu-max-prime=%d run" % (
            cpu_num_threads, cpu_max_prime)], shell=True)
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
        "fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=4k --iodepth=64 --size=%s --readwrite=randwrite > %s" % (
            io_size, file_name)],
        shell=True)


def io_test_rootfs_4k_rand_read(file_name):
    subprocess.check_output([
        "fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=4k --iodepth=64 --size=%s --readwrite=randread > %s" % (
            io_size, file_name)],
        shell=True)


def io_test_rootfs_64k_seq_write(file_name):
    subprocess.check_output([
        "fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=64k --iodepth=64 --size=%s --readwrite=write > %s" % (
            io_size, file_name)],
        shell=True)


def io_test_rootfs_64k_seq_read(file_name):
    subprocess.check_output([
        "fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=64k --iodepth=64 --size=%s --readwrite=read > %s" % (
            io_size, file_name)],
        shell=True)


if __name__ == '__main__':
    packages = ['epel-release', 'sysbench', 'fio', 'iperf', 'tree', 'pciutils']
    install_packages(packages)

    path = "/tmp/%s" % get_ip_list_dir_name()
    os.mkdir(path)
    print "create path: %s" % path

    hardware_dir = "%s/hardware" % path
    os.mkdir(hardware_dir)
    write_hardware_info_to_fine(hardware_dir)
    print "create hardware_dir: %s" % hardware_dir

    write_ip_to_file("%s/%s" % (path, ip_info_file_name))
    write_time_to_file("%s/%s" % (path, start_time_file_name))

    for i in xrange(tests_count):
        print '================================================count: ' + str(i)
        sub_dir = "%s/%d" % (path, i)
        os.mkdir(sub_dir)
        cpu_test("%s/%s" % (sub_dir, cpu_test_file_name))
        memory_test("%s/%s" % (sub_dir, memory_test_file_name))
        io_test_rootfs_4k_rand_write(
            "%s/%s" % (sub_dir, io_test_rootfs_4k_rand_write_file_name))
        io_test_rootfs_4k_rand_read(
            "%s/%s" % (sub_dir, io_test_rootfs_4k_rand_read_file_name))
        io_test_rootfs_64k_seq_write(
            "%s/%s" % (sub_dir, io_test_rootfs_64k_seq_write_file_name))
        io_test_rootfs_64k_seq_read(
            "%s/%s" % (sub_dir, io_test_rootfs_64k_seq_read_file_name))

        time.sleep(tests_interval)
    write_time_to_file("%s/%s" % (path, end_time_file_name))


    # todo tar the dir and send them to server
