jQuery(function() {
	$('.select2').select2({
		placeholder: 'Choose one',
		searchInputPlaceholder: 'Search',
        minimumResultsForSearch: Infinity,
		width: '100%'
	});

});

flatpickr("#date", {});