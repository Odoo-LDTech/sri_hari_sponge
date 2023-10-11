{
    "name": "Employee attendance geo location tracker",
    "author": "Livedigital Technologies Private Limited",
    'website': "ldtech.in",
    "version": "15.0.1.0",
    "images": ["static/description/main_screenshot.png"],
    'summary': 'Employee Check In/Check Out Location Tracker with Google Map',
    "description": """
    This module will helps to track the check in / check out location of employees.
    This module store the location as well facilitates to search that location on Google Map.
    """,
    "license": "OPL-1",
    "depends": ['base', 'web', 'hr', 'hr_attendance'],
    "data": [
        'security/ir.model.access.csv',
        'views/employee_map_attendance_view.xml',
    ],
    'external_dependencies': {
        'python': ['googlegeocoder', 'googlemaps', 'geopy'],
    },
    'demo': [],
    "assets": {
        "web.assets_backend": [
            "ld_emp_attendance_location_track/static/src/css/gmaps.css",
            "ld_emp_attendance_location_track/static/src/js/my_attendances_extend.js",
            "ld_emp_attendance_location_track/static/src/js/gmaps.js",
        ],
        "web.assets_qweb": [
            "ld_emp_attendance_location_track/static/src/xml/my_attendances_extend_template.xml",
        ],
    },
    "auto_install": False,
    "installable": True,
    "category": "Website",
    "price": 100,
    "currency": 'USD',
}