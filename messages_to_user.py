welcome_message = """
Привет! Это первая версия телеграм-бота для отслеживания изменения цен в Перекрестке. \
Принцип работы следующий:\n\
- вы находите на сайте www.perekrestok.ru интересующий вас товар\n\
- нажимаете кнопку "Добавить продукт" и копируете ссылку на сайт\n\
- отправляете ссылку боту.\n\
Теперь цена на этот товар проверяется дважды в день и записывается в базу данных. В любой момент вы \
можете посмотреть список отслеживаемых товаров по кнопке "Мой список".\n
Когда вы идете в магазин, нажмите кнопку "Что по акции?". Бот пришлет вам список тех товаров из вашего списка, \
которые в данный момент продаются по акции.

Вызов помощи /help расскажет немного подробнее об использовании данных, а по команде /demo вы можете подключить небольшую \
демо-базу на 6 продуктов.\n

Это первый рабочий прототип. Если что-то работает не так, или у вас есть идеи, что можно улучшить, \
я буду признателен за /feedback
"""

help_message = """
Цена на продукты в Перекрестке меняются. Наша задача - купить товар по цене ниже средней. Для мониторинга цен мы \
используем цены на официальном сайте магазина - www.perekrestok.ru\n
Для того, чтобы добавить продукт в список наблюдения, нажмите "Добавить продукт" и отправьте боту ссылку на конкретный \
товар на сайте магазина. В базе данных ему будет присвоен идентификатор (ID), который будет отображаться вместе с названием \
в списке, доступном по кнопке "Мой список". Если вы в какой-то момент захотите удалить этот товар, найдите его ID. Нажмите \
"Удалить продукт" и напишите ID - продукт будет удален из вашего списка.\n

База данных обновляется дважды в день - в 9 и 21 час по Москве. После этого производится анализ цен. Товары, которые в данный \
момент стоят дешевле, чем в среднем, доступны вам по кнопке "Что по акции?". Список отсортирован по выгоде (товары с \
максимальной выгодой показаны первыми), выгода меньше 10р не показана. В скобках также приведена относительная выгода - \
текущая цена товара в долях средней цены.
"""