$(document).ready(function (e) {
    $("#btn_update_bid").click(function (e) {
        $.ajax({
            url: "/rfq/update",
            data: { order_id: $("#order_id").val() },
            type: "post",
            cache: false,
            success: function (result) {
                $("#update_message").show();
                $("#error_message").show();
            },
        });
    });
    $("#btn_cancel_new_bid").click(function (e) {
		$('.cancel_bid').modal('show');
    });
	$(".btn_cancel_bid_new_modal").click(function (e) {
		$.ajax({
            url: "/rfq/cancel/new",
            data: { order_id: $('#order_id').val() },
            type: "post",
            cache: false,
            success: function (result) {
                var datas = JSON.parse(result);
                if (datas.url) {
                    window.location.href = datas.url;
                }
            },
        });
	});
});
