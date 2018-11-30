jQuery(document).ready(function ($) {
    var cardBase = '<div class="hc-refers"></div>';
    $(".anno").hovercard({
        detailsHTML: cardBase,
        showCustomCard: false,
        openOnTop: true,
        onHoverIn: function () {
            if (!$(".anno_search").is(":checked")) return false;
            //var kw = this.firstChild.textContent;
            var kw = this.getElementsByClassName("hc-title")[0].textContent;
            console.log(this);
            console.log("hover in: " + kw);
            var rows = 0;
            cards.forEach(function (v, i, a) {
                // cards確認
                $(".hc-refers").empty();
                $.ajax({
                    type: v.ajax_conf.type,
                    url: v.get_url(kw),
                    dataType: v.ajax_conf.dataType
                }, cards).then(function (d) {
                    var req_type = v["request_type"];
                    var pages = parser[req_type](d);

                    if (v.ququest_type == "link"){
                            var t = v.title(kw)
                            $(".hc-refers").append(t);
                    } else if (pages.length > 0) {
                        rows += pages.length;
                        var t = v.title(kw)
                        $(".hc-refers").append(t);

                        var i = 0;
                        while (i < pages.length && i < v.max_lines) {
                            var c = pages[i];
                            var elem = v.views(kw, c);
                            $(".hc-refers").append(elem);
                            i++
                        }
                    }
                });
                // styleの変更
                if (rows > 0) {
                    $(".hc-details .s-card").attr("style", "display:block");
                } else {
                    $(".hc-details .s-card").attr("style", "display:none");
                }
            });
        }
    });
});