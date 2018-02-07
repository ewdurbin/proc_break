#!/usr/bin/python

import sys
import re
import getpass
import os
import errno


# wrapper to make sure that we don't rewrite a directory #
def safe_mkdir(path):
  try:
    os.mkdir(path)
  except OSError, exc: 
    if exc.errno == errno.EEXIST: pass
    else: raise

# takes string and returns list of lists #
def clean_routine(routines_string):
  routines_list = routines_string.split("'),('")

  routines_list[0] = routines_list[0].replace('(\'','')
  routines_list[-1] = routines_list[-1].replace('\');','')

  all_routines = []
  for routine in routines_list:
    all_routines.append(routine.split("','"))
 
  new_routines = []
  for routine in all_routines:
    field_list = []
    for field in routine:
      field = field.replace('\\n','\n')
      field = field.replace('\\','')
      field_list.append(field)
    new_routines.append(field_list)

  return new_routines

# does all the jockeying to inject our real data in to the template provided #
def write_to_file(routine,template):
  
  safe_mkdir(os.path.join(os.getcwd(),routine[0]+'_routines'))

  w = open(os.path.join(os.getcwd(),routine[0]+'_routines',routine[1]+'_'+routine[2].lower()+'.sql'),'w')
  formatted = template
  formatted = formatted.replace('%%db%%',routine[0])
  formatted = formatted.replace('%%specific_name%%',routine[3])
  formatted = formatted.replace('%%language%%',routine[4])
  formatted = formatted.replace('%%sql_data_access%%',routine[5])
  
  if routine[6].lower() == 'yes':
    boolean_det = ''
  elif routine[6].lower() == 'no':
    boolean_det = 'NOT '
  else:
    print 'You may have a bad mysql dump!'
    exit(0)
  formatted = formatted.replace('%boolean_det%',boolean_det)

  formatted = formatted.replace('%%security_type%%',routine[7])
  formatted = formatted.replace('%%param_list%%',routine[8].replace('\\n','\r'))
  formatted = formatted.replace('%%returns%%',routine[9])
  formatted = formatted.replace('%%body%%',routine[10].replace('\\n','\r'))
  formatted = formatted.replace('%%definer%%',routine[11])
  if len(routine[15]) > 1:
    formatted = formatted.replace('%%comment%%',routine[15])
  else:
    formatted = formatted.replace('%%comment%%','$Revision$')
  w.write(formatted)
  print "written to file:  "+routine[0]+"."+routine[3]
  w.close()


def main():
  # set incoming arguments #
  args = sys.argv[1:] 
  
  if not args:
    print "usage: --host `host` --user `user`";
    sys.exit(1)
  
  host = ''
  if len(args) > 1 and args[0] == '--host':
    host = args[1]
    del args[0:2]
  else:
    print "error: must specify host"
    print "\tusage: --host `host` --user `user` [--database `lv_bpo`]";
    sys.exit(1)
  
  user = ''
  if len(args) > 1 and args[0] == '--user':
    user = args[1]
    del args[0:2]
  else:
    print "error: must specify user"
    print "\tusage: --host `host` --user `user` [--database `lv_bpo`]";
    sys.exit(1)
  
  database = 'lv_bpo'
    
  output_file = os.path.join(os.getcwd(),'lv_bpo_proc_dump.sql')
  
  print 'Input mysql password user '+user
  passwd=getpass.getpass()
  print '\n'
  
  os.system('mysqldump mysql proc -h'+host+' -u'+user+' -p'+passwd+' > '+output_file)
  
  # read incoming mysqldump of mysql.proc and extract juicy data cleanup the file#
  f = open(output_file, 'rU')
  for line in f:
    match = re.search(r'INSERT INTO `proc` VALUES (.+)',line)
    if match:
      routines_string = match.group(1)
      break
  f.close()
  os.unlink(output_file)
  
  # takes string and returns a list of lists #
  all_routines = clean_routine(routines_string)

  # pickup user templates #
  f = open(os.path.join(os.getcwd(),'templates','template_procedure.txt'), 'rU')
  procedure_template = f.read()
  f.close()
  
  f = open(os.path.join(os.getcwd(),'templates','template_function.txt'), 'rU')
  function_template = f.read()
  f.close()
  
  # creates output directories #
  safe_mkdir(os.path.join(os.getcwd(),database+'_routines'))  

  # cleans out old procedure files #
  folder = os.path.join(os.getcwd(),database+'_routines')
  for the_file in os.listdir(folder):
	file_path = os.path.join(folder, the_file)
	try:
	  if os.path.isfile(file_path):
		print "removed  "+file_path
		os.unlink(file_path)
	except Exception, e:
	  print e

  # finalize and write output #
  for routine in all_routines:
    if routine[2].lower() == 'function':
      template = function_template
    elif routine[2].lower() == 'procedure':
      template = procedure_template
    else:
      print 'You may have a bad mysql dump!'
    
    if routine[0] == database:
      write_to_file(routine,template)
    
  # say goodnight! #
  print "\nexport complete!"

if __name__ == '__main__':
  main()
