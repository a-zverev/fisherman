### Fisherman

*Что у нас там сегодня по акции?*

#### I. Интро

Все мы любим что-то свое. А еще мы любим экономить, покупать любимые товары немножечко дешевле, чем обычно. Можно делать это хаотично - а можно упорядочить этот процесс. Я захотел оптимизировать этот процесс, и написал бот для мониторинга цен в Перекрестке

*Это первая версия readme, ее задача - мотивировать меня написать более детальное и более приличное readme*


#### I. Структура базы данных

В качестве простого решения для базы данных была выбрана SQLite. Преимуществом здесь были удобство представления базы данных (одним файлом, который легко копировать), а также простое взаимодействие со скриптами python через библиотеку sqlite3. Недостатком является невозможность множественных обращений к базе. На данный момент это ограничение не критично.

База данных fisherman.db содержит четыре таблицы. Все таблицы взаимосвязаны при помощи `id`, уникального для продукта.

- `info` (поля `id`, `url`, `name`):  Здесь содержится информация о названии продукта, ссылка на сайт магазина и его уникальный идентификатор `id`, автоматически генерируемый при добавлении нового продукта.
- `users` (поля `id`, `users`):  В таблице в длинном формате записываются отслеживаемые каждым пользователем `id`, в длинном формате.
- `prices` (`id`, `datetime`, `price`):  С каждой итерацией мониторинга цен в таблицу `prices` дописывается информация о цене на продукт, и дате, когда эта цена была получена. Также использован длинный формат данных
- `stats` (`id`, `mean_price`, `datetime`, `price_last`, `abs_profit`, `rel_profit`):  Каждая итерация мониторинга цен заканчивается формированием таблицы статистики `stats`. Для каждого `id` приводится средняя цена, последняя на указанную дату цена, а также абсолютная и относительная выгода.

#### II. Мониторинг цен

За мониторинг цен отвечает модуль watchdog. Его файлы:

- `watchdog.py`:  Основной скрипт. Парсинг цен, заполнение базы данных
- `watchdog_run.sh`:  Запуск скрипта `watchdog.py` из `crone`, перенаправление ошибок в `watchdog_errors.log`, перенаправление stderr запущенного `watchdog.py`
- `watchdog.log`:  лог работы `watchdog.py`

Обновление цен запускается при помощи расписаний crone. В моем случае это дважды в сутки – в 9 и в 21. Непосредственно модуль watchdog делает следующее: а) читает все `url` в базе данных таблицы `info`; б) делает запросы к сайту, разбирает выдачу, извлекая текущую цену продукта; в) дописывает время и цену в таблицу `prices`; г) пересчитывает статистику с учетом новых цен и записывает в таблицу `stats`.

#### III. Telegram Бот

За взаимодействие с пользователем отвечает модуль `bot`. Его файлы:

- `bot.py`:  Основной скрипт бота. Функции диалога с пользователем: обработки полученных сообщений и формирования ответов.
- `operations.py`:  Набор непосредственно функций реализации запросов пользователя. Используется как библиотека для импорта функций в `bot.py`
- `config.py`:  Данные авторизации и глобальных переменных.
- `message_to_user.py` – большие текстовые сообщения для пользователей.

#### Ограничения

Ограничения бота на данный момент

- Сервер расположен в Петербурге. Так как передать локацию в том или ином виде при помощи `requests` не получилось, все цены привязаны именно к Петербургу. Также нет гарантии, что цена в локальном магазине будет той же, что и на сайте
- Отклонение от среднего скорее всего не является оптимальной мерой. Однако эта мера самая простая - предполагаю провести EDA с различными другими вариантами после появления большего количества данных (за пару месяцев)
- Эффективность мониторинга будет также зависеть от наполнения базы данных.