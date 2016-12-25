from oslo_config import cfg
from oslo_log import log as logging


LOG = logging.getLogger(__name__)
CONF = cfg.CONF

# ?
DOMAIN = "demo"

options = logging.register_options(CONF)


logging.setup(CONF, DOMAIN)

LOG.info("oslo info log")
LOG.warning("oslo warning log")
LOG.error("oslo error log")

