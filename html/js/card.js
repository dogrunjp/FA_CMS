jQuery(document).ready(function ($) {
    var cardBase = '<div class="hc-refers"></div>';
    $(".anno").hovercard({
        detailsHTML: cardBase,
        showCustomCard: false,
        openOnTop: true,
        onHoverIn: function () {
            //if (!$(".anno_search").is(":checked")) return false;
            var kw = this.data("kw");
            var rows = 0;
            cards.forEach(function (v, i, a) {
                $(".hc-refers").empty();
                console.log(v["dbname"]);
                $.ajax({
                    type: v.ajax_conf.type,
                    url: v.get_url(kw),
                    dataType: v.ajax_conf.dataType
                }, cards).then(function (d) {
                    console.log(v["dbname"])
                    var req_type = v["request_type"];
                    var pages = parser[req_type](d);
                    if (pages.length > 0) {
                        rows += pages.length;
                        var t = v.title(kw);
                        $(".hc-refers").append(t);
                        var i = 0;
                        while (i < pages.length && i < v.max_lines) {
                            var c = pages[i];
                            if ($.isFunction(v.views)) {
                                var elem = v.views(kw, c);
                                $(".hc-refers").append(elem);
                            }
                            i++
                        }
                    }
                });
            });
        }
    });
});
