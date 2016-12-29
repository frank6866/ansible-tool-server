import ftplib
import os
filename = "/tmp/hello.txt"
ftp = ftplib.FTP("ec2-54-223-95-71.cn-north-1.compute.amazonaws.com.cn")
# ftp = ftplib.FTP("54.223.95.71")
ftp.set_debuglevel(2)
# ftp.set_pasv(1)
ftp.login("bmark", "mark2")
print ftp.getwelcome()
print ftp.dir()
# ftp.cwd("/home/bmark/benchmark_results")
# os.chdir(os.path.dirname(filename))
# myfile = open(filename, 'rb')
# ftp.storbinary('RETR %s' % os.path.dirname(filename), myfile)
# # ftp.storlines('STOR ' + filename, myfile)
# myfile.close()
