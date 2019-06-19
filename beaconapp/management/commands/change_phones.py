from django.core.management.base import BaseCommand

from staff.models import Staff
from parents.models import Parent


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for obj in Staff.objects.all():
            phone = self.convert_phone(obj.cell_phone)

            if len(phone) != 14:
                print('error {} || {} | {}'.format(
                    phone, len(phone), obj.id
                ))

            obj.cell_phone = phone
            obj.save()

        for obj in Parent.objects.all():
            phone = self.convert_phone(obj.cell_phone)
            home_phone = self.convert_phone(obj.home_phone)
            alter_phone = self.convert_phone(obj.alternate_phone)

            if phone:
                obj.cell_phone = phone
            else:
                print('phone - {}, id - {}'.format(phone, obj.id))

            if home_phone:
                obj.home_phone = home_phone

            if alter_phone:
                obj.alternate_phone = alter_phone

            obj.save()
        self.stdout.write('Finished')

    def convert_phone(self, phone):
        if phone:
            alter_phone = phone.replace('+1', '')\
                               .replace('(', '')\
                               .replace(')', '')\
                               .replace('-', '')\
                               .replace(' ', '')
            alter_phone = '({}) {}-{}'.format(
                alter_phone[:3], alter_phone[3:6], alter_phone[6:]
            )
        else:
            alter_phone = ''

        return alter_phone
