"use strict";

// var $ = django.jQuery;

var DEFAULT_RIBBON_DEF = {
	// List of tabs to be rendered
	tabs: [
		"home",
	],

	// Tab definitions (at a minimum, must define all tabs listed in the "tabs" list above).
	tab: {
		"home": {
			groups: [
				"directory",
				"file",
				"select"
			],
			active: true,
			caption: "Home"
		},
		"debug": {
			caption: "Debug",
			active: false,
			groups: [
				"debug"
			]
		},
	},

	// Each tab will contain one or more button groups defined here (at a minimum, must define all 
	// group entries list in tab.{tabName}.groups lists above).
	group: {
		"directory": {
			caption: "Directory",
			buttons: [
				"change-directory-up",
				"goto-home-directory",
				"create-directory",
			],
		},
		"file": {
			caption: "File",
			buttons: [
				"file-upload",
				"file-move",
				"file-delete",
                "file-link",
                "file-open",
			],
		},
		"select": {
			buttons: [
				"file-select-all",
				"file-select-none",
				"file-invert-selection",
			],
			caption: "Select"
		},
		"debug": {
			buttons: [
				"maven",
				"show-state",
			],
			caption: "Debug"
		},
	},

	// Button definitions
	button: {
		"file-move": {
			caption: "Move",
			type: "large-button",
			image: "maven/img/32/FileMove.png",
			onClick: ".moveFile()",
			description: "Move file to a new destination.",
		},
		"file-upload": {
			caption: "Upload",
			type: "large-button",
			image: "maven/img/32/FileUpload.png",
			onClick: ".uploadFile()",
			description: "Upload a file.",
		},
		"delete-directory": {
			caption: "Delete<br>Directory",
			type: "large-button",
			image: "maven/img/32/DirectoryDelete.png",
			onClick: ".deleteDirectory()",
			description: "Delete selected directory.",
		},
		"file-select-none": {
			caption: "Select None",
			type: "small-button",
			image: "maven/img/16/SelectNone.png",
			onClick: ".unselectAllFiles()",
			description: "Unselect all files in folder.",
		},
		"file-select-all": {
			caption: "Select All",
			type: "small-button",
			image: "maven/img/16/SelectAll.png",
			onClick: ".selectAllFiles()",
			description: "Select all files in folder.",
		},
		"file-invert-selection": {
			caption: "Invert Selection",
			type: "small-button",
			image: "maven/img/16/SelectInvert.png",
			onClick: ".toggleAllFiles()",
			description: "Invert selected files in folder.",
		},
		"file-delete": {
			caption: "Delete",
			type: "large-button",
			image: "maven/img/32/FileDelete.png",
			onClick: ".deleteFile()",
			description: "Delete selected file(s).",
		},
		"file-link": {
			caption: "Get<br>Link",
			type: "large-button",
			image: "maven/img/32/FileLink.png",
			onClick: ".getFileLink()",
			description: "Get link for selected file.",
		},
		"file-open": {
			caption: "Open",
			type: "large-button",
			image: "maven/img/32/FileToWindow.png",
			onClick: ".openFile()",
			description: "Open selected file.",
		},
		"goto-home-directory": {
			caption: "Home",
			type: "large-button",
			image: "maven/img/32/DirectoryHome.png",
			onClick: ".homeDirectory()",
			description: "Go to home directory.",
		},
		"create-directory": {
			caption: "New",
			type: "large-button",
			image: "maven/img/32/DirectoryNew.png",
			onClick: ".launchCreateDirectoryDialog()",
			description: "Created a new directory.",
		},
		"change-directory-up": {
			caption: "Move<br>Up",
			type: "large-button",
			image: "maven/img/32/ChangeDirectoryUp.png",
			onClick: ".changeDirUp()",
			description: "Change directory up on level.",
		},
		"show-state": {
			caption: "Show<br>State",
			type: "large-button",
			image: "maven/img/32/State.png",
			onClick: ".showState()",
			description: "Show state variable.",
		},
		"maven": {
			caption: "Media<br>Maven",
			type: "large-button",
			image: "maven/img/32/LogoLight.png",
			onClick: ".showAbout()",
			description: "Media Maven info.",
		},
	},
};

var MAVEN_INSTANCE = {};

function csrfSafeMethod(method) {
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

$(document).ready(function () {
	$.ajaxSetup({
		beforeSend: function (xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});
});

/*
 __  __          _                   ____  _ _     _
|  \/  | ___  __| |_   _ ___  __ _  |  _ \(_) |__ | |__   ___  _ __
| |\/| |/ _ \/ _` | | | / __|/ _` | | |_) | | '_ \| '_ \ / _ \| '_ \
| |  | |  __/ (_| | |_| \__ \ (_| | |  _ <| | |_) | |_) | (_) | | | |
|_|  |_|\___|\__,_|\__,_|___/\__,_| |_| \_\_|_.__/|_.__/ \___/|_| |_|

 */

 function MavenRibbon(arg) {
	let me = this;

	// Class instance variables.
	me.activeTab = '';
	me.activeMenu = '';
	me.data = {};

	// Constructor.
	me.init = function (arg = {}) {
		// Set class instance variables.  
		for (let key in arg) {
			me[key] = arg[key];
		}
		me.render();
	};

	// Render the ribbon.
	me.render = function () {
		let staticURL = MAVEN_CONST.url.static;
		let html = [];
		me.activeTab = '';
		html.push(`<div class="tabs">`);
		for (let i = 0; i < me.data.tabs.length; i++) {
			let tabKey = me.data.tabs[i];
			let tabObj = me.data.tab[tabKey];
			let activeClass = '';
			if (i == 0) me.activeTab = `${tabKey}`;
			if (('active' in tabObj) && Boolean(tabObj.active)) {
				activeClass = ' active';
				me.activeTab = `${tabKey}`;
			}
			html.push(`  <div id="${me.mid}-ribbon-${tabKey}-spacer" class="spacer"></div>`);
			html.push(`  <div id="${me.mid}-ribbon-${tabKey}-tab" ribbon-menu-name="${tabKey}" class="tab${activeClass}">${tabObj.caption}</div>`);
		}
		html.push(`</div>`);

		html.push(`<div class="ribbon-menus">`);
		html.push(`  <div class="top-border"></div>`);
		for (let i = 0; i < me.data.tabs.length; i++) {
			let tabKey = me.data.tabs[i];
			let tabObj = me.data.tab[tabKey];
			html.push(`  <div id="${me.mid}-ribbon-${tabKey}-menu" ribbon-menu-name="${tabKey}" class="ribbon-menu" style="display:none;">`);
			html.push(`    <div id="${me.mid}-ribbon-${tabKey}-menu-groups" class="ribbon-menu-groups">`);
			for (let j = 0; j < tabObj.groups.length; j++) {
				let groupKey = tabObj.groups[j];
				let groupObj = me.data.group[groupKey];
				html.push(`      <div id="${me.mid}-ribbon-${tabKey}-menu-${groupKey}-group" class="ribbon-menu-group">`);
				html.push(`        <div class="ribbon-menu-group-top">`);
				html.push(`          <div class="spacer"></div>`);
				let smallButtonCount = 0;
				for (let k = 0; k < groupObj.buttons.length; k++) {
					let buttonKey = groupObj.buttons[k];
					if (!(buttonKey in me.data.button)) {
						console.error(`ERROR: Key "${buttonKey}" not defined in me.data.button object.`);
						continue;
					}
					let buttonObj = me.data.button[buttonKey];
					if (buttonObj.type == 'large-button') {
						if (smallButtonCount > 0) {
							for (let k = smallButtonCount; k < 3; k++) {
								// Insert null button
								html.push(`            <div class="small-filler"></div>`);
							}
							html.push(`          </div>`);
							html.push(`          <div class="spacer"></div>`);
							smallButtonCount = 0;
						}
						let buttonClass = 'large-button';
						if ('menu' in buttonObj) buttonClass = 'large-button has-menu';
						html.push(`          <div class="${me.mid}-ribbon-${buttonKey}-button ${buttonClass}">`);
						html.push(`            <div class="image"><img src="${staticURL}${buttonObj.image}"></div>`);
						html.push(`            <div class="caption">${buttonObj.caption}</div>`);
						if ('menu' in buttonObj) {
							html.push(`            <div class="arrow"><img src="img/xs/ArrowDown.png"></div>`);
							html.push(`            <div class="Menu">`);
							html.push(`              <div class="menu-item">On</div>`);
							html.push(`              <div class="menu-item">Off</div>`);
							html.push(`            </div>`);
						}
						html.push(`          </div>`);
						html.push(`          <div class="spacer"></div>`);
					}
					if (buttonObj.type == 'small-button') {
						if (smallButtonCount == 3) {
							html.push(`          </div>`);
							html.push(`          <div class="spacer"></div>`);
							smallButtonCount = 0;
						}
						if (smallButtonCount == 0) {
							html.push(`          <div class="button-cluster">`);
						}
						html.push(`            <div class="${me.mid}-ribbon-${buttonKey}-button small-button">`);
						html.push(`              <div class="image"><img src="${staticURL}${buttonObj.image}"></div>`);
						html.push(`              <div class="caption">${buttonObj.caption}</div>`);
						html.push(`            </div>`);
						smallButtonCount++
					}
				}
				if (smallButtonCount > 0) {
					for (let k = smallButtonCount; k < 3; k++) {
						// Insert null button.
						html.push(`            <div class="small-filler"></div>`);
					}
					html.push(`          </div>`);
					html.push(`          <div class="spacer"></div>`);
				}

				html.push(`        </div>`);
				html.push(`        <div class="ribbon-menu-group-middle"></div>`);
				html.push(`        <div class="ribbon-menu-group-bottom">${groupObj.caption}</div>`);
				html.push(`      </div>`);
				html.push(`      <div class="spacer"></div>`);
				html.push(`      <div class="separator"></div>`);
				html.push(`      <div class="spacer"></div>`);
			}
			html.push(`    </div>`);
			html.push(`  </div>`);
		}
		html.push(`  <div class="bottom-border"></div>`);
		html.push(`</div>`);

		// Debug print.  Remove later.
		let code = html.join("\n");

		// Display the active menu.
		$(`#${me.mid} .maven-wrapper .ribbon`).html(code);
		$(`#${me.mid}-ribbon-${me.activeTab}-menu`).css('display', 'block');

		// Assign click events to all buttons.
		for (let buttonKey in me.data.button) {
			let buttonObj = me.data.button[buttonKey];
			if ('onClick' in buttonObj) {
				$(`.${me.mid}-ribbon-${buttonKey}-button`).click(
					function () {
						// If the button is disabled, don't do anything.
						if ($(this).hasClass('disabled')) return;
						// Execute the button code.  
						try {
							let evalString = buttonObj.onClick;
							if (evalString.startsWith('.')) {
								evalString = `me.parent` + evalString;
							}
							evalString += ";";
							eval(evalString);
						} catch (e) {
							let dialog = new Dialog();
							dialog.Error(`ERROR: ${e.message}`);
						}
					}
				);
			}
			if ('enabled' in buttonObj && !(buttonObj.enabled)) {
				me.disableButton(buttonKey);
			}
		}

		// Assign click event to all tabs.
		$(`#${me.mid} .maven-wrapper .ribbon .tabs .tab`).click(
			function () {
				$(`#${me.mid} .maven-wrapper .ribbon .tabs .tab`).removeClass('active');
				let menuName = $(this).attr('ribbon-menu-name');
				$(`#${me.mid}-ribbon-${menuName}-tab`).addClass('active');
				$(`#${me.mid}-ribbon-${me.activeTab}-menu`).hide();
				me.activeTab = menuName;
				$(`#${me.mid}-ribbon-${me.activeTab}-menu`).fadeIn(100);
			}
		);

		// Assign click events to dropdown button menu items.  
		$(`#${me.mid} .maven-wrapper .ribbon .has-menu`).click(
			function () {
				if ($(this).hasClass('disabled')) return;
				$(this).find('.menu').css({
					position: 'absolute',
					top: $(this).height() + 1,
					left: -1,
				});
				$(this).find('.menu').fadeIn(100);
				let menuID = $(this).attr('id');
				$(this).mouseleave(function () {
					me.hideMenu(menuID);
				});
			}
		);

	};

	me.disableButton = function (name) {
		$(`.${me.mid}-ribbon-${name}-button`).addClass('disabled');
	};

	me.enableButton = function (name) {
		$(`.${me.mid}-ribbon-${name}-button`).removeClass('disabled');
	};

	me.hideMenu = function (menuID) {
		$('#' + menuID).find('.menu').hide(100);
	};

	me.hideMenus = function () {
		if (me.activeMenu.length == 0) return;
		$('#' + me.activeMenu).find('.menu').hide(50);
	};

	me.init(arg);
};

/*
 __  __          _                   _____                 _   _
|  \/  | ___  __| |_   _ ___  __ _  |  ___|   _ _ __   ___| |_(_) ___  _ __
| |\/| |/ _ \/ _` | | | / __|/ _` | | |_ | | | | '_ \ / __| __| |/ _ \| '_ \
| |  | |  __/ (_| | |_| \__ \ (_| | |  _|| |_| | | | | (__| |_| | (_) | | | |
|_|  |_|\___|\__,_|\__,_|___/\__,_| |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|

 _____          _
|  ___|_ _  ___| |_ ___  _ __ _   _
| |_ / _` |/ __| __/ _ \| '__| | | |
|  _| (_| | (__| || (_) | |  | |_| |
|_|  \__,_|\___|\__\___/|_|   \__, |
                              |___/
 */

let mavenFunctionFactory = {

	errorMessage: function(title, msg="") {
		if (msg.length == 0) {
			msg = "An unspecified error was encountered servicing this request.";
		}

		let width = 400;
		let height = 350;
		if (msg.length > 150) {
			let width = 700;
			let height = 550;
		}

		dialog.Launch({
			Title: title,
			Height: Math.min(height, 0.9*$(window).height()),
			Width: Math.min(width, 0.9*$(window).width()),
			Content: msg,
			Icon: 'error',
		});


	},

	validateArgs: function (inst, arg, valid) {
		// Cycle through all keys in arg object ...
		for (let key in arg) {
			// valid[key] must be defined.
			if (!(key in valid)) throw "ERROR: Invalid key \"" + key + "\".";
			// valid[key].type must be defined and type of arg[key] must match specified value.
			if ('type' in valid[key]) {
				if (!(typeof (arg[key]) === valid[key].type)) throw "ERROR: Attribute \"" + key + "\" is not of type \"" + valid[key].type + "\"";
			}
		}

		// Now cycle through each key in valid object.
		for (let key in valid) {
			// Assign default value to arg[key] if no value is specified.  
			if (('default' in valid[key]) && (!(key in arg))) {
				arg[key] = valid[key].default;
			}
			// If arg[key] is not defined but required, throw an error.
			if (('required' in valid[key]) && (valid[key].required)) {
				if (!(key in arg)) throw "ERROR: Required key \"" + key + "\" not defined.";
			}
		}

		// Set class instance variables.  
		for (let key in arg) {
			inst[key] = arg[key];
		}
	},

};

/*
 __  __          _                   _____ _ _
|  \/  | ___  __| |_   _ ___  __ _  |  ___(_) | ___
| |\/| |/ _ \/ _` | | | / __|/ _` | | |_  | | |/ _ \
| |  | |  __/ (_| | |_| \__ \ (_| | |  _| | | |  __/
|_|  |_|\___|\__,_|\__,_|___/\__,_| |_|   |_|_|\___|

 ____       _           _
/ ___|  ___| | ___  ___| |_ ___  _ __
\___ \ / _ \ |/ _ \/ __| __/ _ \| '__|
 ___) |  __/ |  __/ (__| || (_) | |
|____/ \___|_|\___|\___|\__\___/|_|

 */

function MavenFileSelector(field, cwd, type) {
	let me = this;

	me.state = {
		view: 'maven-file-selector',
		action: null, // ajax action
		name: null, // field name of form element
		id: null, // HTML id attribute
		cwd: null, // current working directory
		selected: null, // full url for selected file
		image: null, // src for selected file if image
		type: null, // type of file and widget, either 'file' or 'image'
	};

	me.fileSelectorDialog = new Dialog();

	me.init = function (field, cwd, type) {

		let ts = String(new Date().getTime());
		me.id = me.state.id = `maven-${field}-${ts}`;
		me.state.name = field;
		me.state.cwd = cwd;
		me.state.type = type;
		MAVEN_INSTANCE[me.id] = me;

		let typeString = me.state.type == 'file' ? 'File' : 'Image';
		me.fileSelectorDialog.Launch({
			Title: `Select ${typeString}`,
			Height: Math.min(500, 0.9*$(window).height()),
			Width: Math.min(600, 0.9*$(window).width()),
			Content: `<div id="${me.id}"></div>`,
			Buttons: [{
					Name: 'Select ' + typeString,
					Function: function () {
						if (me.state.selected) {
							$(`#maven-${me.state.name}-widget .maven-input`).val(me.state.selected);
							$(`#maven-${me.state.name}-widget .maven-mirror`).val(me.state.selected);
							if (me.state.type == 'image') {
								$(`#maven-${me.state.name}-widget .maven-image`).html(`<img src="${me.state.image}">`);
							}
							me.fileSelectorDialog.Close();
						}
					}
				},
				{
					Name: 'Cancel',
					Function: me.fileSelectorDialog.Close
				},
			],
		});

		me.state.action = 'get-file-select-html';
		me.ajax(me.state);

	};

	me.ajax = function(postData) {
		let title = me.state.action;
		let words = title.split("-");
		for (let i = 0; i < words.length; i++) {
			words[i] = words[i][0].toUpperCase() + words[i].substr(1);
		}
		title = words.join(" ") + ' Error';
		$.ajax({
			url: MAVEN_CONST.url.refresh,
			type: 'POST',
			data: postData,
			dataType: 'json',
			success: function (responseData) {
				if (responseData.valid) {
					me.refresh(responseData);
				} else {
					if ('error' in data) {
						mavenFunctionFactory.errorMessage(title, data.error);
					}
					else {
						mavenFunctionFactory.errorMessage(title);
					}
				}
			},
			error: function(request, status, error) {
				me.statusMessage('Ready');
				mavenFunctionFactory.errorMessage(title, request.responseText);
			},
		});
	};

	me.render = function() {
		$(`#${me.id} .file-tab`).click(function () {
			$(`#${me.id} .view-tab`).removeClass('active');
			$(`#${me.id} .file-tab`).addClass('active');
			$(`#${me.id} .select-list`).removeClass('active');
			$(`#${me.id} .file-select-list`).addClass('active');
		});
		
		$(`#${me.id} .dir-tab`).click(function () {
			$(`#${me.id} .view-tab`).removeClass('active');
			$(`#${me.id} .dir-tab`).addClass('active');
			$(`#${me.id} .select-list`).removeClass('active');
			$(`#${me.id} .dir-select-list`).addClass('active');
		});

	};
	
	me.refresh = function(data) {
		if (data.action == 'get-file-select-html') {
			me.state.dirAccess = data.ajax['dir-access'];
			$(`#${me.id}`).html(data.ajax['file-select-html']);
			$(`#${me.id} .crumbs-data`).html(data.ajax['crumbs']);
			$(`#${me.id} .dir-select-list`).html(data.ajax['dir-list']);
			$(`#${me.id} .file-select-list`).html(data.ajax['file-list']);
			me.render();
			return;
		}
		if (data.action == 'dir-select') {
			me.state.dirAccess = data.ajax['dir-access'];
			me.state.cwd = data.ajax['cwd'];
			$(`#${me.id} .crumbs-data`).html(data.ajax['crumbs']);
			$(`#${me.id} .dir-select-list`).html(data.ajax['dir-list']);
			$(`#${me.id} .file-select-list`).html(data.ajax['file-list']);
			return;
		}
	};
	
	me.clickFileTab = function () {
		if ($(`#${me.id} .file-tab`).hasClass('active')) return;
		$(`#${me.id} .view-tab`).toggleClass('active');
		$(`#${me.id} .dir-select-list`).removeClass('active');
		$(`#${me.id} .file-select-list`).addClass('active');
	};

	me.clickDirTab = function () {
		if ($(`#${me.id} .dir-tab`).hasClass('active')) return;
		$(`#${me.id} .view-tab`).toggleClass('active');
		$(`#${me.id} .file-select-list`).removeClass('active');
		$(`#${me.id} .dir-select-list`).addClass('active');
	};

	me.selectDir = function (id, name, url) {
		me.state.selected = null;
		me.state.action = 'dir-select';
		me.state.arg = url;
		me.ajax(me.state);
	};

	me.selectFile = function (id, name, url, thumb) {
		$(`#${me.id} .file-entry`).removeClass('selected');
		$(`#${id}`).addClass('selected');
		me.state.selected =  url;
		me.state.image = thumb;
	};

	me.init(field, cwd, type);
};

/*
 __  __          _                   ____  _
|  \/  | ___  __| |_   _ ___  __ _  |  _ \(_)_ __
| |\/| |/ _ \/ _` | | | / __|/ _` | | | | | | '__|
| |  | |  __/ (_| | |_| \__ \ (_| | | |_| | | |
|_|  |_|\___|\__,_|\__,_|___/\__,_| |____/|_|_|

 ____       _           _
/ ___|  ___| | ___  ___| |_ ___  _ __
\___ \ / _ \ |/ _ \/ __| __/ _ \| '__|
 ___) |  __/ |  __/ (__| || (_) | |
|____/ \___|_|\___|\___|\__\___/|_|

*/

function MavenDirSelector(arg) {
	let me = this;

	me.state = {
		view: 'maven-dir-selector',
		action: null,
		name: null,
		id: null,
		cwd: null, // current working directory
		selected: null, // full URL for selected dir
		image: null, 
		type: null,
		parent: null,
		selectButtonID: null,
	};

	me.dirSelectorDialog = new Dialog();

	me.init = function (arg) {

		let field = arg.widgetName;
		let cwd = arg.mediaURL;
		let type = 'widgetType' in arg ? arg.widgetType : null;
		let parent = 'parentID' in arg ? arg.parentID : null;
		let checkAccess = 'checkAccess' in arg ? arg.checkAccess : false;

		let ts = String(new Date().getTime());
		me.id = me.state.id = `maven-${field}-${ts}`;
		me.state.name = field;
		me.state.cwd = cwd;
		me.state.type = type;
		me.state.parent = parent;
		me.state.checkAccess = checkAccess;
		MAVEN_INSTANCE[me.id] = me;

		let title = 'Select Directory';
		if (me.state.type == 'move-target') {
			title = 'Select Target Directory';
		}

		me.state.selectButtonID = 'MavenDirSelector-SelectButton-' +  String(new Date().getTime());

		me.dirSelectorDialog.Launch({
			Title: title,
			Height: Math.min(500, 0.9*$(window).height()),
			Width: Math.min(600, 0.9*$(window).width()),
			Content: `<div id="${me.id}"></div>`,
			Buttons: [{
					Name: 'Select Directory',
					Function: function () {
						if (me.state.selected) {
							if (me.state.checkAccess && me.state.dirAccess < 2) {
								let dialog = new Dialog();
								dialog.Error("You cannot select this directory.");
								return;
							}
							me.dirSelectorDialog.Close();
							if (me.state.type == 'move-target') {
								MAVEN_INSTANCE[me.state.parent].executeMoveFile(me.state.selected);
							}
							else {
								$(`#maven-${me.state.name}-widget .maven-input`).val(me.state.selected);
								$(`#maven-${me.state.name}-widget .maven-mirror`).val(me.state.selected);
							}
						}
					},
					Class: me.state.selectButtonID,
				},
				{
					Name: 'Cancel',
					Function: me.dirSelectorDialog.Close
				},
			],
		});

		me.state.action = 'get-dir-select-html';
		me.ajax(me.state);

	};

	me.ajax = function(postData) {
		let title = me.state.action;
		let words = title.split("-");
		for (let i = 0; i < words.length; i++) {
			words[i] = words[i][0].toUpperCase() + words[i].substr(1);
		}
		title = words.join(" ") + ' Error';
		$.ajax({
			url: MAVEN_CONST.url.refresh,
			type: 'POST',
			data: postData,
			dataType: 'json',
			success: function (responseData) {
				if (responseData.valid) {
					me.refresh(responseData);
				} else {
					if ('error' in data) {
						mavenFunctionFactory.errorMessage(title, data.error);
					}
					else {
						mavenFunctionFactory.errorMessage(title);
					}
				}
			},
			error: function(request, status, error) {
				me.statusMessage('Ready');
				mavenFunctionFactory.errorMessage(title, request.responseText);
			},
		});
	};

	me.render = function() {
	};
	
	me.refresh = function(data) {
		if (data.action == 'get-dir-select-html') {
			me.state.dirAccess = data.ajax['dir-access'];
			$(`#${me.id}`).html(data.ajax['dir-select-html']);
			$(`#${me.id} .crumbs-data`).html(data.ajax['crumbs']);
			$(`#${me.id} .dir-select-list`).html(data.ajax['dir-list']);
			me.render();
			return;
		}
		if (data.action == 'dir-select') {
			me.state.dirAccess = data.ajax['dir-access'];
			me.state.cwd = data.ajax['cwd'];
			me.state.selected =  me.state.cwd;
			$(`#${me.id} .crumbs-data`).html(data.ajax['crumbs']);
			$(`#${me.id} .dir-select-list`).html(data.ajax['dir-list']);
			if ((me.state.checkAccess) && (me.state.dirAccess < 2)) {
				$(`.${me.state.selectButtonID}`).addClass('disabled');
			} else {
				$(`.${me.state.selectButtonID}`).removeClass('disabled');
			}
			return;
		}
	};
	
	me.selectDir = function (id, name, url) {
		me.state.selected =  me.state.cwd;
		me.state.action = 'dir-select';
		me.state.arg = url;
		me.ajax(me.state);
	};

	me.init(arg);
};

/*
 __  __          _                   _____            _
|  \/  | ___  __| |_   _ ___  __ _  | ____|_  ___ __ | | ___  _ __ ___ _ __
| |\/| |/ _ \/ _` | | | / __|/ _` | |  _| \ \/ / '_ \| |/ _ \| '__/ _ \ '__|
| |  | |  __/ (_| | |_| \__ \ (_| | | |___ >  <| |_) | | (_) | | |  __/ |
|_|  |_|\___|\__,_|\__,_|___/\__,_| |_____/_/\_\ .__/|_|\___/|_|  \___|_|
                                               |_|
 */

function MavenExplorer(arg) {
	let me = this;

	me.state = {
		id: null,
		view: 'maven-wrapper',
		action: null,
		cwd: null,
		type: 'file',
	};

	me.fileUploadDialog = null;

	/***********************************************************************************************
	 * MavenExplorer constructor.
	 * 
	 * ## Usage
	 * 
	 * ```
	 * let explorer = new MavenExplorer({
	 *     mid: `media-explorer-` + String(new Date().getTime()),
	 *     height: 650,
	 * });
	 * ```
	 * 
	 * ## Arguments
	 * 
	 * - `arg`: object (supports attributes `mid`, `ribbon`, `height`)
	 * 
	 * ## Returns
	 * 
	 * MavenExplorer object.  
	 * 
	 ***********************************************************************************************/		
	me.init = function (arg = {}) {
		// Check arguments.
		let valid = {
			mid:    {required: true},
			ribbon: {type: 'object', default: DEFAULT_RIBBON_DEF, required: false},
			height: {default: 0, required: false},
		};
		mavenFunctionFactory.validateArgs(me, arg, valid);
		
		// Launch ribbon.
		me.ribbon = new MavenRibbon({
			mid: me.mid,
			data: me.ribbon,
			parent: me,
		});

		// Render the HTML.
		me.statusMessage('Ready');
		if (me.height > 0) {
			me.setHeight(me.height);
		}
		me.afterFileSelect();

		me.state.id = me.mid;
		me.fileUploadDialog = new Dialog();
		MAVEN_INSTANCE[me.mid] = me;
	};

	/***********************************************************************************************
	 * Called on successful ajax request. This method processes the response data. Updates the 
	 * HTML view and renders any message or error dialogs as directed by the response data.  
	 * 
	 * ## Arguments
	 * 
	 * - `data`: response data from the successful ajax request
	 * 
	 * ## Algorithm
	 * 
	 * 1. Set `action` = `me.state.action`.
	 * 2. Resets `me.state.action` and `me.state.arg`.
	 * 3. Render error dialog if `data.error` is defined.
	 * 4. Expect action to be one of: 'dir-select', 'file-delete', 'file-move', 'directory-create',
	 *    'get-file-upload-form', or 'file-upload'. Service the requested action.  This includes 
	 *    rendering any dialog messages and updating the view.
	 * 
	 ***********************************************************************************************/		
	me.refresh = function(data) {
		let action = me.state.action;
		delete me.state.action;
		delete me.state.arg;
		// Process any error.
		if (data.error) {
			let dialog = new Dialog();
			dialog.Error(data.error);
			me.statusMessage('<i class="fas fa-exclamation-triangle"></i> Operation failed')
			return;
		}
		// For actions: dir-select, file-delete, file-move, directory-create.
		if (action == 'dir-select' || action == 'file-delete' || action == 'file-move' || action == 'directory-create') {
			me.state.dirAccess = data.ajax['dir-access'];
			me.state.cwd = data.ajax['cwd'];
			me.updateView(data);
			if ('message' in data) {
				let dialog = new Dialog();
				dialog.Info(data.message);
			}
			return;
		}
		// For action get-file-upload-form.
		if (action == 'get-file-upload-form') {
			me.fileUploadDialog.Launch({
				Title: 'File Upload',
				Width: Math.min(0.9*$(window).width(), 600),
				Height: Math.min(0.9*$(window).height(), 470),
				Content: data.ajax['upload-form'],
				Buttons: [
					{
						Name: 'Cancel',
						Function: me.fileUploadDialog.Close
					},
				],
			});
			return;
		}
		// For action file-upload.
		if (action == 'file-upload') {
			me.fileUploadDialog.Close();
			me.state.cwd = data.ajax['cwd'];
			me.updateView(data);
			let dialog = new Dialog();
			dialog.Info(data.message);
			return;
		}
	};

	/***********************************************************************************************
	 * Called during `me.refresh()` if it that function needs to update the view.  
	 * 
	 * ## Arguments
	 * 
	 * - `data`: response data from the successful ajax request
	 * 
	 * ## Algorithm
	 * 
	 * 1. Update HTML `crumbs-data` class with `data.ajax['crumbs']`.
	 * 2. Update HTML `dir-list` class with `data.ajax['dir-list']`.
	 * 3. Update HTML `file-list` class with `data.ajax['file-list']`.
	 * 
	 ***********************************************************************************************/		
	me.updateView = function(data) {
		me.state.dirAccess = data.ajax['dir-access'];
		$(`#${me.mid} .crumbs-data`).html(data.ajax['crumbs']);
		$(`#${me.mid} .dir-list`).html(data.ajax['dir-list']);
		$(`#${me.mid} .file-list`).html(data.ajax['file-list']);
		me.afterFileSelect();
	};

	/***********************************************************************************************
	 * Callback when file is clicked.  
	 ***********************************************************************************************/		
	me.selectFile = function(id, name, url) {
		if ($(`#${id}`).hasClass('selected')) {
			$(`#${id}`).removeClass('selected');
		} else {
			$(`#${id}`).addClass('selected');
		}
		me.afterFileSelect();
	};

	/***********************************************************************************************
	 * Callback when file move button is clicked.  
	 ***********************************************************************************************/		
	me.moveFile = function () {
		if (!me.canUpdateSelectedFiles()) return;
		// me.state.action = 'file-move';
		new MavenDirSelector
		(
			{
				'widgetName': String(new Date().getTime()), 
				'mediaURL': '', 
				'widgetType': 'move-target',
				'parentID': me.state.id,
				'checkAccess': true,
			}
		);
	};

	/***********************************************************************************************
	 * Execute file move action.  
	 ***********************************************************************************************/		
	me.executeMoveFile = function(moveToDir) {
		me.state.action = 'file-move';
		me.state.source = me.state.cwd;
		me.state.target = moveToDir;
		me.state.files = JSON.stringify(me.state.selectedFiles);
		// me.state.arg = JSON.stringify(me.state.selectedFiles);
		me.ajax();
	};

	/***********************************************************************************************
	 * Callback when file upload button is clicked.  
	 ***********************************************************************************************/		
	me.uploadFile = function() {
		if (!me.canUpdateCurrentDir()) return;
		me.state.action = 'get-file-upload-form';
		if ('arg' in me.state) delete me.state.arg;
		me.statusMessage('Getting upload form ...', true);
		me.ajax();
	};

	/***********************************************************************************************
	 * Execute file upload action.  
	 ***********************************************************************************************/		
	me.executeUploadFile = function(ajaxData) {
		if (!me.canUpdateCurrentDir()) return;
		me.state.action = 'file-upload';
		ajaxData.append('id', me.state.id);
		ajaxData.append('action', 'file-upload');
		ajaxData.append('arg', me.state.cwd);
		$.ajax({
			url: MAVEN_CONST.url.refresh,
			data: ajaxData,
			type: 'POST',
			contentType: false, // NEEDED, DON'T OMIT THIS (requires jQuery 1.6+)
			processData: false, // NEEDED, DON'T OMIT THIS
			success: function (data) {
				me.statusMessage('Ready');
				if (data.valid) {
					me.refresh(data);
				} else {
					if ('error' in data) {
						mavenFunctionFactory.errorMessage('File Upload Error', data.error);
					}
					else {
						mavenFunctionFactory.errorMessage('File Upload Error');
					}
				}
			},
			error: function(request, status, error) {
				me.statusMessage('Ready');
				mavenFunctionFactory.errorMessage('File Upload Error', request.responseText);
			},
		});

	};
	
	/***********************************************************************************************
	 * Callback when delete file button is clicked.  
	 ***********************************************************************************************/		
	me.deleteFile = function () {
		let dialog = new Dialog();
		if (!(me.state.selectedFiles) || (me.state.selectedFiles.length == 0)) {
			dialog.Error('No files selected.')
		}
		if (!me.canUpdateSelectedFiles()) return;
		let html = [];
		let numFilesSelected = me.state.selectedFiles.length;
		let s = numFilesSelected == 1 ? '' : 's';
		if (numFilesSelected == 1) {
			html.push(`Delete file ${me.state.selectedFiles[0].filename}?`);
		} else {
			html.push(`Delete ${numFilesSelected} files?`);
		}
		html.push(`<p></p>`);
		dialog.Launch({
			Title: `Delete File${s}`,
			Icon: 'question',
			Content: html.join(''),
			Buttons: [
				{
					Name: 'Yes',
					Function: function () {
						me.state.action = 'file-delete';
						me.state.arg = JSON.stringify(me.state.selectedFiles);
						dialog.Close();
						me.ajax();
					}
				},
				{
					Name: 'No',
					Function: dialog.Close
				},
			],
		});
	};

	/***********************************************************************************************
	 * Callback when open file button is clicked.  
	 ***********************************************************************************************/		
    me.openFile = function() {
        let url = '';
        if (me.state.cwd.length > 0) {
            url = `${HTTP_MEDIA_URL}${me.state.cwd}/${me.state.selectedFiles[0].filename}`;
        } else {
            url = `${HTTP_MEDIA_URL}${me.state.selectedFiles[0].filename}`;
        }
        window.open(url, '_blank');
    };

	/***********************************************************************************************
	 * Callback when get file link button is clicked.  
	 ***********************************************************************************************/		
    me.getFileLink = function() {
        let url = '';
        if (me.state.cwd.length > 0) {
            url = `${HTTP_MEDIA_URL}${me.state.cwd}/${me.state.selectedFiles[0].filename}`;
        } else {
            url = `${HTTP_MEDIA_URL}${me.state.selectedFiles[0].filename}`;
        }
        let html = [];
        html.push(`<p>Right click on the URL link below and select <strong>Copy Link Address</strong> to copy to the clipboard.</p>`)
        html.push(`<p><strong>File:</strong><br>${me.state.selectedFiles[0].filename}</p>`)
        html.push(`<p><strong>URL:</strong><br><a href="${url}" style="font-size: 80%;">${url}</a></p>`)
		let dialog = new Dialog();
		dialog.Launch({
			Title: `File Link`,
			Content: html.join(''),
            Height: 360,
			Buttons: [
				{
					Name: 'OK',
					Function: dialog.Close
				},
			],
		});
    };

	/***********************************************************************************************
	 * Callback when delete directory button is clicked. (FIX!!! Not implemented.  Maybe remove?)  
	 ***********************************************************************************************/		
	me.deleteDirectory = function () {
		me.state.action = 'directory-delete';
	};

	/***********************************************************************************************
	 * Callback when create directory button is clicked.
	 ***********************************************************************************************/		
	me.launchCreateDirectoryDialog = function () {
		let dialog = new Dialog();
		let html = [];
		html.push(`<p>Enter new directory name:<br>`);
		html.push(`<input id="${me.mid}-new-directory-name" type="text" style="width: 100%;">`);
		html.push(`<div id="${me.mid}-new-directory-error" style="position: relative; top: -10px; color: red; font-size: 12px; line-height: 14px;"></p>`);
		dialog.Launch({
			Title: 'Create Directory',
			Height: 260,
			Width: 330,
			Content: html.join(''),
			Buttons: [{
					Name: 'Create',
					Function: function () {
						delete me.state.action;
						delete me.state.arg;
						let name = $(`#${me.mid}-new-directory-name`).val();
						if (/^([\w \-])+$/.test(name)) {
							dialog.Close();
							me.state.action = 'directory-create';
							if (me.state.cwd.length == 0) {
								me.state.arg = JSON.stringify([me.state.cwd, name]);
							}
							else {
								me.state.arg = JSON.stringify([me.state.cwd, me.state.cwd + '/' + name]);
							}
							me.ajax();
						} else {
							$(`#${me.mid}-new-directory-error`).html(`<strong>ERROR</strong>: Directory name can only consist of letters, numbers, underscores, spaces and dashes.`)
						}
					}
				},
				{
					Name: 'Cancel',
					Function: dialog.Close
				},
			],
		});
	};

	/***********************************************************************************************
	 * Callback when select all files button is clicked.
	 ***********************************************************************************************/		
	me.selectAllFiles = function () {
		$(`#${me.mid} .file-entry`).addClass('selected');
		me.afterFileSelect();
	};

	/***********************************************************************************************
	 * Callback when unselect all files button is clicked.
	 ***********************************************************************************************/		
	me.unselectAllFiles = function () {
		$(`#${me.mid} .file-entry`).removeClass('selected');
		me.afterFileSelect();
	};

	/***********************************************************************************************
	 * Callback when toggle all files button is clicked.
	 ***********************************************************************************************/		
	me.toggleAllFiles = function () {
		$(`#${me.mid} .file-entry`).toggleClass('selected');
		me.afterFileSelect();
	};

	/***********************************************************************************************
	 * Callback when select directory button is clicked.
	 ***********************************************************************************************/		
	me.selectDir = function (id, name, url) {
		me.state.action = 'dir-select';
		me.state.arg = url;
		me.statusMessage('Refreshing view ...', true);
		me.ajax();
	};

	/***********************************************************************************************
	 * Callback when home directory button is clicked.
	 ***********************************************************************************************/		
	me.homeDirectory = function() {
		me.selectDir(null, '', '');
	};

	/***********************************************************************************************
	 * Callback when change directory up button is clicked.
	 ***********************************************************************************************/		
	me.changeDirUp = function() {
		if (me.state.cwd.length == 0) {
			me.selectDir(null, '', '');
		}
		else {
			let parts = me.state.cwd.split('/');
			parts.pop();
			let url = parts.join('/');
			me.selectDir(null, '', url);
		}
	};	

	/***********************************************************************************************
	 * Execute AJAX action.  
	 ***********************************************************************************************/		
	me.ajax = function() {

		let title = me.state.action;
		let words = title.split("-");
		for (let i = 0; i < words.length; i++) {
			words[i] = words[i][0].toUpperCase() + words[i].substr(1);
		}
		title = words.join(" ") + ' Error';

		$.ajax({
			url: MAVEN_CONST.url.refresh,
			type: 'POST',
			data: me.state,
			dataType: 'json',
			success: function (data) {
				me.statusMessage('Ready');
				if (data.valid) {
					me.refresh(data);
				} else {
					if ('error' in data) {
						mavenFunctionFactory.errorMessage(title, data.error);
					}
					else {
						mavenFunctionFactory.errorMessage(title);
					}
				}
			},
			error: function(request, status, error) {
				me.statusMessage('Ready');
				mavenFunctionFactory.errorMessage(title, request.responseText);
			},
		});
	};

	/***********************************************************************************************
	 * Set height of Explorer view.  
	 ***********************************************************************************************/		
	me.setHeight = function (val) {
		let info = {};
		info.instHeight = $(`#${me.mid}`).outerHeight();
		info.fileListHeight = $(`#${me.mid} .file-list`).outerHeight();
		info.fileListAdjust = val - info.instHeight;
		info.newFileListHeight = info.fileListHeight + info.fileListAdjust;
		$(`#${me.mid} .file-list`).css({
			'min-height': info.newFileListHeight,
			'max-height': info.newFileListHeight,
			'height': info.newFileListHeight,
		});
		info.newInstHeight = $(`#${me.mid}`).outerHeight();
	};

	/***********************************************************************************************
	 * Display debug dialog showing me.state values.  
	 ***********************************************************************************************/		
	me.showState = function () {
		let stateJSON = JSON.stringify(me.state, null, 2);
		let dialog = new Dialog();
		dialog.Launch({
			Title: 'State',
			Width: 800,
			Height: 500,
			Content: `<pre style="font-family: monospace;">${stateJSON}</pre>`,
		});
	};

	/***********************************************************************************************
	 * Display about dialog.  
	 ***********************************************************************************************/		
	me.showAbout = function() {
		let width = Math.floor(Math.min($(window).width()-70, 500));
		let height = Math.floor(width * (550/700));
		let top = Math.floor(height * 0.4);
		let fontSize = 12;
		let lineHeight = 14;
		let padding = 20;
		if ($(window).width() > 500) {
			top = Math.floor(height * 0.45);
			fontSize = 18;
			lineHeight = 20;
			padding = 40;
		}
		let dialog = new Dialog();
		dialog.Launch({
			Title: 'About',
			Width: width+55,
			Height: height+150,
			Content: 
			`
			<div style="height: ${height}px; width: ${width}px; position: relative;">
			<img style="height: ${height}px; width: ${width}px; position: absolute; top: 0; left: 5px;" src="${MAVEN_CONST.url.static}maven/img/misc/About.png">
			<div style="font-size: ${fontSize}px; line-height: ${lineHeight}px; padding: 0 ${padding}px; position: relative; top: ${top}px; left: 5px; width: 100%; color: #fff; text-align: center;">
			<div style="margin-top: 15px; font-size: 100%; word-wrap: break-word;">Version: ${MAVEN_CONST.version}</div>
			<div style="margin-top: 15px; font-size: 100%; word-wrap: break-word;">Media Maven is a Django app for managing media files.</div>
			<div style="margin-top: 15px; font-size: 100%; word-wrap: break-word;">rodney.kadura@gmail.com</div>
			</div>
			</div>
			`,
		});
	};

	/***********************************************************************************************
	 * Log debug statement to console.  
	 ***********************************************************************************************/		
	me.debugLog = function (val) {
		console.log(val);
	};

	/***********************************************************************************************
	 * Render Explorer status bar message.  
	 ***********************************************************************************************/		
	me.statusMessage = function (val, spinner = false) {
		if (spinner) {
			val = '<i class="fas fa-spinner fa-spin"></i> ' + val;
		}
		$(`#${me.mid} .footer .text`).html(val);
	};

	/***********************************************************************************************
	 * Helper function called after files are selected.  
	 ***********************************************************************************************/		
	me.afterFileSelect = function () {
		let total = $(`#${me.mid} .file-entry`).length;
		let selected = $(`#${me.mid} .file-entry.selected`).length;
		let s = total == 1 ? '' : 's';
		me.statusMessage(`${selected} of ${total} file${s} selected`);
		if (selected == 0) {
			me.ribbon.disableButton('file-move');
			me.ribbon.disableButton('file-delete');
			me.ribbon.disableButton('file-link');
			me.ribbon.disableButton('file-open');
		} else {
            if (selected == 1) {
                me.ribbon.enableButton('file-link');
                me.ribbon.enableButton('file-open');
            } else {
                me.ribbon.disableButton('file-link');
                me.ribbon.disableButton('file-open');
            }
            me.ribbon.enableButton('file-move');
			me.ribbon.enableButton('file-delete');
		}
		me.state.selectedFiles = [];
		$(`#${me.mid} .file-entry.selected`).each(
			function () {
				let data = {
					index: $(this).attr('index'),
					filename: $(this).find('.filename').html(),
					canEdit: Boolean(parseInt($(this).find('.filename').attr('access'))),
				};
				me.state.selectedFiles.push(data);
			}
		);
	};

	/***********************************************************************************************
	 * Check if user has access to update the current working directory.  
	 ***********************************************************************************************/		
	me.canUpdateCurrentDir = function() {
		if (me.state.dirAccess < 2) {	
			let dialog = new Dialog();
			dialog.Error(`Sorry, you do not have access to perform the requested action in this directory.`);
			return false;
		} 
		return true;
	};

	/***********************************************************************************************
	 * Check if user has access to modify selected files.  
	 ***********************************************************************************************/		
	me.canUpdateSelectedFiles = function() {

		if (!(me.state.selectedFiles) || (me.state.selectedFiles.length == 0)) {
			let dialog = new Dialog();
			dialog.Warning('No files selected.')
			return false;
		}

		let canEditAll = true;
		let accessFails = 0;
		let fileCount = me.state.selectedFiles.length;
		for (let file of me.state.selectedFiles) {
			if (!file.canEdit) {
				canEditAll = false;
				accessFails++;
			}
		}

		if (!canEditAll) {
			let dialog = new Dialog();
			if (fileCount == 1) {
				dialog.Error(`Sorry, you do not have access to perform the requested action on the file.`);
			}
			else {
				dialog.Error(`Sorry, you do not have access to perform the requested action on ${accessFails} of ${fileCount} files.`);
			}
			return false;
		}
		return true;
	};

	me.init(arg);
};

function mavenSelectDir(mid, eid, name, url) {
	MAVEN_INSTANCE[mid].selectDir(eid, name, url);
};

function mavenSelectFile(mid, eid, name, url, thumb=null) {
	MAVEN_INSTANCE[mid].selectFile(eid, name, url, thumb);
};

function mavenFileUpload(mid, ajaxData) {
	MAVEN_INSTANCE[mid].executeUploadFile(ajaxData);
};

function mavenFileSelectorWidgetSet(widgetName, mediaURL, widgetType) {
	new MavenFileSelector(widgetName, mediaURL, widgetType);
}

function mavenFileSelectorWidgetClear(widgetName, widgetType) {
	$(`#maven-${widgetName}-widget .maven-mirror`).val('');
	$(`#maven-${widgetName}-widget .maven-input`).val('');
	if (widgetType == 'image') {
		$(`#maven-${widgetName}-widget .maven-image`).html('');
	}
}

function mavenDirSelectorWidgetSet(widgetName, mediaURL, widgetType) {
	new MavenDirSelector
	(
		{
			'widgetName': widgetName, 
			'mediaURL': mediaURL, 
			'widgetType': widgetType,
		}
	);
}

function mavenDirSelectorWidgetClear(widgetName, widgetType) {
	$(`#maven-${widgetName}-widget .maven-mirror`).val('');
	$(`#maven-${widgetName}-widget .maven-input`).val('');
}

