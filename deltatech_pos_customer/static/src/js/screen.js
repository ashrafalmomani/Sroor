odoo.define('deltatech_pos_customer.screens', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var models = require('point_of_sale.models');
var QWeb = core.qweb;
var _t = core._t;

models.load_fields('account.journal', ['credit_journal']);

screens.PaymentScreenWidget.include({

    order_is_valid: function(force_validation) {
        var self = this;
        var res = this._super(force_validation);
        var order = this.pos.get_order();
        var credit_journal = false;
        var lines = this.pos.get_order().get_paymentlines();

        for (var i = 0; i < lines.length; i++) {
            var journal = lines[i].cashregister.journal;
            if (journal.credit_journal == true){
                credit_journal = true;
            }
        }

        if (credit_journal) {
            if(!order.get_client()){
                 self.gui.show_popup('confirm',{
                        'title': _t('Please select the Customer'),
                        'body': _t('You need to select the customer for selected journal.'),
                        confirm: function(){
                            self.gui.show_screen('clientlist');
                        },
                    });
                return false;
            }
        }
        return res;
    },

});

});
