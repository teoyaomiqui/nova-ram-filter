import importlib
from oslo_log import log


LOG = log.getLogger('nova.scheduler.filter')


def import_driver(driver_class, driver_path):

    LOG.debug("importing module from path %s" % driver_path)
    imported_driver_module = importlib.import_module(driver_path)
    try:
        driver_object = getattr(imported_driver_module, driver_class)
        return driver_object
    except Exception as e:
        LOG.warning('Could not load class {} from module {}'.format(driver_class,
                                                                    driver_path))
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

