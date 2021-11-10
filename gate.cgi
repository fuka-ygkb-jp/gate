#!/usr/bin/perl
$ver  = "1.0";		#変更しないで下さい
#+------------------------------------------------------------------------
#|最後の良心 (ページの門番 - CGI方式)
#|(C)1999-2003 不可思議絵の具 (http://yugen.main.jp/)
#+------------------------------------------------------------------------
#- 改修履歴 -
# 2003/01/13 1.0 より柔軟なアドレス指定。ログ機能追加。
# 2000/06/09 0.3 さらにクソつまんない欠陥を修正。　逝ってよし＞俺
# 2000/06/07 0.2 つまんないsyntax errorを修正。
# 1999/10/12 0.1 ちくちく作ってみる。
#+------------------------------------------------------------------------
#☆☆☆☆☆ 設定部 ☆☆☆☆☆
#+------------------------------------------------------------------------
### ≪必須設定項目≫
# [来て欲しくない人(ホスト)ブラックリスト]
# ワイルドカードを使用できます。　* は任意数の文字列を、? は１文字を表します。
@uDenyHost = (
	'proxy*.*',		#先頭に"proxy"を含むドメイン全てを排除 = プロキシを使うユーザを排除
	'*.ed.jp',		#教育機関(小・中・高校)からの訪問者を排除
	'*.go.jp',		#政府機関からの訪問者を排除
	'*.edu',		#米国教育機関からの訪問者を排除
);

# [ログファイル名]
$uLogName = 'gate.log';

# [ログ保存件数]
$uMaxLog = 50;

# [チェックした後に転送したいページ]
$uURL = './gate.html';


### ≪警告画面の表示設定≫
# [スタイルシートファイル名]
$uCssName = 'gate.css';

# [警告画面のタイトル]
$uMsgTitle = '注意';

# [警告画面の内容]
# HTMLを使用できます。
$uMsgBody = '
<body bgcolor="#000000" text="#ffffff" link="#7726c8" alink="#5c4fff" vlink="#ff5959">

<h1 class="title">－注意－</h1>
<hr>
<div class="message">
	<p>残念ですが、あなたのアクセスは許されていません。</p>
	<p>直ちに退去してください。</p>
</div>
';


# ※ここからは分かる人だけ弄って下さい。
# 　(タブのサイズ・[4]、折返し・[無し]で綺麗に表示されます)
#+------------------------------------------------------------------------
#|&main
#+------------------------------------------------------------------------

### 初期処理
# 変数宣言
my @log;			# ログ格納用ワーク
my $NewLine  = '';	# 新規ログ行
my $IsReject = 0;	# 招かれざる客であるか？
my $host     = '';	# IP/ホスト名

# HTMLヘッダ部
$HTMLHeader = "
<html>
<head>
	<meta name='Content-Type' content='text/html; charset=Shift-JIS'>
	<meta name='ROBOTS' content='NOINDEX,NOFOLLOW'>
	<meta name='Content-Style-Type' content='text/css'>
	<meta name='generator' content='gate.cgi ${ver}'>
	<meta name='copyright' content='&copy; 1999-2003 Yugen-Koubou'>
	<title>$uMsgTitle</title>
	<link rel='Stylesheet' href='./${uCssName}' type='text/css'>
</head>
";

# HTMLフッタ部（＋コピーライト）
$HTMLFooter = "
<hr>
	<address class='GateCopyright'>
		<a href='http://yugen.main.jp/'>最後の良心 ${ver}</a>
	</address>
</body>
</html>
";


# 訪問者のリモートホストを取得する
$host = &getRemoteHost($ENV{'REMOTE_ADDR'});

### メイン処理
&openLog;										# ログファイルを開く

$IsReject = &compareIP(\@uDenyHost, $host);		# IPをチェックする

if ($IsReject == 0) {							## ブラックリストと一致しなかった場合
	$NewLine = &makeNewLine('OK', $host);		# ログ新規行準備
	# 本来のページに飛ばす
	print "Location: $uURL\n\n";
} else {										## ブラックリストと一致した場合
	$NewLine = &makeNewLine('NG', $host);		# ログ新規行準備
	# 準備したエラー画面を出力する
	print "Content-type: text/html\n\n";
	print "$HTMLHeader";
	print "$uMsgBody";
	print "$HTMLFooter";
}

### 後処理
&writeLog;										# ログを書き込む
&closeLog;										# ログファイルを閉じる
exit;


### ログ新規行準備
sub makeNewLine {
	my($status, $host) = @_;
	return &makeDate(time)."\t$status\t$host";
}


### ログ開く
sub openLog {
	unless (open(LOG,"+<./${uLogName}")) {
		print "$HTMLHeader";
		print "<p>ログファイルを開くことができませんでした。</p>";
		print "$HTMLFooter";
		exit(1);
	}
	flock(LOG, 2);
	chomp(@log = <LOG>);
}

### ログ書き込む
sub writeLog {
	unshift(@log, $NewLine);	# 新しいログを付け足し、
	splice(@log,  $uMaxLog);	# 古いログは消し去る

	seek(LOG, 0, 0);

	foreach (@log) { print LOG "$_\n"; }

	truncate(LOG,tell);
}

### ログ閉じる
sub closeLog {
	flock(LOG, 8);
	close(LOG);
}


### リモートホストを取得する
sub getRemoteHost {
	my($ip) = @_;
	$ip = gethostbyaddr(pack("C4", split(/\./, $ip)), 2) || $ip;
	return $ip;
}


#---------------------------------------------------------------------
# 弾くべきIPかチェック ($IPlistと$targetIPを比較し、一致数を返す)
# 引数：
#	$IPlist   (IPアドレス/FQDN入り配列参照)
#	$targetIP (比較対象IPアドレス/FQDN)
# 返り値：
#	0     (一致無し)
#	1以上 (一致有り／一致件数)
#---------------------------------------------------------------------
sub compareIP {
	my($IPlist, $targetIP) = @_;
	my $hit = 0;

	foreach (@$IPlist) {
		$_ = '^'.$_.'$';
		s/\./\\\./g;	# "." → "\."
		s/\?/\./g;		# "?" → "."
		s/\*/\.\*/g;	# "*" → ".*"
		if ($targetIP =~ $_) { $hit++; }
	}

	return $hit;
}

#---------------------------------------------------------------------
# 通算秒から日時を得る関数
# 引数：
#	通算秒　(1970/01/01 00:00:00から)
# 返り値：
#	文字列　[年/月/日/(曜) 時:分:秒]
#---------------------------------------------------------------------
sub makeDate {
	my($t) = @_;
	my(@wdays, $sec, $min, $hour, $day, $mon, $year, $wday);
	@wdays=('日','月','火','水','木','金','土');
	($sec,$min,$hour,$day,$mon,$year,$wday) = localtime($t);
	return sprintf("%d/%02d/%02d(%s) %02d:%02d:%02d",1900+$year,$mon+1,$day,$wdays[$wday],$hour,$min,$sec);
}
