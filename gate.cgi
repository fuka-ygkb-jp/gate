#!/usr/bin/perl
$ver  = "1.0";		#�ύX���Ȃ��ŉ�����
#+------------------------------------------------------------------------
#|�Ō�̗ǐS (�y�[�W�̖�� - CGI����)
#|(C)1999-2003 �s�v�c�G�̋� (http://yugen.main.jp/)
#+------------------------------------------------------------------------
#- ���C���� -
# 2003/01/13 1.0 ���_��ȃA�h���X�w��B���O�@�\�ǉ��B
# 2000/06/09 0.3 ����ɃN�\�܂�Ȃ����ׂ��C���B�@�����Ă悵����
# 2000/06/07 0.2 �܂�Ȃ�syntax error���C���B
# 1999/10/12 0.1 ������������Ă݂�B
#+------------------------------------------------------------------------
#���������� �ݒ蕔 ����������
#+------------------------------------------------------------------------
### ��K�{�ݒ荀�ځ�
# [���ė~�����Ȃ��l(�z�X�g)�u���b�N���X�g]
# ���C���h�J�[�h���g�p�ł��܂��B�@* �͔C�Ӑ��̕�������A? �͂P������\���܂��B
@uDenyHost = (
	'proxy*.*',		#�擪��"proxy"���܂ރh���C���S�Ă�r�� = �v���L�V���g�����[�U��r��
	'*.ed.jp',		#����@��(���E���E���Z)����̖K��҂�r��
	'*.go.jp',		#���{�@�ւ���̖K��҂�r��
	'*.edu',		#�č�����@�ւ���̖K��҂�r��
);

# [���O�t�@�C����]
$uLogName = 'gate.log';

# [���O�ۑ�����]
$uMaxLog = 50;

# [�`�F�b�N������ɓ]���������y�[�W]
$uURL = './gate.html';


### ��x����ʂ̕\���ݒ��
# [�X�^�C���V�[�g�t�@�C����]
$uCssName = 'gate.css';

# [�x����ʂ̃^�C�g��]
$uMsgTitle = '����';

# [�x����ʂ̓��e]
# HTML���g�p�ł��܂��B
$uMsgBody = '
<body bgcolor="#000000" text="#ffffff" link="#7726c8" alink="#5c4fff" vlink="#ff5959">

<h1 class="title">�|���Ӂ|</h1>
<hr>
<div class="message">
	<p>�c�O�ł����A���Ȃ��̃A�N�Z�X�͋�����Ă��܂���B</p>
	<p>�����ɑދ����Ă��������B</p>
</div>
';


# ����������͕�����l�����M���ĉ������B
# �@(�^�u�̃T�C�Y�E[4]�A�ܕԂ��E[����]���Y��ɕ\������܂�)
#+------------------------------------------------------------------------
#|&main
#+------------------------------------------------------------------------

### ��������
# �ϐ��錾
my @log;			# ���O�i�[�p���[�N
my $NewLine  = '';	# �V�K���O�s
my $IsReject = 0;	# �����ꂴ��q�ł��邩�H
my $host     = '';	# IP/�z�X�g��

# HTML�w�b�_��
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

# HTML�t�b�^���i�{�R�s�[���C�g�j
$HTMLFooter = "
<hr>
	<address class='GateCopyright'>
		<a href='http://yugen.main.jp/'>�Ō�̗ǐS ${ver}</a>
	</address>
</body>
</html>
";


# �K��҂̃����[�g�z�X�g���擾����
$host = &getRemoteHost($ENV{'REMOTE_ADDR'});

### ���C������
&openLog;										# ���O�t�@�C�����J��

$IsReject = &compareIP(\@uDenyHost, $host);		# IP���`�F�b�N����

if ($IsReject == 0) {							## �u���b�N���X�g�ƈ�v���Ȃ������ꍇ
	$NewLine = &makeNewLine('OK', $host);		# ���O�V�K�s����
	# �{���̃y�[�W�ɔ�΂�
	print "Location: $uURL\n\n";
} else {										## �u���b�N���X�g�ƈ�v�����ꍇ
	$NewLine = &makeNewLine('NG', $host);		# ���O�V�K�s����
	# ���������G���[��ʂ��o�͂���
	print "Content-type: text/html\n\n";
	print "$HTMLHeader";
	print "$uMsgBody";
	print "$HTMLFooter";
}

### �㏈��
&writeLog;										# ���O����������
&closeLog;										# ���O�t�@�C�������
exit;


### ���O�V�K�s����
sub makeNewLine {
	my($status, $host) = @_;
	return &makeDate(time)."\t$status\t$host";
}


### ���O�J��
sub openLog {
	unless (open(LOG,"+<./${uLogName}")) {
		print "$HTMLHeader";
		print "<p>���O�t�@�C�����J�����Ƃ��ł��܂���ł����B</p>";
		print "$HTMLFooter";
		exit(1);
	}
	flock(LOG, 2);
	chomp(@log = <LOG>);
}

### ���O��������
sub writeLog {
	unshift(@log, $NewLine);	# �V�������O��t�������A
	splice(@log,  $uMaxLog);	# �Â����O�͏�������

	seek(LOG, 0, 0);

	foreach (@log) { print LOG "$_\n"; }

	truncate(LOG,tell);
}

### ���O����
sub closeLog {
	flock(LOG, 8);
	close(LOG);
}


### �����[�g�z�X�g���擾����
sub getRemoteHost {
	my($ip) = @_;
	$ip = gethostbyaddr(pack("C4", split(/\./, $ip)), 2) || $ip;
	return $ip;
}


#---------------------------------------------------------------------
# �e���ׂ�IP���`�F�b�N ($IPlist��$targetIP���r���A��v����Ԃ�)
# �����F
#	$IPlist   (IP�A�h���X/FQDN����z��Q��)
#	$targetIP (��r�Ώ�IP�A�h���X/FQDN)
# �Ԃ�l�F
#	0     (��v����)
#	1�ȏ� (��v�L��^��v����)
#---------------------------------------------------------------------
sub compareIP {
	my($IPlist, $targetIP) = @_;
	my $hit = 0;

	foreach (@$IPlist) {
		$_ = '^'.$_.'$';
		s/\./\\\./g;	# "." �� "\."
		s/\?/\./g;		# "?" �� "."
		s/\*/\.\*/g;	# "*" �� ".*"
		if ($targetIP =~ $_) { $hit++; }
	}

	return $hit;
}

#---------------------------------------------------------------------
# �ʎZ�b��������𓾂�֐�
# �����F
#	�ʎZ�b�@(1970/01/01 00:00:00����)
# �Ԃ�l�F
#	������@[�N/��/��/(�j) ��:��:�b]
#---------------------------------------------------------------------
sub makeDate {
	my($t) = @_;
	my(@wdays, $sec, $min, $hour, $day, $mon, $year, $wday);
	@wdays=('��','��','��','��','��','��','�y');
	($sec,$min,$hour,$day,$mon,$year,$wday) = localtime($t);
	return sprintf("%d/%02d/%02d(%s) %02d:%02d:%02d",1900+$year,$mon+1,$day,$wdays[$wday],$hour,$min,$sec);
}
