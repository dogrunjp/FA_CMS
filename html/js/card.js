jQuery(document).ready(function ($) {
    var cardBase = '<div class="hc-refers"></div>';
    $(".anno").hovercard({
        detailsHTML: cardBase,
        showCustomCard: false,
        openOnTop: true,
        onHoverIn: function () {
            //if (!$(".anno_search").is(":checked")) return false;
            var attributes = this[0].childNodes[0].childNodes[1].attributes;
            var kw = this.data("kw");
            var rows = 0;
            cards.forEach(function (v, i, a) {
                $(".hc-refers").empty();
                //console.log(v["dbname"]);
                $.ajax({
                    type: v.ajax_conf.type,
                    url: v.get_url(kw),
                    dataType: v.ajax_conf.dataType
                }, cards).then(function (d) {
                    var targetdb =  v.dbname;
                    var req_type = v["request_type"];
                    var pages = parser[req_type](d);
                    if (pages.length > 0) {
                        rows += pages.length;
                        if (targetdb === "refex" || targetdb ==="ggrna"){
                           var t = v.title(attributes[2].value);
                           // リンクを追加
                        $(".hc-refers").append(t);
                        }else if (targetdb === "uniprot" && attributes[3].value !== ""){
                            var t = v.title(attributes[3].value)
                            // リンクを追加
                            $(".hc-refers").append(t);
                        }

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
