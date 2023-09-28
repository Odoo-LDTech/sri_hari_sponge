# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from datetime import datetime, timedelta


class BiometricApi(http.Controller):

    @staticmethod
    def convert_ist_to_utc(ts):
        if not ts:
            return False
        datetime_object = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5, minutes=30)
        return datetime_object.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def hr_attendance_vals(data):
        employee_id = request.env['hr.employee'].sudo().search([('employee_id','=',data.get('UserID'))])
        punch_in_utc = BiometricApi.convert_ist_to_utc(data.get('punch_in'))
        punch_out_utc = BiometricApi.convert_ist_to_utc(data.get('punch_out'))
        return dict(employee_id=employee_id.id or False,
                    check_in=punch_in_utc, check_out=punch_out_utc) if employee_id else False

    @http.route('/create/attendance', methods=['POST'], type='json', auth='public')
    def biometric_create_attendance(self, **kwargs):
        data = request.get_json_data()
        response = dict(status='fail')
        for data_dict in data.get('json'):
            att_obj = BiometricApi.hr_attendance_vals(data_dict)
            if att_obj:
                att_id = request.env['hr.attendance'].sudo().create(att_obj)
                response.update(status='success', record_id=att_id.id)
        return response
