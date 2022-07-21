import os
import re
import sys
import yaml
import signal
import argparse
import subprocess as sb

fullpath = os.path.abspath(os.path.dirname(__file__))

def load_configs():
  try:
    yaml_data               = open(f'{fullpath}/config.yaml', 'r').read()
    data                    = yaml.safe_load(yaml_data)
    return data
  except Exception as err:
    print(f'error loading config data!')
    sys.exit(1)

def start():
  try:
    # get status
    s = status()
    if s['yeve_status']:
      print('YEVE already is running!')
      sys.exit(0)
    else:
      configs                 = load_configs()
      yeve_bind_address       = configs['yeve_bind_address']
      yeve_port               = configs['yeve_port']
      os.environ['FLASK_APP'] = f'{fullpath}/app/app.py'
      cmd                     = f'flask run --host {yeve_bind_address} --port {yeve_port} \
                                > {fullpath}/yeve.log 2> {fullpath}/yeve.log &'
      os.system(cmd)
  except Exception as err:
    print(f'error: {str(err)}')
    sys.exit()

def stop():
  try:
    # get status
    s = status()
    if not s['yeve_status']:
      print('YEVE is not running!')
      sys.exit(0)
    else:
      pid = s['yeve_pid']
      os.kill(int(pid), signal.SIGTERM)
      print('YEVE stopped!')
  except Exception as err:
    print(f'error: {str(err)}')
    sys.exit()

def status():
  try:
    cmd                     = ['ps', '-ef']
    ps                      = sb.run(cmd, stdout=sb.PIPE, stderr=sb.PIPE, text=True)
    yeve_status             = False
    yeve_pid                = ''
    configs                 = load_configs()
    yeve_bind_address       = configs['yeve_bind_address']
    yeve_port               = configs['yeve_port']
    if ps.returncode == 0:
      lines = ps.stdout.split('\n')
      for line in lines:
        if re.search(f'flask run --host {yeve_bind_address} --port {yeve_port}', line):
          pid         = line.split()[1]
          yeve_pid    = pid
          yeve_status = True
      return {
        'yeve_status' : yeve_status,
        'yeve_pid'    : yeve_pid
      }
    else:
      print(f'error: {str(sys.stderr)}')
      sys.exit(ps.returncode)
  except Exception as err:
    print(f'error: {str(err)}')
    sys.exit()
  
def show_status():
  s = status()
  if s['yeve_status']:
    pid = s['yeve_pid']
    print(f'YEVE is running. ( pid: {pid} )')
    sys.exit()
  else:
    print('YEVE is not running!')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(allow_abbrev=False)
  parser.add_argument('--start',  help='start YEVE',       action='store_true')
  parser.add_argument('--stop',   help='stop YEVE',        action='store_true')
  parser.add_argument('--status', help='show YEVE status', action='store_true')
  args = vars(parser.parse_args())
  true_args = [ args[x] for x in args if args[x] ]
  if len(true_args) != 1:
    print('error: You need to use only one option!')
    parser.print_help()
    sys.exit(1)
  else:
    arg = [ x for x in args if args[x]][0]
    if arg == 'start' : start()
    if arg == 'stop'  : stop()
    if arg == 'status': show_status()
