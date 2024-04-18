# Инструкция по удалению пересылок на почтовый адрес

Эта инструкция описывает процесс удаления пересылок на почтовый адрес 'user@email' с почтовых ящиков.

## Шаги по удалению пересылок

1. Откройте MySQL/MariaDB CLI или используйте любой инструмент для управления базами данных.
    ```bash
    mysql
    ```
    Выбериле БД
 ```sql
    USE vmail;
```

3. Запустите следующий SQL-запрос, чтобы удалить пересылки с почтового адреса 'user@email':

    ```sql
    DELETE FROM forwardings WHERE forwarding = 'user@email;
    ```

    Этот запрос удалит все записи пересылки, где адрес получателя равен 'user@email'.

4. Проверьте, что пересылки успешно удалены, выполнив следующий SQL-запрос:

    ```sql
    SELECT * FROM forwardings WHERE forwarding = 'user@email';
    ```

    Если запрос не вернет результатов, это означает, что пересылки были успешно удалены.

5. Повторите необходимые шаги для других почтовых адресов или дополнительных проверок, если это необходимо.

6. После завершения всех необходимых действий, убедитесь, что сохранены все изменения в базе данных.
