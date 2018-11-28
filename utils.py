import importlib
from oslo_log import log


LOG = log.getLogger('nova.scheduler.filter')


def import_driver(driver_class, driver_path):

    LOG.debug("importing module from path %s" % driver_path)
    try:
        imported_driver_class = importlib.import_module(driver_path)
    except ImportError as e:
        LOG.warning("Can not import module named:%s" % driver_path)
        LOG.error(e)
        return None
    try:
        driver_object = getattr(imported_driver_class, driver_class)
        return driver_object
    except Exception as e:
        LOG.error(e)
        return None


def parse_nova_hostname(nova_node_name, use_nova_as_is_nodename):

    parsed_nova_hostname = nova_node_name
    if not use_nova_as_is_nodename:
        raise NotImplementedError
    return parsed_nova_hostname


def metric_passes(metric_value, metric_opts_dict):
    operator = metric_opts_dict["comparison_operator"]
    threshold = metric_opts_dict["threshold"]
    if operator == "greater_than":
        result = metric_value > threshold
    elif operator == "less_than":
        result = metric_value < threshold
    elif operator == "equals":
        result = metric_value == threshold
    else:
        raise NotImplementedError
    return result

