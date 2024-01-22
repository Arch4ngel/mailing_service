from django.db import models

from config import settings

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Пользователь',
                             **NULLABLE)
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    surname = models.CharField(max_length=150, verbose_name='Отчество')
    email = models.EmailField(unique=True, verbose_name='Почта')
    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    header = models.CharField(max_length=150, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Пользователь',
                             **NULLABLE)

    def __str__(self):
        return self.header

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Mailing(models.Model):
    status_choice = [
        ('start', 'Запущена'),
        ('finish', 'Завершена'),
        ('created', 'Создана')
    ]

    period_choice = [
        ('day', 'Раз в день'),
        ('week', 'Раз в неделю'),
        ('month', 'Раз в месяц')
    ]
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение', **NULLABLE)
    client = models.ManyToManyField(Client)
    status = models.CharField(max_length=10, choices=status_choice, default='start', verbose_name='Статус')
    time = models.TimeField(auto_now_add=True, verbose_name='Время рассылки')
    create_date = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    period = models.CharField(choices=period_choice, default='day', verbose_name='Переодичность')
    finish_date = models.DateField(verbose_name='Дата завершения рассылки', default='2024-01-01')
    finish_time = models.TimeField(verbose_name='Время завершения рассылки', default='00:00')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Пользователь',
                             **NULLABLE)

    def __str__(self):
        return f'{self.pk}-{self.message}'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Log(models.Model):
    status_choice = [
        ('success', 'успешно'),
        ('failure', 'отказ')
    ]

    date_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время отправки')
    status = models.CharField(max_length=100, choices=status_choice, verbose_name='Статус')
    server_response = models.TextField(verbose_name='Ответ почтового сервера', **NULLABLE)
    mailing = models.ForeignKey(Mailing, on_delete=models.SET_NULL, verbose_name='Рассылка', **NULLABLE)

    class Meta:
        verbose_name = 'Лог рассылка'
        verbose_name_plural = 'Логи рассылок'

    def __str__(self):
        return f'Лог {self.mailing}'
