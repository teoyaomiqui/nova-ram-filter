import importlib

def import_driver(driver_name, driver_path="drivers"):
  _path_array = driver_name.split(".")
  driver_class_name = _path_array[-1]
  driver_class_path = _path_array[:-1]
  class_full_path = ".".join([driver_path] + driver_class_path)
  print("importing module from path %s" % (class_full_path))
  try:
    imported_driver_class = importlib.import_module(class_full_path)
  except ImportError as e:
    print("Can not import module named:%s" % class_full_path)
    print("Original Traceback: %s" % e.args[0])
    return None
  try:
    driver_object = getattr(imported_driver_class, driver_class_name)
    return driver_object
  except Exception as e:
    print(e)
    return None
