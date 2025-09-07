"use strict";



function ImageButton()
{
	var me = this;
	me.init = function()
	{
		let empty = [];
		for (let i = 0; i < 12; i++) empty.push('<div class="ImageButtonEmpty"></div>');
		empty = empty.join('');
		$('.ImageButtonWrapper').append(empty);
		$('.ImageButton').hover
		(
			function()
			{
				$(this).addClass('active');
				// let color = $(this).find('div').css('background-color');
				// $(this).css('border-color', color);
			}
		);
		$('.ImageButton').mouseleave
		(
			function()
			{
				$(this).removeClass('active');
				// $(this).css('border-color', 'transparent');
			}
		);
		
	};
	me.randColor = function()
	{
		let colors = 
		[
			'MediumVioletRed',
			'DarkViolet',
			'Purple',
			'DarkSlateBlue',
			'Indigo',
			'Crimson',
			'Red',
			'FireBrick',
			'DarkRed',
			'OrangeRed',
			'Gold',
			'LimeGreen',
			'SeaGreen',
			'Green',
			'DarkGreen',
			'DarkOliveGreen',
			'Teal',
			'SteelBlue',
			'Navy',
			'MidnightBlue',
			'DarkGoldenRod',
			'Chocolate',
			'SaddleBrown',
			'Brown',
			'Maroon',
			'DarkSlateGray',
		];
		// $('.ImageButton > div').each
		// (
		// 	function()
		// 	{
		// 		let color = colors[Math.floor(Math.random() * colors.length)];
		// 		console.log(color);
		// 		// $(this).addClass(color);
		// 		// $(this).css('background-color', color);
		// 		$(this).attr('style', 'background-color: ' + color);
		// 	}
		// );
		$('.ImageButton').each
		(
			function()
			{
				let color = colors[Math.floor(Math.random() * colors.length)];
				console.log(color);
				// $(this).find('> div').attr('style', 'background-color: ' + color);
				$(this).find('> div').css('background-color', color);
			}
		);
	};
	me.init();
};


// let b = new ImageButton();
// // b.randColor();

$( document ).ready(function() {
  new ImageButton();
});


