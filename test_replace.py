import re

#
# 1.正規表現によるターゲット文字列の認識
# 2.idの抽出
# 3.htmlタグの生成と置き換え

st = '''
<br><a name="F1"></a>
<div id="fig1-caption-text" style="display: none;"><strong>図1　Cas9，sgRNA，標的となる2本鎖DNAからなる複合体の結晶構造</strong><br>（a）<em>F</em>. <em>novicida</em>に由来するCas9を含む複合体．<br>（b）<em>S</em>. <em>pyogenes</em>に由来するCas9を含む複合体．<br>（c）<em>S</em>. <em>aureus</em>に由来するCas9を含む複合体．<br><a href="http://first.lifesciencedb.jp/wordpress/wp-content/uploads/2015/12/Nureki-Cell-16.2.25-Fig.1.jpg" target="_blank">[Download]</a>
</div>[hs_figure id=1&amp;image=/wordpress/wp-content/uploads/2015/12/Nureki-Cell-16.2.25-Fig.1.png&amp;caption=fig1-caption-text]<br><br>　<em>F</em>. <em>novicida</em>に由来するCas9において，sgRNAのガイド配列は相補鎖DNAとRNA：DNAヘテロ2本鎖を形成し，RuvCドメインとRECドメインのあいだに収容されていた．PAMを含む2本鎖DNAはWEDドメインとPIドメインにより形成される溝に結合していた．sgRNAのガイド配列以外の領域はリ<a href="#" class="anno">ピート</a>
：アンチリピート2本鎖，<a href="#" class="anno">ステム</a>
<a href="#" class="anno">ループ</a>
1，ステムループ2を形成し，おもにRECドメインおよびWEDドメインにより認識されていた．<br><br><h2>3．<em>F</em>. <em>novicida</em>に由来するCas9のRNAに依存的なDNAの認識機構</h2><br>　<em>F</em>. <em>novicida</em>に由来するCas9において，RNA：DNAヘテロ2本鎖は，その糖-<a href="#" class="anno">リン酸</a>
骨格とブリッジヘリックスおよびRECドメインとのあいだの<a href="#" class="anno">相互作用</a>
を介して配列に<a href="#" class="anno">非依存</a>
的に認識されていた．この構造的な特徴から，<em>F</em>. <em>novicida</em>に由来するCas9がガイドRNAに依存的に任意のDNA配列を認識できる性質が説明された．とくに，PAMの近傍の約8塩基からなるシード領域はブリッジヘリックスのArgやHisにより強固に認識されていた．これは，シード領域のRNA：DNA<a href="#" class="anno">塩基対</a>
合がDNAの切断に重要であるという結果と一致した<a href="#R9"><sup>9)</sup></a>
．リピート：アンチリピート2本鎖，ステムループ1，ステムループ2はRECドメインおよびWEDドメインにより特異的に認識されていた．<br><br><h2>4．<em>F</em>. <em>novicida</em>に由来するCas9のPAMの認識機構</h2><br>　<em>F</em>. <em>novicida</em>に由来するCas9において，PAM（5’-TGG-3’あるいは5’-TGA-3’）はPIドメインにより認識されていた（<a href="#F2">図2a</a>
）．1文字目のTはCas9とは相互作用していなかった一方，2文字目のGはArg1585と2本の<a href="#" class="anno">水素結合</a>
を形成していた．このことから，<em>F</em>. <em>novicida</em>に由来するCas9のPAMの1文字目，2文字目がそれぞれN，Gであることが説明された．PAMとして5’-TGG-3’をもつ標的2本鎖DNAを含む複合体において3文字目のGはArg1556と2本の水素結合を形成していた一方，PAMとして5’-TGA-3’をもつ標的2本鎖DNAを含む複合体において3文字目のAはArg1556と1本の水素結合を形成していた．これらの構造の違いから，GよりAを好むというPAMの3文字目の<a href="#" class="anno">嗜好性</a>
が説明された．以上の構造的な特徴から，<em>F</em>. <em>novicida</em>に由来するCas9によるPAMの認識機構が明らかにされた．<br><br><a name="F2"></a>
<div id="fig2-caption-text" style="display: none;"><strong>図2　Cas9によるPAMの認識機構</strong><br>（a）<em>F</em>. <em>novicida</em>に由来するCas9による認識機構．相補鎖DNAは省略した．<br>（b）<em>S</em>. <em>pyogenes</em>に由来するCas9による認識機構．相補鎖DNAは省略した．<br>（c）<em>S</em>. <em>aureus</em>に由来するCas9による認識機構．相補鎖DNAは省略した．<br>（d）<em>F</em>. <em>novicida</em>に由来する<a href="#" class="anno">野生型</a>
のCas9による認識機構．<br>（e）<em>F</em>. <em>novicida</em>に由来する改変型のCas9による認識機構．変異させた<a href="#" class="anno">アミノ酸</a>
残基を赤色で示した．<br><a href="http://first.lifesciencedb.jp/wordpress/wp-content/uploads/2015/12/Nureki-Cell-16.2.25-Fig.2.jpg" target="_blank">[Download]</a>
</div>[hs_figure id=2&amp;image=/wordpress/wp-content/uploads/2015/12/Nureki-Cell-16.2.25-Fig.2.png&amp;caption=fig2-caption-text]<br><br><br>
'''

# 実際は置き換える文字列が複数あるケースがあるのでre.search()は使えない。
# 複数の置換（検出・置換）に対応する必要がある
pat1 = "\[hs_figure id=(\d).+caption-text\]"
obj = re.findall(pat1, st)


def multiple_replace(s):
    Fig1_jpg = "Okae-Cell-Stem-Cell-18.1.4-Fig.1.jpg"
    Fig2_jpg = "Okae-Cell-Stem-Cell-18.1.4-Fig.2.jpg"
    txt = s
    if obj:
        print(obj)
        # 取得したidリストでイテレーションする
        for i in obj:
            print(i)
            # group()を利用してidを抽出することができる。
            # 置き換えはidが一致する部分のみ
            pat2 = "\[hs_figure id={}.+caption-text\]".format(i)

            tmp = '''
                        <div id="figure{id_num}" class="hs-figure">
                            <div class="hs-figure-box">
                                <a class="highslide" title="$(fig1-caption-text)" onclick="return hs.expand(this, {{captionText: $('fig1-caption-text').innerHTML}})" href="{file_path}/{fig}" target="_blank">
                                    <img src="{file_path}/{fig}" alt="figure{id_num}" width="200px" />
                                </a>
                            </div>
                            <div id="fig{id_num}-caption" class="hs-figure-caption"></div>
                        </div>

                        <script type="text/javascript">$('fig1-caption').innerHTML = $('fig1-caption-text').innerHTML;</script>
                        <div style='clear:both;'></div>
                        '''

            file_path = "./uplodad"

            # figはid=1のときはFig1_jpg, id=2の時はFig2_jpg
            f = eval("Fig" + i + "_jpg")
            subs = tmp.format(id_num=i, file_path=file_path, fig=f)
            txt = re.sub(pat2, subs, st)


multiple_replace(str)


