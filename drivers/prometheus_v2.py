import requests
from base_driver import SourceDriver


class PrometheusDriver(SourceDriver):
  def __init__(self, driver_opts):
    self.prometheus_endpoint = driver_opts["prometheus_endpoint"]

  def get_metric(self, metric_name):
    return "metric name is " + metric_name + " from prometheus endpoint: " + self.prometheus_endpoint



