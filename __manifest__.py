{
    "name": "sponsor_educative_credit",
    "license": "LGPL-3",
    "summary": """
        Crédito educativo Sponsor
    """,
    "author": "",
    "website": "",
    "category": "sponsor",
    "version": "16.0.0.1.0",
    "depends": ['base',
                'account',
                'l10n_pe',
                'contacts',
                'crm', 
                'crm_enterprise', 
                'sale',
                'sale_crm',
                'sale_management',
                'mail'],
    "data": [
        # Data
        "data/info_data.xml",
        
        #security
        "security/ir.model.access.csv",
        "security/cuota_security.xml",
        #views
        "views/spo_settings_view.xml",
        "views/spo_res_partner.xml",
        "views/spo_crem_leads.xml",
        "views/spo_sale_order_view.xml",
        "views/spo_res_config_settings.xml",
        "views/spo_product_attribute_value.xml",
        "views/mail_cuota_payment.xml",
        "views/spo_account_payment.xml",
        "views/cron.xml",
        "views/menu.xml",
        # Wizards
        "wizards/report_cuota_view.xml",
        # Reports
        "reports/report_cuota_template.xml",
    ],
    # 'pre_init_hook': 'pre_init_hook',
    'post_init_hook':'value_params',

    # only loaded in demonstration mode
    "assets": {
        "web.assets_backend": [
            # '/sponsor_educative_credit/static/src/scss/inherit_emterprise_theme.scss',
        ],
    },
}
