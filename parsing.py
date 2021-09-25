#----------------------------------------------------------------#
import re
from datetime import datetime
from datetime import date
from datetime import timedelta
#----------------------------------------------------------------#
class ParsDateSequence(object):
    """ Парсит и проверяет даты в передаваемых строках, 
        проверяет корректность возрастающей последовательности дат.
    """
    _comment = ''
    _line = ''

    def __init__(self, date_min="2000.01.01", date_format="%Y.%m.%d"):
        """ date_min  - минимальная возможная дата
        """
        self._date_min = datetime.strptime(date_min, date_format).date()  # первая переданная дата (наименьшая)
        self._date_min_b = False  # признак инициализации _date_min
        self._date_max = self._date_min  # последняя переданная дата (наибольшая)
        # Текущая указанная дата
        self._date = self._date_min  # заносим точку начального сравнения
        self._date_str = ''
        self._date_min_str = ''
        # 
        n = 0  # количество проанализированных строк с датой

    def pars(self, prefix_re, line, date_format="%Y.%m.%d"):
        """ Поиск даты в переданной строке и ошибок в дате.
         date_format  - в таком формате будет искать дату
        Return values:
         0  - дата не найдена
         1  - дата найдена, всё хорошо
         2  - дата найдена, незначительно поправлен формат строки(удалены лишние пробелы)
         3  - error, неправильный формат даты
         4  - error, неправильная последовательность дат, когда следующая дата <= предыдущей
        """
        temp_str_re = "^[\t ]*"+prefix_re+"([\t ]*)"+  \
                     +"([0-9]+[.,-][0-9]+[.,-][0-9]+)[\t ]*"  \
                     +"([^\r\n){0,1}[\r\n\t\f ]*$"
        find_date = re.findall(temp_str_re, line, flags=re.ASCII)

        if find_date :
            n += 1
            _line = line
            self._date_str = find_date[0][1].replace(',', '.').replace('-', '.')





        return 0

    def get_line(self):
        """ Возвращает последнюю строку с датой, скорректированную если нужно
        """
        return self._line

    def get_comment(self):
        return self._comment

    def get_date(self):
        if self._date_str :
            return self._date_max
        else:
            return False

    def get_date_str(self):
        return self._date_str

    def get_date_min(self):
        if self._date_min_str :
            return self._date_min 
        else:
            return False 

    def get_date_min(self):
        return self._date_min_str

    def get_n(self):
        return self._date_min_str
