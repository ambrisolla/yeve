import os
import re
import yaml
import subprocess as sb
from flask import render_template, request

class Vagrant:
  def __init__(self):
    self.vagrant_dir = vagrant_dir = os.environ['YEVE_TEMPLATES_STORAGE']
  
  def list_box(self):
    #return str(sb.check_output('ls'))
    app_dir = str(os.path.abspath(os.path.dirname(__file__)))
    config_file_path = f'{app_dir}/../../config.yaml'
    boxes = open(config_file_path).read()
    boxes_yaml = yaml.safe_load(boxes)
    box_list = []
    for box in sorted(boxes_yaml['vagrant_boxes']):
      if 'box_url' not in boxes_yaml['vagrant_boxes'][box]:
        box_url = ''
      else:
        box_url = boxes_yaml['vagrant_boxes'][box]['box_url']
      box_list.append({
        'box' : box,
        'title' : boxes_yaml['vagrant_boxes'][box]['title'],
        'box_url' : box_url
      })
    return box_list

  def generate_vagrant_file(self):
    vm_data = request.form
    vf = render_template('Vagrantfile',
      memory=vm_data['memory'],
      cpus=vm_data['cpus'],
      ip=vm_data['ip'],
      netmask=vm_data['netmask'],
      gateway=vm_data['gateway'],
      nic=vm_data['nic'],
      box=vm_data['box'],
      vm_name=vm_data['vm_name'],
      salt=vm_data['salt'],
      salt_master=vm_data['salt_master'],
      enable_root=vm_data['enable_root'],
      ssh_public_key=vm_data['ssh_public_key'],
      box_url=vm_data['box_url']
    )
    return vf

  def create_vm(self, vm_name):
    try:
      if not os.path.exists(f'{self.vagrant_dir}/{vm_name}/'):
        # Create vagrant directory structure & vagrant file
        os.system(f'mkdir -p {self.vagrant_dir}/{vm_name}/')
        vagrant_file = self.generate_vagrant_file()
        vf = open(f'/{self.vagrant_dir}/{vm_name}/Vagrantfile', 'w')
        vf.write(vagrant_file)
        vf.close()
        # execute vagrant init/up
        os.chdir(f'{self.vagrant_dir}/{vm_name}/')
        os.system(f'rm -f {self.vagrant_dir}/{vm_name}/{vm_name}*.log')
        os.system(f'vagrant init 2> /dev/null 2> /dev/null')
        os.system(f'vagrant up 2> {self.vagrant_dir}/{vm_name}/{vm_name}_error.log  \
          > {self.vagrant_dir}/{vm_name}/{vm_name}.log &')
      return True
    except Exception as err:
      return str(err)

  def console_output(self, vm_name):
    file = f'{self.vagrant_dir}/{vm_name}/{vm_name}.log'
    o_file = open(file, 'r')
    data = o_file.read()
    step = ''
    prog = '0'
    for l in data.split('\n'):
      if re.search('Progress', l):
        prog = l.split('%')[0].replace(' ', '').split(':')[1]
      if re.search('==>', l):
        step = l.split('default:')[1]
    o_file.close()
    # check if finished
    if re.search('script_finished', data):
      finished = True
    else:
      finished = False
    error = os.path.exists(f'{self.vagrant_dir}/{vm_name}/{vm_name}_error.log')
    error_content = open(f'{self.vagrant_dir}/{vm_name}/{vm_name}_error.log', 'r').read()
    if error_content != '':
      finished = True
      error = True
    else:
      error = False
      error_content = ''
    return {
      'output': str(data),
      'progress' : prog,
      'step' : step,
      'finished' : finished,
      'error' : error,
      'error_content' : str(error_content)
    }