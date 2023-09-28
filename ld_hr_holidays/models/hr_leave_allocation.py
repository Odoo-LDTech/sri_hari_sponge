# -*- coding: utf-8 -*-
import math
from odoo import api, models, fields
import datetime
from calendar import monthrange



class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    def compute_worked_days(self, emp_id):
        tod = datetime.datetime.today()
        start_date = tod.replace(day=1, minute=0, hour=0, second=0, month=3)
        tod2 = datetime.datetime.today().replace(month=start_date.month + 1, day=1)
        end_date = tod2 - datetime.timedelta(days=1)
        end_date = end_date.replace(minute=59, hour=23, second=59)
        att_ids = self.env['employee.attendance.report'].search([
            ('check_in', '>', start_date), ('check_out', '<', end_date),
            ('payroll_status', 'not in', ['abs', 'suspend']),
            ('employee_id', '=', emp_id)
        ])
        full_days_att_ids = att_ids.filtered(lambda q:q.payroll_status != 'halfday')
        half_days_att_ids = att_ids.filtered(lambda q:q.payroll_status == 'halfday')
        days = float(len(full_days_att_ids))
        for day_cnt in range(len(half_days_att_ids)):
            days += 0.5
        return days

    def auto_create_causal_leave_allocation(self):
        cusual_time_off = self.env['hr.leave.type'].search([('name','=','Causal Timeoff')],limit=1)
        if cusual_time_off:
            employee_allocation_type = []
            if cusual_time_off.employee_type_stages_probation:
                employee_allocation_type.append('probation')
            if cusual_time_off.employee_type_stages_regular:
                employee_allocation_type.append('regular')
            if cusual_time_off.employee_type_stages_notice_period:
                employee_allocation_type.append('notice_period')

            today = datetime.date.today()
            first = today.replace(day=1)
            last_month_data = first - datetime.timedelta(days=1)
            # print(last_month.strftime("%Y%m"))
            last_year = int(last_month_data.strftime("%Y"))
            last_month = int(last_month_data.strftime("%m"))

            if employee_allocation_type:
                employee_records = self.env['hr.employee'].search([('employee_stage','in',employee_allocation_type)])
            if not employee_allocation_type or not employee_records:
                employee_records = self.env['hr.employee'].search([ ])
            for emp in employee_records:
                present_employee_attendance = self.env['employee.attendance.report'].search([('employee_id', '=', emp.id),('payroll_status','in',['reg','od']),]).filtered(lambda
                                                                      a: a.today_date_atte.month == last_month and a.today_date_atte.year == last_year and a.today_date_atte.year ==  last_year and a.today_date_atte.month ==  last_month ).ids
                leave_payable_employee_attendance = self.env['employee.attendance.report'].search([('employee_id', '=', emp.id),('payroll_status','in',['leave'])]).filtered(lambda
                                                                      a: a.today_date_atte.month == last_month and a.today_date_atte.year == last_year and a.today_date_atte.year ==  last_year and a.today_date_atte.month ==  last_month ).ids
                holiday_employee_attendance = self.env['employee.attendance.report'].search(
                    [('employee_id', '=', emp.id), ('payroll_status', 'in', ['abs', 'holiday']), ]).filtered(lambda
                                                                                                                 a: a.today_date_atte.month == last_month and a.today_date_atte.year == last_year and a.today_date_atte.year == last_year and a.today_date_atte.month == last_month).ids
                abs_employee_attendance = self.env['employee.attendance.report'].search(
                    [('employee_id', '=', emp.id), ('payroll_status', 'in', ['abs']), ]).filtered(lambda
                                                                                                                 a: a.today_date_atte.month == last_month and a.today_date_atte.year == last_year and a.today_date_atte.year == last_year and a.today_date_atte.month == last_month).ids
                weekoff_employee_attendance = self.env['employee.attendance.report'].search(
                    [('employee_id', '=', emp.id), ('payroll_status', 'in', ['weekoff']), ]).filtered(lambda
                                                                                                      a: a.today_date_atte.month == last_month and a.today_date_atte.year == last_year and a.today_date_atte.year == last_year and a.today_date_atte.month == last_month).ids

                employee_half_attendance = self.env['employee.attendance.report'].search(
                    [('employee_id', '=', emp.id), ('payroll_status', 'in', ['halfday'])]).filtered(lambda
                                                                                                        a: a.today_date_atte.month == last_month and a.today_date_atte.year == last_year and a.today_date_atte.year == last_year and a.today_date_atte.month == last_month).ids
                total_present_days = (len(present_employee_attendance) + len(employee_half_attendance)/2)
                payable_days =  monthrange(last_year, last_month)[1] - len(holiday_employee_attendance) - len(weekoff_employee_attendance)
                # total_number_of_month = monthrange(last_year, last_month)
                # final_days = self.compute_worked_days(emp.id)

                if  total_present_days  and payable_days >1:
                    final_days = (2.5 / payable_days) * (total_present_days)
                    vals_pl = {
                        'name': 'Casual Leave Allocation',
                        'holiday_status_id': self.env.ref('ld_hr_holidays.holiday_status_causal_leave').id,
                        'holiday_type': 'employee',
                        'employee_id': emp.id,
                        'allocation_type': 'regular',
                        'number_of_days': round(final_days,2) ,
                    }
                    allocation_rec = self.env['hr.leave.allocation'].create(vals_pl)
                    allocation_rec.action_confirm()
                    allocation_rec.action_validate()
                # else :
                #     vals_pl = {
                #         'name': 'Casual Leave Allocation',
                #         'holiday_status_id': self.env.ref('ld_hr_holidays.holiday_status_causal_leave').id,
                #         'holiday_type': 'employee',
                #         'employee_id': emp.id,
                #         'allocation_type': 'regular',
                #         'number_of_days': 2.5,
                #     }
                #     allocation_rec = self.env['hr.leave.allocation'].create(vals_pl)
                #     allocation_rec.action_confirm()
                #     allocation_rec.action_validate()