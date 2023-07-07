odoo.define("sh_all_in_one_tender_bundle.add_bid", function (require) {
    "use strict";
    require("web.dom_ready");
    var concurrency = require("web.concurrency");
    var core = require("web.core");
    var publicWidget = require("web.public.widget");
    publicWidget.registry.sh_po_tender_portal = publicWidget.Widget.extend({
    	selector:"#tender_content,#tender_tr",
    	events: {
            'click #btn_add_bid_form': '_onClickAddBid',
            'click .btn_add_bid': '_onClickAddBidList',
        },
        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },
        /*Click method of add/update bid and create new rfq*/
        _onClickAddBid: function (ev) {
        	ev.preventDefault();
        	var self = this;
        	return this._rpc({
                route: "/rfq/create",
                params: {tender_id: ev.target.dataset.id},
            }).then((data) => {
                _.each(data, function (record) {
                    window.location.href = record;
                });
            });
        },
        /*Click method of add/update bid and create new rfq(tender portal list view)*/
        _onClickAddBidList: function (ev) {
        	ev.preventDefault();
        	var self = this;
        	var $el = $(ev.target).parents("tr").find("#tender_id").attr("tender_id");
        	var tender_id = parseInt($el);
        	return this._rpc({
                route: "/rfq/create",
                params: {tender_id: tender_id},
            }).then((data) => {
                _.each(data, function (record) {
                    window.location.href = record;
                });
            });
        },
    });
});

