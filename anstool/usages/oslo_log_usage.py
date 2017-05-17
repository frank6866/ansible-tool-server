import sys

import os
from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

# ?
DOMAIN = "demo"

options = logging.register_options(CONF)

CONF(sys.argv[1:],
     default_config_files=['ini/oslo_config_usage.ini'])

if not os.path.exists(CONF.log_dir):
    os.mkdir(CONF.log_dir)

# with open(CONF.log_dir + "/" + CONF.log_file, 'a') as f:
#     # f.write("")
#     pass

logging.setup(CONF, DOMAIN)


LOG.info("oslo info log")
LOG.warning("oslo warning log")
LOG.error("oslo error log")
