from datetime import datetime
import pytz
from django.core.mail import send_mail
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from config import settings
from mailing.models import Log


class MessageService:
    def __init__(self, mailing):
        self.mailing = mailing

    def create_task(self):
        crontab = self.crontab_create()
        PeriodicTask.objects.create(crontab=crontab, name=str(self.mailing), task='send_message',
                                    args=[self.mailing.pk])

    def crontab_create(self):
        minute = self.mailing.time.minute
        hour = self.mailing.time.hour

        if self.mailing.period == 'day':
            day_of_week = '*'
            day_of_month = '*'

        elif self.mailing.period == 'week':
            day_of_week = self.mailing.create_date.weekday()
            day_of_month = '*'

        else:
            day_of_week = '*',
            day_of_month = self.mailing.create_date.day if self.mailing.create_date.day <= 28 else 28

        schedule, _ = CrontabSchedule.objects.get_or_create(minute=minute, hour=hour, day_of_week=day_of_week,
                                                            day_of_month=day_of_month, month_of_year='*')

        return schedule

    def finish_task(self):
        end_time = f'{self.mailing.finish_date} {self.mailing.finish_time}'
        end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

        current_time = datetime.now(pytz.timezone('Europe/Moscow'))
        current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        return current_time > str(end_time)

    def delete_task(self):
        task = PeriodicTask.objects.get(name=str(self.mailing))
        task.delete()
        self.mailing.status = 'finish'
        self.mailing.save()

    def send_mailing(self):
        message = self.mailing.message
        clients = self.mailing.client.all()
        for client in clients:
            try:
                send_mail(
                    subject=message.header,
                    message=message.body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[client.email]
                )
                mailing_log = Log(
                    date_time=datetime.now(),
                    status='success',
                    server_response='Сообщение успешно отправлено',
                    mailing=self.mailing,
                )
                mailing_log.save()
                return mailing_log

            except RuntimeError:
                mailing_log = Log(
                    date_time=datetime.now(),
                    status='failure',
                    server_response='Сообщение не отправлено!',
                    mailing=self.mailing,
                )
                mailing_log.save()
                return mailing_log
