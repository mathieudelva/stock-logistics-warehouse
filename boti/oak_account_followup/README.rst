When Mass Mailing from Odoo and when the contact record
has multiple email address being separated like this: >,< 
The emails are not going out and causing issues.


Tech Specification
==================

At enterprise/account_followup/models/account_followup_report.py, send_email(): 
This method finds the invoicing contact, then sends the follow up email to it.
It needs to be overridden to set the email to the Contacts list we want.
For this we need to modify the "message_post()" call,
setting the appropriate value on "partner_ids" argument.

To get the list of Partners to send the email to,
call "_message_get_default_recipients()".
An autosubscribe rule on "account.followup.report" needs to be added for this to work.
See the "social/mail_autosubscribe" module for more information.
Add this customization to module "oak_Account", including dependency on "mail_autosubscribe".
