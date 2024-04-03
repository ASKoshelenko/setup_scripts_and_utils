markdown

# Email Alias Configuration for Pritunl

This guide explains how to create a mail alias for Pritunl with SQL command line and set up forwarding to multiple email addresses.

## Prerequisites

Ensure you have the following before you start:

- Access to the MariaDB/MySQL server where Pritunl's `vmail` database is hosted.
- Appropriate permissions to execute insert commands on the `vmail` database.
- Knowledge of the target domain and email addresses to which emails will be forwarded.

## Creating Mail Alias and Forwarding Rules

### 1. Connect to the MariaDB/MySQL Server

Log in to your MySQL server with the following command:

```bash
mysql -u [username] -p

```

Replace [username] with your MySQL username. Enter the password when prompted.
2. Select the vmail Database

Switch to the vmail database with the following SQL command:

```sql

USE vmail;
```
3. Add a New Alias

Insert a new alias into the alias table:

```sql

INSERT INTO alias (address, domain, active) VALUES ('откуда берем письма (почтовій ящик)', 'домен', 1);
```
You should receive a confirmation message indicating the command was successful.
4. Add Forwarding Rules

Set up the forwarding rules with the following SQL commands:

For the first email address:

```sql

INSERT INTO forwardings (address, forwarding, domain, dest_domain, is_list, active)
VALUES ('откуда берем письма', 'куда пересілаем', 'домен откуда', 'домен куда', 0, 1);
```
