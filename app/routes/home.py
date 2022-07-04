from app import yeve
from flask import render_template, request
from lib.vboxmanage import VboxManage
from lib.vagrant import Vagrant

@yeve.route("/home", methods=['POST', 'GET'])
def home():
  if 'list_vms' in request.args:
    if 'stop_vm' in request.args:
      vm_name = request.args['stop_vm']
      VboxManage().stop_vm(vm_name)
    elif 'start_vm' in request.args:
      vm_name = request.args['start_vm']
      VboxManage().start_vm(vm_name)
    elif 'destroy_vm' in request.args:
      vm_name = request.args['destroy_vm']
      VboxManage().destroy_vm(vm_name)
    list_vms = VboxManage().get_vm_info()
    return render_template('home.html', list_vms=list_vms)
  elif 'new_vm' in request.args:
    nics = VboxManage().list_nics()
    box = Vagrant().list_box()
    return render_template('home.html', nics=nics, box=box)
  elif 'console_log' in request.args:
    vm_name = request.args['vm_name']
    return render_template('home.html', vm_name=vm_name)
  elif 'create_vm' in request.args:
    if 'vm_name' in request.args:
      vm_name = request.args['vm_name']
    elif 'vm_name' in request.form:
      vm_name = request.form['vm_name']
    r = Vagrant().create_vm(vm_name)
    if r == True:
      return render_template('home.html', vm_name=vm_name)
    else:
      return str(r)
  elif len(request.args) == 0:
    return render_template('home.html')

@yeve.route("/vagrant/consoleoutput", methods=['POST', 'GET'])
def console_output():
  vm_name = request.args['vm_name']
  res = Vagrant().console_output(vm_name=vm_name)
  return {
    'data' : res
  }

@yeve.route("/vagrant/console_log", methods=['POST', 'GET'])
def console_log():
  vm_name = request.args['vm_name']
  res = Vagrant().console_log(vm_name=vm_name)
  return {
    'data' : res
  }


@yeve.route("/test", methods=['POST', 'GET'])
def test():
  res = Vagrant().list_box()
  return {
    'data' : res
  }
