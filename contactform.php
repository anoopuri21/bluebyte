<?php
if(isset($_POST['submit']))
{
	$toemail = "info@bluebyteitsolutions.com,websitesexperts@gmail.com";
	$strMessage='<table width="650px" border="2" align="center" cellpadding="5" cellspacing="0" bordercolor="#ddd" bgcolor="#ffffff" style=" border-collapse:collapse;font-family: sans-serif;">
		<tr>
			<td height="45" colspan="2" bgcolor="">
			<center><strong style="font-size:14px;">Bluebyte IT Solutions <br/> Contact Form</strong></center></td>
		</tr>
		<tr>
		<td width="30%" style="padding: 15px;background-color: #f9f2e2;">WebPage Url</td>
		<td width="70%" style="padding: 15px;color: #555;">'.$_SERVER['HTTP_REFERER'].'</td>
		</tr>
		<tr>
			<td width="30%" style="padding: 15px;background-color: #f9f2e2;">First Name</td>
			<td width="70%" style="padding: 15px;color: #555;">'.$_POST['firstName'].'</td>
		</tr>
		<tr>
			<td width="30%" style="padding: 15px;background-color: #f9f2e2;">Last Name</td>
			<td width="70%" style="padding: 15px;color: #555;">'.$_POST['lastName'].'</td>
		</tr>
		<tr> 
			<td width="30%" style="padding: 15px;background-color: #f9f2e2;">Contact Number</td>
			<td width="70%" style="padding: 15px;color: #555;">'.$_POST['phone'].'</td>
		</tr>
		<tr>
			<td width="30%" style="padding: 15px;background-color: #f9f2e2;">E-mail</td>
			<td width="70%" style="padding: 15px;color: #555;">'.$_POST['email'].'</td>
		</tr>
		<tr> 
			<td width="30%" style="padding: 15px;background-color: #f9f2e2;">Message</td>
			<td width="70%" style="padding: 15px;color: #555;">'.$_POST['message'].'</td>
		</tr>
	</table>';
	$strSubject = "Contact Form - Bluebyte IT Solutions ";
	$email = "no-reply@bluebyteitsolutions.com";
	$header = "From: " . $_POST['firstName'] . " <" . $email . ">\r\n";
	$header .= 'Content-type: text/html; charset=UTF-8' . "\r\n";
	$mail = mail($toemail, $strSubject, $strMessage, $header);
	if ($mail) {
		header('location:contact.html');
	}
}
?>
