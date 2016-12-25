from oslo_config import cfg

from anstool.conf import database
CONF = cfg.CONF


database.register_opts(CONF)

