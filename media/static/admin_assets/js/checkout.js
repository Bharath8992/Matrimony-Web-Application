
$(function () {
    'use strict'
    
    //Warning Message
	$('#palce-order').click(function () {
		$('body').removeClass('timer-alert');
		swal({
		  title: "Are you sure?",
		  text: "Your will not be able to recover order details!",
		  type: "warning",
		  showCancelButton: true,
		  confirmButtonClass: "btn btn-danger",
		  confirmButtonText: "Yes, conform!",
		  closeOnConfirm: false,
		},
		function(){
		  swal("Congratulations!", "Your order is placed.", "success");
		});
	});
});