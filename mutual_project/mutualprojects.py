#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv
from openerp import api
from datetime import date, datetime, timedelta
import requests
import random
import time
import re
import urllib
import urllib2
from xml.dom.minidom import parseString
import requests

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
      'cms_remarks': fields.one2many('cms.remarks', 'complaint_title', 'CMS Remarks', store=True),
      'bank_remarks': fields.one2many('bank.remarks', 'complaint_title', 'Bank Remarks', store=True),
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
      'pending': fields.boolean('Pending',store=True, read=['project.group_project_manager'], write=['project.group_project_manager']),
      'sms_status': fields.char('SMS Staus')
  }

  def write(self, cr, uid, ids, vals, context=None):
      # stage change: update date_last_stage_update
      obj = self.browse(cr, uid, ids, context=context)
      if 'stage_id' in vals:
          if obj.stage_id['name']=='Online Resolved' or obj.stage_id['name']=='Resolved':
              raise osv.except_osv('Alert....', 'You are not able to move this card')
          else:
              vals.update(self.onchange_stage_id(cr, uid, ids, vals.get('stage_id'), context=context)['value'])
              vals['date_last_stage_update'] = fields.datetime.now()
              if 'kanban_state' not in vals:
                  vals['kanban_state'] = 'normal'
      # user_id change: update date_open
      if vals.get('user_id') and 'date_open' not in vals:
          vals['date_open'] = fields.datetime.now()

      return super(mutual_issues, self).write(cr, uid, ids, vals, context)

  @api.model
  def create(self, vals):
      self.env.cr.execute("SELECT project_issue.name,project_issue.partner_id,project_task_type.name FROM project_issue INNER JOIN project_task_type ON project_issue.stage_id = project_task_type.id WHERE (project_task_type.name != 'Resolved' and project_task_type.name != 'Online Resolved') and project_issue.check = 'Issue' and project_issue.partner_id="+str(vals['partner_id']))
      list_of_customers = self.env.cr.dictfetchall()
      if len(list_of_customers) > 0:
          raise osv.except_osv('Alert..................', 'Complaint of this branch has been logged already')
      else:
          return super(mutual_issues, self).create(vals)


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
      technician = ''
      for technicians in self.tech_name:
          technician += str(technicians.technician_name.name) + ' '
      self.tech = technician

  @api.depends('stage_id','tech')
  def restrictAssignedtoTech(self):
      self.restrict = self.stage_id.name
      # if self.tech_name.reason == False or self.tech_name.compute_total_time == False:
      #     raise osv.except_osv('You cannot resolved this complainy', 'Kindly mention status and T/T')
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
          if self.techContact and self.sms:
              ''' Sends post request to get session Id against username & password '''
              number = urllib.unquote(self.techContact).encode('utf8')
              message = urllib.quote((self.sms).encode("utf-8"))
              if int(self.count):
                  url = ("https://bsms.ufone.com/bsms_v8_api/sendapi-0.3.jsp?id=03315506614&message=%s&shortcode=MUTUAL&lang=English&mobilenum=%s&password=Ptml@123456&groupname=&messagetype=Transactional" % (message, number))
                  repsonse = requests.get(url, verify=False)
                  result = parseString(repsonse.content).getElementsByTagName('response_text')[0].childNodes[0].data
                  #self.env['sms'].create({'mobile_no':self.techContact, 'message_body':self.sms})
                  self.sms_status = result
                  self.env['sms.report'].create({'to':number,'sms':self.sms,'status':result,'type':'Complaint Message'})
                  return result
              else:
                  raise osv.except_osv('Limit Exceed', 'SMS must be within 160 characters')
      else:
          raise osv.except_osv('Empty Field','Kindly enter mobile number of technician')

  @api.multi
  def create_sms(self):

      list_of_sms = []
      rec_dict = {'sms': self.sms, 'contact': self.techContact,'status':'sending','name':self.technician_name.name}
      rec2_dict={'sms':self.sms , 'contact':self.env.user.mobile ,'status':'sending','name':self.env.user.name }
      list_of_sms.append(dict(rec_dict))
      list_of_sms.append(dict(rec2_dict))
      for l in list_of_sms:
          print l
          self.env['complaint.messages'].create({
              'message': l.get('sms'),
              'receiver_contact': l.get('contact'),
              'receiver_name':l.get('name'),
              'status':l.get('status'),
          })

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
        'bas': fields.selection([('GSM Only','GSM Only'),('Bentel Only','Bentel Only'),
                                 ('PTCL Only','PTCL Only'),('Bentel and PTCL','Bentel and PTCL')
                                ,('GSM and PTCL', 'GSM and PTCL'),('Nil','Nil')], string='BAS Connected To',store=True),
        'sim_status': fields.selection([('Postpaid', 'Postpaid'), ('Prepaid', 'Prepaid'), ('Inactive', 'Inactive'),
                                        ('Not Available', 'Not Available'), ('Nil', 'Nil')],
                                       string='Sim Status', store=True),
        'pending': fields.selection([('Yes', 'Yes'), ('No', 'No'), ('Nil', 'Nil')], string='Work is Pending', store=True),
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
        'status': fields.selection([('Time In/Out','Time In/Out'),('Resolved','Resolved'),('Under Process','Under Process'),('Issue at bank end','Issue at bank end'),('Additional/Device Replacement','Additional/Device Replacement'),('Assigned to Technician','Assigned to Technician'),('Complaints/Tasks','Complaints/Tasks'),('Online Resolved','Online Resolved'),('Inventory Check','Inventory Check')],'Complaint Marking',store=True,onchange='changestatus()'),
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

        elif self.status == "Inventory Check":
            self.env.cr.execute('UPDATE project_issue SET stage_id = 22 WHERE id =' + str(self.issue_id))
            # self.env.cr.execute('UPDATE tech_activities_issues SET status=' + "'" + self.status + "'" + ' WHERE tech_name = ' + str(self.issue_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        else:
            raise osv.except_osv('Error....', 'You do not have rights to move this card into this bucket')


class low_messages(osv.osv):
    _name = "low.messages"
    _columns = {
        'count': fields.char('Count', store=True, readonly=True, compute='_count'),
        'bank': fields.many2one('res.partner', 'Customer',store=True,required=True),
        'employee_name': fields.many2one('hr.employee', 'Technician Name',domain="[('department_id','=','Technician')]", defaults='',old='technician_name'),
        'cs': fields.char('CS Number',store=True,readonly=True),
        'branch_code': fields.char('Branch Code', store=True, readonly=True),
        'address': fields.text('Address',store=True, readonly=True),
        'sms': fields.text('SMS',store=True, default='Backup Battery is running low due to long electric failures. Please recharge it within 1.5hr for smooth working of system(MSS 111-238-222)'),
        'number': fields.char('Contact Number',store=True,size=11,required=True),
        'technician':fields.boolean('Technician',store=True),
        'rso_sms': fields.boolean('RSO', store=True),
        'sms_status': fields.char('SMS Status')

    }

    @api.depends('sms')
    def _count(self):
        if self.sms:
            self.count = len(self.sms)

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
        if self.number:
            if self.number and self.sms:
                ''' Sends post request to get session Id against username & password '''
                number = urllib.unquote(self.number).encode('utf8')
                message = urllib.quote((self.sms).encode("utf-8"))
                if int(self.count):
                    url = ("https://bsms.ufone.com/bsms_v8_api/sendapi-0.3.jsp?id=03315506614&message=%s&shortcode=MUTUAL&lang=English&mobilenum=%s&password=Ptml@123456&groupname=&messagetype=Transactional" % (
                        message, number))
                    repsonse = requests.get(url, verify=False)
                    result = parseString(repsonse.content).getElementsByTagName('response_text')[0].childNodes[0].data
                    #self.env['sms'].create({'mobile_no': self.techContact, 'message_body': self.sms})
                    self.sms_status = result
                    self.env['sms.report'].create({'to': number, 'sms':self.sms, 'status': result, 'type': 'RSO Message'})
                    return result
                else:
                    raise osv.except_osv('Limit Exceed', 'SMS must be within 160 characters')
        else:
            raise osv.except_osv('Empty Field', 'Kindly enter mobile number of technician')


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


class cms_remarks(osv.osv):
    _name = "cms.remarks"
    _columns = {
        'complaint_title': fields.many2one('project.issue', 'Complaint Title'),
        'remarks': fields.char('Remarks',store=True),
        'client_name': fields.char('Client',store=True),
        'responsible_person': fields.char('Responsible Person', store=True),
    }


class bank_remarks(osv.osv):
    _name = "bank.remarks"
    _columns = {
        'complaint_title': fields.many2one('project.issue', 'Complaint Title'),
        'remarks': fields.char('Remarks',store=True),
        'client_name': fields.char('Client',store=True),
        'responsible_person': fields.char('Responsible Person', store=True),
    }


class oldTimeInOut(osv.osv):
    _name = "old.time"
    _columns = {
        'date': fields.date('Date', store=True),
        'name': fields.char('Name', store=True),
        'cs': fields.char('CS Number', store=True),
        'timein': fields.char('TimeIn', store=True),
        'timeout': fields.char('TimeOut', store=True),
        'status1': fields.char('Status1', store=True),
        'status2': fields.char('Status2', store=True),
        'bas': fields.char('BAS', store=True),
        'branch': fields.char('Branch', store=True),
    }


class basicPackage(osv.osv):
    _name = "basic.package"
    _rec_name = 'bank'
    _columns = {
        'bank': fields.many2one('res.partner','Bank', store=True ,domain=[('is_company','=',True),('is_branch','=',False)]),
        'product_lines': fields.one2many('basic.package.items', 'product_basic_package_line', 'Items', store=True)
    }


class basicPackageItems(osv.osv):
    _name = "basic.package.items"
    _rec_name = 'products'
    _columns = {
        'product_basic_package_line': fields.many2one('basic.package', 'Product Line', store=True),
        'courier_sheet_product_line': fields.many2one('courier.sheet', 'Product Line', store=True),
        'products': fields.many2one('product.template', 'Products', store=True),
        'courier_sheet_products': fields.many2one('product.items', 'Products', store=True),
        'faulty_sheet_products': fields.many2one('faulty.devices', 'Products', store=True),
        'stock_return_products': fields.many2one('stock.return', 'Products', store=True),
        'quantity': fields.float('Quantity',store=True),
        'req_slip': fields.many2one('mutual.requisition','Requisition Slip',store=True),
        'req_code': fields.related('req_slip', 'req_code', type='char', string='Req. Ref', readonly=True),
        'issue_product_details': fields.related('req_slip', 'title', type='char', string='Issue Product Details', readonly=True),
        'date': fields.related('req_slip', 'date', type='date', string='Issue Product Details',readonly=True),
        'stock_sheet_date': fields.related('stock_return_products', 'date', type='date', string='Date', readonly=True),
        'product_type': fields.selection([('New', 'New'), ('Used', 'Used'),
                                  ('Faulty', 'Faulty')], 'Type', default='New', store=True),
        'type': fields.selection([('For Technician', 'For Technician'), ('For Customer', 'For Customer'),('Handover To Warehouse', 'Handover To Warehouse')], 'Type',
                                 store=True),
        'customer': fields.many2one('res.partner', 'Customer/Technician', store=True, required=True),
        'ref_to': fields.char('Reference', store=True),
        'location':fields.char('Location',store=True),
        'cs_number': fields.char('CS Number', store=True),
        'branch_code': fields.char('Branch Code', store=True),
        'status': fields.selection([('Available', 'Available'), ('Unavailable', 'Unavailable')], 'Status',
                                 store=True),
        'req_ref': fields.char('Req. #', store=True),
    }

    _defaults = {
        'status': 'Available'
    }

    @api.one
    @api.onchange('customer')
    def cal_cs_bc(self):
        if self.customer.customer==True:
            self.location = self.customer.city
            self.cs_number = self.customer.cs_number
            self.branch_code = self.customer.branch_code
        else:
            self.location = self.customer.city

class couriersheet(osv.osv):
    _name = "courier.sheet"
    _rec_name = "partner_id"
    _columns = {
        'technician_name': fields.many2one('hr.employee', 'Technician Name',select=1,
                                           track_visibility='onchange', domain="[('department_id','=','Technician')]",
                                           defaults=''),
        'partner_id': fields.many2one('res.partner', 'Customer', required=True),
        'cs_number': fields.related('partner_id', 'cs_number', type='char',string='CS Number',readonly=True),
        'city': fields.related('partner_id', 'city', type='char', string='City', readonly=True),
        'branch_code': fields.related('partner_id', 'branch_code', type='char', string='Branch Code',readonly=True),
        'bank_code': fields.related('partner_id', 'bank_code', type='char',string='Bank Code', readonly=True),
        'monitoring_address': fields.related('partner_id', 'street', type='char', string='Bank address', readonly=True),
        'date': fields.date('Date', store=True, required=True),
        'complaint_reference': fields.integer('Complaint/Task Reference', store=True),
        'tcs_receipt': fields.char('TCS Receipt No.', store=True, size=30),
        'remarks': fields.text('Tcs Delivery Status', store=True),
        'devices': fields.char('Devices',store=True, defaults=' ', compute='devices_details'),
        'qty': fields.char('Qty', store=True, compute='devices_details'),
        'product_lines': fields.one2many('basic.package.items', 'courier_sheet_product_line', 'Items', store=True),
        'state': fields.selection([('draft','Draft'),('confirmed','Confirmed')],'State',store=True,default='draft',track_visibility='onchange'),
        'ref':fields.char('Ref',store=True,compute='devices_details'),
        'location':fields.related('technician_name','work_location',type='char',string='Technician Work Address',readonly=True)
    }

    _defaults = {
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
    }

    @api.depends('product_lines.courier_sheet_products','product_lines.quantity')
    def devices_details(self):
        for line in self.product_lines:
            self.devices = str(self.devices) + line.courier_sheet_products.name + ","
            self.devices=self.devices.replace('False',' ')
            self.qty = str(self.qty)+ str(line.quantity) + ","
            self.qty = self.qty.replace('False', ' ')
            self.ref=str(self.ref)+str(line.ref_to)+","
            self.ref=self.ref.replace('False',' ')

    @api.multi
    def validate(self):
        return self.write({'state': 'confirmed'})

    @api.multi
    def cancel(self):
        return self.write({'state': 'draft'})

    @api.one
    @api.onchange('complaint_reference')
    def auto_select(self, context=None):
        if self.complaint_reference:
            self.env.cr.execute(
                'select id from res_partner where id = any(select partner_id from project_issue where id =' + str(self.complaint_reference) + ')')
            customer = self.env.cr.dictfetchall()
            list = self.env['res.partner'].search([['id', '=', customer[0]['id']], ])
            self.partner_id = list


class productitems(osv.osv):
    _name = "product.items"
    _rec_name = "name"
    _columns = {
        'name': fields.char('Name', store=True, size=30),
        'product_lines': fields.one2many('product.items.line', 'name', 'Items', store=True),
    }


class productitemsline(osv.osv):
    _name = "product.items.line"
    _columns = {
        'name': fields.many2one('product.items', 'Product', type='char', store=True),
        'products': fields.many2one('product.template', 'Products', store=True),
        'quantity': fields.float('Quantity', store=True),
    }

class faultyDevices(osv.osv):
    _name = "faulty.devices"
    _rec_name = "partner_id"
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer', required=True),
        'cs_number': fields.related('partner_id', 'cs_number', type='char', string='CS Number', readonly=True),
        'city': fields.related('partner_id', 'city', type='char', string='City', readonly=True),
        'branch_code': fields.related('partner_id', 'branch_code', type='char', string='Branch Code',readonly=True),
        'bank_code': fields.related('partner_id', 'bank_code', type='char',string='Bank Code', readonly=True),
        'monitoring_address': fields.related('partner_id', 'street', type='char', string='Bank address', readonly=True),
        'date': fields.date('Date', store=True, required=True),
        'status': fields.char('Status', store=True),
        'devices_received': fields.char('New Devices Received',store=True),
        'devices_received_qty': fields.char('New Devices Quantity', store=True),
        'product_lines': fields.one2many('basic.package.items', 'faulty_sheet_products', 'Items', store=True),
        'devices': fields.char('Faulty Devices Received', store=True, compute='devices_details'),
        'qty': fields.char('Qty', store=True, compute='devices_details'),
    }

    _defaults = {
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
    }

    @api.depends('product_lines.products', 'product_lines.quantity')
    def devices_details(self):
        print ">>>>>>>>>>>>>>>>>>>>>>>SingleTOn>>>>>>>>>>>>."
        for line in self.product_lines:
            print ">>>>>>>>>>>>for singlton>>>>>>>>>>>>>>>>>"
            self.devices = str(self.devices) + line.products.name + ","
            self.devices = self.devices.replace('False', ' ')
            self.qty = str(self.qty) + str(line.quantity) + ","
            self.qty = self.qty.replace('False', ' ')

class stockreturn(osv.osv):
    _name='stock.return'
    _rec_name = "title"
    _columns = {
        'title': fields.char('Title', store=True, required=True),
        'date': fields.date('Date', store=True, required=True),
        'req_slip_ref': fields.char('Requisition slip Reference', store=True, required=True, compute='devices_details'),
        'products': fields.one2many('basic.package.items', 'stock_return_products', 'Items', store=True),
        'devices': fields.char('Devices', compute='devices_details'),
        'qty': fields.char('Qty', store=True, compute='devices_details'),
        'ref_cs': fields.char('sales order reference', store=True),
        'ref': fields.char('Ref', store=True, defaults=' ', compute='devices_details', readonly=True, size=15),
        'ref_two': fields.char('Ref', defaults=' ', compute='devices_details', readonly=True, )
    }

    _defaults = {
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
    }

    # get cummulative data of products in req slip
    def cumm_product_new_data(self):
        cumm_prod, data = [], {}
        for line in self.products:
            if line.product_type == 'New':
                if not any(d['name'] == line.products.name for d in cumm_prod) or not any(cumm_prod):
                    data = {
                        'name': line.products.name,
                        'quantity': line.quantity,
                    }
                    cumm_prod.append(data)
                else:
                    for item in cumm_prod:
                        if item['name'] == line.products.name:
                            item['quantity'] += line.quantity
        return cumm_prod

    def cumm_product_used_data(self):
        cumm_prod, data = [], {}
        for line in self.products:
            if line.product_type == 'Used':
                if not any(d['name'] == line.products.name for d in cumm_prod) or not any(cumm_prod):
                    data = {
                        'name': line.products.name,
                        'quantity': line.quantity,
                    }
                    cumm_prod.append(data)
                else:
                    for item in cumm_prod:
                        if item['name'] == line.products.name:
                            item['quantity'] += line.quantity
        return cumm_prod

    def cumm_product_faulty_data(self):
        cumm_prod, data = [], {}
        for line in self.products:
            if line.product_type == 'Faulty':
                if not any(d['name'] == line.products.name for d in cumm_prod) or not any(cumm_prod):
                    data = {
                        'name': line.products.name,
                        'quantity': line.quantity,
                    }
                    cumm_prod.append(data)
                else:
                    for item in cumm_prod:
                        if item['name'] == line.products.name:
                            item['quantity'] += line.quantity
        return cumm_prod

    @api.one
    @api.depends('products.products', 'products.quantity','products.customer', 'products.cs_number')
    def devices_details(self):
        all_cus = ''
        for line in self.products:
            if str(self.req_slip_ref).find(line.req_ref) == -1:
                self.req_slip_ref = str(self.req_slip_ref) + str(line.req_ref) + ","
                self.req_slip_ref = self.req_slip_ref.replace('False', ' ')
            self.devices = str(self.devices) + str(line.courier_sheet_products.name) + ","
            self.devices = self.devices.replace('False', ' ')
            self.qty = str(self.qty) + str(line.quantity) + ","
            self.qty = self.qty.replace('False', ' ')
            # self.ref = str(self.ref) + str(line.cs_number) + ","
            # self.ref = self.ref.replace('False', ' ')
            self.ref_two = str(self.ref_two) + str(line.cs_number) + ","
            self.ref_two = self.ref_two.replace('False', ' ')
            all_cus = str(all_cus) + str(line.customer.name) + ","
            all_cus = all_cus.replace('False', ' ')
        self.ref = all_cus[:-1]
        all_cus = ''
        self.env.cr.execute("select id from mutual_requisition where ref_two is null")
        emp_ref_two = self.env.cr.dictfetchall()
        if len(emp_ref_two) > 0:
            self.append_ref_two(emp_ref_two)

    def append_ref_two(self, lst):
        if len(lst) > 0:
            cumm_prods = ''
            for item in lst:
                self.env.cr.execute("""select * from basic_package_items where req_slip=""" + str(item['id']))
                itemlst = self.env.cr.dictfetchall()
                for line in itemlst:
                    cumm_prods += str(line['cs_number'])
                # self.env.cr.execute(
                #     "update mutual_requisition set ref_two= '" + cumm_prods[:-1] + "' where id=" + str(item['id']))
                # cumm_prods = ''

            # self.devices = str(self.devices) + line.products.name + ","
            # self.devices = self.devices.replace('False', ' ')
            # self.qty = str(self.qty) + str(line.quantity) + ","
            # self.qty = self.qty.replace('False', ' ')
            # self.ref_cs = str(self.ref_cs) + str(line.ref_to) + ","
            # self.ref_cs = self.ref_cs.replace('False', ' ')

class mark_attendance(osv.osv):
    _name = 'mark.attendance'
    _columns = {
        'employee_id': fields.many2one('hr.employee','Name',store=True,readonly=True),
        'check_in': fields.datetime('Check In', store=True),
        'check_in_view': fields.datetime('Time In', store=True),
        'status': fields.selection([('Present','Present'),('Absent','Absent')], string='Status',store=True),
    }


class sms_report(osv.osv):
    _name = 'sms.report'
    _columns = {
        'date': fields.datetime('Date', store=True,default=datetime.today()),
        'sms': fields.text('SMS', store=True),
        'to': fields.char('To', store=True),
        'status': fields.char('Status', store=True),
        'type':fields.char('Type', store=True)
    }


class attendance_logs(osv.osv):
    _name = 'attendance.logs'
    _columns = {
        'text': fields.char('Text', store=True),
        'contact': fields.char('Contact', store=True),
        'date_': fields.char('Date', store=True),
        'time_': fields.char('Time', store=True),
    }

    def cron_tech_attendance(self, cr, uid, context=None):
        mark_attendance = self.pool.get('mark.attendance')
        cr.execute('select id,name_related,work_phone from hr_employee where department_id=1 order by id asc')
        employees = cr.dictfetchall()
        for employee in employees:
            cr.execute("select * from attendance_logs where contact='"+str(employee['work_phone'])+ "'" +"and date_='"+str(datetime.now()).split(' ')[0]+"'"+ "limit 1")
            present_employee = cr.dictfetchall()
            if len(present_employee)>0:
                res = {
                    'employee_id': employee['id'],
                    'check_in': present_employee[0]['date_']+" "+present_employee[0]['time_'],
                    'check_in_view': datetime.strptime(str(present_employee[0]['date_'] + " " + present_employee[0]['time_']),"%Y-%m-%d %H:%M:%S")-timedelta(hours=5),
                    'status':'Present'
                }
                mark_attendance.create(cr, uid, res, context=None)
            else:
                res = {
                    'employee_id': employee['id'],
                    'status': 'Absent'
                }
                mark_attendance.create(cr, uid, res, context=context)
        print "Job done......................."
        return True




