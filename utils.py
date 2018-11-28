import importlib


def import_driver(driver_class, driver_path):

    print("importing module from path %s" % driver_path)
    try:
        imported_driver_class = importlib.import_module(driver_path)
    except ImportError as e:
        print("Can not import module named:%s" % driver_path)
        print("Original Traceback: %s" % e.args[0])
        return None
    try:
        driver_object = getattr(imported_driver_class, driver_class)
        return driver_object
    except Exception as e:
        print(e)
        return None


def parse_nova_hostname(nova_node_name, use_nova_asis_nodename):
    parsed_nova_hostname = nova_node_name
    if not use_nova_asis_nodename:
        raise NotImplementedError
    return parsed_nova_hostname

