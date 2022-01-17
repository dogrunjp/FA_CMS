# 新着論文レビュー　pyssによる静的サイト構築メモ

## Google sheet apiの利用

- 従来のPythonからのapi利用は
- [Google SpreadSheetをAPI経由で読み書きする](http://www.yoheim.net/blog.php?q=20160205)
※　2016にSpread Sheet API v4がリリースされ、APIの機能が強化された。可能であればv4を利用できるか検討

### Google Drive APIの有効化と秘密鍵取得

1. [Dvelopers Console](https://console.developers.google.com/cloud-resource-manager)でプロジェクトを選択する。無い場合は適当な名前でプロジェクトを作成する。
1. API Managerをメニューから選び次いでダッシュボードから「Drive API」を有効にする。
1. OAuthクライアントIDと鍵を作成する。Developer Consoleでプロジェクトを開き、「認証情報/認証情報」に移動。
1. 「サービスアカウント＞新しいサービスアカウント」を選択し「サービスアカウント名」を入力し、役割を選択する。ex. FAManager
1. JSON形式でキーを作成する

### スプレッドシートの共有設定

- API Managerで設定したアカウントのメールアドレスを入力して、送信する。（メールアドレスは「サービスアカウントの管理」に表示されている）

これでPythonのgdata, oauth2clientを使ってアクセスできるはず

[PythonからOAuth2.0を利用してスプレッドシートにアクセスする](http://qiita.com/koyopro/items/d8d56f69f863f07e9378)


### v4 の場合認可の流れ

[Googleスプレドシートをプログラムから操作する](http://qiita.com/howdy39/items/ca719537bba676dce1cf)


### pythonでspreadsheetを使う

- 以前はSignedJwtAssertionCredentialsだったのだが2016年のアップデートで、ServiceAccountCredentialsになった
- PythonでOAuth2を扱うのはPyOpenSSLが必要。
- oauth2clientをアップデートする必要がある。下のコマンドでoauth2clientをインストール

```
pip install --upgrade oauth2client --ignore-instaed six
```

[pythonでGoogle Spread Sheetをいじる](http://qiita.com/AAkira@github/items/22719cbbd41b26dbd0d1)


## jinja2 & bootstrap 

bootstrap4を使ってみる

### css selector

-blog.css
    - h1: blog.css:{@media(min-width:40em).blog-title}
    - blog-post h2: .blog-post-title
    - blog-post ul: .blog-post ul  //追加
    - h2: .blog-post h2  //追加
    - blog-post ur br: .blog-post ul > br //追加＋display: noneにしliのline hightで調整
    - side bar h4: .sidebar-module h4 //追加
    - side bar p: .sidebar-module p //追加
 
    

[Bootstrap-blog](https://getbootstrap.com/docs/4.0/examples/blog/)


## S3にPythonからファイルアップロードする場合

[boto3でデータをファイルに保存せず直接アップロードする方法](http://dev.classmethod.jp/cloud/aws/upload-json-directry-to-s3-with-python-boto3/)
[botoを使ってS３にファイルを保存する](https://remotestance.com/blog/1671/)

### S3のポリシー&boto3を使ったアップロード

テスト用にIAMを使って管理者アカウントを作った
1.  ユーザを追加
1. 認証情報でアクセスキーを追加
1. アクセス権限の追加（AdministratorAccessを選択した。本来はS3の特定のバケットの管理のみ指定したい）
1. 認証情報でパスワードを有効化

バケットポリシー：Adminユーザの操作の許可を[AWS Policy Generator](http://awspolicygen.s3.amazonaws.com/policygen.html)を使って
作成する
- Effect: Allow
- Principal(設定したポリシーを受ける対象)：ユーザのARNを入力
- AWS Service : Step 1でS3 Bucket Policyのポリシータイプを選択する（とりあえずall actionにした。組み合わせが悪いとpolicyが通らない）
- Amazon Resource Name：バケットのARNを入力する。S3のアクセス権限を見ると書いてある。
- Generate Policyし、これをバケットのアクセス権限・バケットポリシーにコピペする


### ファイルの公開属性

何もしないと非公開のママっぽい

```
obj_acl = s3.ObjectAcl(bucket_name, object_key)
res = object_acl.put(ACL='public-read')
```

### アクセスキーのインストール

~/.awsに設定ファイルを置くと何も考えずboto3から利用できる雰囲気ではあるが、、、

[アクセスキーのインストール](https://www.saintsouth.net/blog/upload-file-to-s3-bucket-from-a-host-by-aws-sdk/)

boto3.sessionを使った方が明示的で良いと思う（キーの切替等）下記リンクでは、デフォルトの場合、keyの明示的指定、~/.aws/credentialのケースを紹介している
[boto3でデフォルトprofile以外を使う](http://qiita.com/inouet/items/f9723d7ae7d8d134280b)

[Botoを使ってS3にアップロードしたファイルを取得する](http://akiyoko.hatenablog.jp/entry/2015/08/13/020202)

## JST シソーラスを利用した単語アノテーション

### キーワードデータ
get_keywords() 取得サンプル

```
{'一般語フラグ1': 0, '出現頻度': 1, 'FA見出し語': 'Ambyst対応するシソーラス語の数': 1, '削除候補': 0, '一般語フラグ2': 'UNKNOWN_1'}, 
{'一般語フラグ1': 0, '出現頻度': 1, 'FA見出し語': 'Alzheimer', 'シソーラス語の標準名とカテゴリー': 'Ａｌｚｈｅｉｍｅｒ病/病気・', '見出しに対応するシソーラス語の数': 1, '削除候補': 0, '一般語フラグ2': 'UNKNOWN_1'}, 

```
コンテンツデータ取得サンプル
```
{'update': '', 
'Fig2_caption': '', 
'OriginalArticle': 'Cell', 
'Fig1_caption': '図1\u3000老化により概日時計とリンクする代謝経路の再編成が進行する', 
'Author': '佐藤章悟・Paolo Sassone-Corsi', 
'OriginalArtr Solanas, Francisca Oliveira Peixoto, Leonardo Bee, Aikaterini Symeonidi, Mark S. Schmidt, Charles Brenner, Selma Masri, Salvador Aznar Benitah, Paolo Sassone-Corsi', 
'Title': '概日時計の機能の再編成が'Fig3_caption': '', 
'Fig2_jpg': '', 
'Post_Content': '<strong>佐藤章悟・Paolo Sassone-Corsi</strong><br>（米国California大学Irvine校Center for Epigenetics and Metabolism）<br>email：<a href="mailto:satos章悟</a><br>DOI: <a href="http://dx.doi.org/10.7875/first.author.2017.099">10.7875/first.author.2017.099</a><br><div class="reference"><br><span class="ti">Circadian reprogramming in the liver identifiemetabolic pathways of aging.</span><br><span class="au">Shogo Sato, Guiomar Solanas, Francisca Oliveira Peixoto, Leonardo Bee, Aikaterini Symeonidi, Mark S. Schmidt, Charles Brenner, Selma Masri, Salvador Aznar Benitah, Paolo Sassone-Corsi</span><br><span class="so"><a href="http://www.ncbi.nlm.nih.gov/pubmed/28802039" target="_blank"><em>Cell</em>, <strong>170</strong>, 664-677.e11 (2017)</a></span></div><br><br><!--more--><br><br><h2>要 約</h2><br>\u3000老化と概日リズムの劣化は水魚之交であるが，末梢組織において代謝を制御する概日時計に対し老化はどのように影響するのだろうか．また，カロリーの摂取の制した若齢あるいは老齢のマウスの肝臓における概日リズムを示す転写産物のプロファイリングにより，老化に特有な代謝，とくに，タンパク質のアセチル化修飾に関与する代謝経路の再編成が進行することが明らかにされた．リズムは，老齢のマウスにおいて消失していた．また，カロリーの摂取の制限はNAD<sup>+</sup>-SIRT1代謝経路において概日時計の制御を向上させ，タンパク質のアセチル化修飾を亢進することが示された．この研究により，計は，地球の自転がつくりだす明暗のサイクルに同調し行動や生理機能に概日リズムを生じさせる．概日リズムは24時間周期の転写-翻訳フィードバックループにより制御される．この分子機構の中心を担うコア時計遺伝子の産MAL1およびCLOCKは，転写因子として標的となる多くの遺伝子の発現の概日リズムも制御する．そのため，不規則なライフスタイルにともなう概日時計の機能の障害，あるいは，時計遺伝子そのものの遺伝的な変異により，代謝リン抵抗性など代謝の恒常性を維持する機能の劣化，睡眠障害など概日リズムの減弱があげられる．しかし，老化が概日時計による代謝の制御におよぼす影響については不明である．また，アンチエイジングの鍵として有力な方，時計遺伝子の発現を増強することが報告されている<a href="#R1"><sup>1)</sup></a>．そのため，寿命を延長しうるカロリーの摂取の制限への適用を仲介する概日リズムを示す代謝の解明は重要な研究課題である．この研取の制限による概日時計への影響</h2><br>\u3000肝臓における概日時計および概日時計により制御される代謝におよぼす老化の影響について検討するため，若齢および老齢のマウスを12時間-12時間の明暗サイクルにおき，4時のマウスに特異的に概日リズムを示した．概日リズムの振幅は老齢のマウスにおいて減弱していた．また，コア時計遺伝子およびそれらの標的となる遺伝子の発現レベルを若齢のマウスと老齢のマウスとのあいだで比較したとに効果的であるとされるカロリーの摂取の制限が概日時計と代謝との相互作用におよぼす影響について明らかにするため，30％カロリー制限食あるいは通常食を若齢マウスあるいは老齢のマウスに6カ月にわたり負荷した．その示した．くわえて，カロリー制限食を負荷したマウスにおける概日リズムの振幅は，通常食を負荷したマウスに比べて顕著に大きかった．さらに，カロリーの摂取の制限によりコア時計遺伝子およびそれらの標的となる遺伝子チル化修飾</h2><br>\u3000肝臓におけるトランスクリプトームのデータを用いて，遺伝子オントロジー解析により概日リズムを示す代謝経路や生物学的な機能の特定を試みた．ほかの組織におけるトランスクリプトームのデーおよびタンパク質のアセチル化修飾が見い出され，これらは老化により再編成されると推察された．そこで，12時間-12時間の明暗サイクルにおいたマウスの肝臓における全タンパク質のアセチル化修飾のレベルを比較したとこル化修飾を劇的に亢進させた．以上の結果から，カロリーの摂取の制限は老化にともなうタンパク質のアセチル化修飾の制御の不全をふせぐ可能性が見い出された．<br>\u3000タンパク質のアセチル化修飾の変化はヒストンのるヒストンH3のLys9，Lys14，Lys27のアセチル化は，若齢および老齢のマウスにおいてカロリーの摂取の制限により亢進した．さらに，コア時計遺伝子だけでなく，一部の代謝関連遺伝子のプロモーター領域におけるヒストンは一致したため，カロリーの摂取の制限による遺伝子の発現の亢進および時計遺伝子の発現の制御には，ダイナミックなヒストンの修飾およびそれにともなうクロマチン構造の再編成が強く関与することが示唆された．<br><bミドホスホリボシルトランスフェラーゼを介したNAD<sup>+</sup>の生合成経路は老化に直接的に寄与するだけでなく，NAD<sup>+</sup>のレベルの上昇は延命や老後の健康の維持に貢献すると報告されている<a href="#R3"><s効果を仲介するタンパク質として大きく注目されている．NAD<sup>+</sup>のレベルは概日リズムを示すだけでなく，SIRTが肝臓における転写および代謝の概日リズムの制御を担うことから<a href="#R4"><sup>4,5)</sup></a>3000そこで，老化あるいはカロリーの摂取の制限によるNAD<sup>+</sup>の代謝における概日リズムの制御への影響を明確にするため，12時間-12時間の明暗サイクルにおいたマウスの肝臓におけるNAD<sup>+</sup>およびNAD<sp>はカロリーを制限したマウスの，とくに明期の開始時において顕著に増加した．同様に，ニコチンアミドアデニンジヌクレオチドリン酸も明期の開始時および暗期の開始時において有意に増加した．また，カロリーの摂取のde novo</em>合成に利用されるニコチン酸アデニンジヌクレオチドはカロリーの摂取の制限により減少した．一方，NAD<sup>+</sup>の消費により生じるニコチンアミドやADPリボースは老齢のマウスにおいて増加していた．以sup>の代謝回転を促進する可能性が示された．一方で，カロリーの摂取の制限はNAD<sup>+</sup>の代謝における概日リズムの制御を鋭利にし，とくに，NAD<sup>+</sup>サルベージ経路に対する再編成を促進するものと考えら連する代謝産物のダイナミックな変化をうけ，NAD<sup>+</sup>に依存的な脱アセチル化酵素であるSIRT1の活性に注目した．そこで，肝臓に特異的なSIRT1ノックアウトマウスの肝臓におけるトランスクリプトームのデータ<a わせた．その結果，カロリー制限食を負荷した若齢および老齢のマウスの肝臓における時計遺伝子にしめるSIRT1の標的となる遺伝子は，通常食を負荷したマウスと比べて約5倍も多かった．このことから，カロリーの摂取の制>\u3000老化の進行にブレーキをかけるカロリーの摂取の制限により，肝臓における代謝の概日リズムがどのように変わるか検討した．とくに，カロリーを制限したマウスの肝臓においてみられたタンパク質のアセチル化修飾のとつであるが，解糖系を担う酵素の発現はカロリーの摂取の制限により激減した．他方，クエン酸からアセチルCoAへの変換を担うATPクエン酸シンターゼは脂質の<em>de novo</em>合成の制御を担う転写因子SREBPにより制御さな再編成が認められ，これらの代謝経路からのアセチルCoAの供給の断絶が示唆された．<br>\u3000アセチルCoAの供給にかかわるそのほかの代謝経路として，アセチルCoAシンターゼによる酢酸からアセチルCoAへの変換が考えリズムを示す<a href="#R7"><sup>7)</sup></a>．実際に，カロリーを制限したマウスの肝臓において酢酸の増加が観察された．アセチルCoAシンターゼのアセチル化のレベルは通常食を負荷したマウスの肝臓では12時間-12時間チルCoAシンターゼが活性化していると推察された．これまでにも，カロリーの摂取の制限による肝臓における酢酸およびアセチルCoAの増加が報告されているため<a href="#R8"><sup>8)</sup></a>，最終的に，SIRT1によるア><h2>おわりに</h2><br>\u3000この研究により，肝臓の概日時計とリンクする代謝経路の大胆な再編成が老化により進行することが示された（<a href="#F1">図1</a>）．また，アンチエイジングに効果的とされるカロリーの摂a href="#F1">図1</a>）．とくに，種々の時計遺伝子や発現が概日リズムを示す遺伝子のプロモーター領域において観察されたカロリーの摂取の制限によるヒストンのアセチル化の亢進が，概日時計の制御を向上させる，あるが注視されることを望む．<br><br><a name="F1"></a><div id="fig1-caption-text" style="display: none;"><strong>図1\u3000老化により概日時計とリンクする代謝経路の再編成が進行する</strong><br><a href="http://nt/uploads/2017/09/Sato-Cell-17.8.10-Fig.1.jpg" target="_blank">[Download]</a></div>[hs_figure id=1&amp;image=/wordpress/wp-content/uploads/2017/09/Sato-Cell-17.8.10-Fig.1.png&amp;caption=fig1-caption-text]<br><br><br><h2>文 献</h2><br><ol><br><li id="R1"><span class=\'au\'>Asher, G. & Sassone-Corsi, P.</span>: <span class="ti">Time for food: the intimate interplay between nutrition, metabolism, and t circadian clock.</span> <span class=\'so\'>Cell, 161, 84-92 (2015)[<a href="http://www.ncbi.nlm.nih.gov/pubmed/25815987" target="_blank">PubMed</a>]</span></li><br><li id="R2"><span class=\'au\'>Solanas, G., Oliveira Peixoto, F., Perdiguero, E. et al.</span>: <span class="ti">Aged stem cells reprogram their daily rhythmic functions to adapt to stress.</span> <span class=\'so\'>Cell, 170, 678-692 (2017)[<a href="http://www.ncbi.nlm.nih.gov/pubmed/28802040" target="_blank">PubMed</a>]</span></li><br><li id="R3"><span class=\'au\'>Zhang, H., Ryu, D., Wu, Y. et al.</span>: <span class="ti">NAD<sup>+</sup> repletion improves mitochondrial and stem cell function and enhances life span in mice.</span> <span class=\'so\'>Science, 352, 1436-1443 (2016)[<a href="http://www.ncbi.nlm.nih.gov/pubmed/27127236" target="_blank">PubMed</a>]</span></li><br><li id="R4"><span class=\'au\'>Nakahata, Y., Kaluzova, M., Grimaldi, B. et al.</span>: <span class="ti">The NAD<sup>+</sup>-dependent deacetylase SIRT1 modulates CLOCK-mediated chromatin remodeling and circadian control.</span> <span class=\'so\'>Cell, 134, 329-340 (2008)[<a href="http://www.ncbi.nlm.nih.gov/pubmed/18662547" target="_blank">PubMed</a>]</span></li><br><li id="R5"><span class=\'au\'>Nakahata, Y., Sahar, S., Astarita, G. et al.</span>: <span class="ti">Circadian control of the NAD<sup>+</sup> salvage pathway by CLOCK-SIRT1.</span> <span class=\'so\'>Science, 324, 654-657 (2009)[<a href="http://www.ncbi.nlm.nih.gov/pubmed/19286518" target="_blank">PubMed</a>]</span></li><br><li id="R6"><span class=\'au\'>Masri, S., Rigor, P., Cervantes, M. et al.</span>: <span class="ti">Partitioning circadian transcription by SIRT6 leads to segregated control cellular metabolism.</span> <span class=\'so\'>Cell, 158, 659-672 (2014)[<a href="http://www.ncbi.nlm.nih.gov/pubmed/25083875" target="_blank">PubMed</a>]</span></li><br><li id="R7"><span class=\'au\'>Sahar, S., Masubuchi, S., Eckel-Mahan, K. et al.</span>: <span class="ti">Circadian control of fatty acid elongation by SIRT1-mediated deacetylation of acetyl-CoA synthetase 1.</span> <span class=\'so\'>J. Biol. Chem., 289, 6091-6097 (2014)[<a href="http://www.ncbi.nlm.nih.gov/pubmed/24425865" target="_blank">PubMed</a>]</span></li><br><li id="R8"><span class=\'au\'>Pietrocola, F., Galluzzi, L., Bravo-san Pedro, J. M. et al.</span>: <span class="ti">Acetyl coenzyme A: a central metabolite and second messenger.</span> <span class=\'so\'>Cell Metab., 21, 805-821 (2015)[<a href="http://www.ncbi.nlm.nih.gov/pubmed/26039447" target="_blank">PubMed</a>]</span></li><br></ol><br><h2>生命科学の教科書におンへのリンク</h2><br><a href="http://www.adves.c.u-tokyo.ac.jp/" target="_blank">東京大学 大学院総合文化研究科・教養学部附属教養教育高度化機構自然科学教育高度化部門</a>から公開されている生命科学の教科書 Comprehensive Approach To LIFE SCIENCE</a>”（羊土社『理系総合のための生命科学 第2版』の英語版）における関連するセクションへのリンクです．<br><ul><br><li><a href="http://csls-text3.c.u-tokyo.ac.jp/inacton and Fermentation: Glycolysis</a></li><br><li><a href="http://csls-text3.c.u-tokyo.ac.jp/inactive/02_05.html" target="_blank">2.5 Proliferation and Growth of Organisms and Environment</a></li><br><li><a href="http://csls-text3.c.u-tokyo.ac.jp/inactive/04_01.html" target="_blank">4.1 Enzyme Sets Determine the Organism’s Way of Life</a></li><br><li><a href="http://csls-text3.c.u-tokyo.ac.jp/inactive/04_03.html" target="_blank">4.3 Fundamentals of the Flow of Energy and Substances</a></li><br><li><a href="http://csls-text3.c.u-tokyo.ac.jp/inactive/04_04.html" target="_blank">4.4 Intracellular Metabolism</a></li><br></ul><br><div class="au-profile"><br><h2>著者プロフィール</h2><br><span class="author">佐藤 章悟（Shogo Sato）</span><br>略歴：2012年 早稲田大学大学院人間科学研究科博士課程 修了，同年 杏dical CenterにてPost-doctoral fellowを経て，2015年より米国California大学Irvine校Post-doctoral fellow．<br>研究テーマ：概日時計のマジックの種明かしおよび健康への利用．<br>抱負：社会的な時間にしばられないだねた生活をおくる．<br><br><strong>Paolo Sassone-Corsi</strong><br>米国California大学Irvine校Professor．<br></div><br>© 2017 佐藤章悟・Paolo Sassone-Corsi Licensed under <a href="http://creativecommonsjp/" target="_blank">CC 表示 2.1 日本</a>', 
'FA_ID': 1117, 'Fig4_jpg': '', 
'Fig3_jpg': '', 
'OriginalArticle_Number': '170, 664-677.e11 (2017)', 
'Doc': 'Sato-Cell-17.8.10.doc', 
'FA_URL': 'http://first.liiencedb.jp/archives/17134', 
'filename': 1117, 'Txt': 'Sato-Cell-17.8.10.txt', 
'Post_Tag': 'マウス, 分子生物学, 概日時計, 老化', 
'DOI': '10.7875/first.author.2017.099', 
'Date': '2017/09/14', 
'Fig1_jpg': 8.10-Fig.1.jpg', 
'OriginalArticle_Title': 'Circadian reprogramming in the liver identifies metabolic pathways of aging.', 
'Fig4_caption': ''}

```

### hover card表示について

- 必要なライブラリはjquery(1 or 2)とhovercard

```
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js"></script>
    <script type="text/javascript" src="js/jquery.hovercard.min.js"></script>
```
- hovercardを表示したい要素のセレクターにhovercard()を渡せば表示される

```
<script type="text/javascript">

      $(document).ready(function () {
          var cardBase = '<p class="title">Title: Hover card test!<p><br/><p class="link">Link: http://ja.dbpedia.org/page/</p>';
          var aboutKW = {
              name: "FA Hover Card test",
              link: "http://ja.dbpedia.org/page/",
          };
          // callback
          $(".anno").hovercard({
              detailsHTML: cardBase,
              openOnTop: true,
              width: 400,
              cardImgSrc: 'http://togotv.dbcls.jp/images/s/201309_DNA.png',
              showCustomCard: true,
              customCardJSON: aboutKW,
              onHoverIn: function(){
                  var kw = this.firstChild.textContent;
                  $(".hc-details .s-card .s-loc").text(kw).attr("href",baseurl + kw)
              }
            })
              }
            })
      });
  </script>

```

## annotationのデータソース

### DBpedia

SPARQLでcsvを取得する場合（例：対立遺伝子）
```
http://ja.dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fja.dbpedia.org&query=select+distinct+*+where+%7B+%3Chttp%3A%2F%2Fja.dbpedia.org%2Fresource%2F対立遺伝子%3E+dbpedia-owl%3Aabstract+%3Fo+.++%7D+LIMIT+1&should-sponge=&format=text%2Fcsv&timeout=0&debug=on
```

## githubにpushする際に Google cloud api key, aws iamの情報、aws s3のfull＿access_confを一旦コミットしてしまった

GitGurdian (GCP)、AWS、Google-cloud-complianceから警告が届く

- GoogleのAPI key conf/FirstAuthor-30b6c7309175.json を作り直した方が良い
- awsのiamを作り直す
- aws s3のfullaccess confを作り直す（fa-bmu-jp）

### 対応

ユーザから削除＆新規作成
- pyss_testを削除した（コピーはpyss-test-2）
- fa-bmu-jpを削除fa-bmu-jp-２をコピー、aws configureを登録し直した。
- GCP にユーザを作り直し（famanager2）jsonkeyを取得。テスト環境は"famanager2@firstauthor-176006.iam.gserviceaccount.com"で実験中（先ずはローカルで）
- famanagerのrollをeditorからviewerに変更
- FAのconfigをfamanager2で対応
- LAのconfigもfamanager2に変更


### 2020-21

Spread


## S3

テストサイト用のバケットと同期する

```
aws s3 sync html/ s3://fa.bmu.jp --profile fa-bmu-jp --content-type "text/html"
aws s3 sync s3://leading.lifesciencedb.jp/d3 --profile la-s3
```

バケットから特定のファイルを削除する

```
aws s3 rm s3://fa.bmu.jp/{file name} d3 --profile la-s3
```

バケットのファイル一覧取得
```
$ aws s3 ls s3://fa.bmu.jp/ --profile fa-bmu-jp

```

## gitのリモートからのみファイルを削除する

- git rm --cached hoge.json
- git add -u
- git commit -m "delete some file"
- git push origin master

# gitの履歴を削除する

- 指定したファイルを消す
git filter-branch --tree-filter "rm -f [消したいファイルパス]" HEAD

- 指定したディレクトり以下を消す
git filter-branch --tree-filter "rm -f -r [消したいディレクトリパス] " HEAD

- リポジトリを最適化
git gc --aggressive --prune=now

で、git push -f

[Git リポジトリに上が

## 正規表現を利用した置き換え

### タグ内部を置き換えの対象としない

- tagを丸ごと置き換える正規表現

タグの正規表現は
"\<.+?\>"

```
>>> import re
>>> s = '<a href="mailto:taket0901@cpnet.med.keio.ac.jp">貞廣威太郎</a>，<a href="mailto:mieda@md.tsukuba.ac.jp">家田真樹</a><br>'
>>> import re
>>> txt = re.sub("\<.+?\>", "--", s)
>>> txt
'--貞廣威太郎--，--家田真樹----'
```

他の書き方では

```
>>> m = re.search('(\<.+?\>)', s)
>>> m.group()
'<a href="mailto:taket0901@cpnet.med.keio.ac.jp">'

```

- 任意の文字列を含まない文字列の正規表現（否定先読み、否定戻り読み）

一文の先頭や行末にPatternがあるか無いかの正規表現

[正規表現：文字列を「含まない」否定の表現まとめ](http://www-creators.com/archives/1827)


 m = re.search(r'Nikon(?=FE2)', camera)
 
 先読みアサーションで"NiconFE2"がマッチする
 
 [pythonの先読みアサーション](https://qiita.com/kawarayu/items/64b44e04eb57cbef8718)

- AND条件
[正規表現：AND（かつ）の表現方法](http://www-creators.com/archives/5332)

```
s = '<a href="mailto:taket0901@cpnet.med.keio.ac.jp">acdc</a>，<a href="mailto:mieda@md.tsukuba.ac.jp">beatles</a><br>'
>>> m = re.search('(ac)(dc)', s)
>>> m.group()
'acdc'
```

- findall, finditer
finallはマッチした文字をリストで返す
finditerはポジションをiteratorで返す

- pythonでの先読みの利用
```
s = '<a href="mailto:taket0901@cpnet.med.keio.ac.jp">acdc</a>，<a href="mailto:mieda@md.tsukuba.ac.jp">beatles</a><br>'
>>> m = re.search('(?=.*ac)dc', s)
>>> m
<_sre.SRE_Match object; span=(50, 52), match='dc'>
>>> m.group(0)
'dc'
```

- >を後ろにもたないacを置換--上手くいかない
```
>>> new_t = re.sub('ac((?!.\>).)*?', 'sample', s)
>>> new_t
'<a href="mailto:taket0901@cpnet.med.keio.sample.jp">sampledc</a>，<a href="mailto:mieda@md.tsukuba.sample.jp">beatles</a><br>'
>>> 
```

```
'<a href="mailto:taket0901@cpnet.med.keio.ac.jp">acdc</a>，<a href="mailto:mieda@md.tsukuba.ac.jp">beatles</a><br>'
>>> new_t = re.sub('ac((?!dc).)*', 'hoge', s)
>>> new_t
'<a href="mailto:taket0901@cpnet.med.keio.hogedc</a>，<a href="mailto:mieda@md.tsukuba.hoge'

```

###　正規表現、ほぼ回答があった

ただしaタグの時のみ

(?!<a[^>]*?>)(Test)(?![^<]*?</a>)

[Regex replace text but exclude when text is between specific tag](https://stackoverflow.com/questions/12493128/regex-replace-text-but-exclude-when-text-is-between-specific-tag)

### 置き換え語にマッチした単語を含める

```
ptn = '(?!<a[^>]*?>)({})(?![^<]*?</a>)'.format(k)
rep = r'<a href="#" class="anno \1">\1</a>'
s = re.sub(ptn, rep, s, 1)
```
```
rep = r'<a href="#" class="anno \g<0>">\g<0></a>'
```
でも同様の結果となった

### 否定的あと読みの修正

否定的後読みは直前のアルファベットのみ
否定的先読みに</a>タグを残した

ptn = '(?<![a-zA-Z])({})(?![^<]*?</a>)'.format(k)

[正規表現の先読み・あと読みを極める](https://abicky.net/2010/05/30/135112/)

### AND条件の追加　アルファベットに連続してキーワードが出現したときはアノテーションしないケースでは

先用み否定形に下記を追加するとアルファベットに続くキーワードは排除される
(?![a-z]+)
```
ptn = '(?!<a[^>]*?>)(?![a-z]+)({})(?![^<]*?</a>)'.format(k)
```
   

### マッチオブジェクト

group(), start(), end(), span()のメソッドをもつ


### 否定先読みをAND条件でを使うとre.IGNORECASEが正常に働かない？

ptn = re.compile('(?![a-zA-Z])(?!<a[^>]*?>)({})(?![^<]*?</a>)'.format(k), re.IGNORECASE)
ptn = re.compile('(?!<a[^>]*?>)(?![a-zA-Z])({})(?![^<]*?</a>)'.format(k), re.IGNORECASE)

このパターンは機能しない。re.IGNORECASE と (?![a-z])が両立しない。どちらかがなければ動く

厳しくアノテーションするなら、re.IGNORECASEを外ししか、現状ないかも

## 辞書ルックアップ（ahocorapy.keywordtreee）でヒットする単語の検出とオーバーラップするポジションの検出



## beautifulsoupをtextの検索に使う場合

__beautifulsoupのx.text.lower()を利用してテキストを取得した場合、タグに囲まれた範囲で完全に一致するtextを検索することになる__
したがって、<em>Tbx6</em>とかは取得できるけど、他のテキストに混じって出現する場合は検索にならない

```
def test_bs4(kws, txt):
    sp = bs(txt, 'html.parser')
    for w in kws:
        w = w.lower()
        # lower()無しだとcase sensitive
        m = sp.find(lambda x: x.text.lower() == w)
```

[テキストで検索し、HTMLで置換するBeautifulSoup](https://code-examples.net/ja/q/10059c9)

```
>>> soup = bs4.BeautifulSoup(test)
>>> matches = soup.find_all(lambda x: x.text.lower() == 'here is some silly text'):
>>> for match in matches:
...     match.wrap(soup.new_tag('mark'))
>>> soup
<html><body><h1>oh hey</h1><mark><div>here is some <b>SILLY</b> text</div></mark></body></html>
```

[BS4のfind()とfind_all()](http://mankuro.hateblo.jp/entry/2017/05/02/beautifulsoup4-find-and-find_all/)


## キーワードの取得

- 現状（2018-10）ではスプレッドシートの見出し語候補から、dictionary=Geneで一般語フラグと削除フラグが立っていない語を取得している。
- 取得はpyss.get_keywords(config): keyword_list

## 更新操作&コマンド

- アップデートする記事にGoogle docsのFA_MasterFileの"update"からむの値に何かを入力する（ex. testなど）
- ステージング環境にページを生成する：　$ sudo python3 pyss.py -u
- htmlファイルを同期する： $ sudo python3 pyss.py -s
- html以外のファイルを同期する: $ sudo python3 pyss.py -b

* htmlは拡張子をつけないため、htmlファイルとして扱うようにS3にアップする際に設定を追加するためhtmlのみ別処理となる


## 確認
- test server: http://fa-render.dbcls.jp