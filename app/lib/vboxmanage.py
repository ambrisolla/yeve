import os
import re
import json
import subprocess as sb


class VboxManage:
  def __init__(self):
    self.vagrant_dir = vagrant_dir = os.environ['YEVE_TEMPLATES_STORAGE']

  def get_vms_uuid(self):
    '''
        get ID's of Virtualbox vms
    '''
    try:
      cmd = ['vboxmanage', 'list', 'vms']
      res = sb.run(cmd, stderr=sb.PIPE, stdout=sb.PIPE)
      if res.returncode != 0:
        return {
          'status' : False,
          'data' : str(res.stderr)
        }
      else:
        data = res.stdout.decode('utf-8').split('\n')
        list_vms = [ re.sub('{|}','',x.split()[1]) for x in data if x != '' ]
        return {
          'data' : list_vms
        }
    except Exception as err:
      raise str(err)

  def get_vm_info(self):
    try:
      uuid_list = self.get_vms_uuid()
      list_vms = {}
      for uuid in uuid_list['data']:
        cmd = ['vboxmanage',  'showvminfo', str(uuid)]
        res = sb.run(cmd, stderr=sb.PIPE, stdout=sb.PIPE)
        if res.returncode != 0:
          return {
            'status' : False,
            'data' : str(res.stderr)
          }
        else:
          data = res.stdout.decode('utf-8').split('\n')
          vm_list_info = {}
          for a in data:
            line = a.split(':')
            if len(line) > 1:
              new_str = ' '.join(line[1:100])
              if line[0] not in vm_list_info:
                vm_list_info[line[0]] = re.sub('^ *','', new_str)
          list_vms[uuid] = vm_list_info
      return {
        'data' : list_vms
      }
    except Exception as err:
      raise str(err)

  def stop_vm(self, vm_name):
    try:
      cmd = ['vboxmanage', 'controlvm', vm_name, 'poweroff','acpipowerbutton']
      res = sb.Popen(cmd, stderr=sb.PIPE, stdout=sb.PIPE)
      res.communicate()
      res.wait()
      if res.returncode == 0:
        return {
          'status' : True,
          'name' : vm_name
        }
      else:
        return {
          'status' : False,
          'name' : str(res.stderr),
          'nn' : str(res.stdout)
        }
    except Exception as err:
      raise str(err)

  def start_vm(self, vm_name):
    try:
      cmd = ['vboxmanage', 'startvm', vm_name, '--type','headless']
      res = sb.Popen(cmd, stderr=sb.PIPE, stdout=sb.PIPE)
      res.communicate()
      res.wait()
      if res.returncode == 0:
        return {
          'status' : True,
          'name' : vm_name
        }
      else:
        return {
          'status' : False,
          'name' : str(res.stderr),
          'nn' : str(res.stdout)
        }
    except Exception as err:
      raise str(err)

  def destroy_vm(self, vm_name):
    try:
      cmd = ['vboxmanage', 'unregistervm', vm_name, '--delete']
      os.system(f'rm -rf {self.vagrant_dir}/{vm_name}')
      res = sb.Popen(cmd, stderr=sb.PIPE, stdout=sb.PIPE)
      res.communicate()
      res.wait()
      if res.returncode == 0:
        return {
          'status' : True,
          'name' : vm_name
        }
      else:
        return {
          'status' : False,
          'name' : str(res.stderr),
          'nn' : str(res.stdout)
        }
    except Exception as err:
      raise str(err)
  
  def list_nics(self):
    try:
      cmd = ['vboxmanage', 'list', 'bridgedifs']
      res = sb.run(cmd, stderr=sb.PIPE, stdout=sb.PIPE)
      nics = []
      for l in res.stdout.decode('utf-8').split('\n'):
        if l.startswith('Name:'):
          nic = l.split(':')[-1].replace(' ','')
          nics.append(nic)
      return nics
    except Exception as err:
      raise str(err)


#print(VboxManage().get_vm_info())