#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv
from openerp import api
from datetime import date,datetime
import requests
import random

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
      'system_status':fields.char('System Status',store=True),
      'stage_id': fields.many2one('project.task.type', 'Stage', track_visibility='onchange', select=True, on_change='_change_stage()'),
      'complaint_status':fields.char('Complaint Status',store=True),
      'sale_order_issue': fields.many2one('sale.order', 'Sale Order', store=True),
      'contact': fields.related('user_id', 'mobile', type='char', size=12, string='Contact', readonly=True),
      'bm_number_issue': fields.related('partner_id', 'office', type='char', size=12, string='bm_number_issue',readonly=True),
      'om_number_issue': fields.related('partner_id', 'phone', type='char', size=12, string='om_number_issue',readonly=True),
      'sms': fields.text('SMS', store=True),
      'techContact': fields.char('Contact', store=True, size=11),
      'cs_number_issue': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
      'city_issue': fields.related('partner_id', 'city', type='char', size=12, string='City',readonly=True),
      'branch_code_issue': fields.related('partner_id', 'branch_code', type='char', size=12, string='Branch Code',readonly=True),
      'bank_code_issue': fields.related('partner_id', 'bank_code', type='char', size=12, string='Bank Code', readonly=True),
      'monitoring_address_issue': fields.related('partner_id', 'street', type='char', string='Bank address', readonly=True),
      'remark_by_cms': fields.text('Remarks By CMS',store=True),
      'complaint_source':fields.selection([("Complaint generated by LSR", "Complaint generated by LSR"),("By Email","By Email"),("By CMS","By CMS"),("Direct","Direct")],'Complaint Source'),
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
      'name': fields.selection([("PANIC BUTTON DAMAGED","PANIC BUTTON DAMAGED"),
                                ("PCB KIT FAULTY","PCB KIT FAULTY"),
                                ("SIM BLOCKED/OUTGOING SERVICE ISSUE","SIM BLOCKED/OUTGOING SERVICE ISSUE"),
                                ("SIM BALANCE PROBLEM","SIM BALANCE PROBLEM"),
                                ("SYSTEM BRIEFING REQUIRED"	,"SYSTEM BRIEFING REQUIRED"),
                                ("HEAVY METAL PROBLEM","HEAVY METAL PROBLEM"),
                                ("RE-INSTALLATION OF SYSTEM/DEVICES","RE-INSTALLATION OF SYSTEM/DEVICES"),
                                ("KEYPAD DEAD	","KEYPAD DEAD"),
                                ("BREFING REQUIRED",	"BREFING REQUIRED"),
                                ("gsm balance issue","gsm balance issue"),
                                ("SIGNAL ISSUE	","SIGNAL ISSUE"),
                                ("BUGLARY ALARM PROBLEM", "BUGLARY ALARM PROBLEM"),
                                ("Panic Button Wiring Problem", "Panic Button Wiring Problem"),
                                ("ZONE 7", "ZONE 7"),
                                ("NO RESPONSE	","NO RESPONSE"),
                                ("SIM BLOCKED	","SIM BLOCKED"),
                                ("user code provide","user code provide	"),
                                ("DEVICES RE-INSTALL",	"DEVICES RE-INSTALL"),
                                ("BRANCH  CLOSED","BRANCH  CLOSED	"),
                                ("GSM INSTALL	","GSM INSTALL	"),
                                ("SYSTEM BEEPING","SYSTEM BEEPING"	),
                                ("REMOTE PANIC PROBLEM","REMOTE PANIC PROBLEM	"),
                                ("Zone 7 Problem","Zone 7 Problem"),
                                ("PANIC BUTTON INSTALL","PANIC BUTTON INSTALL"),
                                ("hooter install","hooter install"),
                                ("TECHNICIAN REQUIRED","TECHNICIAN REQUIRED"),
                                ("SMOKE DECTECTOR PROBLEM","SMOKE DECTECTOR PROBLEM"),
                                ("SMOOK DETECTOR INSTAL","SMOOK DETECTOR INSTAL"),
                                ("PENAL LOCATION CHANGE","PENAL LOCATION CHANGE"),
                                ("SYSTEM HANG","SYSTEM HANG"),
                                ("BRANCH SHIFT","BRANCH SHIFT"),
                                ("Ptcl Connect"	,"Ptcl Connect"),
                                ("Panic Not Working","Panic Not Working"),
                                ("SD Not Working","SD Not Working"),
                                ("Zone 8 Problem","Zone 8 Problem"),
                                ("Cancel","Cancel"),
                                ("DEVICES INSTALL","DEVICES INSTALL"	),
                                ("Programming Error Urgent Check","Programming Error Urgent Check"	),
                                ("SIM Install In GSM","SIM Install In GSM"),
                                ("All Panic not working"	,"All Panic not working"	),
                                ("Ptcl Change","	Ptcl Change"),
                                ("temper problem","temper problem"),
                                ("Guard less Activation"	,"Guard less Activation"	),
                                ("Most Urgent Complain","Most Urgent Complain"),
                                ("ADDITONAL WORK IN PENDING","ADDITONAL WORK IN PENDING"),
                                ("BENTAL PROBLEM","BENTAL PROBLEM"),
                                ("GSM CONNECT","GSM CONNECT"),
                                ("GSM FAULTY","GSM FAULTY"),
                                ("GSM POWER PROBLEM","GSM POWER PROBLEM")
                                ],
                               'Complaint Title', required=True, read=['__export__.res_groups_52'], write=['project.group_project_user']),
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
      'courtesy':fields.text('Courtesy Remarks', store=True),
      'clientname': fields.char('Client Name', store=True,size=30)
  }

  # @api.one
  # @api.depends('date_start')
  # @api.onchange('date_start')
  # def _change_stage(self):
  #     self.sms = self.stage_id

  @api.one
  @api.depends('stage_id')
  @api.onchange('stage_id')
  def _change_stage(self):
      self.complaint_status = 'New'
      self.complaint_status = self.stage_id

  @api.multi
  def details(self):
      self.techContact = self.contact
      self.sms = self.name+"\n"+\
                 self.cs_number_issue+"\n"+self.branch_code_issue+"\n"+self.bank_code_issue+"\n"+self.monitoring_address_issue+"\n"+self.city_issue;
      return {
        'warning': {
            'title': "Something bad happened",
            'message': "It was very bad indeed",
        }
      }

  @api.multi
  def smsSent(self):
      r = requests.post("http://localhost:3000", data={'sms':self.sms,'contact':self.techContact})
      return {
        'warning': {
            'title': "Something bad happened",
            'message': "It was very bad indeed",
        }
      }

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
        'technician_name': fields.many2one('hr.employee', 'Technician Name', required=False, select=1, track_visibility='onchange', domain="[('department_id','=','Technician')]", defaults=''),
        'reason': fields.char('Final Status',size=100,store=True),
        'systemstatus': fields.char('System Status', size=100, store=True),
        'total_time': fields.float('Total Time', store=True),
        'date': fields.date('Date',store=True),
        'compute_total_time': fields.char('T/T', store=True, readonly=True, compute='_compute_total_time', ),
        'first_signal': fields.datetime('F/T', select=True, copy=True, write=['project.group_project_manager'],
                                        read=['project.group_project_user']),
        'date_start': fields.datetime('T/I', select=True, copy=True, write=['project.group_project_manager'],
                                      read=['project.group_project_user']),
        'date_end': fields.datetime('T/O', select=True, copy=True, write=['project.group_project_manager'],
                                    read=['project.group_project_user']),
        'cs_number': fields.related('tech_name', 'cs_number_issue', type='char', string='CS Number'),
        #'stage_id': fields.related('tech_name','stage_id',type='many2one',relation='project.issue',string='Stage_id'),
        'issue_id': fields.related('tech_name', 'id', type='char', string='Complaint ID'),
        'branch_code': fields.related('tech_name', 'branch_code_issue', type='char', string='Branch Code'),
        'multi_tech': fields.many2many('hr.employee', string='Other Tech', domain="[('department_id','=','Technician')]"),

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


class tech_activities_tasks(osv.osv):
    _name = "tech.activities.tasks"
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


