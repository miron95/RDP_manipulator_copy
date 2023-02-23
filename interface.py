import os
from datetime import datetime
import tkinter.font
import tkinter.ttk
from tkinter import messagebox, filedialog, Tk, Frame, Label, Button, Entry, Checkbutton, StringVar, IntVar, Menu
from tkinter.constants import RIDGE, DISABLED, CENTER, RIGHT, LEFT, N, W, BOTH, Y

from manipulator import get_list_connect, connect_user


class MainInterface:

    def __init__(self):
        self.parent_dir = os.getcwd()

        self.win = Tk()
        self.file_name = StringVar(self.win, value='Выбрать файл...')
        self.file_path = ''
        self.selected = IntVar()

        self.main_menu = Menu(bg="green")
        self.help = Menu(tearoff=False)
        self.help.add_command(label="Что нового?", command=self.show_news)
        self.help.add_command(label="Как пользоваться программой?", command=self.show_help)
        self.main_menu.add_cascade(label="Помощь", menu=self.help)
        self.win.config(menu=self.main_menu)

        self.win.title("RDP Manipulator v1.2")
        self.win.iconbitmap(os.path.dirname(os.path.abspath(__file__)) + '\\' + 'Amuri.ico')
        self.fontsize = tkinter.font.Font(family="Arial", size=11)
        self.frame0 = Frame(self.win)
        self.frame1 = Frame(self.frame0)
        self.frame2 = Frame(self.frame0, bg='yellow')

        self.label_username = Label(self.frame1, text='Введите\n username:', font=self.fontsize)
        self.enter_username = Entry(self.frame1, width=20, font=self.fontsize)

        self.button_srv = Button(self.frame1, text='Выбрать файл...', command=self.enter_srv_file, font=self.fontsize)
        self.label_srv_file = Entry(self.frame1, textvariable=self.file_name, font=self.fontsize, borderwidth=1,
                                    relief=RIDGE, state=DISABLED)

        self.choise_first_conn = Checkbutton(self.frame1, text='Подключаться автоматически к первому найденному сеансу',
                                             variable=self.selected,
                                             font=("Arial", 9, "italic"), wraplength=130)

        self.button1 = Button(self.frame1, text='Вывести список сеансов', command=self.show_list_connect,
                              font=self.fontsize,
                              wraplength=120, background='#66ffff')
        self.button2 = Button(self.frame1, text='Подключится для управления',
                              command=lambda: self.enter_in_table(view=False),
                              font=("Arial", 11, "bold"),
                              wraplength=125, background='#00cc00')
        self.button3 = Button(self.frame1, text='Подключится для просмотра',
                              command=lambda: self.enter_in_table(view=True),
                              font=("Arial", 11, "bold"),
                              wraplength=125, background='#66ff99')

        heads = ['ID', 'Сервер', 'Пользователь', 'Сеанс', 'Статус', 'Бездействие', 'Время входа']

        self.table = tkinter.ttk.Treeview(self.frame2, show='headings')
        self.table['columns'] = heads
        for header in heads:
            self.table.column(header, width=100)
            print(heads.index(header))
            self.table.heading(header, text=header, anchor=CENTER,
                               command=lambda h=heads.index(header): self.sort_table_column(col=h, reverse=False))
        self.table.column(heads[0], width=30)

        self.scrollpanel = tkinter.ttk.Scrollbar(self.frame2, command=self.table.yview)
        self.table.configure(yscrollcommand=self.scrollpanel.set)

    def sort_table_column(self, col, reverse):
        """ Функция сортировки значений в столбце """
        # получаем все значения столбцов в виде отдельного списка
        items = [(self.table.set(k, col), k) for k in self.table.get_children("")]
        # сортируем список
        try:
            # если столбец "IP"
            if col == 1:
                items.sort(key=lambda item: tuple(map(int, item[0].split('.'))), reverse=reverse)
            # если столбец "Время входа"
            elif col == 6:
                items.sort(key=lambda item: datetime.strptime(item[0], '%d.%m.%Y %H:%M'), reverse=reverse)
            else:
                items.sort(key=lambda item: int(item[0]), reverse=reverse)
        except ValueError:
            items.sort(key=lambda item: item[0], reverse=reverse)
        # переупорядочиваем значения в отсортированном порядке
        for index, (_, k) in enumerate(items):
            self.table.move(k, "", index)
        # в следующий раз выполняем сортировку в обратном порядке
        self.table.heading(col, command=lambda: self.sort_table_column(col, not reverse))

    def initial_us(self):
        self.frame0.pack(expand=True, fill=BOTH)

        # Фрейм слева
        self.frame1.pack(anchor=W, fill=Y, side=LEFT, padx=10, pady=10)
        # Фрейм справа
        self.frame2.pack(expand=True, fill=BOTH, side=RIGHT, padx=10, pady=10)
        self.table.pack(expand=True, fill=BOTH, side=LEFT)
        self.scrollpanel.pack(side=RIGHT, fill=Y)

        self.label_username.grid(column=0, row=1, padx=10)
        self.enter_username.grid(column=1, row=1, padx=10)

        self.button_srv.grid(column=0, row=2, sticky=N + W, padx=10, pady=10)
        self.label_srv_file.grid(column=1, row=2, sticky=N + W, padx=10, pady=10)

        # self.choise_first_conn.select()
        self.choise_first_conn.grid(column=0, row=4, sticky=N + W, pady=10)

        self.button1.grid(column=1, row=4, pady=10)
        self.button2.grid(column=1, row=5, pady=10)
        self.button3.grid(column=0, row=5, pady=10)

    def initial_table(self):
        pass

    def enter_srv_file(self):
        filetypes = [('Текстовый файл', '*.txt')]

        if not self.file_path:
            self.file_path = self.parent_dir

        self.file_path = filedialog.askopenfilename(title='Открыть файл', initialdir=self.file_path,
                                                    filetypes=filetypes)

        _, file_name = os.path.split(self.file_path)
        self.file_name.set(file_name)

    def show_list_connect(self):
        """Получает список доступных сеансов для подключения и выводит их в таблицу"""

        username = self.enter_username.get()
        if not self.file_path:
            self.on_error_file_path()
            return
        server_list = self.file_path

        if username:
            first_conn = self.selected.get()
            table = get_list_connect(username, first_conn, server_list, view=None)
            self.table.delete(*self.table.get_children())
            if table:
                table = sorted(table, key=lambda k: k['Пользователь'])
                for row in table:
                    row = list(row.values())
                    self.table.insert('', 'end', values=row)

        else:
            self.on_error_username()

    def enter_in_table(self, view):

        if self.table.selection():
            select = self.table.selection()[0]
            value = self.table.item(select, option='values')
            user_ip = value[0]
            server_ip = value[1]
            connect_user(user_ip, view, server=server_ip)

        else:
            messagebox.showerror('Информация',
                                 'Сначала выберете из списка активный сеанс, затем нажмите "Подключиться из списка"')

    @staticmethod
    def show_news():
        messagebox.showinfo('Что нового?', "Версия 1.2\n\n"
                                           "НОВОЕ В ВЕРСИИ:\n"
                                           "- добавлена функция для сортировки значений в таблице,"
                                           " активируемая по нажатию на заголовок столбца\n"
                                           "- добавлена возможность растягивать содержимое окна\n"
                                           "- добавлен вывод ошибки при не выбранном файле серверов\n\n"
                                           "Исправления:\n"
                                           "- убран вывод ошибки при подключении к активному сеансу, "
                                           "если его бездействие > 1 минуты(теперь можно подключиться к любому сеансу)\n"
                                           "- доработано определение пути к файлу"
                                           " серверов при последующем его перевыборе.\n"
                                           )

    @staticmethod
    def show_help():
        messagebox.showinfo('Как пользоваться программой?',
                            '1) Выберите .txt файл со списком серверов нажав на кнопку "Выбрать файл..."\n\n'
                            '2) Введите username искомого пользователя в соответствующее поле "Введите username",\n\n'
                            ' Например "i.petrov" или "petrov" или "petr"\n'
                            '3) Нажмите "Вывести список сеансов" для поиска и отображения найденных сеансов\n'
                            ' Можете установить галку напротив пункта'
                            '    "Подключаться автоматически к первому найденному сеансу"\n\n'
                            '4) После успешного поиска нужно выбрать в таблице строку с нужным сеансом и'
                            '   нажать на кнопку "Подключиться для управления" или "Подключиться для просмотра"')

    @staticmethod
    def on_error_username():
        messagebox.showerror('Ошибка',
                             'Укажите username пользователя полностью или частично для выполнения подключения по RDP.'
                             '\n\n'
                             'Например "i.ivanon" или "ivanov" или "iva"')

    @staticmethod
    def on_error_file_path():
        messagebox.showerror('Ошибка',
                             'Для поиска доступных сеансов укажите файл со списком IP серверов в формате txt.\n\n')

    @staticmethod
    def on_info_empty_username_conn():
        messagebox.showinfo('Информация', 'Не найдено ни одного пользователя с активным сеансом для подключения')

    @staticmethod
    def on_info_many_username_conn():
        messagebox.showinfo('Информация', 'Найдено несколько активных сеансов!\n\n'
                                          'Вы можете установить параметр "Подключиться автоматически к первому '
                                          'найденному сеансу" для подключения')

    def run(self):
        self.win.mainloop()
