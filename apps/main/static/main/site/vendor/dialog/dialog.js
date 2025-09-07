"use strict";

var SWANK_DIALOG_SCRIPT_PATH = document.currentScript.src.split('/').slice(0, -1).join('/');
var SWANK_ACTIVE_DIALOG_COUNT = 0;
var SWANK_INDEX_LIST = [];

/*
  ____             __ _          ___        _   _
 / ___|___  _ __  / _(_) __ _   / _ \ _ __ | |_(_) ___  _ __  ___
| |   / _ \| '_ \| |_| |/ _` | | | | | '_ \| __| |/ _ \| '_ \/ __|
| |__| (_) | | | |  _| | (_| | | |_| | |_) | |_| | (_) | | | \__ \
 \____\___/|_| |_|_| |_|\__, |  \___/| .__/ \__|_|\___/|_| |_|___/
                        |___/        |_|
*/

var SWANK_DIALOG_CONFIG =
{
	/* =============================================================================================
	 * Disable vertical scrollbar when dialog is displayed?
	 * ---------------------------------------------------------------------------------------------
	 * If true, the vertical scrollbar for the page is hidden when a dialog is displayed.  This 
	 * has the effect of not allowing the user to scroll up or down out of the current view until 
	 * he/she dismisses the dialog.  Depending on the application, it may or may not make sense to 
	 * do this, and there are tradeoffs.  If you choose to disable the vertical scroll bar, it can 
	 * cause elements to resize as they adjust to the missing scrollbar.  To solve this problem, I 
	 * attempt to add right padding to the body when the scrollbar is hidden, this only if the 
	 * window is larger than that of a mobile device.  In the case of mobile devices, the vertical
	 * scrollbar doesn't take up space in the view.  If you don't hide the vertical scrollbar, you
	 * will be able to move up or down when the dialog is displayed.  You may also notice that the
	 * scrollbar dimensions change.  This is because the dialog adds height to the view.  
	 * =============================================================================================
	 */
	'DisableScrollBar': false,

	/* =============================================================================================
	 * Perform slide up effect when a dialog is dismissed?
	 * ---------------------------------------------------------------------------------------------
	 * If true, a slide up animation is performed on the dialog as it is being dismissed.  
	 * =============================================================================================
	 */
	'SlideUpOnExit': true,

	/* =============================================================================================
	 * Allow dialog to be moveable?
	 * ---------------------------------------------------------------------------------------------
	 * If true, users can click on the header and drag-move a dialog.  
	 * =============================================================================================
	 */
	'IsMovable': true,

	/* =============================================================================================
	 * Fade out time in milliseconds.
	 * ---------------------------------------------------------------------------------------------
	 * When a dialog is displayed or dismissed, a fade out effect is used.  Setting this value 
	 * configures the time, in milliseconds, for the effect.
	 * =============================================================================================
	 */
	'FadeOutTime': 300,
};

function Dialog()
{
	var me = this;

	me.index = 0;

	// Global variables used to if DisableScrollBar config option is true.
	me.rightBodyPaddingValue = 0;
	me.rightBodyPaddingModified = false;

	// Used when dialog movable.
	me.pos1 = 0;
	me.pos2 = 0;
	me.pos3 = 0;
	me.pos4 = 0;

	/*
		 ____        _     _ _        __  __      _   _               _
		|  _ \ _   _| |__ | (_) ___  |  \/  | ___| |_| |__   ___   __| |___
		| |_) | | | | '_ \| | |/ __| | |\/| |/ _ \ __| '_ \ / _ \ / _` / __|
		|  __/| |_| | |_) | | | (__  | |  | |  __/ |_| | | | (_) | (_| \__ \
		|_|    \__,_|_.__/|_|_|\___| |_|  |_|\___|\__|_| |_|\___/ \__,_|___/
		
	*/

	/* =============================================================================================
	 * Launch(Settings) 
	 * ---------------------------------------------------------------------------------------------
	 * Launch a dialog.  Settings are:
	 * - Title: Title that appears on the header bar (Default = '')
	 * - Content: HTML content for the button.
	 * - Icon: If specified, the dialog will be rendered with an image on the left, and the content
	 *     on the right.  If Icon is one of 'info', 'warning', 'error' or 'question', the default
	 *     image for each of those types is used.  Otherwise, Icon is expected to be an image file.
	 * - Width: Width of the dialog in pixels.  The width will be truncated to 90% of the window 
	 *     width if a value greater than the window width is specified. (Default = 500)
	 * - Height: Height of the dialog in pixels.  (Default = 300)
	 * - Buttons: List of button objects to be displayed.  Each button object must match the form
	 *     {Name: <Button Text>, Function: <Function to Do>}. By default, a single "OK" button is 
	 *     displayed that, when clicked, dismisses the dialog.
	 * - CSS: A hash object, similar to what you would pass to $('some-elem').css().  Use this
	 *     to configure the content.  For example, CSS is implicitly used by ScrollText() to set a 
	 *     scrollbar in the content div.  But you can use if for whatever you desire.
	 * - OnClose: Action to be performed when the dialog is closed via the close button on the
	 *     header. Default is the .Close() method.  If you specify an OnClose value, it must 
	 *     include the .Close() method if you want to dismiss the dialog.  NOTE: OnClose is not 
	 *     exercised with the dialog is closed with an option button from the button bar.  If you
	 *     want OnClose to be exercised there, you must explicitly call it.  
	 * - OnRender: Action to be performed after the dialog is rendered.
	 * =============================================================================================
	 */
	me.Launch = function(Settings)
	{
		// Create a unique index for the dialog elements to be created.
		me.index = new Date().getTime();

		// Create and dialog elements.  This does not, as yet, create the dialog itself.  But it 
		// creates an empty container for the dialog that we will later populate.
		$('body').append(`<div id="DialogBackground-${me.index}" class="DialogBackground"></div>`);
		$('body').append(`<div id="DialogWrapper-${me.index}" class="DialogWrapper"></div>`);
		$(`#DialogWrapper-${me.index}`).html
		(
			`<div id="DialogWindow-${me.index}" class="DialogWindow">
				<div class="HeaderBar">
					<div class="Title"></div>
					<div class="CloseButton"><img src="${SWANK_DIALOG_SCRIPT_PATH}/img/close.png"></div>
				</div>
				<div class="Body">
					<div class="Content"></div>
					<div class="Line"></div>
					<div class="ButtonBar"></div>
				</div>			
			</div>`
		);

		// Make the dialog draggable.
		if (SWANK_DIALOG_CONFIG['IsMovable'])
		{
			me._makeDialogDraggable();
		}

		// Nested dialogs are possible.  The SWANK_INDEX_LIST keep track of all dialogs.  Only the
		// topmost will be active.  For now, that means we inactivate all.  Later, after creating
		// the new dialog, we will activate it.  
		SWANK_INDEX_LIST.push(me.index);
		for (let i = 0; i < SWANK_INDEX_LIST.length - 1; i++)
		{
			let index = SWANK_INDEX_LIST[i];
			$(`#DialogWrapper-${index}`).addClass('Inactive');
		}

		// Increment the global dialog count.
		SWANK_ACTIVE_DIALOG_COUNT++;

		// Process settings. 
		if (!('Title' in Settings)) Settings.Title = '';
		if (!('Content' in Settings)) Settings.Content = '';
		if (!('Width' in Settings)) Settings.Width = 500;
		if (!('Height' in Settings)) Settings.Height = 300;
		if (!('OnClose' in Settings)) Settings.OnClose = me.Close;
		if (!('Buttons' in Settings)) 
		{
			Settings.Buttons =
			[
				{Name: 'OK', Function: me.Close},
			];
		}

		// Create the dialog content.
		let content = Settings.Content;
		if ('Icon' in Settings)
		{
			let iconLink = Settings.Icon;
			let cannedButtons = ['info', 'error', 'warning', 'question'];
			if (cannedButtons.includes(Settings.Icon))
			{
				iconLink = SWANK_DIALOG_SCRIPT_PATH + '/img/' + Settings.Icon + '.png';
			}
			let TopPadding = 0;
			if (Settings.Content.length > 100) TopPadding = 5;
			let Content = [];
			Content.push('<table><tr>');
			Content.push('<td style="vertical-align: top; padding: 5px;"><div style="height: ' + TopPadding + 'px;"></div><img src="' + iconLink + '"></td>');
			Content.push('<td style="vertical-align: top; padding: 5px;">' + Settings.Content + '</td>');
			Content.push('</tr></table>');
			content = Content.join('');
		}

		// Configure the buttons.
		let ButtonsHTML = [];
		for (let i = 0; i < Settings.Buttons.length; i++)
		{
			if ('Width' in Settings.Buttons[i])
			{
				ButtonsHTML.push('<a class="btn btn-primary Button Button' + i + '" href="javascript:void(0)" style="min-width: 50px; width: ' + Settings.Buttons[i].Width + 'px;">' + Settings.Buttons[i].Name + '</a>');
			}
			else
			{
				ButtonsHTML.push('<a class="btn btn-primary Button Button' + i + '" href="javascript:void(0)" style="min-width: 50px;">' + Settings.Buttons[i].Name + '</a>');
			}
		}

		// Clear dialog background.  
		$(`#DialogBackground-${me.index}`).html('');
		
		// Don't allow the dialog to be larger than the window width -20. 
		let smallerBy = 20;
		let settingsWidth = Math.min(Settings.Width, $(window).outerWidth() - smallerBy);

		// If this is the first active dialog (no nesting) there are a few things that we want to
		// do ...
		if (SWANK_ACTIVE_DIALOG_COUNT == 1) 
		{
			// Disable vertical scroll bar when dialog is displayed (if instructed to do so by the
			// config settings).
			if (SWANK_DIALOG_CONFIG['DisableScrollBar'])
			{
				// This command hides the vertical scrollbar ...
				$('html').css('overflow-y','hidden');

				// And this block of code first looks to see if the window has a vertical scrollbar
				// (i.e. $(document).height() > $(window).height()?).  If so, the code adds padding 
				// to the right side of the body equal to the vertical scrollbar width.  The reason 
				// is that hiding the scrollbar can cause elements on the page to resize.  This is 
				// not the desire effect.  Items on the page shouldn't jump out of place just 
				// because a dialog appears.  The dialog should have the appearance of floating over
				// the page.     
				if ($(document).outerHeight() > $(window).outerHeight())
				{
					me.rightBodyPaddingValue = $('body').css('padding-right');
					$('body').css({'padding-right': parseInt(me.rightBodyPaddingValue) + me.vertScrollBarWidthValue});
					me.rightBodyPaddingModified = true;
				}
			}	
			// Display the grayed out background filter.  This will make the dialog modal.  The user
			// will have to dismiss the dialog before he or she can exercise any functionality on
			// the page.
			$(`#DialogBackground-${me.index}`).css
			(
				{
					'opacity': '0.5', 
					'background-color': '#aaaaaa',
					'height': $(document).outerHeight(),
					'width': $(document).outerWidth(),
				}
			);
		}
		// If this is not the first active dialog, meaning that there are other nested dialogs 
		// visible, make the top one clearly visible (i.e. opacity = 0).  Previously we 
		// inactivated all dialogs.  Now we remedy that with regards to the topmost dialog.
		else 
		{
			$(`#DialogBackground-${me.index}`).css
			(
				{
					'opacity': '0.0', 
					'background-color': '#ffffff'
				}
			);
		}

		// Configure dialog wrapper.
		$(`#DialogWrapper-${me.index}`).css
		(
			{
				'height': $(document).outerHeight(),
				'width': $(document).outerWidth(),
			}
		);

		me.SetSize(settingsWidth, Settings.Height);
		
		$(`#DialogWrapper-${me.index} .ButtonBar`).html(ButtonsHTML.join('&nbsp;&nbsp;'));
		$(`#DialogWrapper-${me.index} .Title`).html(Settings.Title);
		$(`#DialogWrapper-${me.index} .Content`).html(content);

		if ('CSS' in Settings) $(`#DialogWrapper-${me.index} .Content`).css(Settings.CSS);
		$(`#DialogWrapper-${me.index} .CloseButton`).click(Settings.OnClose);
		
		me.Center(false);
		
		// Add click functions to all buttons.  
		for (let i = 0; i < Settings.Buttons.length; i++)
		{
			$(`#DialogWrapper-${me.index} .Button` + i).click(function(){Settings.Buttons[i].Function()});
		}
		if ('OnRender' in Settings) Settings.OnRender();
		
		// Show the dialog immediately and fade in the grayed out background. 
		$(`#DialogWrapper-${me.index}`).show();
		$(`#DialogBackground-${me.index}`).fadeIn(SWANK_DIALOG_CONFIG['FadeOutTime']);

		$(window).resize(function(){me.Refresh();});
	};

	me.SetSize = function(w, h)
	{
		$(`#DialogWrapper-${me.index} .DialogWindow`).css({'height': h, 'width': w});
		$(`#DialogWrapper-${me.index} .Body`).css({'height': h-45, 'width': w-15});
		$(`#DialogWrapper-${me.index} .Content`).css({'height': h-120, 'border': 0});
	};

	me.Center = function(withAnimation)
	{
		if (SWANK_ACTIVE_DIALOG_COUNT == 0) return;
		if ($(`#DialogWindow-${me.index}`).length == 0) return;
		// Configure dialog window.
		let dialogWidth = $(`#DialogWindow-${me.index}`).outerWidth();
		let dialogHeight = $(`#DialogWindow-${me.index}`).outerHeight();
		let docWidth = $(window).outerWidth();

		// Set left edge.
		let left = 0.5*(docWidth-dialogWidth);
		if (docWidth > 500) left -= 10;

		// Center the dialog vertically (not really, we do center -20px because it looks better). If you center on the
		// view, then it looks lower than it really is because of the browser's toolbar.  
		let topWindowPos = $(document).scrollTop();
		let windowHeight = $(window).outerHeight();
		let top = 0.5*(windowHeight-dialogHeight) - 20  + topWindowPos;

		// Cascade nested menus unless we are dealing with mobile screen widths (where we don't 
		// have enough room to do so).
		if ($(window).outerWidth() > 500)
		{
			left += SWANK_ACTIVE_DIALOG_COUNT*10;
		}
		top += SWANK_ACTIVE_DIALOG_COUNT*10;

		// Place the dialog window.
		if (withAnimation)
		{
			$(`#DialogWindow-${me.index}`).animate({'left': left, 'top': top});
		}
		else
		{
			$(`#DialogWindow-${me.index}`).css({'left': left, 'top': top});
		}
	};

	me.servicingRefreshRequest = false;
	me.lastRefreshTimeStamp = Date.now();
	me.inRefreshTimeout = false;

	me.Refresh = function()
	{
		// Configure dialog wrapper.
		$(`#DialogBackground-${me.index}`).css
		(
			{
				'height': $(document).outerHeight(),
				'width': $(document).outerWidth(),
			}
		);
		$(`#DialogWrapper-${me.index}`).css
		(
			{
				'height': $(document).outerHeight(),
				'width': $(document).outerWidth(),
			}
		);

		me.lastRefreshTimeStamp = Date.now();
		me.inRefreshTimeout = true;
		setTimeout
		(
			function() 
			{
				let interval = Date.now() - me.lastRefreshTimeStamp;
				if (interval > 50)
				{
					me._Refresh();
				}
				me.inRefreshTimeout = false;
			},
			100
		);
	};

	me._Refresh = function()
	{
		if (SWANK_ACTIVE_DIALOG_COUNT == 0) return;
		if ($(`#DialogWindow-${me.index}`).length == 0) return;
		if (me.servicingRefreshRequest) return;
		me.servicingRefreshRequest = true;

		let p = $(`#DialogWindow-${me.index}`).position();

		let dialogWidth = $(`#DialogWindow-${me.index}`).outerWidth();
		let dialogHeight = $(`#DialogWindow-${me.index}`).outerHeight();
		let dialogLeft = p.left;
		let dialogTop = p.top;
		let dialogRight = dialogLeft + dialogWidth;
		let dialogBottom = dialogTop + dialogHeight;

		let windowWidth = $(window).outerWidth();
		let windowHeight = $(window).outerHeight();
		let windowLeft = $(window).scrollLeft();
		let windowTop = $(window).scrollTop();
		let windowRight = windowLeft + windowWidth - 10;
		let windowBottom = windowTop + windowHeight - 10;

		console.log('in Refresh()');
		console.log(` dialogLeft=${dialogLeft}`);
		console.log(` windowLeft=${windowLeft}`);
		console.log(` dialogRight=${dialogRight}`);
		console.log(` windowRight=${windowRight}`);
		console.log(` dialogWidth=${dialogWidth}`);
		console.log(` windowWidth=${windowWidth}`);

		let offset = 20;
		if (me.vertScrollBarHiddenFunc()) offset += me.vertScrollBarWidthValue;
		if (dialogWidth > windowWidth - offset)
		{
			console.log("Resizing window ...");
			me.SetSize(windowWidth - offset, dialogHeight);
			me.Center(true);
			me.servicingRefreshRequest = false;
			return;
		}
		if (dialogRight > windowRight)
		{
			console.log("Moving window left ...");
			$(`#DialogWindow-${me.index}`).css('left', windowRight - dialogWidth);
			me.Center(true);
			me.servicingRefreshRequest = false;
			return;
		}
		if (dialogLeft < windowLeft)
		{
			console.log("Moving window right ...");
			$(`#DialogWrapper-${me.index}`).css('left', windowLeft);
			me.Center(true);
			me.servicingRefreshRequest = false;
			return;
		}
		me.servicingRefreshRequest = false;
	};	

	me.ScrollText = function(Arg)
	{
		if (typeof(Arg) == 'string')
		{
			Arg = 
			{
				Content: Arg,
			};
		}
		if (!('Title' in Arg)) Arg.Title = '';
		if (!('Height' in Arg)) Arg.Height = 400;
		if (!('Width' in Arg)) Arg.Width = 500;
		if (!('BackgroundColor' in Arg)) Arg.BackgroundColor = '#fff';
		if (!('Border' in Arg)) Arg.Border = '1px solid #aaa';
		if (!('Buttons' in Arg)) Arg.Buttons = 
		[
			{Name: 'OK', Function: me.Close},
		];
		me.Launch
		(
			{
				Title: Arg.Title,
				Content: Arg.Content,
				Height: Arg.Height,
				Width: Arg.Width,
				CSS: 
				{
					'border': Arg.Border,
					'background-color': Arg.BackgroundColor,
				},
				Buttons: Arg.Buttons,
				OnClose: me.Close,
			}
		);
	};
	
	me.Info = function(Arg)
	{
		if (typeof(Arg) == 'string') {Arg = {Content: Arg};}
		Arg.Icon = 'info';
		Arg.Height = 200;
		Arg.Width = 400;
		me.Launch(Arg);
	};
	
	me.Error = function(Arg)
	{
		if (typeof(Arg) == 'string') {Arg = {Content: Arg};}
		Arg.Icon = 'error';
		if (!('Title' in Arg)) Arg.Title = 'Error';
		Arg.Height = 200;
		Arg.Width = 400;
		me.Launch(Arg);
	};
	
	me.Warning = function(Arg)
	{
		if (typeof(Arg) == 'string') {Arg = {Content: Arg};}
		Arg.Icon = 'warning';
		if (!('Title' in Arg)) Arg.Title = 'Warning';
		Arg.Height = 200;
		Arg.Width = 400;
		me.Launch(Arg);
	};

	me.Close = function()
	{
		SWANK_ACTIVE_DIALOG_COUNT--;
		if (SWANK_ACTIVE_DIALOG_COUNT < 0) SWANK_ACTIVE_DIALOG_COUNT = 0;
		if (SWANK_DIALOG_CONFIG['SlideUpOnExit'])
		{
			$(`#DialogWrapper-${me.index}`).animate({top: "-=35", opacity: 0}, SWANK_DIALOG_CONFIG['FadeOutTime']);
		}
		$(`#DialogWrapper-${me.index}`).fadeOut(SWANK_DIALOG_CONFIG['FadeOutTime']);
		$(`#DialogBackground-${me.index}`).fadeOut(SWANK_DIALOG_CONFIG['FadeOutTime']);
		setTimeout
		(
			function()
			{
				$(`#DialogWrapper-${me.index}`).remove();
				$(`#DialogBackground-${me.index}`).remove();
				if (SWANK_INDEX_LIST.length > 0) 
				{
					SWANK_INDEX_LIST.pop();
					if (SWANK_INDEX_LIST.length > 0)
					{
						let index = SWANK_INDEX_LIST[SWANK_INDEX_LIST.length-1];
						$(`#DialogWrapper-${index}`).removeClass('Inactive');
					}
				}
				// Re-enable scroll bars
				if (SWANK_INDEX_LIST.length == 0) 
				{
					if (SWANK_DIALOG_CONFIG['DisableScrollBar'])
					{
						$('html').css('overflow-y','auto');
						if (me.rightBodyPaddingModified)
						{
							$('body').css({'padding-right': me.rightBodyPaddingValue});
						}
					}
				}
			},
			SWANK_DIALOG_CONFIG['FadeOutTime']
		);
	};

	/*
		 ____       _            _         __  __      _   _               _
		|  _ \ _ __(_)_   ____ _| |_ ___  |  \/  | ___| |_| |__   ___   __| |___
		| |_) | '__| \ \ / / _` | __/ _ \ | |\/| |/ _ \ __| '_ \ / _ \ / _` / __|
		|  __/| |  | |\ V / (_| | ||  __/ | |  | |  __/ |_| | | | (_) | (_| \__ \
		|_|   |_|  |_| \_/ \__,_|\__\___| |_|  |_|\___|\__|_| |_|\___/ \__,_|___/

	*/

	me._makeDialogDraggable = function()
	{
		me.pos1 = 0, me.pos2 = 0, me.pos3 = 0, me.pos4 = 0;
		let header = $(`#DialogWindow-${me.index} .HeaderBar`)[0];
		header.onmousedown = me._dragMouseDown;
	}

	me._dragMouseDown = function(e) 
	{
		e = e || window.event;
		e.preventDefault();
		// get the mouse cursor position at startup:
		me.pos3 = e.clientX;
		me.pos4 = e.clientY;
		document.onmouseup = me._closeDragElement;
		// call a function whenever the cursor moves:
		document.onmousemove = me._elementDrag;
	};

	me._elementDrag = function(e) 
	{
		let element = $(`#DialogWindow-${me.index}`)[0];
		e = e || window.event;
		e.preventDefault();
		// calculate the new cursor position:
		me.pos1 = me.pos3 - e.clientX;
		me.pos2 = me.pos4 - e.clientY;
		me.pos3 = e.clientX;
		me.pos4 = e.clientY;
		// set the element's new position:
		let posTop = element.offsetTop - me.pos2;
		if (posTop < 0) posTop = 0;
		let posLeft = element.offsetLeft - me.pos1;
		if (posLeft < 0) posLeft = 0;
		
		let elemWidth = $(`#DialogWindow-${me.index}`).width();
		let elemHeight = $(`#DialogWindow-${me.index}`).height();

		let windowWidth = $(window).innerWidth();
		let windowHeight = $(window).innerHeight();
		let windowLeft = $(window).scrollLeft();
		let windowTop = $(window).scrollTop();
		let windowRight = windowLeft + windowWidth - 12;
		let windowBottom = windowTop + windowHeight - 12;
		
		// if ((posLeft + elemWidth) > documentWidth) posLeft = documentWidth - elemWidth;
		// if ((posTop + elemHeight) > documentHeight) posTop = documentHeight - elemHeight;

		if ((posLeft + elemWidth) > windowRight) posLeft = windowRight - elemWidth;
		if ((posTop + elemHeight) > windowBottom) posTop = windowBottom - elemHeight;
		if (posTop < windowTop) posTop = windowTop;
		if (posLeft < windowLeft) posLeft = windowLeft;
		
		element.style.top = (posTop) + "px";
		element.style.left = (posLeft) + "px";
	};

	me._closeDragElement = function() 
	{
		// stop moving when mouse button is released:
		document.onmouseup = null;
		document.onmousemove = null;
	}
	
	me._getVertScrollBarWidth = function() 
	{
		var $outer = $('<div>').css({visibility: 'hidden', width: 100, overflow: 'scroll'}).appendTo('body'),
			widthWithScroll = $('<div>').css({width: '100%'}).appendTo($outer).outerWidth();
		$outer.remove();
		return 100 - widthWithScroll;
	};

	me.vertScrollBarWidthValue = me._getVertScrollBarWidth();

	me.vertScrollBarEnabledFunc = function()
	{
		return ($(document).outerHeight() > $(window).outerHeight());
	};

	me.vertScrollBarHiddenFunc = function()
	{
		return ((SWANK_DIALOG_CONFIG['DisableScrollBar']) && (SWANK_ACTIVE_DIALOG_COUNT > 1) && me.vertScrollBarEnabledFunc);
	};
};
