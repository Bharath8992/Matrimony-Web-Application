$(function(e){
  'use strict'

   /*echart2*/
  var chartdata = [
    {
      name: 'Male',
      type: 'bar',
      data: [10, 15, 9, 18, 10, 15, 13, 14, 18, 17, 16, 14],
	  symbolSize:10,
	    itemStyle: {
			normal: { barBorderRadius: [100 ,100, 0 ,0],
			}
		},
    },
    {
      name: 'Female',
      type: 'bar',
      data: [10, 14, 10, 15, 9, 25, 18, 17, 14, 12, 16, 13],
	  symbolSize:10,
	    itemStyle: {
			normal: { barBorderRadius: [100 ,100, 0 ,0],
			barBorderWidth:['2']
			}
		},
    }
  ];

  var chart = document.getElementById('echart1');
  var barChart = echarts.init(chart);

  var option = {
    grid: {
      top: '6',
      right: '0',
      bottom: '17',
      left: '25',
	  borderColor: 'rgba(119, 119, 142, 0.08)',
    },
    xAxis: {
      data: [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov','Dec' ],

      axisLine: {
        lineStyle: {
          color:'rgba(161, 161, 161,0.3)'
        }
      },
      axisLabel: {
        fontSize: 10,
        color: '#a1a1a1'
      }
    },
	tooltip: {
		show: true,
		showContent: true,
		alwaysShowContent: true,
		triggerOn: 'mousemove',
		trigger: 'axis',
		axisPointer:
		{
			label: {
				show: false,
			}
		}

	},
    yAxis: {
      splitLine: {
        lineStyle: {
          color: 'rgba(119, 119, 142, 0.08)'
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(119, 119, 142, 0.08)'
        }
      },
      axisLabel: {
        fontSize: 10,
        color: '#a1a1a1'
      }
    },
    series: chartdata,
    color:[ '#467fcf', '#5eba00',]
  };

  barChart.setOption(option);
  window.addEventListener('resize',function(){
    barChart.resize();
  })

  /*--echart-1---*/

  /*chart-donut*/
var options = {
    chart: {
        height: 280,
        type: "radialBar",
    },
	
    colors: ["#467fcf", "#5eba00"],

    plotOptions: {
        
        radialBar: {
            hollow: {
                size: "55%"
              },
            track: {
                background: "rgba(0, 0, 0, 0.05)",
                opacity: 0.5,
            },
            dataLabels: {
                name: {
                    fontSize: "14px",
                },
                value: {
                    fontSize: "16px",
                    color: "#0f4069",
                },
                total: {
                    show: !0,
                    label: "Total Visits",
                    color: "#0f4069",
                    formatter: function(e) {
                        return 249;
                    },
                },
            },
        },
    },

    stroke: {
        lineCap: "round",
    },
    series: [55, 78],
    labels: ["Cardiology", "Dermatology"],
    legend: {
        show: false,
        floating: true,
        fontSize: "13px",
        position: "left",
        offsetX: 0,
        offsetY: 1,
        labels: {
            useSeriesColors: true,
        },
        markers: {
            size: 1,
        },
    },
  };

var chart = new ApexCharts(document.querySelector("#visit-by-departments"), options);

chart.render();


});


 function index4() { 	
	var options = {
		chart: {
			height: 320,
			type: 'bar',
      toolbar: {
        show: false
      },
		},
		plotOptions: {
			bar: {
				horizontal: false,
				columnWidth: '45%',
        borderRadius: 2
			},
		},
		grid: {
			borderColor: 'rgba(119, 119, 142, 0.08)'
		},
		dataLabels: {
			enabled: false
		},
		stroke: {
			show: true,
			width: 2,
			colors: ['transparent']
		},
		legend: {
			tooltipHoverFormatter: function(val, opts) {
			return val + ' - ' + opts.w.globals.series[opts.seriesIndex][opts.dataPointIndex] + ''
			},
			fontSize: '12px',
			labels: {
				colors: '#74767c',
			},
			markers: {
				width: 7,
				height: 7,
				strokeWidth: 0,
				radius: 12,
				offsetX: 0,
				offsetY: 0
			},
		},
		series: [{
			name: 'In Patient',
			data: [44, 55, 57, 56, 61, 58, 63, 60, 66, 44, 55]
		}, {
			name: 'Out Patient',
			data: [76, 85, 101, 98, 87, 105, 91, 114, 94, 85, 101]
		}],
		colors: [myVarVal, '#5eba00'],
		xaxis: {
			categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
			axisBorder: {
				show: false,
				olor: 'rgba(119, 119, 142, 0.05)',
			},
			axisTicks: {
				show: false,
				olor: 'rgba(119, 119, 142, 0.05)',
			},
		},
		fill: {
			opacity: 1

		},
		tooltip: {
			y: {
				formatter: function (val) {
					return "$ " + val + " thousands"
				}
			}
		}
	}
	document.querySelector("#patient-visit").innerHTML= " ";
	var chart = new ApexCharts(document.querySelector("#patient-visit"), options);
	chart.render();
}

