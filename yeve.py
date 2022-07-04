#!/usr/bin/python3
import os
import re
import yaml
import time
import argparse
import subprocess as sb

class Yeve:

  def __init__(self):
    self.full_path = os.path.abspath(os.path.dirname(__file__))
    self.yeve_config = self.load_config()

  def load_config(self):
    try:
      config_data = open(f'{self.full_path}/config.yaml').read()
      yeve_config = yaml.safe_load(config_data)
      return yeve_config
    except Exception as err:
      raise str(err)

  def start_app(self):
    try:
      app_status = self.status_app()
      if app_status['status'] == True:
        print('YEVE it\'s already running!')
      else:
        # Set flask envs
        os.environ['FLASK_APP'] = f'{self.full_path}/app/app.py'
        os.environ['FLASK_ENV'] = 'development'
        os.environ['YEVE_ACCESS_KEY'] = self.yeve_config['yeve_access_token']
        os.environ['YEVE_TEMPLATES_STORAGE'] = self.yeve_config['vagrant_templates_storage'] #
        # Set flask command variables
        yeve_bind_address = self.yeve_config['yeve_bind_address']
        yeve_port = self.yeve_config['yeve_port']
        # set log file
        log_file = open(f'{self.full_path}/yeve.log','a')
        # create list with parameter to start flask
        cmd = ['flask','run','--host',yeve_bind_address,'--port',str(yeve_port)]
        # start flask
        res = sb.Popen(cmd, stderr=log_file, stdout=log_file)
        # show message
        print('Yeve started!')
        print(f'Access: http://{yeve_bind_address}:{yeve_port}')
        print(f'Logo file: {self.full_path}/yeve.log')
        # create pid file
        pid_file = open(f'{self.full_path}/yeve.pid','w')
        pid_file.write(str(res.pid))
        pid_file.close()
    except Exception as err:
      raise str(err)
  
  def status_app(self): 
    try:
      if os.path.exists(f'{self.full_path}/yeve.pid'):
        pid = int(open(f'{self.full_path}/yeve.pid','r').read())
        child_pid = sb.run(
          ['pgrep','-P', str(pid)], stdout=sb.PIPE)
        import sys
        if child_pid.returncode != 0:
          print('Removing yeve.pid...')
          os.remove(f'{self.full_path}/yeve.pid')
          child_pid = sb.run(
          ['pgrep','-P', str(pid)], stdout=sb.PIPE)
        child_pid = child_pid.stdout.decode('utf-8').replace('\n','')
      else:
        return {
          'status' : False
        }
      pids = sb.check_output(['ps','-ef']).decode('utf-8').split('\n')
      yeve_is_running = False
      for _pid in pids:
        if re.search('flask',_pid) \
        and re.search(str(self.yeve_config['yeve_port']), _pid) \
        and re.search(str(self.yeve_config['yeve_bind_address']), _pid) \
        and re.search(str(pid), _pid):
          yeve_is_running = True
      return {
        'status' : yeve_is_running,
        'pid' : child_pid 
      }
    except Exception as err:
      raise str(err)
    
  def show_status(self):
    try:
      data = self.status_app()
      if data['status'] == True:
        print('Yeve is running!')
      else:
        print('Yeve is not running!')
    except Exception as err:
      raise str(err)

  def stop_app(self):
    try:
      data = self.status_app()
      if data['status'] == True:
        pid = data['pid']
        print('Stopping Flask...')
        log_file = open(f'{self.full_path}/yeve.log','a')
        cmd = ['kill', '-9', str(pid)]
        print(f'Killing process {pid}... ', end='')
        time.sleep(0.5)
        res = sb.Popen(cmd, stderr=sb.PIPE, stdout=sb.PIPE)
        rc = res.communicate()[0]
        if res.returncode == 0:
          print(f'\rKilling process {pid}... Ok')
        else:
          print(f'\rKilling process {pid}... Fail')
          print(str(res.stderr))
        os.remove(f'{self.full_path}/yeve.pid')
      else:
        print('YEVE is not running!')
    except Exception as err:
      raise str(err)
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--start', help='Start YEVE', action="store_true")
  parser.add_argument('--stop', help='Stop YEVE', action="store_true")
  parser.add_argument('--status', help='Show YEVE status', action="store_true")
  args = vars(parser.parse_args())
  some_args_is_true = True in [ args[x] for x in args ]
  if not some_args_is_true:
    print('You need to pass one parameter!\n')
    parser.print_help()
  else:
    get_function = [ x for x in args if args[x] == True  ]
    if len(get_function) != 1:
      print('You need to choose only one parameter!\n')
      parser.print_help()
    else:
      y = Yeve()
      f = get_function[0]
      if f == 'start': y.start_app()
      elif f == 'status': y.show_status()
      elif f == 'stop': y.stop_app()
      else:
        parser.print_help()