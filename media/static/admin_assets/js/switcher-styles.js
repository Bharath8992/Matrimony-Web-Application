
let html = document.querySelector('html');

//Switcher Styles
function switcherEvents() {
	'use strict';

	/***************** RTL Start*********************/
	$(document).on("click", '#myonoffswitch55', function () {
		if (this.checked) {
			$('body').addClass('rtl');
			$('body').removeClass('ltr');
			$("html[lang=en]").attr("dir", "rtl");
			$(".select2-container").attr("dir", "rtl");
			
			$('.fc-theme-standard').removeClass('fc-direction-ltr');
			$('.fc-theme-standard').addClass('fc-direction-rtl');
			$('.fc-header-toolbar').removeClass('fc-toolbar-ltr');
			$('.fc-header-toolbar').addClass('fc-toolbar-rtl');
			localStorage.setItem("sparicrtl", true);
			localStorage.removeItem("sparicltr");
			$("head link#style").attr("href", $(this));
			(document.getElementById("style")?.setAttribute("href", "static/assets/plugins/bootstrap/css/bootstrap.rtl.min.css"));

			var carousel = $('.owl-carousel');
			$.each(carousel, function (index, element) {
				// element == this
				var carouselData = $(element).data('owl.carousel');
				carouselData.settings.rtl = true; //don't know if both are necessary
				carouselData.options.rtl = true;
				$(element).trigger('refresh.owl.carousel');
			});
			if (document.querySelector('body').classList.contains('horizontal')&& !(document.querySelector('body').classList.contains('bg-account'))) {
				checkHoriMenu();
				$('.newsticker').breakingNews(
					{
						direction: "ltr",
					}
				); 
			}
		}
	});
	/***************** RTL End *********************/

	/***************** LTR Start *********************/
	$(document).on("click", '#myonoffswitch54', function () {

		if (this.checked) {
			$('body').addClass('ltr');
			$('body').removeClass('rtl');
			$("html[lang=en]").attr("dir", "ltr");
			$(".select2-container").attr("dir", "ltr");
			$('.newsticker').breakingNews(
				{
					direction: "ltr",
				}
			); 
			$('.fc-theme-standard').addClass('fc-direction-ltr');
			$('.fc-theme-standard').removeClass('fc-direction-rtl');
			$('.fc-header-toolbar').addClass('fc-toolbar-ltr');
			$('.fc-header-toolbar').removeClass('fc-toolbar-rtl');
			localStorage.setItem("sparicltr", true);
			localStorage.removeItem("sparicrtl");
			$("head link#style").attr("href", $(this));
			(document.getElementById("style")?.setAttribute("href", "static/assets/plugins/bootstrap/css/bootstrap.min.css"));
			var carousel = $('.owl-carousel');
			$.each(carousel, function (index, element) {
				// element == this
				var carouselData = $(element).data('owl.carousel');
				carouselData.settings.rtl = false; //don't know if both are necessary
				carouselData.options.rtl = false;
				$(element).trigger('refresh.owl.carousel');
			});
			if (document.querySelector('body').classList.contains('horizontal')&& !(document.querySelector('body').classList.contains('bg-account'))) {
				checkHoriMenu();
			}
		} 
	});
	/***************** LTR End*********************/

	/***************** LIGHT THEME Start*********************/
	$(document).on("click", '#myonoffswitch1', function () {
		if (this.checked) {
			$('body').addClass('light-mode');
			$('body').removeClass('dark-mode');
			$('body').removeClass('light-menu');
			$('body').removeClass('dark-menu');
			$('body').removeClass('color-menu');
			$('body').removeClass('light-header');
			$('body').removeClass('color-header');
			$('body').removeClass('dark-header');

			$('#myonoffswitch3').prop('checked', true);
			$('#myonoffswitch6').prop('checked', true);

			localStorage.setItem('spariclightMode', true)
			localStorage.removeItem('sparicdarkMode', false)
		} 
		checkOptions();
	});
	/***************** LIGHT THEME End *********************/

	/***************** DARK THEME Start*********************/
	$(document).on("click", '#myonoffswitch2', function () {
		if (this.checked) {
			$('body').addClass('dark-mode');
			$('body').removeClass('light-mode');
			$('body').removeClass('light-menu');
			$('body').removeClass('color-menu');
			$('body').removeClass('dark-menu');
			$('body').removeClass('dark-header');
			$('body').removeClass('color-header');
			$('body').removeClass('light-header');

			$('#myonoffswitch5').prop('checked', true);
			$('#myonoffswitch8').prop('checked', true);

			html.style.removeProperty("--dark-body");
			html.style.removeProperty("--dark-theme");
			localStorage.removeItem("sparicbgColor");
			localStorage.removeItem("sparicthemeColor");

			localStorage.setItem('sparicdarkMode', true);
			localStorage.removeItem('spariclightMode', false);
			
		} 
		checkOptions();
	});
	/***************** Dark THEME End*********************/

	/***************** VERTICAL-MENU Start*********************/
	$(document).on("click", '#myonoffswitch34', function () {
		if (this.checked) {
			ActiveSubmenu();
			$('body').removeClass('horizontal');
			$('body').removeClass('horizontal-hover');
			$(".main-content").removeClass("horizontal-content");
			$(".main-content").addClass("app-content");
			$(".main-container").removeClass("container");
			$(".main-container").addClass("container-fluid");
			$(".header").removeClass("hor-header");
			$(".app-header").removeClass("side-header");
			$(".header").addClass("app-header");
			$(".app-sidebar").removeClass("horizontal-main")
			$(".main-sidemenu").removeClass("container")
			$('#slide-left').removeClass('d-none');
			$('#slide-right').removeClass('d-none');
			$('body').addClass('sidebar-mini');
			$('body').removeClass('default-logo');
			$('body').removeClass('center-logo');

			$('#myonoffswitch13').prop('checked', true);

			localStorage.setItem("sparicvertical", true);
			localStorage.removeItem("sparichorizontal");
			localStorage.removeItem("sparichorizontalHover");
			localStorage.removeItem("sparicdefaultlogo");
			localStorage.removeItem("spariccenterlogo");
			localStorage.removeItem("sparicclosedmenu");
			localStorage.removeItem("sparicicontextmenu");
			localStorage.removeItem("sparicsideiconmenu");
			localStorage.removeItem("sparichoversubmenu");
			localStorage.removeItem("sparichoversubmenu1");
			localStorage.removeItem("sparicdoublemenu");
			localStorage.removeItem("sparicdoublemenutabs");

			responsive();
		} 
	});
	/***************** VERTICAL-MENU End*********************/

	/***************** HORIZONTAL-CLICK-MENU Start*********************/
	$(document).on("click", '#myonoffswitch35', function () {
		if (this.checked) {
			ActiveSubmenu();
			if (window.innerWidth >= 992) {
				let li = document.querySelectorAll('.side-menu li')
				li.forEach((e, i) => {
					e.classList.remove('is-expanded')
				})
				var animationSpeed = 300;
				// first level
				var parent = $("[data-bs-toggle='sub-slide']").parents('ul');
				var ul = parent.find('ul.slide-menu:visible').slideUp(animationSpeed);
				ul.removeClass('open');
				var parent1 = $("[data-bs-toggle='sub-slide2']").parents('ul');
				var ul1 = parent1.find('ul.slide-menu:visible').slideUp(animationSpeed);
				ul1.removeClass('open');
			}
			$('body').addClass('horizontal');
			$(".main-content").addClass("horizontal-content");
			$(".main-content").removeClass("app-content");
			$(".main-container").addClass("container");
			$(".main-container").removeClass("container-fluid");
			$(".app-header").addClass("hor-header");
			$(".header").removeClass("app-header");
			$(".app-header").removeClass("side-header");
			$(".app-sidebar").addClass("horizontal-main")
			$(".main-sidemenu").addClass("container")
			$('body').removeClass('sidebar-mini');
			$('body').removeClass('sidenav-toggled');
			$('body').removeClass('horizontal-hover');
			$('body').removeClass('closed-menu');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			$('body').removeClass('double-menu');
			$('body').removeClass('double-menu-tabs');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('sideicon-menu');
			$('body').removeClass('center-logo');
			$('.slide-menu').removeClass('double-menu-active');

			$('#switchbtn-defaultlogo').prop('checked', true);

			localStorage.setItem("sparichorizontal", true);
			localStorage.removeItem("sparichorizontalHover");
			localStorage.removeItem("sparicvertical");
			localStorage.removeItem("sparicdefaultmenu");
			localStorage.removeItem("sparicclosedmenu");
			localStorage.removeItem("sparicicontextmenu");
			localStorage.removeItem("sparicsideiconmenu");
			localStorage.removeItem("sparichoversubmenu");
			localStorage.removeItem("sparichoversubmenu1");
			localStorage.removeItem("sparicdoublemenu");
			localStorage.removeItem("sparicdoublemenutabs");
			// $('#slide-left').removeClass('d-none');
			// $('#slide-right').removeClass('d-none');
			if (document.querySelector('body').classList.contains('horizontal')&& !(document.querySelector('body').classList.contains('bg-account'))) {
				checkHoriMenu();
				responsive();
				document.querySelector('.horizontal .side-menu').style.flexWrap = 'noWrap'
			}
		}
	});
	/***************** HORIZONTAL-CLICK-MENU End*********************/

	/***************** HORIZONTAL-HOVER-MENU Start*********************/
	$(document).on("click", '#myonoffswitch111', function () {
		if (this.checked) {
			let li = document.querySelectorAll('.side-menu li')
			li.forEach((e, i) => {
				e.classList.remove('is-expanded')
			})
			var animationSpeed = 300;
			// first level
			var parent = $("[data-bs-toggle='sub-slide']").parents('ul');
			var ul = parent.find('ul.slide-menu:visible').slideUp(animationSpeed);
			ul.removeClass('open');
			var parent1 = $("[data-bs-toggle='sub-slide2']").parents('ul');
			var ul1 = parent1.find('ul.slide-menu:visible').slideUp(animationSpeed);
			ul1.removeClass('open');
			$('body').addClass('horizontal-hover');
			$('body').addClass('horizontal');
			let subNavSub = document.querySelectorAll('.sub-slide-menu');
			subNavSub.forEach((e) => {
				e.style.display = '';
			})
			let subNav = document.querySelectorAll('.slide-menu')
			subNav.forEach((e) => {
				e.style.display = '';
			})
			// $('#slide-left').addClass('d-none');
			// $('#slide-right').addClass('d-none');
			$(".main-content").addClass("horizontal-content");
			$(".main-content").removeClass("app-content");
			$(".main-container").addClass("container");
			$(".main-container").removeClass("container-fluid");
			$(".app-header").addClass("hor-header");
			$(".app-header").removeClass("side-header");
			$(".header").removeClass("app-header");
			$(".app-sidebar").addClass("horizontal-main")
			$(".main-sidemenu").addClass("container")
			$('body').removeClass('sidebar-mini');
			$('body').removeClass('sidenav-toggled');
			$('body').removeClass('closed-menu');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			$('body').removeClass('double-menu');
			$('body').removeClass('double-menu-tabs');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('sideicon-menu');
			$('body').removeClass('center-logo');
			$('.slide-menu').removeClass('double-menu-active');

			$('#switchbtn-defaultlogo').prop('checked', true);

			localStorage.setItem("sparichorizontalHover", true);
			localStorage.removeItem("sparichorizontal");
			localStorage.removeItem("sparicvertical");
			localStorage.removeItem("sparicdefaultmenu");
			localStorage.removeItem("sparicclosedmenu");
			localStorage.removeItem("sparicicontextmenu");
			localStorage.removeItem("sparicsideiconmenu");
			localStorage.removeItem("sparichoversubmenu");
			localStorage.removeItem("sparichoversubmenu1");
			localStorage.removeItem("sparicdoublemenu");
			localStorage.removeItem("sparicdoublemenutabs");
			// HorizontalHovermenu();
			if (document.querySelector('body').classList.contains('horizontal')&& !(document.querySelector('body').classList.contains('bg-account'))) {
				checkHoriMenu();
				responsive();
				document.querySelector('.horizontal .side-menu').style.flexWrap = 'nowrap'
			}
		}
	});
	/***************** HORIZONTAL-HOVER-MENU End*********************/

	/***************** Default Logo Start*********************/
	$(document).on("click", '#switchbtn-defaultlogo', function () {
		if (this.checked) {
			$('body').addClass('default-logo');
			$('body').removeClass('center-logo');
			localStorage.setItem("sparicdefaultlogo", true);
			localStorage.removeItem("spariccenterlogo");
		}
	});
	/***************** Default Logo End*********************/

	/***************** Center Logo Start*********************/
	$(document).on("click", '#switchbtn-centerlogo', function () {
		if (this.checked) {
			$('body').addClass('center-logo');
			$('body').removeClass('default-logo');
			localStorage.setItem("spariccenterlogo", true);
			localStorage.removeItem("sparicdefaultlogo");
		}
	});
	/***************** Center Logo End*********************/

	/***************** DEFAULT-MENU Start*********************/
	$(document).on("click", '#myonoffswitch13', function () {
		if (this.checked) {
			$('body').addClass('default-menu');
			hovermenu();
			$('body').removeClass('closed-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('sideicon-menu');
			$('body').removeClass('sidenav-toggled');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			$('body').removeClass('double-menu');
			$('body').removeClass('double-menu-tabs');
			$('body').removeClass('center-logo');
			$('body').removeClass('default-logo');

			localStorage.setItem("sparicdefaultmenu", true);
			localStorage.removeItem("sparicclosedmenu");
			localStorage.removeItem("sparicicontextmenu");
			localStorage.removeItem("sparicsideiconmenu");
			localStorage.removeItem("sparichoversubmenu");
			localStorage.removeItem("sparichoversubmenu1");
			localStorage.removeItem("sparicdoublemenu");
			localStorage.removeItem("sparicdoublemenutabs");
			localStorage.removeItem("spariccenterlogo");
			localStorage.removeItem("sparicdefaultlogo");
		}
	});
	/***************** DEFAULT-MENU End*********************/

	/***************** CLOSED-MENU Start*********************/
	$(document).on("click", '#myonoffswitch30', function () {
		if (this.checked) {
			$('body').addClass('closed-menu');
			hovermenu();
			$('body').addClass('sidenav-toggled');
			$('body').removeClass('default-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('sideicon-menu');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			$('body').removeClass('double-menu');
			$('body').removeClass('double-menu-tabs');
			$('body').removeClass('center-logo');
			$('body').removeClass('default-logo');

			localStorage.setItem("sparicclosedmenu", true);
			localStorage.removeItem("sparicdefaultmenu");
			localStorage.removeItem("sparicicontextmenu");
			localStorage.removeItem("sparicsideiconmenu");
			localStorage.removeItem("sparichoversubmenu");
			localStorage.removeItem("sparichoversubmenu1");
			localStorage.removeItem("sparicdoublemenu");
			localStorage.removeItem("sparicdoublemenutabs");
			localStorage.removeItem("spariccenterlogo");
			localStorage.removeItem("sparicdefaultlogo");
		}
	});
	/***************** CLOSED-MENU End*********************/

	/***************** ICON-TEXT-MENU Start*********************/
	$(document).on("click", '#myonoffswitch14', function () {
		if (this.checked) {
			$('body').addClass('icontext-menu');
			icontext();
			$('body').addClass('sidenav-toggled');
			$('body').removeClass('default-menu');
			$('body').removeClass('sideicon-menu');
			$('body').removeClass('closed-menu');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			$('body').removeClass('double-menu');
			$('body').removeClass('double-menu-tabs');
			$('body').removeClass('center-logo');
			$('body').removeClass('default-logo');

			localStorage.setItem("sparicicontextmenu", true);
			localStorage.removeItem("sparicdefaultmenu");
			localStorage.removeItem("sparicclosedmenu");
			localStorage.removeItem("sparicsideiconmenu");
			localStorage.removeItem("sparichoversubmenu");
			localStorage.removeItem("sparichoversubmenu1");
			localStorage.removeItem("sparicdoublemenu");
			localStorage.removeItem("sparicdoublemenutabs");
			localStorage.removeItem("spariccenterlogo");
			localStorage.removeItem("sparicdefaultlogo");

		}
	});
	/***************** ICON-TEXT-MENU End*********************/

	/***************** ICON-OVERLAY-MENU Start*********************/
	$(document).on("click", '#myonoffswitch15', function () {
		if (this.checked) {
			$('body').addClass('sideicon-menu');
			hovermenu();
			$('body').addClass('sidenav-toggled');
			$('body').removeClass('default-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('closed-menu');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			$('body').removeClass('double-menu');
			$('body').removeClass('double-menu-tabs');
			$('body').removeClass('center-logo');
			$('body').removeClass('default-logo');

			localStorage.setItem("sparicsideiconmenu", true);
			localStorage.removeItem("sparicdefaultmenu");
			localStorage.removeItem("sparicclosedmenu");
			localStorage.removeItem("sparicicontextmenu");
			localStorage.removeItem("sparichoversubmenu");
			localStorage.removeItem("sparichoversubmenu1");
			localStorage.removeItem("sparicdoublemenu");
			localStorage.removeItem("sparicdoublemenutabs");
			localStorage.removeItem("spariccenterlogo");
			localStorage.removeItem("sparicdefaultlogo");
		}
	});
	/***************** ICON-OVERLAY-MENU End*********************/

	/***************** HOVER-SUBMENU-MENU Start*********************/
	$(document).on("click", '#myonoffswitch32', function () {
		if (this.checked) {
			$('body').addClass('hover-submenu');
			hovermenu();
			$('body').addClass('sidenav-toggled');
			$('body').removeClass('default-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('sideicon-menu');
			$('body').removeClass('closed-menu');
			$('body').removeClass('hover-submenu1');
			$('body').removeClass('double-menu');
			$('body').removeClass('double-menu-tabs');
			$('body').removeClass('center-logo');
			$('body').removeClass('default-logo');

			localStorage.setItem("sparichoversubmenu", true);
			localStorage.removeItem("sparicdefaultmenu");
			localStorage.removeItem("sparicclosedmenu");
			localStorage.removeItem("sparicicontextmenu");
			localStorage.removeItem("sparicsideiconmenu");
			localStorage.removeItem("sparichoversubmenu1");
			localStorage.removeItem("sparicdoublemenu");
			localStorage.removeItem("sparicdoublemenutabs");
			localStorage.removeItem("spariccenterlogo");
			localStorage.removeItem("sparicdefaultlogo");
		}
	});
	/***************** HOVER-SUBMENU-MENU End*********************/

	/***************** HOVER-SUBMENU-MENU-1 Start*********************/
	$(document).on("click", '#myonoffswitch33', function () {
		if (this.checked) {
			$('body').addClass('hover-submenu1');
			hovermenu();
			$('body').addClass('sidenav-toggled');
			$('body').removeClass('default-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('sideicon-menu');
			$('body').removeClass('closed-menu');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('double-menu');
			$('body').removeClass('double-menu-tabs');
			$('body').removeClass('center-logo');
			$('body').removeClass('default-logo');

			localStorage.setItem("sparichoversubmenu1", true);
			localStorage.removeItem("sparicdefaultmenu");
			localStorage.removeItem("sparicclosedmenu");
			localStorage.removeItem("sparicicontextmenu");
			localStorage.removeItem("sparicsideiconmenu");
			localStorage.removeItem("sparichoversubmenu");
			localStorage.removeItem("sparicdoublemenu");
			localStorage.removeItem("sparicdoublemenutabs");
			localStorage.removeItem("spariccenterlogo");
			localStorage.removeItem("sparicdefaultlogo");
		}
	});
	/***************** HOVER-SUBMENU-MENU-1 End*********************/

	/***************** DOUBLE-MENU Start*********************/
	$(document).on("click", '#switchbtn-doublemenu', function () {
		if (this.checked) {
			$('body').addClass('double-menu');
			doubleLayoutFn();
			$('body').removeClass('default-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('sideicon-menu');
			$('body').removeClass('sidenav-toggled');
			$('body').removeClass('sidenav-toggled-open');
			$('body').removeClass('closed-menu');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			$('body').removeClass('center-logo');
			$('body').removeClass('default-logo');
			$('body').removeClass('double-menu-tabs');

			localStorage.setItem("sparicdoublemenu", true);
			localStorage.removeItem("sparicdefaultmenu");
			localStorage.removeItem("sparicclosedmenu");
			localStorage.removeItem("sparicicontextmenu");
			localStorage.removeItem("sparicsideiconmenu");
			localStorage.removeItem("sparichoversubmenu");
			localStorage.removeItem("sparichoversubmenu1");
			localStorage.removeItem("sparicdoublemenutabs");
			localStorage.removeItem("spariccenterlogo");
			localStorage.removeItem("sparicdefaultlogo");
		}
	});
	/***************** DOUBLE-MENU End*********************/

	/***************** DOUBLE-MENU-TABS Start*********************/
	$(document).on("click", '#switchbtn-doublemenutabs', function () {
		if (this.checked) {
			$('body').addClass('double-menu-tabs');
			doubleLayoutFn();
			$('body').removeClass('default-menu');
			$('body').removeClass('icontext-menu');
			$('body').removeClass('sideicon-menu');
			$('body').removeClass('closed-menu');
			$('body').removeClass('sidenav-toggled');
			$('body').removeClass('sidenav-toggled-open');
			$('body').removeClass('hover-submenu');
			$('body').removeClass('hover-submenu1');
			$('body').removeClass('double-menu');
			$('body').removeClass('center-logo');
			$('body').removeClass('default-logo');
			
			localStorage.setItem("sparicdoublemenutabs", true);
			localStorage.removeItem("sparicdefaultmenu");
			localStorage.removeItem("sparicclosedmenu");
			localStorage.removeItem("sparicicontextmenu");
			localStorage.removeItem("sparicsideiconmenu");
			localStorage.removeItem("sparichoversubmenu");
			localStorage.removeItem("sparichoversubmenu1");
			localStorage.removeItem("sparicdoublemenu");
			localStorage.removeItem("spariccenterlogo");
			localStorage.removeItem("sparicdefaultlogo");
		}
	});
	/***************** DOUBLE-MENU-TABS End*********************/

	/***************** LAYOUT-STYLE Start*********************/
	$(document).on("click", '#myonoffswitch9', function () {
		if (this.checked) {
			$('body').addClass('layout-fullwidth');
			$('body').removeClass('layout-boxed');
			localStorage.setItem("sparicfullwidth", true);
			localStorage.removeItem("sparicboxedwidth");
		}
	});

	$(document).on("click", '#myonoffswitch10', function () {
		if (this.checked) {
			$('body').addClass('layout-boxed');
			$('body').removeClass('layout-fullwidth');
			localStorage.setItem("sparicboxedwidth", true);
			localStorage.removeItem("sparicfullwidth");
		}
	});
	/***************** LAYOUT-STYLE End*********************/

	/***************** LAYOUT-POSITIONS Start*********************/
	$(document).on("click", '#myonoffswitch11', function () {
		if (this.checked) {
			$('body').addClass('fixed-layout');
			$('body').removeClass('scrollable-layout');
			localStorage.setItem("sparicfixed", true);
			localStorage.removeItem("sparicscrollable");
		}
	});

	$(document).on("click", '#myonoffswitch12', function () {
		if (this.checked) {
			$('body').addClass('scrollable-layout');
			$('body').removeClass('fixed-layout');
			localStorage.setItem("sparicscrollable", true);
			localStorage.removeItem("sparicfixed");
		}
	});
	/***************** LAYOUT-POSITIONS End*********************/

	/***************** MENU-STYLES Start*********************/
	$(document).on("click", '#myonoffswitch3', function () {
		if (this.checked) {
			$('body').addClass('light-menu');
			$('body').removeClass('color-menu');
			$('body').removeClass('dark-menu');
			localStorage.setItem("spariclightmenu", true);
			localStorage.removeItem("spariccolormenu");
			localStorage.removeItem("sparicdarkmenu");
		}
	});
	
	$(document).on("click", '#myonoffswitch4', function () {
		if (this.checked) {
			$('body').addClass('color-menu');
			$('body').removeClass('light-menu');
			$('body').removeClass('dark-menu');
			localStorage.setItem("spariccolormenu", true);
			localStorage.removeItem("spariclightmenu");
			localStorage.removeItem("sparicdarkmenu");
		}
	});
	
	$(document).on("click", '#myonoffswitch5', function () {
		if (this.checked) {
			$('body').addClass('dark-menu');
			$('body').removeClass('color-menu');
			$('body').removeClass('light-menu');
			localStorage.setItem("sparicdarkmenu", true);
			localStorage.removeItem("spariclightmenu");
			localStorage.removeItem("spariccolormenu");
		}
	});
	/***************** MENU-STYLES End*********************/

	/***************** HEADER-STYLES Start*********************/
	$(document).on("click", '#myonoffswitch6', function () {
		if (this.checked) {
			$('body').addClass('light-header');
			$('body').removeClass('color-header');
			$('body').removeClass('dark-header');
			localStorage.setItem("spariclightheader", true);
			localStorage.removeItem("spariccolorheader");
			localStorage.removeItem("sparicdarkheader");
		} 
	});

	$(document).on("click", '#myonoffswitch7', function () {
		if (this.checked) {
			$('body').addClass('color-header');
			$('body').removeClass('light-header');
			$('body').removeClass('dark-header');
			localStorage.setItem("spariccolorheader", true);
			localStorage.removeItem("spariclightheader");
			localStorage.removeItem("sparicdarkheader");
		}
	});

	$(document).on("click", '#myonoffswitch8', function () {
		if (this.checked) {
			$('body').addClass('dark-header');
			$('body').removeClass('color-header');
			$('body').removeClass('light-header');
			localStorage.setItem("sparicdarkheader", true);
			localStorage.removeItem("spariclightheader");
			localStorage.removeItem("spariccolorheader");
		}
	});
	/***************** HEADER-STYLES End*********************/


	/***************** Add Switcher Classes *********************/
	//LTR & RTL
	if (!localStorage.getItem('sparicrtl') && !localStorage.getItem('sparicltr')) {

		/***************** RTL *********************/
		// $('body').addClass('rtl');
		/***************** RTL *********************/
		/***************** LTR *********************/
		// $('body').addClass('ltr');
		/***************** LTR *********************/

	}
	//Light-mode & Dark-mode
	if (!localStorage.getItem('spariclightMode') && !localStorage.getItem('sparicdarkMode')) {
		/***************** Light THEME *********************/
		// $('body').addClass('light-mode');
		/***************** Light THEME *********************/

		/***************** DARK THEME *********************/
		// $('body').addClass('dark-mode');
		/***************** Dark THEME *********************/
	}

	//Vertical-menu & Horizontal-menu
	if (!localStorage.getItem('sparicvertical') && !localStorage.getItem('sparichorizontal') && !localStorage.getItem('sparichorizontalHover')) {
		/***************** Horizontal THEME *********************/
		// $('body').addClass('horizontal');
		/***************** Horizontal THEME *********************/

		/***************** Horizontal-Hover THEME *********************/
		// $('body').addClass('horizontal-hover');
		/***************** Horizontal-Hover THEME *********************/
	}

	//Vertical Layout Style
	if (!localStorage.getItem('sparicdefaultmenu') && !localStorage.getItem('sparicclosedmenu') && !localStorage.getItem('sparicicontextmenu')&& !localStorage.getItem('sparicsideiconmenu')&& !localStorage.getItem('sparichoversubmenu')&& !localStorage.getItem('sparichoversubmenu1')) {
		/**Default-Menu**/
		// $('body').addClass('default-menu');
		/**Default-Menu**/

		/**closed-Menu**/
		// $('body').addClass('closed-menu');
		/**closed-Menu**/

		/**Icon-Text-Menu**/
		// $('body').addClass('icontext-menu');
		/**Icon-Text-Menu**/

		/**Icon-Overlay-Menu**/
		// $('body').addClass('sideicon-menu');
		/**Icon-Overlay-Menu**/

		/**Hover-Sub-Menu**/
		// $('body').addClass('hover-submenu');
		/**Hover-Sub-Menu**/

		/**Hover-Sub-Menu1**/
		// $('body').addClass('hover-submenu1');
		/**Hover-Sub-Menu1**/

		/**Double-Menu**/
		// $('body').addClass('double-menu');
		/**Double-Menu**/

		/**Double-Menu-Tabs**/
		// $('body').addClass('double-menu-tabs');
		/**Double-Menu-Tabs**/
	}

	//Horizontal Logo Style
	if (!localStorage.getItem('sparicdefaultlogo') && !localStorage.getItem('spariccenterlogo')) {
		/**Default-Logo**/
		// $('body').addClass('default-logo');
		/**Default-Logo**/

		/**Center-Logo**/
		// $('body').addClass('center-logo');
		/**Center-Logo**/

	}

	//Boxed Layout Style
	if (!localStorage.getItem('sparicfullwidth') && !localStorage.getItem('sparicboxedwidth')) {
	// $('body').addClass('layout-boxed');
	}

	//Scrollable-Layout Style
	if (!localStorage.getItem('sparicfixed') && !localStorage.getItem('sparicscrollable')) {
	// $('body').addClass('scrollable-layout');
	}

	//Menu Styles
	if (!localStorage.getItem('spariclightmenu') && !localStorage.getItem('spariccolormenu') && !localStorage.getItem('sparicdarkmenu')) {
		/**Light-menu**/
		// $('body').addClass('light-menu');
		/**Light-menu**/

		/**Color-menu**/
		// $('body').addClass('color-menu');
		/**Color-menu**/

		/**Dark-menu**/
		// $('body').addClass('dark-menu');
		/**Dark-menu**/
	}
	//Header Styles
	if (!localStorage.getItem('spariclightheader') && !localStorage.getItem('spariccolorheader') && !localStorage.getItem('sparicdarkheader')) {
		/**Light-Header**/
		// $('body').addClass('light-header');
		/**Light-Header**/

		/**Color-Header**/
		// $('body').addClass('color-header');
		/**Color-Header**/

		/**Dark-Header**/
		// $('body').addClass('dark-header');
		/**Dark-Header**/

	}
	/***************** Add Switcher Classes *********************/

}
switcherEvents();


(function () {
	"use strict";
	/***************** RTL HAs Class *********************/
	let bodyRtl = $('body').hasClass('rtl');
	if (bodyRtl) {
		$('body').addClass('rtl');
		$('body').removeClass('ltr');
		$("html[lang=en]").attr("dir", "rtl");
		$(".select2-container").attr("dir", "rtl");
		
		$("head link#style").attr("href", $(this));
		(document.getElementById("style")?.setAttribute("href", "static/assets/plugins/bootstrap/css/bootstrap.rtl.min.css"));

		var carousel = $('.owl-carousel');
		$.each(carousel, function (index, element) {
			// element == this
			var carouselData = $(element).data('owl.carousel');
			carouselData.settings.rtl = true; //don't know if both are necessary
			carouselData.options.rtl = true;
			$(element).trigger('refresh.owl.carousel');
		});
		if (document.querySelector('body').classList.contains('horizontal')&& !(document.querySelector('body').classList.contains('bg-account'))) {
			checkHoriMenu();
			$('#newsticker').breakingNews(
				{
					direction: "rtl",
				}
			); 
		}

	}
	/***************** RTL HAs Class *********************/

	/***************** Horizontal HAs Class *********************/
	let bodyhorizontal = $('body').hasClass('horizontal');
	if (bodyhorizontal) {
		if (window.innerWidth >= 992) {
			let li = document.querySelectorAll('.side-menu li')
			li.forEach((e, i) => {
				e.classList.remove('is-expanded')
			})
			var animationSpeed = 300;
			// first level
			var parent = $("[data-bs-toggle='sub-slide']").parents('ul');
			var ul = parent.find('ul.slide-menu:visible').slideUp(animationSpeed);
			ul.removeClass('open');
			var parent1 = $("[data-bs-toggle='sub-slide2']").parents('ul');
			var ul1 = parent1.find('ul.slide-menu:visible').slideUp(animationSpeed);
			ul1.removeClass('open');
		}
		$('body').addClass('horizontal');
		$(".main-content").addClass("horizontal-content");
		$(".main-content").removeClass("app-content");
		$(".main-container").addClass("container");
		$(".main-container").removeClass("container-fluid");
		$(".app-header").addClass("hor-header");
		$(".header").removeClass("app-header");
		$(".app-header").removeClass("side-header");
		$(".app-sidebar").addClass("horizontal-main")
		$(".main-sidemenu").addClass("container")
		$('body').removeClass('sidebar-mini');
		$('body').removeClass('sidenav-toggled');
		$('body').removeClass('horizontal-hover');
		$('body').removeClass('closed-menu');
		$('body').removeClass('hover-submenu');
		$('body').removeClass('hover-submenu1');
		$('body').removeClass('icontext-menu');
		$('body').removeClass('sideicon-menu');
		// $('#slide-left').removeClass('d-none');
		// $('#slide-right').removeClass('d-none');
		if (document.querySelector('body').classList.contains('horizontal')&& !(document.querySelector('body').classList.contains('bg-account'))) {
			checkHoriMenu();
			ActiveSubmenu();
			responsive();
			document.querySelector('.horizontal .side-menu').style.flexWrap = 'noWrap'
		}
	}
	/***************** Horizontal HAs Class *********************/

	/***************** Horizontal Hover HAs Class *********************/
	let bodyhorizontalhover = $('body').hasClass('horizontal-hover');
	if (bodyhorizontalhover) {
		let li = document.querySelectorAll('.side-menu li')
		li.forEach((e, i) => {
			e.classList.remove('is-expanded')
		})
		var animationSpeed = 300;
		// first level
		var parent = $("[data-bs-toggle='sub-slide']").parents('ul');
		var ul = parent.find('ul.slide-menu:visible').slideUp(animationSpeed);
		ul.removeClass('open');
		var parent1 = $("[data-bs-toggle='sub-slide2']").parents('ul');
		var ul1 = parent1.find('ul.slide-menu:visible').slideUp(animationSpeed);
		ul1.removeClass('open');
		$('body').addClass('horizontal-hover');
		$('body').addClass('horizontal');
		let subNavSub = document.querySelectorAll('.sub-slide-menu');
		subNavSub.forEach((e) => {
			e.style.display = '';
		})
		let subNav = document.querySelectorAll('.slide-menu')
		subNav.forEach((e) => {
			e.style.display = '';
		})
		// $('#slide-left').addClass('d-none');
		// $('#slide-right').addClass('d-none');
		$(".main-content").addClass("horizontal-content");
		$(".main-content").removeClass("app-content");
		$(".main-container").addClass("container");
		$(".main-container").removeClass("container-fluid");
		$(".app-header").addClass("hor-header");
		$(".app-header").removeClass("side-header");
		$(".header").removeClass("app-header");
		$(".app-sidebar").addClass("horizontal-main")
		$(".main-sidemenu").addClass("container")
		$('body').removeClass('sidebar-mini');
		$('body').removeClass('sidenav-toggled');
		$('body').removeClass('closed-menu');
		$('body').removeClass('hover-submenu');
		$('body').removeClass('hover-submenu1');
		$('body').removeClass('icontext-menu');
		$('body').removeClass('sideicon-menu');
		// HorizontalHovermenu();
		if (document.querySelector('body').classList.contains('horizontal')&& !(document.querySelector('body').classList.contains('bg-account'))) {
			checkHoriMenu();
			responsive();
			document.querySelector('.horizontal .side-menu').style.flexWrap = 'nowrap'
		}
	}
	/***************** Horizontal Hover HAs Class *********************/

	/***************** CLOSEDMENU HAs Class *********************/
	let bodyclosed = $('body').hasClass('closed-menu');
	if (bodyclosed) {
		$('body').addClass('closed-menu');
		if (!(document.querySelector('body').classList.contains('bg-account'))) {
			hovermenu();
		}
		$('body').addClass('sidenav-toggled');
	}
	/***************** CLOSEDMENU HAs Class *********************/

	/***************** ICONTEXT MENU HAs Class *********************/
	let bodyicontext = $('body').hasClass('icontext-menu');
	if (bodyicontext) {
		$('body').addClass('icontext-menu');
		if (!(document.querySelector('body').classList.contains('bg-account'))) {
			icontext();
		}
		$('body').addClass('sidenav-toggled');
	}
	/***************** ICONTEXT MENU HAs Class *********************/

	/***************** ICONOVERLAY MENU HAs Class *********************/
	let bodyiconoverlay = $('body').hasClass('sideicon-menu');
	if (bodyiconoverlay) {
		$('body').addClass('sideicon-menu');
		if (!(document.querySelector('body').classList.contains('bg-account'))) {
			hovermenu();
		}
		$('body').addClass('sidenav-toggled');
	}
	/***************** ICONOVERLAY MENU HAs Class *********************/

	/***************** HOVER-SUBMENU HAs Class *********************/
	let bodyhover = $('body').hasClass('hover-submenu');
	if (bodyhover) {
		$('body').addClass('hover-submenu');
		if (!(document.querySelector('body').classList.contains('bg-account'))) {
			hovermenu();
		}
		$('body').addClass('sidenav-toggled');
	}
	/***************** HOVER-SUBMENU HAs Class *********************/

	/***************** HOVER-SUBMENU HAs Class *********************/
	let bodyhover1 = $('body').hasClass('hover-submenu1');
	if (bodyhover1) {
		$('body').addClass('hover-submenu1');
		if (!(document.querySelector('body').classList.contains('bg-account'))) {
			hovermenu();
		}
		$('body').addClass('sidenav-toggled');
	}
	/***************** HOVER-SUBMENU HAs Class *********************/

	/***************** Double-Menu has Class *********************/
	let bodydoublemenu = $('body').hasClass('double-menu');
	if (bodydoublemenu) {
		$('body').addClass('double-menu');
		if (!(document.querySelector('body').classList.contains('bg-account'))) {
			doublemenu();
		}
	}
	/***************** Double-Menu has Class *********************/

	/***************** Double-Menu-Tabs has Class *********************/
	let bodydoublemenutabs = $('body').hasClass('double-menu-tabs');
	if (bodydoublemenutabs) {
		$('body').addClass('double-menu-tabs');
		if (!(document.querySelector('body').classList.contains('bg-account'))) {
			doublemenu();
		}
	}
	/***************** Double-Menu-Tabs has Class *********************/

	/***************** NUNITO FONT FAMILY HAs Class *********************/
	let bodynunito = $('body').hasClass('font-family-1');
	if (bodynunito) {
		$('body').addClass('font-family-1');
		
	}
	/***************** NUNITO FONT FAMILY HAs Class *********************/

	/***************** POPPINS FONT FAMILY HAs Class *********************/
	let bodypoppins = $('body').hasClass('font-family-2');
	if (bodypoppins) {
		$('body').addClass('font-family-2');
	}
	/***************** POPPINS FONT FAMILY HAs Class *********************/

	/***************** OPEN-SANS FONT FAMILY HAs Class *********************/
	let bodyopensans = $('body').hasClass('font-family-3');
	if (bodyopensans) {
		$('body').addClass('font-family-3');
	}
	/***************** OPENS-SNAS FONT FAMILY HAs Class *********************/

	/***************** MONTSERRAT FONT FAMILY HAs Class *********************/
	let bodymontserrat = $('body').hasClass('font-family-4');
	if (bodymontserrat) {
		$('body').addClass('font-family-4');
	}
	/***************** MONTSERRAT FONT FAMILY HAs Class *********************/

	/***************** ROBOTO FONT FAMILY HAs Class *********************/
	let bodyroboto = $('body').hasClass('font-family-5');
	if (bodyroboto) {
		$('body').addClass('font-family-5');
	}
	/***************** ROBOTO FONT FAMILY HAs Class *********************/


	checkOptions();
})()

function checkOptions() {
	'use strict'

	// horizontal
	if (document.querySelector('body').classList.contains('horizontal')) {
		$('#myonoffswitch35').prop('checked', true);
	}

	// horizontal-hover
	if (document.querySelector('body').classList.contains('horizontal-hover')) {
		$('#myonoffswitch111').prop('checked', true);
	}

	//RTL 
	if (document.querySelector('body').classList.contains('rtl')) {
		$('#myonoffswitch55').prop('checked', true);
	}

	// light header 
	if (document.querySelector('body').classList.contains('light-header')) {
		$('#myonoffswitch6').prop('checked', true);
	}
	// color header 
	if (document.querySelector('body').classList.contains('color-header')) {
		$('#myonoffswitch7').prop('checked', true);
	}
	// dark header 
	if (document.querySelector('body').classList.contains('dark-header')) {
		$('#myonoffswitch8').prop('checked', true);
	}

	// light menu
	if (document.querySelector('body').classList.contains('light-menu')) {
		$('#myonoffswitch3').prop('checked', true);
	}
	// color menu
	if (document.querySelector('body').classList.contains('color-menu')) {
		$('#myonoffswitch4').prop('checked', true);
	}
	// dark menu
	if (document.querySelector('body').classList.contains('dark-menu')) {
		$('#myonoffswitch5').prop('checked', true);
	}
	// Body style
	if (document.querySelector('body').classList.contains('body-style1')) {
		$('#myonoffswitch06').prop('checked', true);
	}
	// Boxed style
	if (document.querySelector('body').classList.contains('layout-boxed')) {
		$('#myonoffswitch10').prop('checked', true);
	}
	// scrollable-layout style
	if (document.querySelector('body').classList.contains('scrollable-layout')) {
		$('#myonoffswitch12').prop('checked', true);
	}
	// closed-menu style
	if (document.querySelector('body').classList.contains('closed-menu')) {
		$('#myonoffswitch30').prop('checked', true);
	}
	// icontext-menu style
	if (document.querySelector('body').classList.contains('icontext-menu')) {
		$('#myonoffswitch14').prop('checked', true);
	}
	// iconoverlay-menu style
	if (document.querySelector('body').classList.contains('sideicon-menu')) {
		$('#myonoffswitch15').prop('checked', true);
	}
	// hover-submenu style
	if (document.querySelector('body').classList.contains('hover-submenu')) {
		$('#myonoffswitch32').prop('checked', true);
	}
	// hover-submenu1 style
	if (document.querySelector('body').classList.contains('hover-submenu1')) {
		$('#myonoffswitch33').prop('checked', true);
	}
	// double-menu style
	if (document.querySelector('body').classList.contains('double-menu')) {
		$('#switchbtn-doublemenu').prop('checked', true);
	}
	// double-menu-tabs style
	if (document.querySelector('body').classList.contains('double-menu-tabs')) {
		$('#switchbtn-doublemenutabs').prop('checked', true);
	}
	// default-logo style
	if (document.querySelector('body').classList.contains('default-logo')) {
		$('#switchbtn-defaultlogo').prop('checked', true);
	}
	// center-logo style
	if (document.querySelector('body').classList.contains('center-logo')) {
		$('#switchbtn-centerlogo').prop('checked', true);
	}
}
checkOptions()

let reset = document.querySelector('#resetAll');
if (reset) {
	reset.addEventListener('click', () => {
		resetData();
	})
}

function resetData() {
	localStorage.clear();
	document.querySelector('html').style = '';
	names();
	$('#myonoffswitch54').prop('checked', true);
	$('#myonoffswitch1').prop('checked', true);
	$('#myonoffswitch3').prop('checked', true);
	$('#myonoffswitch6').prop('checked', true);
	$('#myonoffswitch9').prop('checked', true);
	$('#myonoffswitch34').prop('checked', true);
	$('#myonoffswitch11').prop('checked', true);
	$('#myonoffswitch13').prop('checked', true);
	$('body')?.addClass('light-mode');
	$('body')?.removeClass('dark-mode');
	$('body')?.removeClass('dark-menu');
	$('body')?.removeClass('light-menu');
	$('body')?.removeClass('color-menu');
	$('body')?.removeClass('dark-header');
	$('body')?.removeClass('light-header');
	$('body')?.removeClass('color-header');
	$('body')?.removeClass('layout-boxed');
	$('body')?.removeClass('icontext-menu');
	$('body')?.removeClass('sideicon-menu');
	$('body')?.removeClass('closed-menu');
	$('body')?.removeClass('hover-submenu');
	$('body')?.removeClass('hover-submenu1');
	$('body')?.removeClass('scrollable-layout');
	$('body')?.removeClass('sidenav-toggled');
	$('body')?.removeClass('body-style1');
	$('body')?.removeClass('scrollable-layout');
	$('body')?.removeClass('double-menu');
	$('body')?.removeClass('double-menu-tabs');
	$(".tab-content-show").addClass("active");
	$(".tab-content-double").removeClass("active")
	$('.slide-menu')?.removeClass('double-menu-active');
	$('body')?.removeClass('default-logo');
	$('body')?.removeClass('center-logo');
	$('body')?.removeClass('font-family-2');
	$('body')?.removeClass('font-family-3');
	$('body')?.removeClass('font-family-4');
	$('body')?.removeClass('font-family-5');


	$('body').removeClass('horizontal');
	$('body').removeClass('horizontal-hover');
	$(".main-content").removeClass("horizontal-content");
	$(".main-content").addClass("app-content");
	$(".main-container").removeClass("container");
	$(".main-container").addClass("container-fluid");
	$(".header").removeClass("hor-header");
	$(".app-header").removeClass("side-header");
	$(".header").addClass("app-header");
	$(".app-sidebar").removeClass("horizontal-main")
	$(".main-sidemenu").removeClass("container")
	$('#slide-left').removeClass('d-none');
	$('#slide-right').removeClass('d-none');
	$('body').addClass('sidebar-mini');
	$('body').removeClass('default-logo');
	$('body').removeClass('center-logo');

	$('#slide-left').removeClass('d-none');
    $('#slide-right').removeClass('d-none');
	$('body').addClass('ltr');
	$('body').removeClass('rtl');
	$("html[lang=en]").attr("dir", "ltr");
	$(".select2-container").attr("dir", "ltr");
	localStorage.setItem("sparicltr", true);
	localStorage.removeItem("sparicrtl");
	$("head link#style").attr("href", $(this));
	(document.getElementById("style")?.setAttribute("href", "static/assets/plugins/bootstrap/css/bootstrap.min.css"));
	var carousel = $('.owl-carousel');
	$.each(carousel, function (index, element) {
		// element == this
		var carouselData = $(element).data('owl.carousel');
		carouselData.settings.rtl = false; //don't know if both are necessary
		carouselData.options.rtl = false;
		$(element).trigger('refresh.owl.carousel');
	});
	if (document.querySelector('body').classList.contains('horizontal')&& !(document.querySelector('body').classList.contains('bg-account'))) {
		checkHoriMenu();
		ActiveSubmenu();
		responsive();
	}
}