/* Copyright 2018 Tecnativa - David Vidal
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define("pos_lot_selection.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var PopupWidget = require("point_of_sale.popups");
    var gui = require('point_of_sale.gui');
    var session = require("web.session");
    var exports = {};


    models.PosModel = models.PosModel.extend({
        get_lot: function(product, location_id) {
            var done = new $.Deferred();
            session.rpc("/web/dataset/search_read", {
                "model": "stock.quant",
                "domain": [
                    ["location_id", "=", location_id],
                    ["product_id", "=", product],
                    ["lot_id", "!=", false]],
            }, {'async': false}).then(function (result) {
                var product_lot = [];
                if (result.length) {
                    for (var i = 0; i < result.length; i++) {
                        product_lot.push({
                            'lot_name': result.records[i].lot_id[1],
                            'qty': result.records[i].quantity,
                            'date': result.records[i].removal_date,
                        });
                    }
                }
                done.resolve(product_lot);
            });
            return done;
        },
    });

    var _orderline_super = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options){
            this.lot_name = "";
            _orderline_super.initialize.apply(this, arguments);
        },
        set_lot_name: function (name) {
            this.lot_name = name;
        },
        get_lot_name: function () {
            return this.lot_name;
        },
        compute_lot_lines: function(){
            var pack_lot_lines = this.pack_lot_lines;
            var done = new $.Deferred();
            var compute_lot_lines = _orderline_super.compute_lot_lines.apply(this, arguments);
            this.pos.get_lot(this.product.id, this.pos.config.stock_location_id[0])
                .then(function (product_lot) {
                var lot_name = [];
                for (var i = 0; i < product_lot.length; i++) {
                    if (product_lot[i].qty >= pack_lot_lines.order_line.quantity) {
                        var date = new Date(product_lot[i].date);
                        date = date.getFullYear() +'-'+ date.getMonth()+'-'+ date.getDate();
//                        lot_name.push("Name: " + product_lot[i].lot_name + " " + " , Qty: " + product_lot[i].qty + "  " + " , Date: " + date );
                        lot_name.push("Name: " + product_lot[i].lot_name);
                    }
                }
                pack_lot_lines.lot_name = lot_name;
//                done.resolve(pack_lot_lines);
            });

        return this.pack_lot_lines;
        },

    });

var PackLotLinePopupWidget = PopupWidget.extend({
    template: 'PackLotLinePopupWidget',
    events: _.extend({}, PopupWidget.prototype.events, {
        'click .remove-lot': 'remove_lot',
        'keydown': 'add_lot',
        'blur .packlot-line-input': 'lose_input_focus'
    }),

    show: function(options){
        this._super(options);
        this.focus();
    },

    click_confirm: function(){
            var lot_name = ""
            var pack_lot_lines = this.options.pack_lot_lines;
            this.$('.packlot-line-input').each(function(index, el){
                var cid = $(el).attr('cid');
                lot_name = $(el).val();
                var pack_line = pack_lot_lines.get({cid: cid});
                pack_line.set_lot_name(lot_name);
            });
            pack_lot_lines.order_line.set_lot_name(lot_name);
            pack_lot_lines.remove_empty_model();
            pack_lot_lines.set_quantity_by_lot();
            this.options.order.save_to_db();
            this.options.order_line.trigger('change', this.options.order_line);
            this.gui.close_popup();
               
    },

    add_lot: function(ev) {
        if (ev.keyCode === $.ui.keyCode.ENTER && this.options.order_line.product.tracking == 'serial'){
            var pack_lot_lines = this.options.pack_lot_lines,
                $input = $(ev.target),
                cid = $input.attr('cid'),
                lot_name = $input.val();

            var lot_model = pack_lot_lines.get({cid: cid});
            lot_model.set_lot_name(lot_name);  // First set current model then add new one
            if(!pack_lot_lines.get_empty_model()){
                var new_lot_model = lot_model.add();
                this.focus_model = new_lot_model;
            }
            pack_lot_lines.set_quantity_by_lot();
            this.renderElement();
            this.focus();
        }
    },

    remove_lot: function(ev){
        var pack_lot_lines = this.options.pack_lot_lines,
            $input = $(ev.target).prev(),
            cid = $input.attr('cid');
        var lot_model = pack_lot_lines.get({cid: cid});
        lot_model.remove();
        pack_lot_lines.set_quantity_by_lot();
        this.renderElement();
    },

    lose_input_focus: function(ev){
        var $input = $(ev.target),
            cid = $input.attr('cid');
        var lot_model = this.options.pack_lot_lines.get({cid: cid});
        lot_model.set_lot_name($input.val());
    },

    focus: function(){
        this.$("input[autofocus]").focus();
        this.focus_model = false;   // after focus clear focus_model on widget
    }
});
gui.define_popup({name:'packlotline', widget:PackLotLinePopupWidget});


});
