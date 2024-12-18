# ProxyKiller

**ProxyKiller** — это графическое приложение, созданное с использованием PyQt5 и предназначенное для выполнения запросов через прокси-серверы. Приложение создаёт интерфейс для выполнения DDoS-атаки на указанный целевой URL с использованием прокси-серверов. Программа разработана исключительно в учебных целях для демонстрации работы с многопоточностью, сетевыми запросами и прокси-серверами.

## Основное назначение:

	1. Генерация большого количества запросов к целевому URL с помощью прокси-серверов, создавая искусственную нагрузку.
	2. Протестировать прокси: Оно позволяет проверить работоспособность прокси-серверов, отслеживая успешные запросы.

## Особенности

- **Поддержка многопоточности**: Использует `ThreadPoolExecutor` для одновременной отправки множества запросов.
- **Интерфейс пользователя**: Простой и удобный интерфейс с полями для ввода целевого URL, загрузки списка прокси и выбора количества потоков.
- **Отображение статуса запросов**: Отображает общее количество и успешные запросы в реальном времени.

## Установка

1. Убедитесь, что у вас установлен Python 3.7 или выше.
2. Установите необходимые библиотеки с помощью `pip`:
   ```bash
   pip install -r requirements.txt
   ```

## Запуск:
     1. Запустите `main.py` командой:
   ```bash
    python main.py
   ```
    2. Введите целевой URL и загрузите файл с прокси-серверами.
    3. Укажите количество потоков.
    4. Нажмите кнопку “Начать атаку”.
    5. Приложение многопоточно отправляет запросы к целевому URL, используя указанные прокси.
    6. Статистика обновляется в реальном времени.
    7. Пользователь может остановить атаку в любой момент, нажав на кнопку "Остановить атаку".