#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv
from openerp import api
from datetime import date,datetime
import requests
import random
import time

#======================================== Project.task class implementation Begins =====================================


class mutual_projects(osv.osv):
  _name="project.task"
  _inherit = "project.task",
  _columns = {
      'remark_by_cms': fields.text('Remarks By CMS', store=True),
      'partner_id': fields.many2one('res.partner', 'Customer', required=True),
      'sale_order_task': fields.many2one('sale.order', 'Sale Order', store=True),
      'reviewer_id': fields.many2one('res.users', 'Forwarded to', select=True, track_visibility='onchange', domain="[('is_technician','=',False)]"),
      'user_id': fields.many2one('res.users', 'Assigned Tech', select=True, track_visibility='onchange', domain="[('is_technician','=',True)]"),
      'city_task': fields.related('partner_id', 'city', type='char', size=12, string='City', readonly=True),
      'branch_code_task': fields.related('partner_id', 'branch_code', type='char', size=12, string='Branch Code',readonly=True),
      'bank_code_task': fields.related('partner_id', 'bank_code', type='char', size=12, string='Bank Code',readonly=True),
      'monitoring_address_task': fields.related('partner_id', 'street', type='char', string='Monitoring address', readonly=True),
      'cs_number_task': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number',readonly=True),
      'tech_name_tasks': fields.one2many('tech.activities.tasks', 'tech_name_tasks', 'Timesheets', store=True),
      'complaint_reference': fields.integer('Complaint Reference',store=True),
      'timeIn': fields.datetime('Time In', select=True, copy=False, store=True),
      'timeOut': fields.datetime('Time Out', select=True, copy=False, store=True),
      'compute_total_time': fields.char('Total Time', store=True, readonly=True, compute='_compute_total_time', old='total_time'),
      'priority': fields.selection([('0', 'Normal'), ('1', 'Urgent'), ('2', 'Most Urgent')], 'Priority',store=True, select=True),
      'first_signal_time_task': fields.datetime('First Signal Time', select=True, copy=True,store=True),
      'name': fields.selection([('Uplink','Uplink'),
                              ('Survey', 'Survey'),
                              ('Disco','Disco'),
                              ('Additional','Additional'),
                              ('Shifting','Shifting'),
                              ('Reconnection', 'Reconnection'),
                              ('NewInstallation', 'NewInstallation'),
                              ],
                             'Task', required=True, store=True, select=True),
  }

  @api.one
  @api.depends('timeIn','timeOut')
  def _compute_total_time(self):
      # set auto-changing field
      # self.total_time = self.date_start * self.date_end
      # Time-In calculation
      if self.timeIn and self.timeOut:
          time_in = self.timeIn
          # time_in=time_in[0:20]
          time_in_hr = int(time_in[11:13]) + 5
          time_in_min = int(time_in[14:16])
          time_in_sec = int(time_in[17:20])
          # Time-Out calculation
          time_out = self.timeOut
          time_out_hr = int(time_out[11:13]) + 5
          time_out_min = int(time_out[14:16])
          time_out_sec = int(time_out[17:20])
          if time_out_min and self.timeOut:
              total_hr = time_out_hr - time_in_hr
              total_min = abs(time_out_min - time_in_min)
              total_sec = abs(time_out_sec - time_in_sec)

              self.compute_total_time = str(total_hr) + ":" + str(total_min) + ":" + str(total_sec)
              # Can optionally return a warning and domains
              return {
                  'warning': {
                      'title': "Something bad happened",
                      'message': "It was very bad indeed",
                  }
              }

# ======================================== Project.Issue class implementation Begins =====================================
class mutual_issues(osv.osv):
  _name="project.issue"
  _inherit = "project.issue",
  _columns = {
      'task_id': fields.many2one('project.task', ' ', domain="[('project_id','=',project_id)]"),
      'system_status':fields.char('System Status',store=True),
      'stage_id': fields.many2one('project.task.type', 'Stage', select=True, on_change='assign_tech()'),
      'complaint_status':fields.char('Complaint Status',store=True),
      'sale_order_issue': fields.many2one('sale.order', 'Sale Order', store=True),
      'contact': fields.related('user_id', 'mobile', type='char', size=12, string='Contact', readonly=True),
      'customer': fields.related('partner_id', 'name', type='char', size=12, string='Customer',readonly=True),
      'bm_number_issue': fields.related('partner_id', 'office', type='char', size=12, string='bm_number_issue',readonly=True),
      'om_number_issue': fields.related('partner_id', 'phone', type='char', size=12, string='om_number_issue',readonly=True),
      'mobile_logged': fields.related('create_uid', 'mobile', type='char', size=12, string='om_number_issue',
                                        readonly=True),
      'sms': fields.text('SMS', store=True),
      'cs_number_issue': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
      'city_issue': fields.related('partner_id', 'city', type='char', size=12, string='City',readonly=True),
      'branch_code_issue': fields.related('partner_id', 'branch_code', type='char', size=12, string='Branch Code',readonly=True),
      'bank_code_issue': fields.related('partner_id', 'bank_code', type='char', size=12, string='Bank Code', readonly=True),
      'monitoring_address_issue': fields.related('partner_id', 'street', type='char', string='Bank address', readonly=True),
      'remark_by_cms': fields.text('Remarks By CMS',store=True),
      'complaint_source': fields.selection([("By Anwar Zaib","By Anwar Zaib"),("Complaint generated by LSR", "By LSR"),("By Email","By Email"),("By CMS","By CMS"),("Direct","Direct")],'Complaint Source',required=True),
      'courtesy_remarks': fields.one2many('courtesy.remarks', 'complaint_title', 'Courtesy Remarks', store=True),
      'tech_name': fields.one2many('tech.activities.issues', 'tech_name', 'Timesheets', store=True),
      'user_id_issue': fields.many2one('res.users', 'Forwarded to', required=False, select=1, track_visibility='onchange', domain="[('is_technician','=',False)]"),
      'user_id': fields.many2one('res.users', 'Assigned Technician', required=False, select=1, track_visibility='onchange', domain="[('is_technician','=',True)]"),
      'compute_total_time':fields.char('Total Time',store=True,readonly=True,compute='_compute_total_time',old='total_time'),
      'partner_id': fields.many2one('res.partner', 'Customer', required=True, domain="[('customer','=',True)]"),
      'categ_ids': fields.many2many('project.category', string='Other Complaints'),
      'date_start': fields.datetime('Time In', select=True, copy=True,on_change='_change_stage()'),
      'date_end': fields.datetime('Time Out', select=True, copy=True),
      'first_signal_time': fields.datetime('First Signal Time', select=True, copy=True),
      'priority': fields.selection([('0','Normal'), ('1','Urgent'), ('2','Most Urgent')], 'Priority', select=True, store=True),
      'name': fields.selection([("Activation & Deactivation Problem	(I)","Activation & Deactivation Problem (I)"),
                                ("ADDITONAL WORK IN PENDING	(I)","ADDITONAL WORK IN PENDING	(I)"),
                                ("ALL PANIC CHECK (I)","ALL PANIC CHECK	(I)"),
                                ("All Zone Check (I)","All Zone Check (I)"),
                                ("BAS Shifting Case with Date of Shifting Urgent (I)","BAS Shifting Case with Date of Shifting Urgent (I)"),
                                ("BATTERY INSTALL (I)","BATTERY INSTALL	(I)"),
                                ("Battery Problem (I)","Battery Problem	(I)"),
                                ("Baypass Zone (I)","Baypass Zone (I)"),
                                ("BENTAL PROBLEM (I)","BENTAL PROBLEM (I)"),
                                ("BRANCH  CLOSED (I)","BRANCH CLOSED (I)"),
                                ("BRANCH SHIFT (I)","BRANCH SHIFT (I)"),
                                ("BRANCH UNDER RENOVATION (I)","BRANCH UNDER RENOVATION (I)"),
                                ("BUGLARY ALARM PROBLEM	(I)","BUGLARY ALARM PROBLEM	(I)"),
                                ("CALL LATER (I)","CALL LATER (I)"),
                                ("Cancel(I)","Cancel (I)"),
                                ("Change Keypad Code (I)","Change Keypad Code(I)"),
                                ("Change PTCL Line (I)","Change PTCL Line (I)"),
                                ("change the location (I)","change the location (I)"),
                                ("CLOSING SIGNAL PROBLEM (I)","CLOSING SIGNAL PROBLEM (I)"),
                                ("Code Dailer Problem (I)","Code Dailer Problem	(I)"),
                                ("Connect PTCL Line	(I)","Connect PTCL Line(I)"),
                                ("Delay Time Problem (I)","Delay Time Problem (I)"),
                                ("DEVICES INSTALL (I)","DEVICES INSTALL	(I)"),
                                ("DEVICES RE-INSTALL (I)","DEVICES RE-INSTALL	(I)"),
                                ("Disable Zone	(I)","	Disable Zone(I)"),
                                ("Electricity Problem(I)","Electricity Problem(I)"),
                                ("False Alarming (I)","False Alarming (I)"),
                                ("Fire Alarm Problem (I)","Fire Alarm Problem (I)"),
                                ("SIM balance issue	(I)","SIM balance issue	(I)"),
                                ("GSM Problem	(I)","GSM Problem	(I)"),
                                ("GSM SIM INSTALL (I)","GSM SIM INSTALL	(I)"),
                                ("Gsm Sim N/A (I)","Gsm Sim N/A (I)"),
                                ("Guard less Activation	(I)","Guard less Activation (I)"),
                                ("HEAVY METAL PROBLEM (I)","HEAVY METAL PROBLEM	(I)"),
                                ("hooter install (I)","hooter install (I)"),
                                ("Hooter Problem (I)","Hooter Problem(I)"),
                                ("Hooter Wire Connect (I)","Hooter Wire Connect	(I)"),
                                ("install keypad (I)","	install keypad	(I)"),
                                ("Keypad Beeping (I)","	Keypad Beeping	(I)"),
                                ("Keypad Code Problem (I)","Keypad Code Problem (I)"),
                                ("KEYPAD DEAD (I)","KEYPAD DEAD(I)"),
                                ("Keypad Hang (I)","Keypad Hang(I)"),
                                ("KEYPAD INSTALL (I)","KEYPAD INSTALL (I)"),
                                ("Keypad Problem (I)","Keypad Problem (I)"),
                                ("KEYPAD SHIFTING (I)","KEYPAD SHIFTING (I)"),
                                ("Late Transmission Problem (I)","Late Transmission Problem (I)"),
                                ("Most Urgent Complain (I)","Most Urgent Complain (I)"),
                                ("NO RESPONSE (I)","NO RESPONSE	(I)"),
                                ("ok (I)","	ok (I)"),
                                ("Other (I)", "Other (I)"),
                                ("Open/Close Problem (I)","	Open/Close Problem (I)"),
                                ("PANIC BUTTON DAMAGED (I)","PANIC BUTTON DAMAGED (I)"),
                                ("Panic Not Working	(I)","Panic Not Working (I)"),
                                ("PCB KIT FAULTY (I)","PCB KIT FAULTY (I)"),
                                ("Penal Beeping	(I)","Penal Beeping (I)"),
                                ("PENAL LOCATION CHANGE	(I)","PENAL LOCATION CHANGE	(I)"),
                                ("Penal Problem (I)", "Penal Problem (I)"),
                                ("PIR Problem (I)", "PIR Problem (I)"),
                                ("Programming Error Urgent Check (I)","Programming Error Urgent Check (I)"),
                                ("Ptcl Change (I)","Ptcl Change (I)"),
                                ("Ptcl Connect (I)","Ptcl Connect (I)"),
                                ("PTCL LINE DEAD (I)","PTCL LINE DEAD (I)"),
                                ("PTCL LINE DISTORTION (I)","PTCL LINE DISTORTION (I)"),
                                ("PTCL N/A (I)","PTCL N/A (I)"),
                                ("PTCL Problem due to System (I)","PTCL Problem due to System (I)"),
                                ("R/S Problem	(I)","	R/S Problem	(I)"),
                                ("RE-INSTALLATION OF SYSTEM/DEVICES (I)", "RE-INSTALLATION OF SYSTEM/DEVICES	(I)"),
                                ("Relocation of O/C	(I)", "Relocation of O/C (I)"),
                                ("REMOTE PANIC PROBLEM(I)", "REMOTE PANIC PROBLEM (I)"),
                                ("SD Not Working (I)","SD Not Working (I)"),
                                ("SIGNAL ISSUE (I)","SIGNAL ISSUE (I)"),
                                ("SIM BALANCE PROBLEM (I)","	SIM BALANCE PROBLEM	(I)"),
                                ("SIM BLOCKED (I)"," SIM BLOCKED (I)"),
                                ("SIM BLOCKED/OUTGOING SERVICE ISSUE (I)","SIM BLOCKED/OUTGOING SERVICE ISSUE (I)"),
                                ("SIM INSTALL (I)","SIM INSTALL (I)"),
                                ("SMOKE DECTECTOR PROBLEM (I)","SMOKE DECTECTOR PROBLEM (I)"),
                                ("SMOOK DETECTOR INSTAL (I)","SMOOK DETECTOR INSTAL	(I)"),
                                ("SMS Receiving Problem (I)","SMS Receiving Problem (I)"),
                                ("SYSTEM BEEPING (I)","SYSTEM BEEPING (I)"),
                                ("SYSTEM BRIEFING REQUIRED (I)","SYSTEM BRIEFING REQUIRED (I)"),
                                ("System Dead (I)","System Dead	(I)"),
                                ("System Dead urgent (I)","System Dead urgent(I)"),
                                ("SYSTEM HANG (I)","SYSTEM HANG (I)"),
                                ("System Problem Urgent check (I)","System Problem Urgent check (I)"),
                                ("System Remove/Dismentle (I)","System Remove/Dismentle (I)"),
                                ("System Remove/Dismentle Case with Date Urgent (I)","System Remove/Dismentle Case with Date Urgent (I)"),
                                ("System Shift(I)","System Shift(I)"),
                                ("TECHNICIAN REQUIRED(I)","TECHNICIAN REQUIRED(I)"),
                                ("Temper problem(I)","Temper problem(I)"),
                                ("Transmission Problem(I)","Transmission Problem(I)"),
                                ("Transmission Problem & System Check (I)","Transmission Problem & System Check(I)"),
                                ("USER CODE CHANGED	(I)","USER CODE CHANGED	(I)"),
                                ("USER CODE PROBLEM	(I)","USER CODE PROBLEM	(I)"),
                                ("user code provide	(I)","user code provide	(I)"),
                                ("V/S Problem (I)","V/S Problem	(I)"),
                                ("Wiring Check (I)","Wiring Check (I)"),
                                ("Zone 1 Problem (I)","Zone 1 Problem (I)"),
                                ("Zone 2 Problem (I)","Zone 2 Problem (I)"),
                                ("Zone 3 Problem (I)","Zone 3 Problem (I)"),
                                ("Zone 4 Problem (I)","Zone 4 Problem (I)"),
                                ("Zone 5 Problem (I)","Zone 5 Problem (I)"),
                                ("Zone 6 Problem (I)","Zone 6 Problem (I)"),
                                ("Zone 7 Problem (I)","Zone 7 Problem (I)"),
                                ("Zone 8 Problem (I)","Zone 8 Problem (I)"),
                                ("Additional(T)", "Additional(T)"),
                                ("Backup Battery Required(T)", "Backup Battery Required (T)"),
                                ("BAS Penal/Device Location Change (T)","BAS Penal/Device Location Change (T)"),
                                ("Fixed Panic Button Required (T)", "Fixed Panic Button Required (T)"),
                                ("Foot Panic Paddles Required T", "Foot Panic Paddles Required T"),
                                ("GSM/Bental Required (T)", "GSM/Bental Required (T)"),
                                ("H/M (Heavy Metal) Required (T)", "H/M (Heavy Metal) Required (T)"),
                                ("Hooter Required (T)", "Hooter Required (T)"),
                                ("Keypad Required (T)", "Keypad Required (T"),
                                ("O/C (Magnetic Door Contact) Required (T)","O/C (Magnetic Door Contact) Required (T)"),
                                ("PCB Required (T)", "PCB Required (T)"),
                                ("PIR (Motion Sensor) Required (T)", "PIR (Motion Sensor) Required (T)"),
                                ("R/S (Roller Shutter) Required (T)", "R/S (Roller Shutter) Required (T)"),
                                ("Remote/Wireless Panic Required (T)", "Remote/Wireless Panic Required (T)"),
                                ("Re-Wiring Required (T)", "Re-Wiring Required (T)"),
                                ("S/D (Smoke Detector) Required (T)", "S/D (Smoke Detector) Required (T)"),
                                ("System Shifting/Re-installation (T)","System Shifting/Re-installation (T)"),
                                ("Transformer Required (T)", "Transformer Required (T)"),
                                ("V/S (Vibration Sensor) Required (T)","V/S (Vibration Sensor) Required (T)"),
                                ("Survey (T)", "Survey (T)"),
                                ("New Installation (T)", "New Installation (T)"),
                                ("Disco (T)", "Disco (T)"),
                                ("Special Task (T)", "Special Task (T)"),
                                ],
                               'Complaint Title', required=True, read=['__export__.res_groups_52'], write=['project.group_project_user'],
                               on_change='type()'),
      'Zone1': fields.boolean('Zone1', store=True),
      'Zone2': fields.boolean('Zone2', store=True),
      'Zone3': fields.boolean('Zone3', store=True),
      'Zone4': fields.boolean('Zone4', store=True),
      'Zone5': fields.boolean('Zone5', store=True),
      'Zone6': fields.boolean('Zone6', store=True),
      'Zone7': fields.boolean('Zone7', store=True),
      'Zone8': fields.boolean('Zone8', store=True),
      'Zone9': fields.boolean('Zone9', store=True),
      'panic': fields.boolean('Panic', store=True),
      'duress': fields.boolean('Duress', store=True),
      'medical': fields.boolean('Medical', store=True),
      'fire': fields.boolean('Fire', store=True),
      'gsm': fields.selection([('GSM', 'GSM'), ('Bental','Bental')],'GSM/Bental'),
      'gsmNumber': fields.char('GSM/Bental',store=True),
      'gsm_postpaid_prepaid': fields.selection([('Prepaid', 'Prepaid'), ('Postpaid', 'Postpaid')],'Prepaid/Postpaid',store=True),
      'ptcl': fields.char('PTCL', store=True),
      'ptcl_dedicated_shared': fields.selection([('Dedicated', 'Dedicated'), ('Shared', 'Shared')],'Dedicated/Shared',store=True),
      'response_check': fields.selection([('Yes', 'Yes'), ('No', 'No')],'Response check',store=True),
      'status': fields.char('Final Status',store=True),
      'complaint_log_bank': fields.char('Complaint Log By Client', size=25, select=True, store=True),
      'check_by': fields.char('Check By Client', size=25, select=True, store=True),
      'courtesy': fields.text('Courtesy Remarks', store=True),
      'clientname': fields.char('Client Name', store=True, size=30, required=True),
      'color': fields.integer(compute='_get_color', string='Color', store=False),
      'check': fields.char('Type', store=True, compute='type'),
      'convert_to_task': fields.boolean('Convert to Task', store=True),
      'tech': fields.char('Assigned to Technician', store=True, compute='assign_tech'),
      'technician_name': fields.many2one('hr.employee', 'Technician Name', required=False, select=1,
                                         track_visibility='onchange', domain="[('department_id','=','Technician')]",
                                         defaults=''),
      'techContact': fields.char('Contact', store=True, size=11,readonly=False,compute='get_contact'),
      'count': fields.char('Count', store=True, readonly=True,compute='_count'),
      'restrict': fields.char('Restrict', store=True, readonly=True, compute='restrictAssignedtoTech'),
      'pending': fields.boolean('Pending',store=True, read=['project.group_project_manager'], write=['project.group_project_manager'])
  }

  @api.one
  @api.depends('name')
  def type(self):
      str = self.name
      if str:
          if str.find('(I)') != -1:
              self.check = "Issue"
          elif str.find('(T)') != -1:
              self.check = "Task"

  @api.depends('check', 'convert_to_task')
  def _get_color(self):
      if self.check == "Issue"and self.convert_to_task is False:
          self.color = 3
      elif self.check == "Task":
          self.color = 14
      elif self.check == "Issue" and self.convert_to_task is True:
          self.color = 10

  @api.depends('technician_name')
  def get_contact(self):
      self.techContact = self.technician_name.work_phone

  @api.depends('sms')
  def _count(self):
      if self.sms:
          self.count = len(self.sms)

  @api.one
  @api.depends('tech_name.technician_name')
  def assign_tech(self):
      print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Technician Name"
      technician = ''
      for technicians in self.tech_name:
          technician += str(technicians.technician_name.name) + ' '
      self.tech = technician

  @api.depends('stage_id','tech')
  def restrictAssignedtoTech(self):
      self.restrict = self.stage_id.name
      if not self.tech and self.stage_id.name == "Assigned to Technician":
          raise osv.except_osv('Must assign technician', 'You cannot move this card into this bucket')
      else:
          if self.tech and self.id:
              for line in self.tech_name:
                  self.env.cr.execute('UPDATE tech_activities_issues SET status='+"'"+self.stage_id.name+"'"+' WHERE tech_name = ' + str(self.id))
                  print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

  @api.multi
  def smsSent(self):
      if self.techContact:
          if len(self.sms) < 140 :
              if self.techContact and self.sms:
                  self.env.cr.execute("insert into complaint_messages(message,receiver_name,receiver_contact,status,date_now)values('"+self.sms.replace('\n',' ')+"','"+str(self.technician_name.name)+"','"+self.techContact+"','0','"+str(datetime.now().date())+"')")
                  r = requests.post("http://localhost:3000", data={'sms': self.sms, 'contact':self.techContact})
              else:
                  raise osv.except_osv('Sorry', 'SMS sending failed')
          else:
              raise osv.except_osv('SMS Limit Exceed', 'SMS length must be less than 140 characters')

      else:
          print 'Kindly enter mobile number of technician'
          raise osv.except_osv('Empty Field','Kindly enter mobile number of technician')


  @api.multi
  def details(self):
      if (self.partner_id.is_company == False):
          self.sms = str(self.id)+"\n"+self.name+"\n"+self.cs_number_issue+"\n"+self.monitoring_address_issue+"\n"+self.city_issue

      elif self.cs_number_issue and self.bank_code_issue and self.branch_code_issue and self.monitoring_address_issue and self.city_issue and self.description:
          self.sms = str(self.id)+"\n"+self.name+"\n"+self.description+"\n"+ \
                     self.bank_code_issue+"\n"+self.cs_number_issue+"\n"+"BC"+self.branch_code_issue+"\n"+self.monitoring_address_issue+"\n"+self.city_issue

      elif self.cs_number_issue and self.bank_code_issue and self.branch_code_issue and self.monitoring_address_issue and self.city_issue:
          self.sms = str(self.id)+"\n"+self.name+"\n"+ \
                     self.bank_code_issue+"\n"+self.cs_number_issue+"\n"+"BC"+self.branch_code_issue+"\n"+self.monitoring_address_issue+"\n"+self.city_issue
      else:
          raise osv.except_osv('Information Incomplete', 'You must have full information before sending an SMS')




  @api.one
  @api.depends('date_start','date_end')
  def _compute_total_time(self):
      # set auto-changing field
      # self.total_time = self.date_start * self.date_end
      print self.date_start

      # Time-In calculation
      if self.date_start and self.date_end:
          time_in = self.date_start
          # time_in=time_in[0:20]
          time_in_hr = int(time_in[11:13]) + 5
          time_in_min = int(time_in[14:16])
          time_in_sec = int(time_in[17:20])
          # Time-Out calculation
          time_out = self.date_end
          time_out_hr = int(time_out[11:13]) + 5
          time_out_min = int(time_out[14:16])
          time_out_sec = int(time_out[17:20])
          if time_out_min and self.date_end:
              total_hr = time_out_hr - time_in_hr
              total_min = abs(time_out_min - time_in_min)
              total_sec = abs(time_out_sec - time_in_sec)

              self.compute_total_time = str(total_hr) + ":" + str(total_min) + ":" + str(total_sec)
              # Can optionally return a warning and domains
              return {
                  'warning': {
                      'title': "Something bad happened",
                      'message': "It was very bad indeed",
                  }
              }

class tech_activities_issues(osv.osv):
    _name = "tech.activities.issues"
    _columns = {
        'tech_name': fields.many2one('project.issue', 'Complaint Title'),
        'technician_name': fields.many2one('hr.employee', 'Technician Name', required=True, select=1, track_visibility='onchange', domain="[('department_id','=','Technician')]", defaults=''),
        'reason': fields.char('Final Status',store=True),
        'systemstatus': fields.char('System Status', store=True),
        'total_time': fields.float('Total Time', store=True),
        'date': fields.date('Date',store=True),
        'compute_total_time': fields.char('T/T', store=True, readonly=True, compute='_compute_total_time', ),
        'first_signal': fields.datetime('F/T', select=True, copy=True,store=True),
        'date_start': fields.datetime('T/I', select=True, copy=True,store=True),
        'date_end': fields.datetime('T/O', select=True, copy=True, store=True),
        'cs_number': fields.related('tech_name', 'cs_number_issue', type='char', string='CS Number'),
        'bank_code': fields.related('tech_name','bank_code_issue',type='char',string='Bank Code'),
        'complaint_source': fields.related('tech_name', 'complaint_source', type='char', string='Complaint Source'),
        'monitoring_address_issue': fields.related('tech_name', 'monitoring_address_issue', type='char', string='Address'),
        #'stage_id': fields.related('tech_name','stage_id',type='many2one',relation='project.issue',string='Stage_id'),
        'issue_id': fields.related('tech_name', 'id', type='integer', string='Complaint ID'),
        'branch_code': fields.related('tech_name', 'branch_code_issue', type='char', string='Branch Code'),
        'multi_tech': fields.many2many('hr.employee', string='Other Tech', domain="[('department_id','=','Technician')]"),
        'status': fields.selection([('Time In/Out','Time In/Out'),('Resolved','Resolved'),('Under Process','Under Process'),('Issue at bank end','Issue at bank end'),('Additional/Device Replacement','Additional/Device Replacement'),('Assigned to Technician','Assigned to Technician'),('Complaints/Tasks','Complaints/Tasks'),('Online Resolved','Online Resolved')],'Complaint Marking',store=True,onchange='changestatus()'),
    }

    @api.one
    @api.depends('date_start', 'date_end')
    def _compute_total_time(self):
        # self.compute_total_time = self.date_start
        if self.date_start and self.date_end:
            # set the date and time format
            date_format = "%Y-%m-%d %H:%M:%S"
            # convert string to actual date and time
            timeIn = datetime.strptime(self.date_start, date_format)
            timeOut = datetime.strptime(self.date_end, date_format)
            # find the difference between two dates
            diff = timeOut - timeIn
            self.compute_total_time = diff

    @api.one
    @api.onchange('status')
    def changestatus(self):
        if self.status == "Resolved":
            self.env.cr.execute('UPDATE project_issue SET stage_id = 15 WHERE id ='+str(self.issue_id))
            #self.env.cr.execute('UPDATE tech_activities_issues SET status=' + "'" + self.status + "'" + ' WHERE tech_name = ' + str(self.issue_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        elif self.status == "Time In/Out":
            self.env.cr.execute('UPDATE project_issue SET stage_id = 13 WHERE id =' + str(self.issue_id))
            #self.env.cr.execute('UPDATE tech_activities_issues SET status=' + "'" + self.status + "'" + ' WHERE tech_name = ' + str(self.issue_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        elif self.status == "Under Process":
            self.env.cr.execute('UPDATE project_issue SET stage_id = 20 WHERE id =' + str(self.issue_id))
           # self.env.cr.execute('UPDATE tech_activities_issues SET status=' + "'" + self.status + "'" + ' WHERE tech_name = ' + str(self.issue_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        elif self.status == "Assigned to Technician":
            self.env.cr.execute('UPDATE project_issue SET stage_id = 12 WHERE id =' + str(self.issue_id))
            #self.env.cr.execute('UPDATE tech_activities_issues SET status=' + "'" + self.status + "'" + ' WHERE tech_name = ' + str(self.issue_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        elif self.status == "Additional/Device Replacement":
            self.env.cr.execute('UPDATE project_issue SET stage_id = 10 WHERE id =' + str(self.issue_id))
           # self.env.cr.execute('UPDATE tech_activities_issues SET status=' + "'" + self.status + "'" + ' WHERE tech_name = ' + str(self.issue_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        elif self.status == "Issue at bank end":
            self.env.cr.execute('UPDATE project_issue SET stage_id = 14 WHERE id =' + str(self.issue_id))
            #self.env.cr.execute('UPDATE tech_activities_issues SET status=' + "'" + self.status + "'" + ' WHERE tech_name = ' + str(self.issue_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        else:
            raise osv.except_osv('Error....', 'You do not have rights to move this card into this bucket')




class low_messages(osv.osv):
    _name = "low.messages"
    _columns = {
        'bank': fields.many2one('res.partner', 'Customer',store=True,required=True),
        'employee_name': fields.many2one('hr.employee', 'Technician Name',domain="[('department_id','=','Technician')]", defaults='',old='technician_name'),
        'cs': fields.char('CS Number',store=True,readonly=True),
        'branch_code': fields.char('Branch Code', store=True, readonly=True),
        'address': fields.text('Address',store=True, readonly=True),
        'sms': fields.text('SMS',store=True, default='Backup Battery is running low due to long electric failures. Please recharge it within 1.5hr for smooth working of system(MSS 111-238-222)'),
        'number': fields.char('Contact Number',store=True,size=11,required=True),
        'technician':fields.boolean('Technician',store=True),
    }

    @api.onchange('bank')
    def customer_details(self):
        if self.technician == False:
            self.cs = self.bank.cs_number
            self.branch_code = self.bank.branch_code
            self.address = str(self.bank.street) + "\n"+str(self.bank.street2) +"\n"+str(self.bank.city)

    @api.onchange('employee_name')
    def technician_contact(self):
        if self.technician == True:
            self.number = self.employee_name.work_phone

    @api.multi
    def smsSent(self):
        if self.number  and self.sms:
            if len(self.sms)<140 :
                r = requests.post("http://localhost:3000", data={'sms': self.sms, 'contact': self.number})
            else:
                raise osv.except_osv('Error....', 'SMS Length must be within 150 characters')
        else:
            raise osv.except_osv('Error....', 'Kindly enter contact number')


class tech_activities_tasks(osv.osv):
    _name = "tech.activities.tasks"
    _order = "date_start desc"
    _columns = {
        'systemstatus': fields.char('System Status', size=100, store=True),
        'tech_name_tasks': fields.many2one('project.task', 'Task Title'),
        'technician_name_tasks':fields.many2one('hr.employee', 'Technician Name', required=False, select=1, track_visibility='onchange', domain="[('department_id','=','Technician')]", defaults=''),
        'reason_tasks': fields.char('Final Status', size=100, store=True),
        'total_time_tasks': fields.float('Total Time', store=True),
        'date_tasks': fields.date('Date', store=True),
        'compute_total_time': fields.char('T/T', store=True, readonly=True, compute='_compute_total_time'),
        'first_signal': fields.datetime('F/T', select=True, copy=True, write=['project.group_project_manager'],
                                        read=['project.group_project_user']),
        'date_start': fields.datetime('T/I', select=True, copy=True, write=['project.group_project_manager'],
                                      read=['project.group_project_user']),
        'date_end': fields.datetime('T/O', select=True, copy=True, write=['project.group_project_manager'],
                                    read=['project.group_project_user']),
        'cs_number': fields.related('tech_name_tasks', 'cs_number_task', type='char', string='CS Number'),
        # 'stage_id': fields.related('tech_name','stage_id',type='many2one',relation='project.issue',string='Stage_id'),
        'task_id': fields.related('tech_name_tasks', 'id', type='char', string='Task ID'),
        'complaint_reference':fields.related('tech_name_tasks', 'complaint_reference', type='char', string='Complaint Reference'),
        'branch_code': fields.related('tech_name_tasks', 'branch_code_task', type='char', string='Branch Code'),
        'multi_tech': fields.many2many('hr.employee', string='Other Tech',domain="[('department_id','=','Technician')]"),
    }

    @api.one
    @api.depends('date_start', 'date_end')
    def _compute_total_time(self):
        # self.compute_total_time = self.date_start
        if self.date_start and self.date_end:
            # set the date and time format
            date_format = "%Y-%m-%d %H:%M:%S"
            # convert string to actual date and time
            timeIn = datetime.strptime(self.date_start, date_format)
            timeOut = datetime.strptime(self.date_end, date_format)
            # find the difference between two dates
            diff = timeOut - timeIn
            self.compute_total_time = diff

class messages(osv.osv):
    _name = "complaint.messages"
    _columns = {
        'message': fields.text('Message', store=True),
        'receiver_contact': fields.char('Receiver Contact', store=True),
        'status': fields.char('Status',store=True, default='0'),
        'receiver_name': fields.char('Receiver Name', store=True),
        'sender_name': fields.char('Sender', store=True),
        'date_now': fields.date('Date', store=True)
    }


class guardtracking(osv.osv):
    _name = "guard.tracking"
    _columns = {
        'card_no': fields.char('RF_ID',store=True),
        'customer': fields.many2one('res.partner','Customer',store=True),
        'branch_code': fields.related('customer', 'branch_code', type='char', string='Branch Code', store=True),
    }


class courtesy_remarks(osv.osv):
    _name = "courtesy.remarks"
    _columns = {
        'complaint_title': fields.many2one('project.issue', 'Complaint Title'),
        'remarks': fields.char('Remarks',store=True,required=True),
    }

    # @api.depends('card_no')
    # def fetch_customer_details(self):
    #     if self.card_no:
    #         list = self.env['res.partner'].search([['rf_id', '=', self.card_no],])
    #         self.customer = list





