#!/usr/bin/env python


import utils

from oslo_config import cfg

from nova.scheduler import filters
from nova.scheduler.filters import utils as nova_utils


opts = [
    cfg.StrOpt('source_driver_class',
               default="PrometheusDriver",
               help='path to the file name ending with class name'),
    cfg.BoolOpt('use_nova_as_is_nodename',
                default='True',
                help='If true, it will take nova node name from host_state object, '
                     'and use it without any further processing, as is.'
                     'Currently only True is supported'),
    cfg.StrOpt('source_driver_path',
               default='drivers.prometheus_v2',
               help='This is the path from where source_driver_class is loaded, '
                    'it should be importable by nova'),
    cfg.FloatOpt('metric_threshold_percent',
                 default=85.0,
                 help='If metric exceeds this value, for particular nova host, '
                      'filter will return false, and host will be excluded from scheduler list'),
    cfg.StrOpt('metric_evaluation_interval',
               default="5m",
               help='This is the period for which avarage metric value will be calculated, '
                    'for more information please refer to prometheus documentation, '
               ),
    cfg.DictOpt('driver_opts',
                default={
                    "prometheus_endpoint": "http://mtr:9094"
                }),
    cfg.DictOpt('metrics_and_options_dict',
                default={
                    "mem_used_percent": "mem_used_percent_options_dict",
                    "cpu_usage_idle": "cpu_usage_idle_options_dict"
                },
                help="Key of this dict is a metric name to be queried from driver, "
                     "Value of key has to correspond to another config option defined in this config, "
                     "Target config option MUST be of a type Dict, and MUST have key following entries: "
                     "comparison_operator: possible values: 'grater_than', 'less_than', "
                     "threshold: should be float, metric value queried from the driver will be compared against this, "
                     "using 'comparison_operator key of this dict"
                     "if True is a result of the operation, filter will remove host from the list "
                     "(instance will not be scheduled on this host) ."

                ),
    cfg.DictOpt('cpu_usage_idle_options_dict',
                default={
                    "comparison_operator": "less_than",
                    "threshold": 25.0,
                }),
    cfg.DictOpt('mem_used_percent_options_dict',
                default={
                    "comparison_operator": "greater_than",
                    "threshold": 75.0
                })
]
CONF = cfg.CONF
CONF.register_opts(opts)

metric_names = ["mem_used_percent", "cpu_usage_idle"]


class ActualRamFilter(filters.BaseHostFilter):

    def host_passes(self, host_state, spec_obj):

        is_valid_host = True
        source_driver_object = utils.import_driver(CONF.source_driver_class, CONF.source_driver_path)

        try:
            tags = {"host": utils.parse_nova_hostname(host_state.nodename, CONF.use_nova_as_is_nodename)}
        except NotImplementedError:
            print("Can not parse nova node name, behavior is not implemented yet."
                  "Please check and set to True use_nova_as_is_nodename in config"
                  "As behavior is not implemented, this host passes, nodename: {}".format(host_state.nodename))
            return is_valid_host

        if source_driver_object:

            driver = source_driver_object(CONF.driver_opts)
            for metric_name in metric_names:

                try:
                    metric_result = driver.get_metric(metric_name, CONF.metric_evaluation_interval,
                                                      tags=tags)
                except Exception as e:
                    print("Could not query metric from driver")
                    print(e)
                if metric_result and metric_result > CONF.metric_threshold_percent:
                    print("host is not valid:\n"
                          "metric: {}\n"
                          "value: {}\n"
                          "threshold: {}".format(metric_name,
                                                 metric_result,
                                                 CONF.metric_threshold_percent))
                    is_valid_host = False
                    return is_valid_host
        else:
            print("driver import failed, please verify that driver class %s exists" % CONF.source_driver_class)

        return is_valid_host


if __name__ == '__main__':
    host_state_from_nova = {"hostname": "node-101"}
    source_driver = ActualRamFilter()
    print(source_driver.host_passes(host_state_from_nova, "pizda"))



