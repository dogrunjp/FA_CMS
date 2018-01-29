jQuery(document).ready(function ($) {

    var $toggle = $('#nav-toggle');
    var $menu = $('#nav-menu');
    $toggle.click(function() {
        $(this).toggleClass('is-active');
        $menu.toggleClass('is-active');
    });

    $('.autopagerize_page_element').children('h1').each(function (index) {
        var article_thumb = $(this).nextUntil('h1');
        article_thumb.wrapAll('<div id="article' + index + '" class="article"></div>').wrapAll('<div class="article_thumb"></div>');
        $('#article' + index).prepend($(this));
    })
});