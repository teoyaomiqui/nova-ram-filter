#!/usr/bin/env python

import utils


source_driver_name = "prometheus_v2.PrometheusDriver"
prometheus_endpoint = "http://mtr01:9100/api"

class ActualRamFilter():


  def host_passes(self, host_state, spec_obj):
    driver_opts = { "prometheus_endpoint": prometheus_endpoint }
    source_driver_object = utils.import_driver(source_driver_name)
    if source_driver_object:
      source_driver = source_driver_object(driver_opts)
      print(source_driver.get_metric("actual_ram_used"))
    else:
      print("driver import failed, please verify that driver %s exists" % source_driver_name)
    return True


if __name__ == '__main__':
  source_driver = ActualRamFilter()
#metric = source_driver.get_metric("pizda_metrica")
  print(source_driver.host_passes("hui", "pizda"))



