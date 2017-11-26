import os, sys, boto3
import argparse
import subprocess

from typing import List

def getFunctionNames(path: str) -> List[str]:
  ''' Returns all Folders names in the paths '''
  xs = os.listdir(path)
  xs = filter(lambda x: x[0] != ".", xs)
  xs = filter(lambda x: os.path.isdir(path + x), xs)
  return list(xs)

def getArns(functions: List[str], stage: str) -> List[str]:
  functions = list(map(lambda x: x + stage, functions))
  client = boto3.client('cloudformation')
  res = client.list_exports()
  arns = {}
  while res is not None:
    for export in res["Exports"]:
      print(export)
      if export["Name"] in functions:
        arns[export["Name"]] = export["Value"]
    if "NextToken" not in res:
      res = None
    else:
      res = client.list_exports(NextToken = res["NextToken"])
  return arns

def exec_tests(path: str, functions: List[str], stage: str):
  arns = getArns(functions, stage)
  for function in functions:
    arn = arns[function + stage]
    test_file = "/".join([path, function, function + "Test.py"])
    exec_cmd = " ".join([test_file, arn])
    result = subprocess.check_output(exec_cmd, shell=True)
    print(result)
  return 0

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-p", "--path", help="Path of the folder with the source \
                       -code of the aws lambda functions", type = str)
  parser.add_argument("-s", "--stage", help="Name of the stage", type = str)
  args = parser.parse_args()
  functions = getFunctionNames(args.path)
  exec_tests(args.path, functions, args.stage)