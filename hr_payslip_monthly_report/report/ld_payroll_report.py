# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from collections import OrderedDict


class LdPayrollReportWiz(models.TransientModel):
    _name = _description = 'ld.payroll.report.wizard'

    emp_ids = fields.Many2many('hr.employee', string='Select Employees')
    all_employees = fields.Boolean('Generate Report For All Employees?')
    date_selected = fields.Boolean('Date Range?')
    from_date = fields.Date('From date')
    to_date = fields.Date('To date')

    @api.onchange('all_employees')
    def _onchange_all_employees(self):
        if self.all_employees:
            emp_ids = self.env['hr.employee'].search([]).mapped('id')
            emp_ids = [(4, emp_id) for emp_id in emp_ids]
            self.update({'emp_ids': emp_ids})
        else:
            self.update({'emp_ids': [(6, 0, [])]})

    @api.onchange('date_selected')
    def _onchange_date_selected(self):
        if self.date_selected:
            first_day_of_next_month = fields.Datetime.today().replace(day=1) + relativedelta(months=1)
            self.from_date = fields.Date.today().replace(day=1)
            self.to_date = first_day_of_next_month - timedelta(days=1)

    def action_generate_xlsx_report(self):
        if not self.emp_ids:
            raise ValidationError("AT LEAST ONE EMPLOYEE SHOULD BE SELECTED TO GENERATE THE REPORT.")
        return self.env.ref('hr_payslip_monthly_report.ld_payroll_report').report_action(self)


class LdPayrollReportXlsx(models.AbstractModel):
    _name = _description = 'report.hr_payslip_monthly_report.report_ld_payroll'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        emp_ids = wizard.emp_ids
        from_date = False if not wizard.from_date else str(wizard.from_date) + ' 00:00:00'
        to_date = False if not wizard.to_date else str(wizard.to_date) + ' 23:59:59'
        domain = [('employee_id', 'in', emp_ids.ids)]
        if wizard.date_selected:
            domain += [('date_from', '>=', from_date), ('date_to', '<=', to_date)]
        records = self.env['hr.payslip'].search(domain, order='create_date DESC')
        sheet = workbook.add_worksheet(f'Payroll Report')
        HEADER_STYLE = dict(bold=True, align='center', text_wrap=True, valign='center', border=2)
        DATA_ROW_STYLE = dict(align='center', text_wrap=True, valign='center')
        header_row_style = workbook.add_format(HEADER_STYLE)
        data_row_style = workbook.add_format(DATA_ROW_STYLE)
        sheet.freeze_panes(1, 0)
        sheet.set_column(0, 20, 15)
        header_map = OrderedDict(CODE={'col': 0, 'o_code': ''}, NAME={'col': 1, 'o_code': ''},
                                ONDA={'col': 2, 'o_code': ''}, PUBD={'col': 3, 'o_code': ''},
                                REGA={'col': 4, 'o_code': ''}, WEO={'col': 5, 'o_code': ''},
                                LEAD={'col': 6, 'o_code': ''}, MISSATTE={'col': 7, 'o_code': ''},
                                TOT_DAYS={'col': 8, 'o_code': ''}, Payable_days={'col': 9, 'o_code': ''},
                                BASIC={'col': 10, 'o_code': 'BASIC'}, HRA={'col': 11, 'o_code': 'HRA'},
                                CON={'col': 12, 'o_code': 'C'}, OTHER={'col': 13, 'o_code': 'Other'},
                                GROSS={'col': 14, 'o_code': 'GROSS'}, PF_DED={'col': 15, 'o_code': 'PF'},
                                PF_EXTRA={'col': 16, 'o_code': 'VPF'}, ESI={'col': 17, 'o_code': 'ESIC'},
                                PTAX_DED={'col': 18, 'o_code': 'PT'}, OTHERDED={'col': 19, 'o_code': 'OTD100'},
                                ADV_DED={'col': 20, 'o_code': 'LO'}, I_TAX={'col': 21, 'o_code': 'INT'},
                                TOT_DED={'col': 22, 'o_code': False}, NET_PAY={'col': 23, 'o_code': False},
                                PSID={'col': 24, 'o_code': ''})

        def get_col_from_map(db_cod):
            for k, v in header_map.items():
                if db_cod in v.values():
                    return v.get('col')

        row_header, row_data, col_count = 0, 1, 0

        for header_cell in header_map.keys():
            sheet.write(row_header, col_count, header_cell, header_row_style)
            col_count += 1
        row_header += 1

        for rec in records:
            sheet.write(row_header, 0, rec.employee_id.employee_id, data_row_style)
            sheet.write(row_header, 1, rec.employee_id.name, data_row_style)

            worked_days_line_ids = rec.worked_days_line_ids
            onda = worked_days_line_ids.filtered(lambda a: a.code == 'ONDA').number_of_days
            pubd = worked_days_line_ids.filtered(lambda a: a.code == 'PUBD').number_of_days
            rega = worked_days_line_ids.filtered(lambda a: a.code == 'REGA').number_of_days
            weo = worked_days_line_ids.filtered(lambda a: a.code == 'WEO').number_of_days
            leave = worked_days_line_ids.filtered(lambda a: a.code == 'LEAD').number_of_days
            absent = worked_days_line_ids.filtered(lambda a: a.code == 'MISSATTE').number_of_days
            sheet.write(row_header, 2, onda, data_row_style)
            sheet.write(row_header, 3, pubd, data_row_style)
            sheet.write(row_header, 4, rega, data_row_style)
            sheet.write(row_header, 5, weo, data_row_style)
            sheet.write(row_header, 6, leave, data_row_style)
            sheet.write(row_header, 7, absent, data_row_style)
            total_days = ((rec.date_to - rec.date_from).days) + 1
            worked_days = rec.line_ids[0].payable_days if rec.line_ids else 0
            sheet.write(row_header, 8, total_days, data_row_style)
            sheet.write(row_header, 9, worked_days, data_row_style)

            for line_id in rec.line_ids:
                db_code = line_id.code
                col_num = get_col_from_map(db_code)
                if col_num:
                    sheet.write(row_header, col_num, line_id.total, data_row_style)

            categ_id = self.env.ref('hr_payroll_community.DED')
            tot_ded = sum(rec.line_ids.filtered(lambda q: q.category_id == categ_id).mapped('total')) or 0
            sheet.write(row_header, 22, tot_ded, data_row_style)
            net_pay = sum(rec.line_ids.filtered(lambda q: q.code == 'NET').mapped('total')) or 0
            sheet.write(row_header, 23, net_pay, data_row_style)
            sheet.write(row_header, 24, rec.number, data_row_style)
            row_header += 1