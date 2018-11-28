from nova.scheduler.host_manager import HostState
import ram_filter
from oslo_log import log
from oslo_config import cfg


CONF = cfg.CONF

host_state = HostState("node-101", "node-169", "12lfaslk-3123fadsfsdjlk")

source_driver = ram_filter.ActualRamFilter()
print(source_driver.host_passes(host_state, "pizda"))