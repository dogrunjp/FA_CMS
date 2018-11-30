﻿//Hovercard plugin (fork)
//Original Documentation: http://designwithpc.com/Plugins/Hovercard
//Author: PC 
//Website: http://designwithpc.com
//Twitter: @chaudharyp

//fork maintained by dogrunjp
//Version 2.5 Jan 11th 2018


(function ($) {
    $.fn.hovercard = function (options) {

        //Set defauls for the control
        var defaults = {
            width: 300,
            openOnLeft: false,
            openOnTop: false,
            cardImgSrc: "",
            detailsHTML: "",
            twitterScreenName: '',
            showTwitterCard: false,
            facebookUserName: '',
            showFacebookCard: false,
            showCustomCard: false,
            customCardJSON: {},
            customDataUrl: '',
            background: "#ffffff",
            delay: 0,
            autoAdjust: true,
            onHoverIn: function () { },
            onHoverOut: function () { }
        };
        //Update unset options with defaults if needed
        var options = $.extend(defaults, options);

        //CSS for hover card. Change per your need, and move these styles to your stylesheet (recommended).
        // if ($('#css-hovercard').length <= 0) {
        //     var hovercardTempCSS = '<style id="css-hovercard" type="text/css">' +
        //                             '.hc-preview { position: relative; display:inline; }' +
        //                             '.hc-name { font-weight:bold; position:relative; display:inline-block; }' +
        //                             '.hc-details { left:-10px; margin-right:80px; text-align:left; font-family:Sans-serif !important; font-size:12px !important; color:#666 !important; line-height:1.5em; border:solid 1px #ddd; position:absolute;-moz-border-radius:3px;-webkit-border-radius:3px;border-radius:3px;top:-10px;padding:2em 10px 10px;-moz-box-shadow:5px 5px 5px #888;-webkit-box-shadow:5px 5px 5px #888;box-shadow:5px 5px 5px #888;display:none;}' +
        //                             '.hc-pic { width:70px; margin-top:-1em; float:right;  }' +
        //                             '.hc-details-open-left { left: auto; right:-10px; text-align:right; margin-left:80px; margin-right:0; } ' +
        //                             '.hc-details-open-left > .hc-pic { float:left; } ' +
        //                             '.hc-details-open-top { bottom:-10px; top:auto; padding: 10px 10px 2em;} ' +
        //                             '.hc-details-open-top > .hc-pic { margin-top:10px; float:right;  }' +
        //                             '.hc-details .s-action{ position: absolute; top:8px; right:5px; } ' +
        //                             '.hc-details .s-card-pad{ border-top: solid 1px #eee; margin-top:10px; padding-top:10px; overflow:hidden; } ' +
        //                             '.hc-details-open-top .s-card-pad { border:none; border-bottom: solid 1px #eee; margin-top:0;padding-top:0; margin-bottom:10px;padding-bottom:10px; }' +
        //                             '.hc-details .s-card .s-strong{ font-weight:bold; color: #555; } ' +
        //                             '.hc-details .s-img{ float: left; margin-right: 10px; max-width: 70px;} ' +
        //                             '.hc-details .s-name{ color:#222; font-weight:bold;} ' +
        //                             '.hc-details .s-loc{ float:left;}' +
        //                             '.hc-details-open-left .s-loc{ float:right;} ' +
        //                             '.hc-details .s-href{ clear:both; float:left;} ' +
        //                             '.hc-details .s-desc{ float:left; font-family: Georgia; font-style: italic; margin-top:5px;width:100%;} ' +
        //                             '.hc-details .s-username{ text-decoration:none;} ' +
        //                             '.hc-details .s-stats { display:block; float:left; margin-top:5px; clear:both; padding:0px;}' +
        //                             '.hc-details ul.s-stats li{ list-style:none; float:left; display:block; padding:0px 10px !important; border-left:solid 1px #eaeaea;} ' +
        //                             '.hc-details ul.s-stats li:first-child{ border:none; padding-left:0 !important;} ' +
        //                             '.hc-details .s-count { font-weight: bold;} ' +
        //                         '.</style>")';
        //
        //     $(hovercardTempCSS).appendTo('head');
        // }
        //Executing functionality on all selected elements
        return this.each(function () {
            var obj = $(this);

            //wrap a parent span to the selected element
            obj.wrapAll('<div class="hc-preview" />').wrapAll('<div class="hc-popup-block" />');

            //add a relatively positioned class to the selected element
            obj.addClass("hc-name");

            //if card image src provided then generate the image elementk
            var hcImg = '';
            if (options.cardImgSrc.length > 0) {
                hcImg = '<img class="hc-pic" src="' + options.cardImgSrc + '" />';
            }

            //generate details span with html provided by the user
            var hcTitle = $('<h3></h3>', {
                text: obj.text(),
                class: "hc-title"
            });
            var hcDetails = $('<div></div>', {
                class: "hc-inner"
            }).html(hcImg + options.detailsHTML);

            var hcCard = $('<div></div>', {
                class: "hc-popup-panel"
            }).append(hcTitle).append(hcDetails);

            var hcCardBlock = $('<div></div>', {
                class: "hc-details",
                css: {display: "none"}
            }).html(hcCard);

            //append this detail after the selected element
            obj.before(hcCardBlock);
            obj.siblings(".hc-details");//.css({ 'width': options.width, 'background': options.background });

            //toggle hover card details on hover
            if ( $(window).width() >= 750) {
                obj.closest(".hc-preview").hover(function () {
                    if (!$(".anno_search").is(":checked")) return false;

                    var $this = $(this);
                    adjustToViewPort($this);

                    //Up the z indiex for the .hc-name to overlay on .hc-details
                    $this.css("z-index", "200");
                    obj.css("z-index", "100").find('.hc-details').css("z-index", "50");

                    var curHCDetails = $this.find(".hc-details").eq(0);
                    curHCDetails.stop(true, true).delay(options.delay).fadeIn();


                    //Default functionality on hoverin, and also allows callback
                    if (typeof options.onHoverIn == 'function') {

                        //check for custom profile. If already loaded don't load again
                        if (options.showCustomCard && curHCDetails.find('.s-card').length <= 0) {

                            //Read data-hovercard url from the hovered element, otherwise look in the options. For custom card, complete url is required than just username.
                            var dataUrl = options.customDataUrl;
                            if (typeof obj.attr('data-hovercard') == 'undefined') {
                                //do nothing. detecting typeof obj.attr('data-hovercard') != 'undefined' didn't work as expected.
                            } else if (obj.attr('data-hovercard').length > 0) {
                                dataUrl = obj.attr('data-hovercard');
                            }

                            LoadSocialProfile("custom", dataUrl, curHCDetails, options.customCardJSON);
                        }

                        //check for twitter profile. If already loaded don't load again
                        if (options.showTwitterCard && curHCDetails.find('.s-card').length <= 0) {

                            //Look for twitter screen name in data-hovercard first, then in options, otherwise try with the hovered text
                            var tUsername = options.twitterScreenName.length > 0 ? options.twitterScreenName : obj.text();
                            if (typeof obj.attr('data-hovercard') == 'undefined') {
                                //do nothing. detecting typeof obj.attr('data-hovercard') != 'undefined' didn't work as expected.
                            } else if (obj.attr('data-hovercard').length > 0) {
                                tUsername = obj.attr('data-hovercard');
                            }

                            LoadSocialProfile("twitter", tUsername, curHCDetails);
                        }

                        //check for facebook profile. If already loaded don't load again
                        if (options.showFacebookCard && curHCDetails.find('.s-card').length <= 0) {

                            //Look for twitter screen name in data-hovercard first, then in options, otherwise try with the hovered text
                            var fbUsername = options.facebookUserName.length > 0 ? options.facebookUserName : obj.text();
                            if (typeof obj.attr('data-hovercard') == 'undefined') {
                                //do nothing. detecting typeof obj.attr('data-hovercard') != 'undefined' didn't work as expected.
                            } else if (obj.attr('data-hovercard').length > 0) {
                                fbUsername = obj.attr('data-hovercard');
                            }

                            LoadSocialProfile("facebook", fbUsername, curHCDetails);
                        }

                        //Callback function
                        options.onHoverIn.call(this);
                    }

                }, function () {
                    //Undo the z indices
                    $this = $(this);

                    $this.find(".hc-details").eq(0).stop(true, true).fadeOut(300, function () {
                        $this.css("z-index", "0");
                        obj.css("z-index", "0").find('.hc-details').css("z-index", "0");

                        if (typeof options.onHoverOut == 'function') {
                            options.onHoverOut.call(this);
                        }
                    });

                });
                obj.closest(".hc-preview").bind("touchmove touchend", function () {
                    $this = $(this);

                    $this.find(".hc-details").eq(0).stop(true, true).fadeOut(300, function () {
                        $this.css("z-index", "0");
                        obj.css("z-index", "0").find('.hc-details').css("z-index", "0");

                        if (typeof options.onHoverOut == 'function') {
                            options.onHoverOut.call(this);
                        }
                    });
                });
            } else {
                var isTouch = ('ontouchstart' in window);
                obj.closest(".hc-preview").bind({
                    'touchstart mousedown': function(e) {
                        e.preventDefault();
                        this.pageX = (isTouch ? event.changedTouches[0].pageX : e.pageX);
                        this.pageY = (isTouch ? event.changedTouches[0].pageY : e.pageY);

                        var $this = $(this);
                        adjustToViewPort($this);

                        //Up the z indiex for the .hc-name to overlay on .hc-details
                        $this.css("z-index", "200");
                        obj.css("z-index", "100").find('.hc-details').css("z-index", "50");

                        var curHCDetails = $this.find(".hc-details").eq(0);
                        curHCDetails.stop(true, true).delay(options.delay).fadeIn();


                        //Default functionality on hoverin, and also allows callback
                        if (typeof options.onHoverIn == 'function') {

                            //check for custom profile. If already loaded don't load again
                            if (options.showCustomCard && curHCDetails.find('.s-card').length <= 0) {

                                //Read data-hovercard url from the hovered element, otherwise look in the options. For custom card, complete url is required than just username.
                                var dataUrl = options.customDataUrl;
                                if (typeof obj.attr('data-hovercard') == 'undefined') {
                                    //do nothing. detecting typeof obj.attr('data-hovercard') != 'undefined' didn't work as expected.
                                } else if (obj.attr('data-hovercard').length > 0) {
                                    dataUrl = obj.attr('data-hovercard');
                                }

                                LoadSocialProfile("custom", dataUrl, curHCDetails, options.customCardJSON);
                            }

                            //check for twitter profile. If already loaded don't load again
                            if (options.showTwitterCard && curHCDetails.find('.s-card').length <= 0) {

                                //Look for twitter screen name in data-hovercard first, then in options, otherwise try with the hovered text
                                var tUsername = options.twitterScreenName.length > 0 ? options.twitterScreenName : obj.text();
                                if (typeof obj.attr('data-hovercard') == 'undefined') {
                                    //do nothing. detecting typeof obj.attr('data-hovercard') != 'undefined' didn't work as expected.
                                } else if (obj.attr('data-hovercard').length > 0) {
                                    tUsername = obj.attr('data-hovercard');
                                }

                                LoadSocialProfile("twitter", tUsername, curHCDetails);
                            }

                            //check for facebook profile. If already loaded don't load again
                            if (options.showFacebookCard && curHCDetails.find('.s-card').length <= 0) {

                                //Look for twitter screen name in data-hovercard first, then in options, otherwise try with the hovered text
                                var fbUsername = options.facebookUserName.length > 0 ? options.facebookUserName : obj.text();
                                if (typeof obj.attr('data-hovercard') == 'undefined') {
                                    //do nothing. detecting typeof obj.attr('data-hovercard') != 'undefined' didn't work as expected.
                                } else if (obj.attr('data-hovercard').length > 0) {
                                    fbUsername = obj.attr('data-hovercard');
                                }

                                LoadSocialProfile("facebook", fbUsername, curHCDetails);
                            }

                            //Callback function
                            options.onHoverIn.call(this);
                        }
                    },
                    'touchmove mousemove': function(e) {
                        e.preventDefault();
                    },
                    'touchend mouseup': function(e) {
                    }
                });
            }


            //Opening Directions adjustment
            function adjustToViewPort(hcPreview) {

                var hcDetails = hcPreview.find('.hc-details').eq(0);
                var hcPreviewRect = hcPreview[0].getBoundingClientRect();

                var hcdTop = hcPreviewRect.top - 20; //Subtracting 20px of padding;
                var hcdRight = hcPreviewRect.left + 35 + hcDetails.width(); //Adding 35px of padding;
                var hcdBottom = hcPreviewRect.top + 35 + hcDetails.height(); //Adding 35px of padding;
                var hcdLeft = hcPreviewRect.top - 10; //Subtracting 10px of padding;

                //Check for forced open directions, or if need to be autoadjusted
                if (options.openOnLeft || (options.autoAdjust && (hcdRight > window.innerWidth))) {
                    hcDetails.addClass("hc-details-open-left");
                } else {
                    hcDetails.removeClass("hc-details-open-left");
                }
                if (options.openOnTop || (options.autoAdjust && (hcdBottom > window.innerHeight))) {
                    hcDetails.addClass("hc-details-open-top");
                } else {
                    hcDetails.removeClass("hc-details-open-top");
                }
            }

            //Private base function to load any social profile
            function LoadSocialProfile(type, username, curHCDetails, customCardJSON) {
                var cardHTML, urlToRequest, customCallback, loadingHTML, errorHTML;

                switch (type) {
                    case "twitter":
                        {
                            urlToRequest = 'http://api.twitter.com/1/users/lookup.json?screen_name=' + username;
                            cardHTML = function (profileData) {
                                profileData = profileData[0];
                                return '<div class="s-card s-card-pad">' +
                                                        (profileData.profile_image_url ? ('<img class="s-img" src="' + profileData.profile_image_url + '" />') : '') +
                                                        (profileData.name ? ('<label class="s-name">' + profileData.name + ' </label>') : '') +
                                                        (profileData.screen_name ? ('(<a class="s-username" title="Visit Twitter profile for ' + profileData.name + '" href="http://twitter.com/' + profileData.screen_name + '">@' + profileData.screen_name + '</a>)<br/>') : '') +
                                                        (profileData.location ? ('<label class="s-loc">' + profileData.location + '</label>') : '') +
                                                        (profileData.description ? ('<p class="s-desc">' + profileData.description + '</p>') : '') +
                                                        (profileData.url ? ('<a class="s-href" href="' + profileData.url + '">' + profileData.url + '</a><br/>') : '') +

                                                        '<ul class="s-stats">' +
                                                            (profileData.statuses_count ? ('<li>Tweets<br /><span class="s-count">' + profileData.statuses_count + '</span></li>') : '') +
                                                            (profileData.friends_count ? ('<li>Following<br /><span class="s-count">' + profileData.friends_count + '</span></li>') : '') +
                                                            (profileData.followers_count ? ('<li>Followers<br /><span class="s-count">' + profileData.followers_count + '</span></li>') : '') +
                                                        '</ul>' +
                                                    '</div>';
                            };
                            loadingHTML = 'Contacting Twitter...';
                            errorHTML = 'Invalid username or you have exceeded Twitter request limit.<br/><small>Please note, Twitter only allows 150 requests per hour.</small>';
                            customCallback = function () { };

                            //Append the twitter script to the document to add a follow button
                            if ($('#t-follow-script').length <= 0) {
                                var script = document.createElement('script');
                                script.type = 'text/javascript';
                                script.src = '//platform.twitter.com/widgets.js';
                                script.id = 't-follow-script';
                                $('body').append(script);
                            }
                            curHCDetails.append('<span class="s-action"><a href="https://twitter.com/' + username + '" data-show-count="false" data-button="grey" data-width="65px" class="twitter-follow-button">Follow</a></span>');

                        }
                        break;
                    case "facebook":
                        {
                            urlToRequest = 'https://graph.facebook.com/' + username,
                            cardHTML = function (profileData) {
                                return '<div class="s-card s-card-pad">' +
                                        '<img class="s-img" src="http://graph.facebook.com/' + profileData.id + '/picture" />' +
                                        '<label class="s-name">' + profileData.name + ' </label><br/>' +
                                        (profileData.link ? ('<a class="s-loc" href="' + profileData.link + '">' + profileData.link + '</a><br/>') : '') +
                                        (profileData.likes ? ('<label class="s-loc">Liked by </span> ' + profileData.likes + '</label><br/>') : '') +
                                        (profileData.description ? ('<p class="s-desc">' + profileData.description + '</p>') : '') +
                                        (profileData.start_time ? ('<p class="s-desc"><span class="s-strong">Start Time:</span><br/>' + profileData.start_time + '</p>') : '') +
                                        (profileData.end_time ? ('<p class="s-desc"><span class="s-strong">End Time:<br/>' + profileData.end_time + '</p>') : '') +
                                        (profileData.founded ? ('<p class="s-desc"><span class="s-strong">Founded:</span><br/>' + profileData.founded + '</p>') : '') +
                                        (profileData.mission ? ('<p class="s-desc"><span class="s-strong">Mission:</span><br/>' + profileData.mission + '</p>') : '') +
                                        (profileData.company_overview ? ('<p class="s-desc"><span class="s-strong">Overview:</span><br/>' + profileData.company_overview + '</p>') : '') +
                                        (profileData.products ? ('<p class="s-desc"><span class="s-strong">Products:</span><br/>' + profileData.products + '</p>') : '') +
                                        (profileData.website ? ('<p class="s-desc"><span class="s-strong">Web:</span><br/><a href="' + profileData.website + '">' + profileData.website + '</a></p>') : '') +
                                        (profileData.email ? ('<p class="s-desc"><span class="s-strong">Email:</span><br/><a href="' + profileData.email + '">' + profileData.email + '</a></p>') : '') +
                                        '</div>';
                            };
                            loadingHTML = "Contacting Facebook...";
                            errorHTML = "The requested user, page, or event could not be found. Please try a different one.";
                            customCallback = function (profileData) {
                                //Append the twitter script to the document to add a follow button
                                if ($('#fb-like-script').length <= 0) {
                                    var script = document.createElement('script');
                                    script.type = 'text/javascript';
                                    script.text = '(function(d, s, id) {' +
                                              'var js, fjs = d.getElementsByTagName(s)[0];' +
                                              'if (d.getElementById(id)) {return;}' +
                                              'js = d.createElement(s); js.id = id;' +
                                              'js.src = "//connect.facebook.net/en_US/all.js#xfbml=1&appId=140270912730552";' +
                                              'fjs.parentNode.insertBefore(js, fjs);' +
                                            '}(document, "script", "facebook-jssdk"));';
                                    script.id = 'fb-like-script';
                                    $('body').prepend(script);
                                    $('body').prepend('<div id="fb-root"></div>');
                                }
                                curHCDetails.append('<span class="s-action"><div class="fb-like" data-href="' + profileData.link + '" data-send="false" data-layout="button_count" data-width="90" data-show-faces="false"></div></span>');
                            }
                        }
                        break;
                    case "custom":
                        {
                            urlToRequest = username,
                            cardHTML = function (profileData) {
                                return '<div class="s-card s-card-pad">' +
                                        (profileData.image ? ('<img class="s-img" src=' + profileData.image + ' />') : '') +
                                        (profileData.name ? ('<label class="s-name">' + profileData.name + ' </label><br/>') : '') +
                                        (profileData.link ? ('<a class="s-loc" href="' + profileData.link + '">' + profileData.link + '</a><br/>') : '') +
                                        (profileData.bio ? ('<p class="s-desc">' + profileData.bio + '</p>') : '') +
                                        (profileData.website ? ('<p class="s-desc"><span class="s-strong">Web:</span><br/><a href="' + profileData.website + '">' + profileData.website + '</a></p>') : '') +
                                        (profileData.email ? ('<p class="s-desc"><span class="s-strong">Email:</span><br/><a href="' + profileData.email + '">' + profileData.email + '</a></p>') : '') +
                                        '</div>';
                            };
                            loadingHTML = "Loading...";
                            errorHTML = "Sorry, no data found.";
                            customCallback = function () { };
                        }
                        break;
                    default: { } break;
                }

                if ($.isEmptyObject(customCardJSON)) {
                    $.ajax({
                        url: urlToRequest,
                        type: 'GET',
                        dataType: 'jsonp', //jsonp for cross domain request
                        timeout: 4000, //timeout if cross domain request didn't respond, or failed silently
                        beforeSend: function () {
                            curHCDetails.find('.s-message').remove();
                            curHCDetails.append('<p class="s-message">' + loadingHTML + '</p>');
                        },
                        success: function (data) {
                            if (data.length <= 0) {
                                curHCDetails.find('.s-message').html(errorHTML);
                            }
                            else {
                                curHCDetails.find('.s-message').remove();
                                curHCDetails.prepend(cardHTML(data));
                                adjustToViewPort(curHCDetails.closest('.hc-preview'));
                                curHCDetails.stop(true, true).delay(options.delay).fadeIn();
                                customCallback(data);
                            }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            curHCDetails.find('.s-message').html(errorHTML);
                        }
                    });
                }
                else {
                    curHCDetails.prepend(cardHTML(customCardJSON));
                }
            };
        });

    };
})(jQuery);