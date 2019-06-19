from django.core.management.base import BaseCommand

from students.models import Student, StudentInClass

from classapp.models import Book, LessonPlan

import xlrd


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        workbook = xlrd.open_workbook('/home/dunice/Downloads/lp_id.xlsx')

        sheet = workbook.sheet_by_name('Sheet1')

        for rownum in range(sheet.nrows):
            row = sheet.row_values(rownum)
            if row[0] != "id" and row[1]:
                book = Book.objects.filter(id=row[4])
                if book.count():
                    lesson_plan = LessonPlan()
                    lesson_plan.book = book[0]
                    lesson_plan.lp_id = row[1]
                    lesson_plan.week = int(row[6])
                    lesson_plan.cw = row[7]
                    lesson_plan.hw = row[8]
                    lesson_plan.save()

        self.stdout.write('Finished')