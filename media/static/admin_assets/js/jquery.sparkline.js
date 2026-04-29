(function($) {
    "use strict";

    // sparkline1
    $(".sparkline_bar").sparkline([2, 4, 3, 4, 5, 4, 5, 4, 3, 4], {
        height: 20,
        type: 'bar',
        colorMap: {
            '7': '#a1a1a1'
        },
        barColor: '#ff5b51'
    });

    // sparkline2
    $(".sparkline_bar1").sparkline([3, 4, 3, 4, 5, 4, 5, 6, 4, 6, ], {
        height: 20,
        type: 'bar',
        colorMap: {
            '7': '#c34444'
        },
        barColor: '#44c386'
    });

    // sparkline3
    $(".sparkline_bar2").sparkline([3, 4, 3, 4, 5, 4, 5, 6, 4, 6, ], {
        height: 20,
        type: 'bar',
        colorMap: {
            '7': '#a1a1a1'
        },
        barColor: '#4454c3'
    });

})(jQuery); 