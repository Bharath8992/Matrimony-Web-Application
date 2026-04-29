(function($) {
	"use strict";
	
	// Toolbar extra buttons
	var btnFinish = $('<button></button>').text('Finish')
		.addClass('btn btn-success')
		.on('click', function(){ alert('Finish Clicked'); });
	var btnCancel = $('<button></button>').text('Cancel')
		.addClass('btn btn-danger')
		.on('click', function(){ $('#smartwizard-3').smartWizard("reset"); });
			
	// Dots Smart Wizard 1
	$('#smartwizard-3').smartWizard({
			selected: 0,
			theme: 'dots',
			transitionEffect:'fade',
			showStepURLhash: false,
			toolbarSettings: {
							  toolbarExtraButtons: [btnFinish, btnCancel]
							}
	});
	
})(jQuery);