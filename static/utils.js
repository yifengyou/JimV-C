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