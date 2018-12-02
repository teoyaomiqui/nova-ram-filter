from nova.scheduler.host_manager import HostState
import ram_filter
from oslo_log import log
from oslo_config import cfg
import sys


CONF = cfg.CONF


log.register_options(CONF)
CONF(sys.argv[1:])
CONF.set_override('use_stderr', False)
host_state = HostState("node-101", "node-77701.stc.bluvalt.com", "12lfaslk-3123fadsfsdjlk")

source_driver = ram_filter.ActualRamFilter()

print(source_driver.host_passes(host_state, "test"))
