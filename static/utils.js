/**
 *
 * Created by James on 15/11/29.
 */

function insert_warning_window(element, content) {
    // 展出警告框
    element.before(
        '<div class="alert alert-warning alert-dismissible fade in" role="alert">' +
        '<button id="warning_window_close_btn" type="button" class="close" data-dismiss="alert" aria-label="Close">' +
        '<span aria-hidden="true">&times;</span>' +
        '</button>' +
        content +
        '</div>');
    // 3秒后自动关闭
    setTimeout(function() {
        $('#warning_window_close_btn').click();
    }, 3000);
}

$.fn.hasAttr = function(name) {
   return this.attr(name) !== undefined;
};

// Public: Constructor
function RandomPassword() {
	this.chrLower="abcdefghjkmnpqrst";
	this.chrUpper="ABCDEFGHJKMNPQRST";
	this.chrNumbers="23456789";
	this.chrSymbols="!#%&?+*_.,:;";

	this.maxLength=255;
	this.minLength=8;
}

/*
	Public: Create password

	length (optional): Password length. If value is not within minLength/maxLength (defined in constructor), length will be adjusted automatically.

	characters (optional): The characters the password will be composed of. Must contain at least one of the following:
		this.chrLower
		this.chrUpper
		this.chrNumbers
		this.chrSymbols
	Use + to combine. You can add your own sets of characters. If not at least one of the constructor defined sets of characters is found, default set of characters will be used.
*/
RandomPassword.prototype.create = function(length, characters) {
	var _length=this.adjustLengthWithinLimits(length);
	var _characters=this.secureCharacterCombination(characters);

	return this.shufflePassword(this.assemblePassword(_characters, _length));
};

// Private: Adjusts password length to be within limits.
RandomPassword.prototype.adjustLengthWithinLimits = function(length) {
	if(!length || length<this.minLength)
		return this.minLength;
	else if(length>this.maxLength)
		return this.maxLength;
	else
		return length;
};

// Private: Make sure characters password is build of contains meaningful set of characters.
RandomPassword.prototype.secureCharacterCombination = function(characters) {
	var defaultCharacters=this.chrLower+this.chrUpper+this.chrNumbers;

	if(!characters || this.trim(characters)=="")
		return defaultCharacters;
	else if(!this.containsAtLeast(characters, [this.chrLower, this.chrUpper, this.chrNumbers, this.chrSymbols]))
		return defaultCharacters;
	else
		return characters;

};

// Private: Assemble password using a string of characters the password will consist of.
RandomPassword.prototype.assemblePassword = function(characters, length) {
	var randMax=this.chrNumbers.length;
	var randMin=randMax-4;
	var index=this.random(0, characters.length-1);
	var password="";

	for(var i=0; i<length; i++) {
		var jump=this.random(randMin, randMax);
		index=((index+jump)>(characters.length-1)?this.random(0, characters.length-1):index+jump);
		password+=characters[index];
	}

	return password;
};

// Private: Shuffle password.
RandomPassword.prototype.shufflePassword = function(password) {
	return password.split('').sort(function(){return 0.5-Math.random()}).join('');
};

// Private: Checks if string contains at least one string in an array
RandomPassword.prototype.containsAtLeast = function(string, strings) {
	for(var i=0; i<strings.length; i++) {
		if(string.indexOf(strings[i])!=-1)
			return true;
	}
	return false;
};

// Private: Returns a random number between min and max.
RandomPassword.prototype.random = function(min, max) {
	return Math.floor((Math.random() * max) + min);
};

// Private: Trims a string (required for compatibility with IE9 or older)
RandomPassword.prototype.trim = function(s) {
	if(typeof String.prototype.trim !== 'function')
		return s.replace(/^\s+|\s+$/g, '');
	else
		return s.trim();
};

function render_bandwidth_slider(bandwidth_slider ,action, bandwidth_unit) {

    if (action === 'create') {
        bandwidth_slider.ionRangeSlider({
            min: 0,
            max: 1000,
            from: 200,
            from_min: 1,
            from_max: 999,
            step: 1,
            grid: true,
            grid_num: 10,
            postfix: ' Mbps'
        });

    } else if (action === 'update') {
        var bandwitdh_slider_instance = bandwidth_slider.data("ionRangeSlider");
        if (bandwidth_unit === 'g') {
            bandwitdh_slider_instance.update({
                min: 0,
                max: 100,
                from: 1,
                from_min: 1,
                from_max: 100,
                step: 1,
                grid: true,
                grid_num: 10,
                postfix: ' Gbps'
            });

        } else if (bandwidth_unit === 'm') {
            bandwitdh_slider_instance.update({
                min: 0,
                max: 1000,
                from: 200,
                from_min: 1,
                from_max: 999,
                step: 1,
                grid: true,
                grid_num: 10,
                postfix: ' Mbps'
            });

        } else if (bandwidth_unit === 'k') {
            bandwitdh_slider_instance.update({
                min: 0,
                max: 1000,
                from: 512,
                from_min: 8,
                from_max: 992,
                step: 8,
                grid: true,
                grid_num: 10,
                postfix: ' Kbps'
            });
        }
    }
}