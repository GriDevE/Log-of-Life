#----------------------------------------------------------------#
# новые правила{
#  n* ++     - хорошо стоял без начальной стимуляции
#  n* +      - в процессе хорошо стоял, но в начале пришлось стимулировать
#  n* -      - в процессе плохо стоял
#  n         - мастурбация, кончил n раз
#  o         - флаг, был оргазм
# }
#----------------------------------------------------------------#
import os
import re
#----------------------------------------------------------------#
class Sex(object):

    def __init__(self, path="sex.txt", encoding="cp1251"):
        self._FILE = path
        self._FILE_ENCODING = encoding

    def process(self):
        if os.path.isfile(self._FILE):
            print("- - - - - - - "+self._FILE)
            with open(self._FILE, mode='r', encoding=self._FILE_ENCODING) as f:
                lines = f.readlines()
            update_file = False

            ## Проверка даты и замена формата dd.mm.2019 на 2019.mm.dd



            ##
            for line in lines:
                find_date = re.findall('^[\t ]*([0-9][0-9][0-9][0-9][.,][0-9][0-9][.,][0-9][0-9])[ ]+' \
                    +'(([0-9]{0,2})([*]{0,1})[ ]*([+]{0,2})([-]{0,1})[ ]*([oOоО]{0,2})[ ]*([,]{0,1})[ ]*){0,2}' \
                    +'[^\r\n]*[\r\n\t\f ]*$', line)
                if find_date :
                    print(find_date)

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
            print("Не найден файл: "+self._FILE)


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
