This guide explains how to create a mail alias with SQL command line and set up forwarding to multiple email addresses.

## Prerequisites

Ensure you have the following before you start:

- Access to the MariaDB/MySQL server where Pritunl's vmail database is hosted.
- Appropriate permissions to execute insert commands on the vmail database.
- Knowledge of the target domain and email addresses to which emails will be forwarded.

## Creating Mail Alias and Forwarding Rules

### 1. Connect to the MariaDB/MySQL Server

Log in to your MySQL server with the following command:

```bash
mysql -u [username] -p
Replace [username] with your MySQL username. Enter the password when prompted.2. Select the vmail DatabaseSwitch to the vmail database with the following SQL command:USE vmail;
3. Add a New AliasInsert a new alias into the alias table:INSERT INTO alias (address, domain, active) VALUES ('office-lic@platymo.com', 'platymo.com', 1);
You should receive a confirmation message indicating the command was successful.4. Add Forwarding RulesSet up the forwarding rules with the following SQL commands:For the first email address:INSERT INTO forwardings (address, forwarding, domain, dest_domain, is_list, active)
VALUES ('office-lic@platymo.com', 'romanko@involve.software', 'platymo.com', 'involve.software', 0, 1);
For the second email address:INSERT INTO forwardings (address, forwarding, domain, dest_domain, is_list, active)
VALUES ('office-lic@platymo.com', 'koshelenko@involve.software', 'platymo.com', 'involve.software', 0, 1);
Each command should be confirmed by a success message.ConclusionAfter executing the above commands, the mail alias office-lic@platymo.com will forward all incoming emails to romanko@involve.software and koshelenko@involve.software.TroubleshootingIf any errors occur, verify that:The domain names and email addresses are correctly spelled.The domain exists in the vmail database.The email addresses you're forwarding to are active.For further assistance, refer to the Pritunl documentation or contact your system administrator.
Remember to replace the email addresses and domain names with the actual ones you're working with.
