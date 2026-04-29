$(function (e) {
	// datatable
	$("#data-table2").DataTable({
		language: {
		  searchPlaceholder: "Search...",
		  sSearch: "",
		},
	});
	
	//______Select2
	$(".select2").select2({
	  minimumResultsForSearch: Infinity,
	  width: '60px'
	});
  });
  

function index2() {
	//Chart12
	var options = {
		series: [{
		  name: "Updates",
		  data: [45, 52, 38, 24, 33, 26, 21, 20, 6, 8, 15, 10]
		},
		{
		  name: "Revenue",
		  data: [35, 41, 62, 42, 13, 18, 29, 37, 36, 51, 32, 35]
		},
		{
		  name: 'Users',
		  data: [87, 57, 74, 99, 75, 38, 62, 47, 82, 56, 45, 47]
		}
	  ],
		chart: {
		height: 310,
		type: 'line',
		zoom: {
		  enabled: false
		},
		toolbar: {
			show: false,
		}
	  },
	  dataLabels: {
		enabled: false
	  },
	  stroke: {
		width: [2, 2, 2],
		curve: 'smooth',
		dashArray: [0, 8, 5]
	  },
	  legend: {
		tooltipHoverFormatter: function(val, opts) {
		  return val + ' - ' + opts.w.globals.series[opts.seriesIndex][opts.dataPointIndex] + ''
		}
	  },
	  markers: {
		size: 0,
		hover: {
		  sizeOffset: 6
		}
	  },
	  colors: [myVarVal, '#5eba00', '#ffc107'],
	  xaxis: {
		categories: ['01 Jan', '02 Feb', '03 Mar', '04 Apr', '05 May', '06 Jun', '07 Jul', '08 Aug', '09 Sep',
		  '10 Oct', '11 Nov', '12 Dec'
		],
		axisBorder: {
			show: true,
			color: 'rgba(119, 119, 142, 0.05)',
		},
		axisTicks: {
			show: true,
			color: 'rgba(119, 119, 142, 0.05)',
		}
	  },
	  grid: {
		borderColor: 'rgba(119, 119, 142, 0.1)'
	  }
	};
	
	document.querySelector("#chart12").innerHTML= " ";
	var chart = new ApexCharts(document.querySelector("#chart12"), options);
	chart.render();
}

/**---- VectorMap ----**/

! function($) {
	"use strict";

	var VectorMap = function() {
	};

	VectorMap.prototype.init = function() {
		//various examples
		$('#world-map-markers').vectorMap({
			map : 'world_mill_en',
			scaleColors : ['#467fcf', '#5eba00'],
			normalizeFunction : 'polynomial',
			hoverOpacity : 0.7,
			hoverColor : false,
			regionStyle : {
				initial : {
					fill : '#f4f5f7',
					'stroke': '#fff',
                    'stroke-width' : 1,
                    'stroke-opacity': 1
				},
				hover: {
					'fill': 'rgb(70, 127, 207, 0.3)',
                    'stroke': '#467fcf',
					'stroke-opacity': 0.5
                }
			},
			 markerStyle: {
                initial: {
                    r: 6,
                    'fill': '#467fcf',
                    'fill-opacity': 0.7,
                    'stroke': '#edf0f5',
                    'stroke-width' : 9,
                    'stroke-opacity': 0.2
                },

                hover: {
                    'stroke': '#fff',
                    'fill-opacity': 0.8,
                    'stroke-width': 1.5
                }
            },
			backgroundColor : 'transparent',
			markers : [{
				latLng : [41.90, 12.45],
				name : 'Vatican City'
			}, {
				latLng : [43.73, 7.41],
				name : 'Monaco'
			},{
				latLng : [43.93, 12.46],
				name : 'San Marino'
			}, {
				latLng : [47.14, 9.52],
				name : 'Liechtenstein'
			},{
				latLng : [17.3, -62.73],
				name : 'Saint Kitts and Nevis'
			}, {
				latLng : [3.2, 73.22],
				name : 'Maldives'
			}, {
				latLng : [35.88, 14.5],
				name : 'Malta'
			}, {
				latLng : [12.05, -61.75],
				name : 'Grenada'
			}, {
				latLng : [13.16, -61.23],
				name : 'Saint Vincent and the Grenadines'
			}, {
				latLng : [13.16, -59.55],
				name : 'Barbados'
			}, {
				latLng : [17.11, -61.85],
				name : 'Antigua and Barbuda'
			}, {
				latLng : [-4.61, 55.45],
				name : 'Seychelles'
			}, {
				latLng : [7.35, 134.46],
				name : 'Palau'
			}, {
				latLng : [42.5, 1.51],
				name : 'Andorra'
			}, {
				latLng : [14.01, -60.98],
				name : 'Saint Lucia'
			},{
				latLng : [1.3, 103.8],
				name : 'Singapore'
			},{
				latLng : [-20.2, 57.5],
				name : 'Mauritius'
			}, {
				latLng : [26.02, 50.55],
				name : 'Bahrain'
			}, {
				latLng : [0.33, 6.73],
				name : 'São Tomé and Príncipe'
			}]
		});

	},
	//init
	$.VectorMap = new VectorMap, $.VectorMap.Constructor =
	VectorMap
}(window.jQuery),

//initializing
function($) {
	"use strict";
	$.VectorMap.init()
}(window.jQuery);
