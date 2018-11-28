import requests
from base_driver import SourceDriver


class PrometheusDriver(SourceDriver):
    def __init__(self, driver_opts):
        self.api_path = "/api/v1/"
        self.query_path = self.api_path + "query?"
        self.prometheus_endpoint = driver_opts["prometheus_endpoint"]

    def get_metric(self, metric_name, interval,
                   tags={}, prometheus_function="avg_over_time"):

        metric = None
        query = "{0}({1}{2}[{3}])".format(prometheus_function,
                                          metric_name,
                                          self._parse_tags(tags),
                                          interval)
        query_result = self._query_metric(query)
        if query_result:
            metric = float(self._parse_results(query_result))
        return metric

    def _query_metric(self, query):
        print("final query: " + query)
        try:
            response = requests.get(self.prometheus_endpoint + self.query_path,
                                    params={"query": query})
        except requests.exceptions.RequestException as e:
            print("Request to prometheus HTTP API has failed, original traceback: {}".format(e))
            return None
        return response.json()["data"]["result"]

    @staticmethod
    def _parse_results(results):
        if len(results) == 1:
            return results[0]["value"][1]
        else:
            print("Filter driver got multiple results from prometheus, no ways to handle it")

    @staticmethod
    def _parse_tags(tags):
        parsed_tags = ""
        if tags != {}:
            parsed_tags = "{" + ",".join(["{}='{}'".format(key, val) for key, val in tags.iteritems()]) + "}"
        return parsed_tags
