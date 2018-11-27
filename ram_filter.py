#!/usr/bin/env python

import utils


source_driver_name = "prometheus_v2.PrometheusDriver"
prometheus_endpoint = "http://172.18.81.87:9094"


class ActualRamFilter():

    def host_passes(self, host_state, spec_obj):
        driver_opts = {"prometheus_endpoint": prometheus_endpoint}
        source_driver_object = utils.import_driver(source_driver_name)
        hostname = host_state["hostname"]
        tags = {"host": hostname}
        if source_driver_object:
            driver = source_driver_object(driver_opts)
            print(driver.get_metric("mem_used_percent", tags))
        else:
            print("driver import failed, please verify that driver %s exists" % source_driver_name)
        return True


if __name__ == '__main__':
    host_state_from_nova = {"hostname": "node-101"}
    source_driver = ActualRamFilter()
    print(source_driver.host_passes(host_state_from_nova, "pizda"))



