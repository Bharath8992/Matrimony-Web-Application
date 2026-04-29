$(function() {
    "use strict";

    const ps7 = new PerfectScrollbar('.main-chat-list', {
        useBothWheelAxes: true,
        suppressScrollX: true,
    });

    const ps8 = new PerfectScrollbar('.main-chat-msgs', {
        useBothWheelAxes: true,
        suppressScrollX: true,
    });
});