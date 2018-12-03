#!/usr/bin/env python
from oslo_config.cfg import ConfigOpts

import utils

from oslo_config import cfg
from oslo_log import log

from nova.scheduler import filters

opts = [
    cfg.StrOpt('source_driver_class',
               default="PrometheusDriver",
               help='path to the file name ending with class name'
                    'value returned from driver should be convertale to float'),
    cfg.BoolOpt('use_nova_as_is_nodename',
                default='False',
                help='If true, it will take nova node name from host_state object, '
                     'and use it without any further processing, as is.'
                     'Currently only True is supported'),
    cfg.StrOpt('source_driver_path',
               default='stc_nova_filters.drivers.prometheus_v1',
               help='This is the path from where source_driver_class is loaded, '
                    'it should be importable by nova'),
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
                     "(instance will not be scheduled on this host),"
                     "metric_evaluation_interval: interval over which to take avarage value"

                ),
    cfg.DictOpt('cpu_usage_idle_options_dict',
                default={
                    "comparison_operator": "less_than",
                    "threshold": 20.0,
                    "metric_evaluation_interval": "5m"
                }),
    cfg.DictOpt('mem_used_percent_options_dict',
                default={
                    "comparison_operator": "greater_than",
                    "threshold": 80.0,
                    "metric_evaluation_interval": "10m"
                })
]

stc_filter_opt_group = cfg.OptGroup(name='stc_filter',
                                    title='custom filter options')

CONF = cfg.CONF  # type: ConfigOpts
CONF.register_group(stc_filter_opt_group)
CONF.register_opts(opts, group=stc_filter_opt_group)

LOG = log.getLogger('nova.scheduler.filter')


class ActualResourceFilter(filters.BaseHostFilter):

    def host_passes(self, host_state, spec_obj):

        is_valid_host = True  # type: bool

        try:
            source_driver_object = utils.import_driver(CONF.stc_filter.source_driver_class,
                                                       CONF.stc_filter.source_driver_path)
        except ImportError:
            LOG.error('Could not import driver class: {0}, module: {1}'. format(CONF.stc_filter.source_driver_class,
                                                                                CONF.stc_filter.source_driver_path))
            return is_valid_host
        try:
            tags = {"host": utils.parse_nova_hostname(host_state.nodename, CONF.stc_filter.use_nova_as_is_nodename)}
        except NotImplementedError:
            LOG.debug("Can not parse nova node name, behavior is not implemented yet."
                      "Please check and set to True use_nova_as_is_nodename in config"
                      "As behavior is not implemented, this host passes, nodename: {}".format(host_state.nodename))
            return is_valid_host

        if source_driver_object:

            driver = source_driver_object(CONF.stc_filter.driver_opts)
            for metric_name, metric_options in CONF.stc_filter.metrics_and_options_dict.iteritems():

                metric_options_dict = getattr(CONF.stc_filter, metric_options)

                metric_result = driver.get_metric(metric_name, metric_options_dict["metric_evaluation_interval"],
                                                  tags=tags)
                try:
                    if metric_result and utils.metric_passes(metric_result, metric_options_dict):
                        LOG.debug("host {} does not pass:\n"
                                  "metric: {}\n"
                                  "value: {}\n"
                                  "threshold: {}\n"
                                  "Operator: {}".format(host_state.nodename,
                                                        metric_name,
                                                        metric_result,
                                                        metric_options_dict["threshold"],
                                                        metric_options_dict["comparison_operator"]))
                        is_valid_host = False
                        return is_valid_host
                    elif not metric_result:
                        LOG.warning('Got empty result from source data driver for host {}:'.format(host_state.nodename))
                except NotImplementedError:
                    LOG.warning('Method is not implemented, filter is not configured properly')
                except ValueError:
                    LOG.warning('Could not convert provided values to FLOAT for comparison:'
                                'threshold value: {}'
                                'metric_result: {}'.format(metric_options_dict["threshold"], metric_result))
        else:
            LOG.warning("driver import failed, please verify that driver class %s exists" %
                        CONF.stc_filter.source_driver_class)
        LOG.debug('Host: {} Passes: {}'.format(host_state.nodename, is_valid_host))
        return is_valid_host
