from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.core.text import LabelBase
from datetime import datetime, timedelta
import calendar
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.properties import ListProperty
from kivy.core.window import Window
Window.size = (390, 844)

#Регистрация шрифтов
LabelBase.register(name="Gilroy-MediumItalic", fn_regular="C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Gilroy-MediumItalic.otf")
LabelBase.register(name="Gilroy-Medium", fn_regular="C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Gilroy-Medium.otf")
LabelBase.register(name="Gilroy-RegularItalic", fn_regular="C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Gilroy-RegularItalic.otf")
LabelBase.register(name="Gilroy-Regular", fn_regular="C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Gilroy-Regular.otf")
LabelBase.register(name="Gilroy-SemiBold", fn_regular="C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Gilroy-SemiBold.otf")

store = JsonStore("user.json")
daily_store = JsonStore("daily.json")

class TimePicker(RecycleView):
    def init(self, values, **kwargs):
        super().init(**kwargs)
        self.data = [{"text": v, "font_size": "42sp"} for v in values]


class RangeButton(Button):
    border_color = ListProperty([0.7137, 0.5294, 0.5294, 1])

    def init(self, **kwargs):
        super().init(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (1,1,1,0)


import locale
try:
    locale.setlocale(locale.LC_TIME, 'UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'UTF-8') 
    except:
        locale.setlocale(locale.LC_TIME, '')


class WelcomeScreen(Screen):
    pass

class InfoScreen(Screen):
    pass

class GreetingScreen(Screen):
    pass

class HomeScreen(Screen):

    current_monday = None        # дата понедельника выбранной недели
    selected_day = None          # выбранный день месяца

    def on_pre_enter(self):
        """Вызывается каждый раз при заходе на экран."""
        if not self.current_monday:
            today = datetime.now()
            weekday = today.weekday()  # 0 = понедельник
            self.current_monday = today - timedelta(days=weekday)
        self.update_calendar()
        self.update_username()
    
    def update_username(self):
        """Обновляет имя пользователя в приветствии."""
        name = App.get_running_app().get_name()
        if name:
            self.ids.username_label.text = f"Как ты себя \n чувствуешь \n сегодня, \n [b]{name}?[/b]"
        

    def update_calendar(self):
        """Отрисовывает дни недели на экране."""
        grid = self.ids.calendar_grid
        grid.clear_widgets()

        monday = self.current_monday
        weekdays_short = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']


        # Обновляем текст месяца
        month_label = self.ids.month_label
        month_label.text = monday.strftime("%B, %Y")

        # Создаём 7 кнопок по одному на каждый день недели
        for i in range(7):
            current_day = monday + timedelta(days=i)
            # Форматируем день с ведущим нулем если нужно
            day_str = f"{current_day.day:02d}"

            btn = CalendarDay(
                day=current_day.day,
                weekday=weekdays_short[i],
                text=f"{day_str}\n{weekdays_short[i]}",
                screen=self
            )

            # Подсветка выбранного дня
            if self.selected_day and current_day.day == self.selected_day:
                btn.is_selected = True

            grid.add_widget(btn)

    def next_week(self):
        """Переключиться на следующую неделю."""
        self.current_monday += timedelta(days=7)
        self.update_calendar()

    def previous_week(self):
        """Переключиться на предыдущую неделю."""
        self.current_monday -= timedelta(days=7)
        self.update_calendar()

    def change_day(self, day):
        """Пользователь выбрал другой день."""
        self.selected_day = day
        # Перекрашиваем кнопки
        for btn in self.ids.calendar_grid.children:
            btn.is_selected = (btn.day == day)
        # Загружаем данные под выбранную дату
        self.load_day_data()

    def load_day_data(self):
        """Загрузить данные воды и шагов под выбранный день."""
        if self.selected_day is None:
            return

        monday = self.current_monday

        # Находим индекс кнопки в сетке
        for index, btn in enumerate(reversed(self.ids.calendar_grid.children)):
            if btn.day == self.selected_day:
                selected_date = monday + timedelta(days=index)
                break

        key = selected_date.strftime("%Y-%m-%d")

        if daily_store.exists(key):
            data = daily_store.get(key)
            self.ids.water_value.text = f"{data['water']} мл"
            self.ids.steps_value.text = f"{data['steps']} шагов"
        else:
            self.ids.water_value.text = "0 мл"
            self.ids.steps_value.text = "0 шагов"

class ShareScreen(Screen):
    pass

class CalendarDay(Button):
    day = NumericProperty(0)
    weekday = StringProperty("")
    is_selected = BooleanProperty(False)
    screen = ObjectProperty(None)

    def on_release(self):
        self.screen.change_day(self.day)

class WaterScreen(Screen):
    water_amount = NumericProperty(0)
    max_water = 1000  # мл – дневная норма

    def add_water(self, amount):
        """Добавление воды (например +100 мл)"""
        self.water_amount += amount
        if self.water_amount > self.max_water:
            self.water_amount = self.max_water
        self.update_display()

    def update_display(self):
        self.ids.water_label.text = f"{self.water_amount}/{self.max_water} ml"
class StepsScreen(Screen):
    selected_steps = NumericProperty(0)

    def choose_range(self, value):
        self.selected_steps = value
        self.ids.steps_input.text = str(value)

    def go_next(self):
        print("Шаги за сегодня:", self.selected_steps)
        # здесь переход дальше

from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty
from kivy.app import App

class SleepScreen(Screen):
    sleep_hour = NumericProperty(23)
    sleep_min = NumericProperty(0)
    wake_hour = NumericProperty(7)
    wake_min = NumericProperty(0)

    def go_next(self):
        print("Сон:", self.sleep_time, "-", self.wake_time)
        # переход дальше

from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.image import Image


class EmotionCarousel(RelativeLayout):
    index = NumericProperty(0)

    emotions = ListProperty([
        ("Ярость", "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Ярость.png"),
        ("Раздражение", "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Раздражение.png"),
        ("Безразличие", "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Безразличие.png"),
        ("Счастье", "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Счастье.png"),
        ("Спокойствие", "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Спокойствие.png"),
        ("Смущение", "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Смущение.png"),
        ("Грусть", "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Грусть.png"),
    ])

    emotion_name = StringProperty("")
    emotion_image = StringProperty("")

    def _init_(self, **kwargs):
        super()._init_(**kwargs)
        self.init_emotion()

    def init_emotion(self, *args):
        self.update_emotion()

    def next_emotion(self):
        self.index = (self.index + 1) % len(self.emotions)
        self.update_emotion()

    def prev_emotion(self):
        self.index = (self.index - 1) % len(self.emotions)
        self.update_emotion()

    def update_emotion(self):
        name, img = self.emotions[self.index]
        self.emotion_name = name
        self.emotion_image = img
        
class MoodScreen(Screen):
    pass

class Share_2_Screen(Screen):
    pass

# ----------------- ResultScreen (Python) -----------------
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, ListProperty
from datetime import datetime

class ResultScreen(Screen):
    # текстовые значения для отображения (в KV связываются через ids)
    date_key = StringProperty("")   # YYYY-MM-DD
    water_ml = NumericProperty(0)
    steps = NumericProperty(0)
    sleep_start = StringProperty("")   # "23:30"
    sleep_end = StringProperty("")     # "07:10"
    sleep_hours = NumericProperty(0.0)
    mood = StringProperty("Не задано")
    rec_texts = ListProperty([])       # список рекомендаций строками

    # пороги (можешь менять)
    WATER_GOAL = 2000     # мл
    STEPS_GOAL = 5000     # шагов
    SLEEP_GOAL_MIN = 7.0  # часов минимальная рекомендованная
    SLEEP_GOAL_MAX = 9.0  # часов желаемая

    def on_pre_enter(self):
        # при заходе, если дата не передана — возьмём сегодня
        if not self.date_key:
            self.update_from_store(None)

    def update_from_store(self, date_key=None):
        """
        Загружает данные из daily_store по ключу 'YYYY-MM-DD'.
        Если date_key is None — берёт сегодня.
        Затем вычисляет рекомендации.
        """
        if date_key is None:
            date = datetime.now()
        else:
            # ожидается строка 'YYYY-MM-DD' или datetime
            if isinstance(date_key, str):
                try:
                    date = datetime.strptime(date_key, "%Y-%m-%d")
                except Exception:
                    date = datetime.now()
            else:
                date = date_key

        key = date.strftime("%Y-%m-%d")
        self.date_key = key

        # defaults
        self.water_ml = 0
        self.steps = 0
        self.sleep_start = ""
        self.sleep_end = ""
        self.sleep_hours = 0.0
        self.mood = "Не задано"

        if daily_store.exists(key):
            d = daily_store.get(key)
            # ожидаем ключи 'water', 'steps', 'sleep_start', 'sleep_end', 'mood'
            self.water_ml = d.get("water", 0)
            self.steps = d.get("steps", 0)
            self.sleep_start = d.get("sleep_start", "")   # "23:30"
            self.sleep_end = d.get("sleep_end", "")       # "07:10"
            if self.sleep_start and self.sleep_end:
                self.sleep_hours = self._calc_sleep_hours(self.sleep_start, self.sleep_end)
            else:
                self.sleep_hours = d.get("sleep_hours", 0.0)
            self.mood = d.get("mood", self.mood)

        # сформируем рекомендации
        self.rec_texts = self._generate_recommendations()

    def _calc_sleep_hours(self, start_str, end_str):
        """Подсчитать длительность сна по строкам 'HH:MM' -> часы (float)."""
        try:
            t0 = datetime.strptime(start_str, "%H:%M")
            t1 = datetime.strptime(end_str, "%H:%M")
            # если заснул до полуночи и проснулся после — учтём перенос через день
            delta = t1 - t0
            if delta.total_seconds() <= 0:
                delta = (t1.replace(day=t1.day+1) if t1.day==t0.day else t1) - t0
                # проще: добавить 24 часа
                delta = delta.total_seconds()
                hours = delta / 3600.0
            else:
                hours = delta.total_seconds() / 3600.0
            # корректнее: проще вычислить с учётом дат:
            start_dt = datetime(2000,1,1, t0.hour, t0.minute)
            end_dt = datetime(2000,1,1, t1.hour, t1.minute)
            if end_dt <= start_dt:
                end_dt = end_dt.replace(day=2)
            hours = (end_dt - start_dt).total_seconds() / 3600.0
            return round(hours, 2)
        except Exception:
            return 0.0

    def _generate_recommendations(self):
        """Возвращает список из 4 рекомендательных строк в том же порядке: вода, шаги, сон, настроение"""
        recs = []
        # 1) вода
        if self.water_ml >= self.WATER_GOAL:
            recs.append("Отлично — с водой всё в порядке. Поддерживайте такой режим.")
        elif self.water_ml >= self.WATER_GOAL * 0.6:
            recs.append("Вы выпили немного воды. Попробуйте добавить ещё 1 стакан в течение часа.")
        else:
            recs.append("Нужно больше воды — выпейте 250–300 мл прямо сейчас и затем ещё стакан через час.")

        # 2) шаги
        if self.steps >= self.STEPS_GOAL:
            recs.append("Хорошо — вы активны сегодня. Продолжайте в том же духе!")
        elif self.steps >= self.STEPS_GOAL * 0.5:
            recs.append("Неплохо, но можно добавить короткую 10–15 минутную прогулку вечером.")
        else:
            recs.append("Мало движения — выйдите на лёгкую прогулку 15–20 минут, чтобы разогнать кровь.")

        # 3) сон
        if self.sleep_hours >= self.SLEEP_GOAL_MIN and self.sleep_hours <= self.SLEEP_GOAL_MAX:
            recs.append(f"Сон {self.sleep_hours} ч — в пределах нормы. Отлично!")
        elif self.sleep_hours >= self.SLEEP_GOAL_MAX:
            recs.append(f"Сон {self.sleep_hours} ч — возможно вы спали слишком много, попробуйте стабилизировать режим.")
        elif 0 < self.sleep_hours < self.SLEEP_GOAL_MIN:
            diff = round(self.SLEEP_GOAL_MIN - self.sleep_hours, 1)
            recs.append(f"Сон {self.sleep_hours} ч — рекомендуется лечь на {diff} ч раньше, чтобы восстановиться.")
        else:
            recs.append("Нет данных о сне — укажите время сна в опросе для персональных рекомендаций.")

        # 4) настроение
        negative = {"Ярость", "Раздражение", "Грусть", "Смущение"}
        neutral = {"Безразличие"}
        positive = {"Счастье", "Спокойствие"}

        if self.mood in positive:
            recs.append("Настроение позитивное — используйте энергию для полезных дел или отдыха.")
        elif self.mood in neutral:
            recs.append("Нейтральное состояние — сделайте небольшую активность или медитацию, чтобы улучшить тонус.")
        elif self.mood in negative:
            recs.append("Настроение отрицательное — постарайтесь сделать дыхательное упражнение 5 минут или короткую прогулку.")
        else:
            recs.append("Нет данных о настроении — пройдите опрос, чтобы получить рекомендации.")

        return recs

    # Вспомогательный метод: можно вызвать из App чтобы открыть экран результатов
    def open_for_date(self, date_key=None):
        """Вызвать перед показом экрана: update_from_store и переключиться"""
        self.update_from_store(date_key)
        self.manager.current = self.name


# KV код как строка
kv_string = '''
<WelcomeScreen>:
    canvas:
        # ВЕРХНИЕ ЛИНИИ - перемещены в canvas корневого виджета
        Color:
            rgba: 1, 0.8, 0.6, 1    
        Line:
            points: [30, root.height * 0.88, root.width * 0.45, root.height * 0.88]
            width: 3

        Color:
            rgba: 1, 0.93, 0.85, 1
        Line:
            points: [root.width * 0.55, root.height * 0.88, root.width - 30, root.height * 0.88]
            width: 3

    FloatLayout:

        # ФОН
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон (1).png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos

        # ЛОГОТИП СВЕРХУ СПРАВА
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/цветочек.png"
            size_hint: (0.15, 0.15)
            pos_hint: {"right": 0.95, "top": 0.98}


        # ТЕКСТ
        Label:
            text: "Добро \\nпожаловать в"
            font_name: "Gilroy-Medium"
            font_size: "34sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": -0.125, "y": 0.10}
            halign: "left"

        Label:
            text: "Sensa"
            font_name: "Gilroy-MediumItalic"
            font_size: "88sp"
            color: 0.7137, 0.5294, 0.5294, 1
            
            pos_hint: {"x": -0.1, "y": -0.01}
            halign: "left"

        Label:
            text: "Введите свое имя чтобы \\nпродолжить"
            font_name: "Gilroy-Medium"
            font_size: "24sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": -0.04, "y": -0.15}

        # ПОЛЕ ВВОДА
        # ПОЛЕ ВВОДА
        TextInput:
            id: username
            hint_text: ""                      # отключаем стандартный hint
            font_name: "Gilroy-Regular"
            font_size: "22sp"
            size_hint: (.8, .08)
            pos_hint: {"center_x": 0.48, "y": 0.22}
            background_normal: ""
            background_color: (0,0,0,0)
            foreground_color: 0.7137, 0.5294, 0.5294, 1
            cursor_color: 0.7137, 0.5294, 0.5294, 1
            padding: [20, 20]

    # Подчёркивание
            canvas.after:
                Color:
                    rgba: 0.55, 0.38, 0.38, .35
                Line:
                    width: 1.2
                    points: [self.x + 20, self.y + 5, self.right - 20, self.y + 5]

    # Кастомный hint-текст — остаётся внутри TextInput
            Label:
                text: "Ввести имя..."
                font_name: "Gilroy-Regular"
                font_size: "22sp"
                color: (0.55, 0.38, 0.38, .5)
                pos: self.parent.x + 20, self.parent.y + self.parent.height/2 - 10
                size_hint: None, None
                opacity: 1 if username.text == "" else 0

        # КНОПКА
        Button:
            text: "Продолжить"
            font_name: "Gilroy-SemiBold"
            size_hint: (.8, .07)
            pos_hint: {"center_x": 0.5, "y": 0.05}
    
            background_normal: ""
            background_down: ""
            background_color: 0, 0, 0, 0   # полностью отключаем стандартный фон

            color: 0.7137, 0.5294, 0.5294, 1
            font_size: "18sp"

            on_press: app.go_to_info(username.text)

            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [self.height/2]   # <-- ЭТО ДЕЛАЕТ КНОПКУ ОВАЛЬНОЙ!

<InfoScreen>:

    FloatLayout:

        # ФОН
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон (1).png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos

        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/цветочек.png"
            size_hint: (0.15, 0.15)
            pos_hint: {"right": 0.95, "top": 0.98}

        # НАЗВАНИЕ Sensa
        Label:
            text: "Sensa"
            font_name: "Gilroy-MediumItalic"
            font_size: "88sp"
            color: 0.7137, 0.5294, 0.5294, 1
            
            pos_hint: {"x": -0.1, "y": -0.01}

        # Блок описания
        BoxLayout:
            orientation: "vertical"
            size_hint: 0.9, None
            height: self.minimum_height
            pos_hint: {"center_x": 0.5, "center_y": 0.3}   # выставляем повыше, чтобы точно было видно

            Label: 
                text: "Приложение помогает пользователю\\nоценить свое психоэмоциональное\\nсостояние и получить рекомендации\\nпо сну, воде, активности и настроению."
                font_name: "Gilroy-Medium"
                font_size: "18sp"
                color: 0.7137, 0.5294, 0.5294, 1

                halign: "left"
                valign: "top"

                text_size: self.width, None

        Button:
            text: "Продолжить"
            font_name: "Gilroy-SemiBold"
            size_hint: (.8, .07)
            pos_hint: {"center_x": 0.5, "y": 0.05}
    
            background_normal: ""
            background_down: ""
            background_color: 0, 0, 0, 0   # полностью отключаем стандартный фон

            color: 0.7137, 0.5294, 0.5294, 1
            font_size: "18sp"

            on_press: app.go_to_greeting() 

            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [self.height/2]   # <-- ЭТО ДЕЛАЕТ КНОПКУ ОВАЛЬНОЙ!

<GreetingScreen>:
    
    FloatLayout:

        # Фон
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон2.png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos

        # Текст "Добрый день,"
        Label:
            text: "Добрый день,"
            font_size: "34sp"
            font_name: "Gilroy-Medium"
            color: 1, 1, 1, 1
            pos_hint: {"center_x": 0.5, "center_y": 0.47}
            halign: "center"

        # Имя пользователя — динамическое
        Label:
            id: username_label
            text: "[b]Имя![/b]"
            markup: True
            font_size: "48sp"
            font_name: "Gilroy-MediumItalic"
            color: 1, 1, 1, 1
            pos_hint: {"center_x": 0.5, "center_y": 0.40}
            halign: "center"
        Button:
            text: "Продолжить"
            font_name: "Gilroy-SemiBold"
            size_hint: (.7, .085)
            pos_hint: {"center_x": 0.5, "y": 0.05}
            background_normal: ""
            background_color: (1,1,1,1)
            color: 0.7137, 0.5294, 0.5294, 1
            font_size: "22sp"
            border: (30, 30, 30, 30)
            on_press: app.go_to_home()

<HomeScreen>:
    name: "home"
    FloatLayout:
        #Фоновое изображение
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон (1).png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos
        
        Label:
            id: month_label
            text: "Ноябрь, 2025"
            font_name: "Gilroy-Medium"
            font_size: "22sp"
            color: 0.7137, 0.5294, 0.5294, 1
            size_hint: None, None
            size: self.texture_size
            pos_hint: {"center_x": 0.5, "center_y": 0.89}               

        Button:
            text: "<"
            size_hint: None, None
            size: 48,48
            pos_hint: {"center_x":0.2, "center_y":0.89}
            background_normal: ""
            background_color: 0,0,0,0
            color:0.7137, 0.5294, 0.5294, 1
            on_release: root.previous_week()

        Button:
            text: ">"
            size_hint: None, None
            size: 48,48
            pos_hint: {"center_x":0.8, "center_y":0.89}
            background_normal: ""
            background_color: 0,0,0,0
            color:0.7137, 0.5294, 0.5294, 1
            on_release: root.next_week()

        # calendar number buttons - created in Python update_calendar (GridLayout)
        GridLayout:
            id: calendar_grid
            cols: 7
            size_hint: 0.9, None
            height: 80
            pos_hint: {"center_x":0.5, "center_y":0.82}
            spacing: 8
            padding: [6,6,6,6]

        # Water card
        BoxLayout:
            orientation: "horizontal"
            size_hint: 0.9, None
            height: 100
            pos_hint: {"center_x":0.5, "center_y":0.70}
            padding: 16
            spacing: 12
            canvas.before:
                Color:
                    rgba: 1,0.9647,0.9333,1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]
                
            Image:
                # can use the small flower icon or other
                source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/вода.png"
                size_hint_x: 0.18
            BoxLayout:
                orientation: "vertical"
                Label:
                    text: "500 мл"
                    font_name: "Gilroy-SemiBold"
                    font_size: "18sp"
                    color: 0.7569, 0.5804, 0.5608, 1
                Label:
                    text: "Водный баланс"
                    font_name: "Gilroy-Medium"
                    font_size: "14sp"
                    color: 0.7569, 0.5804, 0.5608, 1
            # right-side circular placeholder
                

        #Карточка шагов
        BoxLayout:
            orientation: "horizontal"
            size_hint: 0.9, None
            height: 100
            pos_hint: {"center_x":0.5, "center_y":0.59}
            padding: 16
            spacing: 12
            canvas.before:
                Color:
                    rgba: 1,1,1,1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]
                Color:
                    rgba: 0.8, 0.7, 0.7, 0.6   # цвет рамки
                Line:
                    width: 1.0
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 20)
            Image:
                source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/шаги.png"
                size_hint_x: 0.18
            BoxLayout:
                orientation: "vertical"
                Label:
                    text: "2.500 шагов"
                    font_name: "Gilroy-SemiBold"
                    font_size: "18sp"
                    color: 0.7569, 0.5804, 0.5608, 1
                Label:
                    text: "Активность"
                    font_name: "Gilroy-Medium"
                    font_size: "14sp"
                    color: 0.7569, 0.5804, 0.5608, 1

        # Large question block (uses blurred asset as background)
        BoxLayout:
            size_hint: 1, 0.24
            pos_hint: {"center_x":0.5, "center_y":0.34}
            canvas.before:
                Color:
                    rgba: 1,1,1,0
            Label:
                id: username_label
                text: "Как ты себя\\nчувствуешь\\nсегодня,\\n[b]Имя?[/b]"
                markup: True
                font_name: "Gilroy-Regular"
                font_size: "28sp"
                color:  0.7137, 0.5294, 0.5294, 1
                halign: "center"
                text_size: self.width, None

        # ------------------ Нижняя навигация ------------------
        # Контейнер для трех кнопок
        BoxLayout:
            orientation: "horizontal"
            size_hint: 0.7, None
            height: 70
            pos_hint: {"center_x": 0.37, "y": 0.03}
            spacing: 15
            padding: [10, 10]

            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [35]

            # Кнопка Дом - как Image с TouchBehavior
            RelativeLayout:
                size_hint: None, None
                size: 45, 45
                pos_hint: {"center_x": 0.5, "center_y": 0.1}
                
                Image:
                    source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/home.png"
                    allow_stretch: True
                    keep_ratio: True
                    size: self.parent.size
                    pos: self.parent.pos
                
                Button:
                    background_normal: ""
                    background_color: (0, 0, 0, 0)  # Полностью прозрачный
                    size: self.parent.size
                    pos: self.parent.pos
                    on_release: app.go_to_home()

            # Аналогично для Статистики
            RelativeLayout:
                size_hint: None, None
                size: 45, 45
                pos_hint: {"center_x": 0.5, "center_y": 0.1}
                
                Image:
                    source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Статистика.png"
                    allow_stretch: True
                    keep_ratio: True
                    size: self.parent.size
                    pos: self.parent.pos
                
                Button:
                    background_normal: ""
                    background_color: (0, 0, 0, 0)
                    size: self.parent.size
                    pos: self.parent.pos
                    on_release: print("Статистика")

            # Аналогично для Результатов
            RelativeLayout:
                size_hint: None, None
                size: 45, 45
                pos_hint: {"center_x": 0.5, "center_y": 0.1}
                
                Image:
                    source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Результаты.png"
                    allow_stretch: True
                    keep_ratio: True
                    size: self.parent.size
                    pos: self.parent.pos
                
                Button:
                    background_normal: ""
                    background_color: (0, 0, 0, 0)
                    size: self.parent.size
                    pos: self.parent.pos
                    on_release: print("Результаты")
        
        # Контейнер для кнопки "+"
        BoxLayout:
            orientation: "horizontal"
            size_hint: None, None
            width: 70  # Фиксированная ширина для одной кнопки
            height: 70
            pos_hint: {"right": 0.92, "y": 0.03}
            padding: [12, 12]  # Отступы внутри контейнера

            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [35]

            # Кнопка "+" справа (исправленная)
            Button:
                background_normal: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Начать.png"
                background_down: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Начать.png"
                size_hint: None, None
                size: 45, 45
                pos_hint: {"right": 0.94, "center_y": 0.43}
                allow_stretch: True
                keep_ratio: True
                border: (0, 0, 0, 0)  # Добавил - убирает растягивание краев
                background_color: (1, 1, 1, 1)  # Добавил - белый фон
                on_release: app.go_to_share()
            
<CalendarDay>:
    background_normal: ""
    background_color: (1, 1, 1, 0)  # прозрачный фон
    color: 0.55, 0.35, 0.35, 1
    font_name: "Gilroy-SemiBold"
    font_size: "18sp"

    canvas.before:
        Color:
            rgba: (0.95, 0.90, 0.85, 1) if not self.is_selected else (0.8, 0.6, 0.6, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]


<ShareScreen>:
    name: "share"
    FloatLayout:
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон2.png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos

        Button:
            text: "<"
            size_hint: None, None
            size: 44,44
            pos_hint: {"center_x":0.1, "center_y":0.92}
            background_normal: ""
            background_color: 1,1,1,0.5
            on_release: app.go_to_home()
        Label:
            text: "Поделитесь своим\\n[ref=state]состоянием?[/ref]"
            markup: True
            font_size: "34sp"
            font_name: "Gilroy-Medium"
            color: 1,1,1,1
            pos_hint: {"center_x":0.5, "center_y":0.6}
            halign: "center"
            text_size: self.width, None
        Button:
            text: "Пройти опрос"
            font_size: "25sp"
            font_name: "Gilroy-Medium"
            size_hint: (.7, .05)
            pos_hint: {"center_x":0.5, "center_y":0.45}
            background_normal: ""
            background_down: ""
            background_color: 0,0,0,0
            color:  0.7137, 0.5294, 0.5294, 1
            on_release:
                app.go_to_water()
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [self.height/2]   # <-- ЭТО ДЕЛАЕТ КНОПКУ ОВАЛЬНОЙ!
        Button:
            text: "Вернуться на главную"
            font_size: "20sp"
            font_name: "Gilroy-Medium"
            size_hint: 0.7,0.08
            pos_hint: {"center_x":0.5, "center_y":0.12}
            background_normal: ""
            background_down: ""
            background_color:  0, 0, 0, 0
            color: 0.7137, 0.5294, 0.5294, 1
            canvas.before:
                Color:
                    rgba: 0.8, 0.7, 0.7, 0.6   # цвет рамки
                Line:
                    width: 1.0
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 20)
            on_release:
                app.go_to_home()

<WaterScreen>:
    name: "water"
    FloatLayout:
        # Фон
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон для опроса.png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos

        # Заголовок "Вода"
        Label:
            text: "Вода"
            font_name: "Gilroy-Medium"
            font_size: "40sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": -0.3, "y": 0.41}

        # Кнопка назад "<"
        Button:
            text: "<"
            font_size: "30sp"
            background_normal: ""
            background_color: 1,1,1,0.4
            size_hint: None, None
            size: 45,45
            pos_hint: {"right": 0.95, "top": 0.93}
            color: 0.7,0.5,0.5,1
            on_release: app.go_to_home()

        # Подзаголовок
        Label:
            text: "Введи примерно сколько\\nстаканов воды ты сегодня выпил"
            halign: "left"
            font_name: "Gilroy-Medium"
            font_size: "20sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": 0.07, "y": 0.3}
            text_size: self.width, None

        # Стакан воды (только фон)
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/стакан.png"
            size_hint: 0.7, 0.38
            pos_hint: {"center_x": 0.5, "center_y": 0.45}

        # Текст 300/1000 ml
        Label:
            id: water_label
            text: "0/1000 ml"
            font_name: "Gilroy-Medium"
            font_size: "26sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"center_x": 0.5, "center_y": 0.60}
        
            # Контейнер для кнопки "+"
        BoxLayout:
            orientation: "horizontal"
            size_hint: None, None
            width: 70  # Фиксированная ширина для одной кнопки
            height: 70
            pos_hint: {"right": 0.57, "y": 0.36}
            padding: [12, 12]  # Отступы внутри контейнера

            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [35]

            # Кнопка +100мл (ИСПРАВЛЕНА)
            Button:
                background_normal: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Начать (2).png"
                background_down: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Начать (2).png"
                background_color: (1, 1, 1, 1)
                size_hint: None, None
                size: 45, 45
                pos_hint: {"center_x": 0.56, "center_y": 0.44}
                allow_stretch: True
                keep_ratio: True
                border: (0, 0, 0, 0)  # Важно! Убирает растягивание
                on_release: root.add_water(100)

        # Подпись "100мл"
        Label:
            text: "100ml"
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 1, 1, 1, 1
            pos_hint: {"center_x": 0.5, "center_y": 0.34}

        # Подсказка "примерная норма"
        Label:
            text: "Примерная норма в день\\n1 литр воды"
            halign: "left"
            font_name: "Gilroy-Medium"
            font_size: "18sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": 0.072, "y": -0.33}
            text_size: self.width, None
        
        # Круглый белый контейнер для кнопки перехода
        BoxLayout:
            size_hint: None, None
            width: 70
            height: 70
            pos_hint: {"right": 0.95, "y": 0.05}
            padding: [0, 0]  # Убираем внутренние отступы
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [35]  # Полностью круглый

            # Кнопка перехода →
            Button:
                text: ">"
                font_size: "32sp"
                background_normal: ""  # Убираем стандартный фон
                background_color: (0, 0, 0, 0)  # Делаем полностью прозрачным
                color: 0.7137, 0.5294, 0.5294, 1
                size: self.parent.size
                pos: self.parent.pos
                on_release: app.go_to_steps()
            
            
<StepsScreen>:
    name: "steps"

    FloatLayout:

        # ФОН
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон для опроса.png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos

        # Кнопка назад "<"
        Button:
            text: "<"
            font_size: "30sp"
            background_normal: ""
            background_color: 1,1,1,0.4
            size_hint: None, None
            size: 45,45
            pos_hint: {"right": 0.95, "top": 0.93}
            color: 0.7,0.5,0.5,1
            on_release: app.go_to_water()

        # Заголовок
        Label:
            text: "Шаги"
            font_name: "Gilroy-Medium"
            font_size: "38sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": -0.3, "y": 0.41}

        Label:
            text: "Введи примерно сколько\\nты сегодня прошел"
            font_name: "Gilroy-Medium"
            font_size: "20sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": -0.12, "y": 0.3}

        Label:
            text: "Нажми на нужную область"
            pos_hint: {"x": -0.145, "top": 1.15}
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.7137, 0.5294, 0.5294, 1

        # Выбор диапазонов
        BoxLayout:
            orientation: "horizontal"
            size_hint: 0.9, None
            height: 70
            pos_hint: {"center_x":0.5, "top":0.62}
            spacing: 15

            # Ячейка "<2000"
            Button:
                background_normal: ""
                background_color: (0, 0, 0, 0)  # Прозрачный фон
                background_down: ""  # Убираем фон при нажатии
                background_active: ""  # Убираем активный фон
                border: (0, 0, 0, 0)
                on_release: root.choose_range(2000)
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 0.8
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [25, 0, 0, 25]  # Только левые углы скруглены
                canvas.after:
                    Color:
                        rgba: 0.8, 0.7, 0.7, 0.6
                    Line:
                        width: 0.8
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 25, 0, 0, 25)

            # Ячейка "2000–5000"
            Button:
                background_normal: ""
                background_color: (0, 0, 0, 0)  # Прозрачный фон
                background_down: ""  # Убираем фон при нажатии
                background_active: ""  # Убираем активный фон
                border: (0, 0, 0, 0)
                on_release: root.choose_range(3500)
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 0.8
                    Rectangle:
                        pos: self.pos
                        size: self.size
                canvas.after:
                    Color:
                        rgba: 0.8, 0.7, 0.7, 0.6
                    Line:
                        width: 0.8
                        rectangle: (self.x, self.y, self.width, self.height)

            # Ячейка ">5000"
            Button:
                background_normal: ""
                background_color: (0, 0, 0, 0)  # Прозрачный фон
                background_down: ""  # Убираем фон при нажатии
                background_active: ""  # Убираем активный фон
                border: (0, 0, 0, 0)
                on_release: root.choose_range(6000)
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 0.8
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [0, 25, 25, 0]
                canvas.after:
                    Color:
                        rgba: 0.8, 0.7, 0.7, 0.6
                    Line:
                        width: 0.8
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 0, 25, 25, 0)

         # Нижний ряд - текст под ячейками
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: 0.9, None
            spacing: 0
            pos_hint: {"center_x":0.5, "top":0.52}  # Координаты для текста

            Label:
                text: "<2000"
                font_name: "Gilroy-Medium"
                font_size: "16sp"
                color: 0.7137, 0.5294, 0.5294, 1
                halign: "center"
                size_hint_x: 1

            Label:
                text: "2000–5000"
                font_name: "Gilroy-Medium"
                font_size: "16sp"
                color: 0.7137, 0.5294, 0.5294, 1
                halign: "center"
                size_hint_x: 1

            Label:
                text: ">5000"
                font_name: "Gilroy-Medium"
                font_size: "16sp"
                color: 0.7137, 0.5294, 0.5294, 1
                halign: "center"
                size_hint_x: 1       

        # Поле ввода шагов
        Label:
            text: "Или введи самостоятельно"
            pos_hint: {"x": -0.145, "top": 0.92}
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.7137, 0.5294, 0.5294, 1

        TextInput:
            id: steps_input
            hint_text: "7000..."
            font_size: "16sp"
            font_name: "Gilroy-Medium"
            size_hint: 0.9, None
            height: 55
            pos_hint: {"center_x":0.5, "top":0.40}
            background_normal: ""
            background_color: 1,1,1,0.35
            foreground_color: 0.7137, 0.5294, 0.5294, 1
            cursor_color: 0.7137, 0.5294, 0.5294, 1
            multiline: False
            padding: [15, 15]  # Это двигает текст ВНУТРИ поля

            # Убираем синий фон при фокусе
            background_active: ''
            background_disabled: ''
            
            # Отключаем подсветку при фокусе
            canvas.after:
                Color:
                    rgba: 0, 0, 0, 0
                Rectangle:
                    pos: self.pos
                    size: self.size
            on_text: 
                if self.text.isdigit(): root.selected_steps = int(self.text)
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.35
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]  # Скругленные углы
                Color:
                    rgba: 0.8, 0.7, 0.7, 0.6
                Line:
                    width: 1.2
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 25)
            

        # Норма
        Label:
            text: "Примерная норма в день\\n7000 шагов"
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            halign: "left"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": -0.16, "top": 0.68}
        
        # Круглый белый контейнер для кнопки перехода
        BoxLayout:
            size_hint: None, None
            width: 70
            height: 70
            pos_hint: {"right": 0.95, "y": 0.05}
            padding: [0, 0]
            
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [35]

            Button:
                text: ">"
                font_size: "32sp"
                background_normal: ""
                background_color: 0,0,0,0
                color: 0.7137, 0.5294, 0.5294, 1
                size_hint: None,None
                size: 70,70
                pos_hint: {"right": 0.95, "y": 0.05}
                on_release:
                    app.go_to_sleep()
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [self.height] 

        

<RangeButton>:
    background_normal: ""
    background_color: (1, 1, 1, 0)
    canvas.before:
        Color:
            rgba: root.border_color
        Line:
            width: 1.0
            rounded_rectangle: (self.x, self.y, self.width, self.height, 30)            

<SleepScreen>:
    FloatLayout:
        canvas.before:
            Rectangle:
                source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон для сна и эмоций.png"   # твой фон
                size: self.size
                pos: self.pos

        # Заголовок
        Label:
            text: "Сон"
            font_name: "Gilroy-Medium"
            font_size: "36sp"
            color:  0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": -0.32, "y": 0.41}

        # Кнопка назад "<"
        Button:
            text: "<"
            font_size: "30sp"
            background_normal: ""
            background_color: 1,1,1,0.4
            size_hint: None, None
            size: 45,45
            pos_hint: {"right": 0.95, "top": 0.93}
            color: 0.7,0.5,0.5,1
            on_release: app.go_to_steps()

        # Подзаголовок
        Label:
            text: "Введи примерно сколько\\nты сегодня спал"
            font_name: "Gilroy-Medium"
            halign: "left"
            color:  0.7137, 0.5294, 0.5294, 1
            font_size: "20sp"
            pos_hint: {"x": 0.1, "y": 0.3}
            text_size: self.width, None

        # КАРТОЧКА – СОН
        BoxLayout:
            orientation: "vertical"
            size_hint: .9, .24
            pos_hint: {"center_x":0.5, "top":0.75}
            padding: 0
            canvas.before:
                Color:
                    rgba: 1,1,1,0.8
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]
                Color:
                    rgba: 0.8, 0.7, 0.7, 0.6   # цвет рамки
                Line:
                    width: 1.0
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 20)

            Label:
                text: "Время для сна"
                font_name: "Gilroy-Medium"
                font_size: "20sp"
                color:  0.7137, 0.5294, 0.5294, 1
                size_hint_y: .35

            # Time picker (сон)
            BoxLayout:
                size_hint_y: .65
                spacing: dp(5)

                Spinner:
                    background_color: (1, 1, 1, 0)  # прозрачный фон
                    text: str(root.sleep_hour)
                    values: [str(i) for i in range(0, 24)]
                    font_size: "34sp"
                    color: 0.7137, 0.5294, 0.5294, 1
                    on_text: root.sleep_hour = int(self.text)

                Label:
                    text: ":"
                    font_size: "34sp"
                    color: 0.55,0.38,0.38,1

                Spinner:
                    background_color: (1, 1, 1, 0)  # прозрачный фон
                    text: f"{root.sleep_min:02d}"
                    values: ["00","10","20","30","40","50"]
                    font_size: "34sp"
                    color: 0.7137, 0.5294, 0.5294, 1
                    on_text: root.sleep_min = int(self.text)

        # КАРТОЧКА – ПРОБУЖДЕНИЕ
        BoxLayout:
            orientation: "vertical"
            size_hint: .9, .24
            pos_hint: {"center_x":0.5, "top":0.47}
            padding: 0
            canvas.before:
                Color:
                    rgba: 1,1,1,0.8
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]
                Color:
                    rgba: 0.8, 0.7, 0.7, 0.6   # цвет рамки
                Line:
                    width: 1.0
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 20)

            Label:
                text: "Время пробуждения"
                font_name: "Gilroy-Medium"
                font_size: "20sp"
                color:  0.7137, 0.5294, 0.5294, 1
                size_hint_y: .35

            BoxLayout:
                size_hint_y: .65
                spacing: dp(5)

                Spinner:
                    background_color: (1, 1, 1, 0)  # прозрачный фон
                    text: str(root.wake_hour)
                    values: [str(i) for i in range(0, 24)]
                    font_size: "34sp"
                    color: 0.7137, 0.5294, 0.5294, 1
                    on_text: root.wake_hour = int(self.text)

                Label:
                    text: ":"
                    font_size: "34sp"
                    color: 0.7137, 0.5294, 0.5294, 1

                Spinner:
                    background_color: (1, 1, 1, 0)  # прозрачный фон
                    text: f"{root.wake_min:02d}"
                    values: ["00","10","20","30","40","50"]
                    font_size: "34sp"
                    color: 0.7137, 0.5294, 0.5294, 1
                    on_text: root.wake_min = int(self.text)
            # Норма сна
        Label:
            text: "Примерная норма в день\\n8 часов"
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color:  0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": 0.1, "top": 0.67}
            halign: "left"
            text_size: self.width, None

        # Кнопка далее
        Button:
            text: ">"
            font_size: "32sp"
            background_normal: ""
            background_color: 0,0,0,0
            color: 0.7137, 0.5294, 0.5294, 1
            size_hint: None,None
            size: 70,70
            pos_hint: {"right": 0.95, "y": 0.05}
            on_release:
                app.go_to_mood()
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [self.height] 

<EmotionCarousel>:
    canvas.before:
        Color:
            rgba: 1,1,1,0
        Rectangle:
            pos: self.pos
            size: self.size   

<MoodScreen>:
    FloatLayout:
        Label:
            text: "Настроение"
            font_name: "Gilroy-Medium"
            font_size: "36sp"
            color:  0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": 0, "y": 0}

        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон для сна и эмоций.png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos
        Button:
            text: "<"
            font_size: "30sp"
            background_normal: ""
            background_color: 1,1,1,0.4
            size_hint: None, None
            size: 45,45
            pos_hint: {"right": 0.95, "top": 0.93}
            color: 0.7,0.5,0.5,1
            on_release: app.go_to_sleep()
        

        Label:
            text: "Как ты себя ощущаешь?"
            font_name: "Gilroy-Medium"
            font_size: "30sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": 0.1, "y": 0.3}

        EmotionCarousel:
            id: carousel
            size_hint: 1, 0.55
            pos_hint: {"center_x":0.5, "center_y":0.48}

            # Картинка эмоции
            Image:
                id: emoji_img
                source: root.ids.carousel.emotion_image
                size_hint: None, None
                size: 200, 200
                pos_hint: {"center_x":0.5, "center_y":0.6}

            # Название эмоции
            Label:
                text: root.ids.carousel.emotion_name
                font_name: "Gilroy-SemiBold"
                font_size: "26sp"
                color: 0.7137, 0.5294, 0.5294, 1
                pos_hint: {"center_x":0.5, "center_y":0.25}

            # кнопка назад
            Button:
                text: "<"
                size_hint: None, None
                size: 60, 60
                pos_hint: {"center_x":0.2, "center_y":0.5}
                background_normal: ""
                background_color: 1,1,1,0.2
                color: 0.7137, 0.5294, 0.5294, 1
                on_release: root.ids.carousel.prev_emotion()

            # кнопка вперёд
            Button:
                text: ">"
                size_hint: None, None
                size: 60, 60
                pos_hint: {"center_x":0.8, "center_y":0.5}
                background_normal: ""
                background_color: 1,1,1,0.2
                color: 0.7137, 0.5294, 0.5294, 1
                on_release: root.ids.carousel.next_emotion()

        Button:
            text: "Подобрать"
            size_hint: 0.7,0.1
            pos_hint: {"center_x":0.5, "center_y":0.12}
            font_name: "Gilroy-SemiBold"
            background_normal: ""
            background_color: 1,1,1,1
            color: 0.7,0.5,0.5,1
            on_release:
                print("Выбрано:", root.ids.carousel.emotion_name)
        
        # Кнопка далее
        Button:
            text: ">"
            font_size: "32sp"
            background_normal: ""
            background_color: 0,0,0,0
            color: 0.7137, 0.5294, 0.5294, 1
            size_hint: None,None
            size: 70,70
            pos_hint: {"right": 0.95, "y": 0.05}
            on_release:
                app.go_to_share_2()
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [self.height] 

<Share_2_Screen>:
    name: "share_2"
    FloatLayout:
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон2.png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos


        Button:
            text: "<"
            size_hint: None, None
            size: 44,44
            pos_hint: {"center_x":0.1, "center_y":0.92}
            background_normal: ""
            background_color: 1,1,1,0.5
            on_release: app.go_to_mood()
        Label:
            text: "Спасибо,\\n за пройденный опрос!"
            markup: True
            font_size: "34sp"
            font_name: "Gilroy-Medium"
            color: 1,1,1,1
            pos_hint: {"center_x":0.5, "center_y":0.6}
            halign: "center"
            text_size: self.width, None
        Button:
            text: "Узнать результат"
            font_size: "25sp"
            font_name: "Gilroy-Medium"
            size_hint: (.7, .05)
            pos_hint: {"center_x":0.5, "center_y":0.45}
            background_normal: ""
            background_down: ""
            background_color: 0,0,0,0
            color:  0.7137, 0.5294, 0.5294, 1
            on_release:
                app.go_to_water()
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [self.height/2]   # <-- ЭТО ДЕЛАЕТ КНОПКУ ОВАЛЬНОЙ!
        Button:
            text: "Вернуться к опросу"
            font_size: "20sp"
            font_name: "Gilroy-Medium"
            size_hint: 0.7,0.08
            pos_hint: {"center_x":0.5, "center_y":0.12}
            background_normal: ""
            background_down: ""
            background_color:  0, 0, 0, 0
            color: 0.7137, 0.5294, 0.5294, 1
            canvas.before:
                Color:
                    rgba: 0.8, 0.7, 0.7, 0.6   # цвет рамки
                Line:
                    width: 1.0
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 20)
            on_release:
                app.go_to_water()

<ResultScreen>:
    name: "results"

    FloatLayout:
        # фон (вставь путь к вашему фону или оставь однотонный)
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон (1).png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos

        # Заголовок
        Label:
            text: "Результаты"
            font_name: "Gilroy-SemiBold"
            font_size: "34sp"
            color: 0.55,0.38,0.38,1
            pos_hint: {"center_x":0.5, "top":0.95}

        # Подзаголовок / дата
        Label:
            id: results_date
            text: root.date_key
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.55,0.38,0.38,1
            pos_hint: {"center_x":0.5, "top":0.90}

        # ------------- Карточки (в одну колонку, как в дизайне) -------------
        GridLayout:
            cols: 1
            size_hint: 0.94, None
            height: dp(420)
            pos_hint: {"center_x":0.5, "center_y":0.6}
            row_default_height: dp(100)
            row_force_default: True
            spacing: dp(12)

            # Карточка Воды
            BoxLayout:
                orientation: "horizontal"
                padding: dp(14)
                spacing: dp(12)
                canvas.before:
                    Color:
                        rgba: 1, 0.9647, 0.9333, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [18]
                    Color:
                        rgba: 0.85,0.75,0.72,1
                    Line:
                        width: 1.2
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 18)

                Image:
                    source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/вода.png"
                    size_hint_x: None
                    width: dp(60)

                BoxLayout:
                    orientation: "vertical"
                    Label:
                        text: "Водный баланс"
                        font_name: "Gilroy-Medium"
                        font_size: "16sp"
                        color: 0.45,0.32,0.32,1
                        halign: "left"
                        text_size: self.width, None
                    Label:
                        id: water_val
                        text: f"{int(root.water_ml)} мл"
                        font_name: "Gilroy-SemiBold"
                        font_size: "20sp"
                        color: 0.45,0.32,0.32,1
                        halign: "left"
                        text_size: self.width, None

            # Карточка Шагов
            BoxLayout:
                orientation: "horizontal"
                padding: dp(14)
                spacing: dp(12)
                canvas.before:
                    Color:
                        rgba: 1, 0.9647, 0.9333, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [18]
                    Color:
                        rgba: 0.85,0.75,0.72,1
                    Line:
                        width: 1.2
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 18)

                Image:
                    source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/шаги.png"
                    size_hint_x: None
                    width: dp(60)

                BoxLayout:
                    orientation: "vertical"
                    Label:
                        text: "Активность"
                        font_name: "Gilroy-Medium"
                        font_size: "16sp"
                        color: 0.45,0.32,0.32,1
                        halign: "left"
                        text_size: self.width, None
                    Label:
                        id: steps_val
                        text: f"{int(root.steps)} шагов"
                        font_name: "Gilroy-SemiBold"
                        font_size: "20sp"
                        color: 0.45,0.32,0.32,1
                        halign: "left"
                        text_size: self.width, None

            # Карточка Сна
            BoxLayout:
                orientation: "horizontal"
                padding: dp(14)
                spacing: dp(12)
                canvas.before:
                    Color:
                        rgba: 1, 0.9647, 0.9333, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [18]
                    Color:
                        rgba: 0.85,0.75,0.72,1
                    Line:
                        width: 1.2
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 18)

                Image:
                    source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/сон.png"
                    size_hint_x: None
                    width: dp(60)

                BoxLayout:
                    orientation: "vertical"
                    Label:
                        text: "Сон"
                        font_name: "Gilroy-Medium"
                        font_size: "16sp"
                        color: 0.45,0.32,0.32,1
                        halign: "left"
                        text_size: self.width, None
                    Label:
                        id: sleep_val
                        text: (root.sleep_start + " — " + root.sleep_end) if root.sleep_start and root.sleep_end else f"{root.sleep_hours} ч"
                        font_name: "Gilroy-SemiBold"
                        font_size: "20sp"
                        color: 0.45,0.32,0.32,1
                        halign: "left"
                        text_size: self.width, None

            # Карточка Настроения
            BoxLayout:
                orientation: "horizontal"
                padding: dp(14)
                spacing: dp(12)
                canvas.before:
                    Color:
                        rgba: 1, 0.9647, 0.9333, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [18]
                    Color:
                        rgba: 0.85,0.75,0.72,1
                    Line:
                        width: 1.2
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 18)

                # вместо Image можно поставить картинку эмоции, если храните путь
                Image:
                    source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/mood_placeholder.png"
                    size_hint_x: None
                    width: dp(60)

                BoxLayout:
                    orientation: "vertical"
                    Label:
                        text: "Настроение"
                        font_name: "Gilroy-Medium"
                        font_size: "16sp"
                        color: 0.45,0.32,0.32,1
                        halign: "left"
                        text_size: self.width, None
                    Label:
                        id: mood_val
                        text: root.mood
                        font_name: "Gilroy-SemiBold"
                        font_size: "20sp"
                        color: 0.45,0.32,0.32,1
                        halign: "left"
                        text_size: self.width, None

        # ---------------- Блок рекомендаций ----------------
        BoxLayout:
            orientation: "vertical"
            size_hint: 0.94, None
            height: dp(200)
            pos_hint: {"center_x":0.5, "center_y":0.25}
            padding: dp(12)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: 1,1,1,1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [16]
                Color:
                    rgba: 0.9,0.85,0.82,1
                Line:
                    width: 1
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 16)

            Label:
                text: "Рекомендации"
                font_name: "Gilroy-Medium"
                font_size: "18sp"
                color: 0.45,0.32,0.32,1
                size_hint_y: None
                height: dp(26)

            # список рекомендаций
            GridLayout:
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: dp(36)
                row_force_default: True
                padding: [6,0,6,0]

                Label:
                    text: root.rec_texts[0] if root.rec_texts and len(root.rec_texts) > 0 else ""
                    font_name: "Gilroy-Regular"
                    font_size: "14sp"
                    color: 0.45,0.32,0.32,1
                    halign: "left"
                    text_size: self.width, None

                Label:
                    text: root.rec_texts[1] if root.rec_texts and len(root.rec_texts) > 1 else ""
                    font_name: "Gilroy-Regular"
                    font_size: "14sp"
                    color: 0.45,0.32,0.32,1
                    halign: "left"
                    text_size: self.width, None

                Label:
                    text: root.rec_texts[2] if root.rec_texts and len(root.rec_texts) > 2 else ""
                    font_name: "Gilroy-Regular"
                    font_size: "14sp"
                    color: 0.45,0.32,0.32,1
                    halign: "left"
                    text_size: self.width, None

                Label:
                    text: root.rec_texts[3] if root.rec_texts and len(root.rec_texts) > 3 else ""
                    font_name: "Gilroy-Regular"
                    font_size: "14sp"
                    color: 0.45,0.32,0.32,1
                    halign: "left"
                    text_size: self.width, None

        # Кнопки внизу
        BoxLayout:
            orientation: "horizontal"
            size_hint: 0.9, None
            height: dp(64)
            pos_hint: {"center_x":0.5, "y":0.03}
            spacing: dp(12)

            Button:
                text: "На главную"
                size_hint: .7, 1
                background_normal: ""
                background_down: ""
                background_color: 1,1,1,1
                color: 0.55,0.38,0.38,1
                canvas.before:
                    Color:
                        rgba: 1,1,1,1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [self.height/2]
                on_release:
                    app.go_to_home()

            Button:
                text: "Поделиться"
                size_hint: .3, 1
                background_normal: ""
                background_down: ""
                background_color: 0.55,0.38,0.38,1
                color: 1,1,1,1
                canvas.before:
                    Color:
                        rgba: 0.55,0.38,0.38,1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [self.height/2]
                on_release:
                    print("Поделиться: ", root.date_key, root.water_ml, root.steps, root.sleep_hours, root.mood)
'''

class MainApp(App):
    def build(self):
        # Загружаем KV строку вместо файла
        Builder.load_string(kv_string)
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name="welcome"))
        sm.add_widget(InfoScreen(name="info"))
        sm.add_widget(GreetingScreen(name="greeting"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ShareScreen(name="share"))
        sm.add_widget(WaterScreen(name="water"))
        sm.add_widget(StepsScreen(name="steps"))
        sm.add_widget(SleepScreen(name="sleep"))
        sm.add_widget(MoodScreen(name="mood"))
        sm.add_widget(Share_2_Screen(name="share_2"))
        sm.add_widget(ResultScreen(name="results"))
        return sm
    
    def save_name(self, name):
        if name.strip():
            store.put("user", name=name)
    
    def get_name(self):
        if store.exists("user"):
            return store.get("user")["name"]
        return ""
    
    def go_to_info(self, name):
        self.save_name(name)
        self.root.current = "info"
    
    def go_to_greeting(self):
        name = self.get_name()
        screen = self.root.get_screen("greeting")
        screen.ids.username_label.text = f"[b]{name}![/b]"
        self.root.current = "greeting"
    
    def go_to_home(self):
        name = self.get_name()
        screen = self.root.get_screen("home")
        screen.ids.username_label.text = f"[b]{name}?[/b]"
        self.root.current = "home"

    def go_to_share(self):
        self.root.current = "share"

    def go_to_water(self):
        self.root.current = "water"
    def go_to_steps(self):
        self.root.current = "steps"
    
    def go_next(self):
    # если пользователь написал число вручную
        if self.ids.steps_input.text.isdigit():
            self.selected_steps = int(self.ids.steps_input.text)

        key = datetime.now().strftime("%Y-%m-%d")

        data = daily_store.get(key) if daily_store.exists(key) else {}
        data["steps"] = self.selected_steps

        daily_store.put(key, **data)
        print("Сохранены шаги:", data["steps"])

        App.get_running_app().go_to_sleep()

    def go_to_sleep(self):
        self.root.current = "sleep"
    def go_to_mood(self):
        self.root.current = "mood"
    def go_to_share_2(self):
        self.root.current = "share_2"

        App.get_running_app().go_to_results()

    def go_to_results(self, date_key=None):
        scr = self.root.get_screen("results")
        scr.update_from_store(date_key)
        self.root.current = "results"


if __name__ == '__main__':
    MainApp().run()
