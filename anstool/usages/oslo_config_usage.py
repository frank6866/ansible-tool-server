import sys

from oslo_config import cfg

# set an option, the first argument is option name;
# default is the value if the option is not set in config file
# help is the help info of this option
paste_opt = cfg.StrOpt("api_paste_config",
                       default="/etc/ansible-tool/api-paste.default.ini",
                       help="paste configuration file location")

# define a option group
database_group = cfg.OptGroup(name="database", title="database options")

database_options = [
    cfg.StrOpt("connection", default="mysql://ansible:ChangeMe@:3306/ansible",
               help="database connection string"),
    cfg.IntOpt("max_pool_size", default=200, help="max pool size")]

CONF = cfg.CONF

# register one option
CONF.register_opt(paste_opt)

# group must register before options in group
CONF.register_group(database_group)
CONF.register_opts(database_options, database_group)

# the same option in the last config file will overwrite config files before
CONF(sys.argv[1:],
     default_config_files=['ini/oslo_config_usage.ini',
                           'ini/oslo_config_usage2.ini'])

print CONF.api_paste_config
print CONF.database.connection
print CONF.database.max_pool_size
