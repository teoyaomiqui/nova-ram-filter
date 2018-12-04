import requests
from base_driver import SourceDriver
from oslo_log import log


LOG = log.getLogger('nova.scheduler.filter')


class PrometheusDriver(SourceDriver):

    def __init__(self, driver_opts):
        super(PrometheusDriver, self).__init__(driver_opts)
        self.api_path = "/api/v1/"
        self.query_path = self.api_path + "query?"
        self.prometheus_endpoint = driver_opts["prometheus_endpoint"]
        self.request_timeout = driver_opts["request_timeout"] if "request_timeout" in driver_opts else 1.0

    def get_metric(self, metric_name, interval,
                   tags={}, prometheus_function="avg_over_time"):

        metric = None
        query = "{0}({1}{2}[{3}])".format(prometheus_function,
                                          metric_name,
                                          self._parse_tags(tags),
                                          interval)
        query_result = self._query_metric(query)
        if query_result and query_result != []:
            try:
                metric = self._parse_results(query_result)
            except NotImplementedError:
                LOG.warning("Can not parse metrics from prometheus")
        return metric

    def _query_metric(self, query):
        response = None
        data = None
        try:
            response = requests.get(self.prometheus_endpoint + self.query_path,
                                    params={"query": query}, timeout=self.request_timeout)
        except requests.exceptions.ReadTimeout:
            LOG.warning("Request to prometheus HTTP API has failed, prometheus server: {}, "
                        "Consider changing timeout for http request, timeout: {}"
                        .format(self.prometheus_endpoint, self.request_timeout))
        except requests.exceptions.RequestException:
            LOG.warning("Request to prometheus HTTP API has failed, prometheus server: {}, "
                        .format(self.prometheus_endpoint))
        try:
            data = response.json()["data"]["result"] if response else None
        except KeyError:
            LOG.warning("Request to prometheus HTTP API returned invalid result, prometheus server: {}, "
                        .format(self.prometheus_endpoint))
        return data

    @staticmethod
    def _parse_results(results):
        if len(results) == 1:
            return results[0]["value"][1]
        else:
            raise NotImplementedError

    @staticmethod
    def _parse_tags(tags):
        parsed_tags = ""
        if tags != {}:
            parsed_tags = "{" + ",".join(["{}='{}'".format(key, val) for key, val in tags.iteritems()]) + "}"
        return parsed_tags
