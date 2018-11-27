#!/usr/bin/env python

import utils


source_driver_name = "prometheus_v2.PrometheusDriver"
prometheus_endpoint = "http://172.18.81.87:9094"
metric_threshold_percent = 95.0
metric_names = ["mem_used_percent", "cpu_usage_idle"]


class ActualRamFilter():

    def host_passes(self, host_state, spec_obj):

        is_valid_host = True
        driver_opts = {"prometheus_endpoint": prometheus_endpoint}
        source_driver_object = utils.import_driver(source_driver_name)
        hostname = host_state["hostname"]
        tags = {"host": hostname}

        if source_driver_object:
            driver = source_driver_object(driver_opts)
            for metric_name in metric_names:

                try:
                    metric_result = driver.get_metric(metric_name, tags)
                except Exception as e:
                    print("Could not query metric from driver")
                    print(e)
                if metric_result and metric_result > metric_threshold_percent:
                    print("host is not valid:\n"
                          "metric: {}\n"
                          "value: {}\n"
                          "threshold: {}".format(metric_name,
                                                 metric_result,
                                                 metric_threshold_percent))
                    is_valid_host = False
                    return is_valid_host
        else:
            print("driver import failed, please verify that driver %s exists" % source_driver_name)

        return is_valid_host


if __name__ == '__main__':
    host_state_from_nova = {"hostname": "node-101"}
    source_driver = ActualRamFilter()
    print(source_driver.host_passes(host_state_from_nova, "pizda"))



