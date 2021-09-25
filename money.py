# - - - ТЗ - - -
# Парсит всё, выдаёт статистику.
# Выдаёт ошибку если видит в логе дня что-то непонятное.
# Выдаёт ошибку если неправильный формат даты или неправильная последовательность дат.
# Правит файл:
#  Высчитывает где не высчитано сумма или неправильная '=''
#  где +, в начале суммы пишем += и он посчитав сумму подставит её +120=..
#  Высчитывает где не высчитано сумма за день или неправильная, после даты через дефис
#  Добавляет пустое поле на следующий день, без указания числа, только месяц, если ещё нет такого поля.
#  Выравнивает записи.
#----------------------------------------------------------------#
#                              ПРАВИЛА
# += или + =     - доход
# = или ничего   - расход
# 
#                  АВТОМАТИЧЕСКАЯ ОБРАБОТКА ФАЙЛА
# 2019,04,11  - преобразует в "2019.04.11  / -80".
# =15+43+65  - преобразует в " 123=15+43+65", исправит сумму если была неправильная.
#              Можно было-бы разрешить такой формат записи " 33 25 100 комментарий", 
#              но тогда возрастёт вероятность ошибится, напечатать лишний пробел.
# +=43+30   - преобразует в " +73=43+30", исправит сумму если была неправильная.
# Добавит поле на новый день "2019.04.\n\n\n", учтёт если месяц поменялся.
# 
#----------------------------------------------------------------#
#                   РАЗДЕЛЕНИЕ ДЕНЕЖНЫХ ПОТОКОВ
#_Доходы:
# +n прочая работа        - если не содержит ключевых слов
# +n ремонт               - парсить ключевое слово    'за ремонт'
# +n продажи              - парсить ключевое слово    'продал'
# +n мама                 - парсить ключевую фразу    'мама'
#_Расходы:
# n проезд                - парсить ключевое слово    'проезд'
# n еда                   - парсить ключевое слово    'еда'
# n прочее                - если не содержит ключевых слов
# n работа                - парсить ключевую фразу    'по работе'
# 
#----------------------------------------------------------------#
import os
import re
from datetime import datetime
from datetime import date
from datetime import timedelta

from parsing import ParsDateSequence
#----------------------------------------------------------------#
class DayLog(object):
    def __init__(self, date, income_other_work=0, income_of_repair=0, income_sales=0, income_mother=0,  \
                       payment_fare=0, expenses_food=0, expenses_other=0, expenses_work=0):
        self.date = date
        # Доходы
        self.income_other_work  = income_other_work
        self.income_of_repair = income_of_repair
        self.income_sales = income_sales
        self.income_mother = income_mother
        # Расходы
        self.payment_fare = payment_fare
        self.expenses_food = expenses_food
        self.expenses_other = expenses_other
        self.expenses_work = expenses_work 
    def get_income(self):
        return self.income_other_work + \
               self.income_of_repair + \
               self.income_sales
    def get_expenses(self):
        return self.payment_fare + \
               self.expenses_food + \
               self.expenses_other + \
               self.expenses_work
    def get_balance(self):
        return self.get_income() + self.get_expenses() + self.income_mother
    def get_profit(self):
        return self.get_income() + self.get_expenses()

class Money(object):
    ## Посчитать статистику
    balance = 0             # текущий баланс, учитывая займ у мамы
    debt_mother = 0         # текущий долг маме

    income = 0              # общий доход
    expenses = 0            # общий расход
    profit = 0              # прибыль

    income_other_work = 0   # доход с прочей работы
    income_of_repair = 0    # доход с ремонтов
    income_sales = 0        # доход с продаж

    expenses_travel = 0     # расход на проезд
    expenses_food = 0       # расход на еду
    expenses_work = 0       # расходы по работе
    expenses_other = 0      # расходы прочие
    ##

    dict_day = []  # сюда записываем все данные за каждый день

    def __init__(self, path, encoding="cp1251"):
        self._FILE_MONEY = path
        self._FILE_ENCODING = encoding

    def process(self):
        if os.path.isfile(self._FILE_MONEY):
            print("- - - - - - - "+self._FILE_MONEY)
            with open(self._FILE_MONEY, mode='r', encoding=self._FILE_ENCODING) as f:
                lines = f.readlines()
            update_file = False

            end_date = 0  # номер строки с последней записью, для того чтобы автоматически добавлять новый шаблон

            date_sequence = ParsDateSequence("2000.01.01") # для парсинга последовательности дат

            # Для того чтобы отслеживать правильность последовательности дат
            date_max = datetime.strptime("2000.01.01", "%Y.%m.%d").date()
            date_min = date_max
            date_min_b = False
            # Текущая указанная дата
            date = date_max
            date_str = ''
            # Текущая указанная сумма за день
            sum_day_0 = 'no'; 

            j = len(lines) # индекс строки с предыдущей датой
            i = len(lines) # текущий индекс строки
            while i > 0:
                i -= 1
                line = lines[i]

                b = False
                
                sum_day = 0  # сюда считаем фактическую сумму за день

                #### Поиск даты и ошибок в строке даты

                date_sequence.pars('', line, '')

                temp_str_re = "^[\t ]*([0-9]+[.,-][0-9]+[.,-][0-9]+)[\t ]*([/][\t ]*([+-]{0,1}[0-9]*)){0,1}[\r\n\t\f ]*$"
                find_date = re.findall(temp_str_re, line, flags=re.ASCII)

                if find_date :
                    date_str = find_date[0][0].replace(',', '.').replace('-', '.')
                    temp_str_re = "^2[0-9][0-9][0-9].([0-1][0-9]).([0-3][0-9])$"
                    find_noerror = re.findall(temp_str_re, date_str, flags=re.ASCII)
                    if find_noerror :
                        if len(find_noerror[0]) == 2 :
                            m = int(find_noerror[0][0])
                            d = int(find_noerror[0][1])
                            if not( (m >= 1) and (m <= 12) and (d >= 1) and (d <= 31) ) :
                                print("error: Неправильный формат даты: [n="+str(i+1)+"]: " + line)
                                input(); quit()
                        else:
                            print("error: Неправильный формат даты: [n="+str(i+1)+"]: " + line)
                            input(); quit()
                    else:
                        print("error: Неправильный формат даты: [n="+str(i+1)+"]: " + line)
                        input(); quit()

                    date = datetime.strptime(date_str, "%Y.%m.%d").date()
                    end_date = i
                    if not date_min_b :
                        date_min = date
                        date_min_b = True

                    if date > date_max:

                        if find_date[0][2]:
                            if find_date[0][2][0] == '+':
                                sum_day_0 = int(find_date[0][2][1:])
                            elif find_date[0][2][0] == '-':
                                sum_day_0 = -int(find_date[0][2][1:])
                            elif int(find_date[0][2]) != 0:
                                print("error: Нет знака + или -: [n="+str(i+1)+"]: " + line)
                                input(); quit()

                        date_max = date
                        b = True  # нашли корректную дату
                        # Корректируем форматирование строки даты
                        lines[i] = date_str
                        if find_date[0][2] :
                            lines[i] += " / "+find_date[0][2]
                        lines[i] += "\n"
                        # файл изменился
                        if len(line) != len(lines[i]) :  # кроме удаления пробелов, ничего больше не меняем
                            update_file = True
                    else:
                        print("error: Неправильная последовательность дат: [n="+str(i+1)+"]: " + line)
                        input(); quit()

                
                #### Парсим данные за день
                if b :
                    self.dict_day.append( DayLog(date_max) )

                    temp_str_re = "^[\t ]*([+]{0,1}[0-9]*[\t ]*){0,1}"  \
                                +"([=][\t ]*([0-9]+)([\t ]*[+][\t ]*[0-9]*)*){0,1}"  \
                                +"([\t ]+[^0-9\t +=-]+[\t ]*[^\r\n\t\f\v ]+[^\r\n\f\v]*[\r\n\t\f\v ]*)$"
                    for k in range(i+1, j):
                        find_date = re.findall(temp_str_re, lines[k], flags=re.ASCII)
                        
                        def wrong_format():
                            # Проверяем, если это не пробелы, а нечто - сообщаем
                            if not lines[k].isspace() :
                                print("error: Неправильный формат записи [n="+str(k+1)+"]: " + lines[k])
                                input(); quit()  
                        b1 = False
                        if find_date :
                            # find_date[0][0]  - возможные значения: '+  ' or '+n  ' or 'n  ' or empty
                            # find_date[0][1]  - возможные значения: '= 9 +..+ 5' or '=5' or empty
                            if find_date[0][0] or find_date[0][1] :
                                b1 = True
                            else:
                                wrong_format()
                        else:
                            wrong_format()

                        if b1 :
                            ## Пересчитываем сумму
                            sum_day_n = 0
                            temp_str = find_date[0][0].replace(' ', '').replace('\t', '')
                            if find_date[0][1] :  # у нас есть что суммировать
                                temp_str_0 = find_date[0][1].replace('=', '').replace(' ', '').replace('\t', '')
                                temp_str_1 = temp_str_0.replace('+', ' ')
                                for d in temp_str_1.split() :
                                    sum_day_n += int(d)
                                # проверяем правильность указанной суммы и знак
                                # Возможные варианты:
                                #   '+   ' and ' =n.. комментарий'
                                #   'n   ' and ' =n.. комментарий'
                                #   '+n  ' and ' =n.. комментарий'
                                #       '' and ' =n.. комментарий'
                                #  - все корректны.
                                if temp_str :
                                    temp_lines_k = lines[k][:len(lines[k])-1]
                                    b2 = False
                                    if temp_str[0] is '+' :
                                        if len(temp_str) > 1 :
                                            if sum_day_n != int(temp_str[1:]) :
                                                b2 = True
                                                lines[k] = ' +'+str(sum_day_n)+'='+temp_str_0 + find_date[0][4]
                                        else:
                                            lines[k] = ' +'+str(sum_day_n)+'='+temp_str_0 + find_date[0][4]
                                            update_file = True
                                    else:
                                        if len(temp_str) > 1 :
                                            if sum_day_n != int(temp_str) :
                                                b2 = True
                                                lines[k] = ' '+str(sum_day_n)+'='+temp_str_0 + find_date[0][4]
                                        else:
                                            lines[k] = ' '+str(sum_day_n)+'='+temp_str_0 + find_date[0][4]
                                            update_file = True
                                        # 
                                        sum_day_n *= -1
                                    if b2 :
                                        update_file = True
                                        print(" warning: Неправильная сумма [n="+str(k+1)+"]: " + temp_lines_k)
                                        print("Исправлено!")
                                else:  # просто '=n1+n2..' или '=n' передали, без суммы и знака '+'
                                    lines[k] = ' '+str(sum_day_n)+'='+temp_str_0 + find_date[0][4]
                                    update_file = True
                                    # 
                                    sum_day_n *= -1
                            else: 
                                # Возможные оставшиеся варианты:
                                #   '+   ' and ' комментарий'  - неподходящий вариант
                                #   'n   ' and ' комментарий'
                                #   '+n  ' and ' комментарий'
                                #  - пробелы для наглядности, мы уже удалили их раньше.
                                if temp_str[0] is '+' :
                                    if len(temp_str) > 1:
                                        sum_day_n = int(temp_str[1:])
                                    else:
                                        print("error: Неправильный формат записи [n="+str(k+1)+"]: " + lines[k])
                                        input(); quit()   
                                else:
                                    sum_day_n = -int(temp_str)
                            # 
                            sum_day += sum_day_n
                            # Контролируем чтобы вначале строки был один пробел
                            temp = 0
                            for symbol in lines[k] :
                                if (symbol == ' ') or (symbol == '\t') :
                                    temp += 1
                                else:
                                    lines[k] = ' '+lines[k][temp:]
                                    update_file = True
                                    break

                            ## Парсим комментарии, записываем данные за день
                            def parser_keywords(in_str, keyword):
                                temp_str_re = "^[\t ]*[^\r\n\f\v]*"+keyword+"[^\r\n\f\v]*$"
                                find_date = re.findall(temp_str_re, in_str, flags=re.ASCII)
                                if find_date :
                                    return True
                                else:
                                    return False

                            if sum_day_n > 0 :
                                if parser_keywords(find_date[0][4], "[мМ]ама") :
                                    self.dict_day[-1].income_mother += sum_day_n
                                elif parser_keywords(find_date[0][4], "[пП]родал") :
                                    self.dict_day[-1].income_sales += sum_day_n 
                                elif parser_keywords(find_date[0][4], "[зЗ]а ремонт") :
                                    self.dict_day[-1].income_of_repair += sum_day_n
                                else:
                                    self.dict_day[-1].income_other_work += sum_day_n
                                    if parser_keywords(find_date[0][4], "[пП]роезд") :
                                        print("warning: Вроде оплата за проезд, а знак \'+\'. "  \
                                            + self.dict_day[-1].date.strftime('%Y.%m.%d')+": \'" \
                                            + find_date[0][4][:len(find_date[0][4])-1]+"\'")
                                    elif parser_keywords(find_date[0][4], "[еЕ]да") :
                                        print("warning: Вроде оплата за еду, а знак \'+\'. "  \
                                            + self.dict_day[-1].date.strftime('%Y.%m.%d')+": \'" \
                                            + find_date[0][4][:len(find_date[0][4])-1]+"\'")
                                    elif parser_keywords(find_date[0][4], "[пП]о работе") :
                                        print("warning: Вроде расходы по работе, а знак \'+\'. "  \
                                            + self.dict_day[-1].date.strftime('%Y.%m.%d')+": \'" \
                                            + find_date[0][4][:len(find_date[0][4])-1]+"\'")
                            elif sum_day_n < 0 :
                                if parser_keywords(find_date[0][4], "[пП]роезд") :
                                    self.dict_day[-1].payment_fare += sum_day_n
                                elif parser_keywords(find_date[0][4], "[еЕ]да") :
                                    self.dict_day[-1].expenses_food += sum_day_n
                                elif parser_keywords(find_date[0][4], "[пП]о работе") :
                                    self.dict_day[-1].expenses_work += sum_day_n
                                else:
                                    self.dict_day[-1].expenses_other += sum_day_n
                                    if parser_keywords(find_date[0][4], "[мМ]ама") :
                                        print("warning: Вроде дала мама, а знак \'-\'. "  \
                                            + self.dict_day[-1].date.strftime('%Y.%m.%d')+": \'" \
                                            + find_date[0][4][:len(find_date[0][4])-1]+"\'")
                                    elif parser_keywords(find_date[0][4], "[пП]родал") :
                                        print("warning: Вроде прибыль с продажи, а знак \'-\'. "  \
                                            + self.dict_day[-1].date.strftime('%Y.%m.%d')+": \'" \
                                            + find_date[0][4][:len(find_date[0][4])-1]+"\'")
                                    elif parser_keywords(find_date[0][4], "[зЗ]а ремонт") :
                                        print("warning: Вроде заработал с ремонта, а знак \'-\'. "  \
                                            + self.dict_day[-1].date.strftime('%Y.%m.%d')+": \'" \
                                            + find_date[0][4][:len(find_date[0][4])-1]+"\'")


                    ## Проверяем указанную сумму за день
                    def set_sum_dey():
                        temp_str = " / "
                        if sum_day > 0 :
                            temp_str = " / +"
                        elif sum_day < 0:
                            temp_str = " / "
                        lines[i] = date_str + temp_str + str(sum_day) + "\n"

                    if sum_day_0 == 'no' :  # не указана сумма за день
                        set_sum_dey()
                        update_file = True
                    else:
                        if sum_day != sum_day_0 :
                            print("warning: Неправильная сумма [n="+str(i+1)+"]: " +  lines[i][:len(lines[i])-1])
                            print("Исправлено!")
                            set_sum_dey()
                            update_file = True
                        else:
                            temp_str = lines[i]
                            set_sum_dey()
                            # файл изменился
                            if temp_str != lines[i] :
                                update_file = True
                        sum_day_0 = 'no'
           

                    ## сдвигаемся на следующую дату
                    j = i


            #### Подсчитываем собранные данные
            temp2 = 0
            temp3 = 0
            for day in self.dict_day :
                self.balance        += day.get_balance()
                self.profit         += day.get_profit()
                self.income         += day.get_income()
                self.expenses       += day.get_expenses()
                self.income_other_work   += day.income_other_work
                self.income_of_repair    += day.income_of_repair
                self.income_sales        += day.income_sales
                self.expenses_travel += day.payment_fare
                temp2               += day.expenses_food
                temp3               += day.expenses_work
                self.expenses_other += day.expenses_other
            self.expenses_food = temp2
            self.expenses_work = temp3
            self.debt_mother = -(self.balance - self.profit)
            ## Выводим
            print("- - - - - - - - - - - - - - - - - - "+date_min.strftime('%Y.%m.%d') \
                                                +" — "+date_max.strftime('%Y.%m.%d') \
                                                +"  /"+str((date_max - date_min + timedelta(days=1)).days)+" дн.")
            print("           balance = " + str(self.balance))
            print("              debt = " + str(self.debt_mother))
            print("            - - - - - - - -")
            print("            income = " + str(self.income))
            print("          expenses = " + str(self.expenses))
            print("            profit = " + str(self.profit))
            print()
            str_1 = " other work income = " + str(self.income_other_work)
            str_2 = "  of repair income = " + str(self.income_of_repair)
            n_len = max(len(str(self.income_other_work)), len(str(self.income_of_repair))) + 1
            str_1 += (( 21+n_len - len(str_1) )*' ')
            str_2 += (( 21+n_len - len(str_2) )*' ')
            print(str_1 + "--\\")
            print(str_2 + "---\\ profit = " + str(self.income_other_work + self.income_of_repair + self.expenses_work))
            print("      sales income = " + str(self.income_sales))    
            print()
            print("   travel expenses = " + str(self.expenses_travel))
            print("     food expenses = " + str(self.expenses_food))
            print("     work expenses = " + str(self.expenses_work))
            print("    other expenses = " + str(self.expenses_other))
            print("- - - - - - - - - - - - - - - - - -")

            #### Добавляем в начале файла шаблон для нового дня
            # Смотрим выше от последней записи(end_date),
            # если выше нет шаблона вида '2019.04.' то добавляем.
            temp = True
            temp_str_re = "^[\t ]*([0-9]+[.,-][0-9]+[.,-])[\t ]*(!!!текущий месяц[^\r\n]*){0,1}[\r\n\t\f ]*$"
            for i in reversed(range(0, end_date)):
                find_date = re.findall(temp_str_re, lines[i], flags=re.ASCII)
                if find_date :
                    temp = False
                    break
            if temp :
                # Определяем дату следующего дня
                iter_date = ( date_max + timedelta(days=1) ).strftime('%Y.%m.')
                today = ( date.today() ).strftime('%Y.%m.')
                if today != iter_date:
                    lines.insert(end_date, iter_date+" !!!текущий месяц: "+today+"\n \n\n")
                else:
                    lines.insert(end_date, iter_date+"\n \n\n")
                update_file = True

            #### 
            if update_file:
                # записываем в копию сначала
                with open(self._FILE_MONEY + '.tmp', mode='w', encoding=self._FILE_ENCODING) as f:
                    f.writelines(lines)
                # удаляем старый файл
                self.remove(self._FILE_MONEY)
                # переименовываем копию
                self.rename(self._FILE_MONEY + '.tmp', self._FILE_MONEY)
        else:
            print("Не найден файл: "+self._FILE_MONEY)


    #----------------------------------------------------------------#
    #                         вспомогательные
    #----------------------------------------------------------------#
    @staticmethod
    def rename(path_in, path_out):
        """ Переименовываем файл с проверкой переименования.
        Возврат из функции когда убедится что переименовал.
        """
        try:
            if os.path.isfile(path_in):
                os.rename(path_in, path_out)
            else:
                print("error - не найден файл который нужно переименовать ", path_in)
                input("Нажмите Enter чтобы закрыть приложение:")
                input(); quit()

            # Возвращаемся из функции когда гарантированно переименуется
            count = 0
            while not os.path.isfile(path_out):
                count += 1
                if count > 10000:
                    print("error - файл переименовывается слишком долго, либо не удаётся переименовать ", path_in,
                          " в ", os.path.basename(path_out))
                    input("Нажмите Enter чтобы продолжить:")
                    count = 0
        except OSError:
            print("error - не удалось переименовать файл ", path_in, " т.к. файл ", os.path.basename(path_out),
                  " уже существует.")
            input("Нажмите Enter чтобы закрыть приложение:")

    @staticmethod
    def remove(path):
        """ Удаляет файл с проверкой удаления.
        Возврат из функции когда убедится что удалил.
        """
        while True:
            try:
                os.remove(path)
                # Возвращаемся из функции когда гарантированно удалится
                count = 0
                while os.path.isfile(path):
                    count += 1
                    if count > 10000:
                        print("error - файл удаляется слишком долго, либо не удаётся удалить ", path)
                        input("Нажмите Enter чтобы продолжить:")
                        count = 0
                break
            except OSError:
                print("error - не удалось удалить файл, возможно указанный путь является каталогом ", path)
                input("Нажмите Enter чтобы повторить попытку:")
