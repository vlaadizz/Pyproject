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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.recycleview.views import RecycleDataViewBehavior

Window.size = (390, 844)

#Регистрация шрифтов
LabelBase.register(name="Gilroy-MediumItalic", fn_regular="C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Gilroy-MediumItalic.otf")
LabelBase.register(name="Gilroy-Medium", fn_regular="C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Gilroy-Medium.otf")
LabelBase.register(name="Gilroy-RegularItalic", fn_regular="C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Gilroy-RegularItalic.otf")
LabelBase.register(name="Gilroy-Regular", fn_regular="C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Gilroy-Regular.otf")
LabelBase.register(name="Gilroy-SemiBold", fn_regular="C:/Users/vbzai/OneDrive/Desktop/Sensa_project/Gilroy-SemiBold.otf")

store = JsonStore("user.json") # Для имени пользователя
daily_store = JsonStore("daily.json")# Для ежедневных данных

class PickerItem(Button):
    """Элемент для выбора времени"""
    index = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 60
        self.font_size = '34sp'
        self.font_name = 'Gilroy-Medium'
        self.color = (0.7137, 0.5294, 0.5294, 1)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)

class TimePickerColumn(RecycleView):
    """Колонка выбора времени с прокруткой"""
    selected_value = NumericProperty(0)
    on_selected = None
    
    def __init__(self, values, **kwargs):
        super().__init__(**kwargs)
        self.values = values
        self.do_scroll_x = False
        self.do_scroll_y = True
        self.bar_width = 0
        self.bar_color = (0, 0, 0, 0)
        self.bar_inactive_color = (0, 0, 0, 0)
        
        # Контейнер для кнопок
        self.container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=2,
            padding=[0, 80, 0, 80]  # Увеличен padding для лучшего центрирования
        )
        
        # Создаем кнопки для каждого значения
        self.buttons = []
        for i, value in enumerate(values):
            btn = PickerItem(
                text=f"{value:02d}",
                index=i
            )
            btn.bind(on_release=self._on_button_press)
            self.container.add_widget(btn)
            self.buttons.append(btn)
        
        # Вычисляем высоту контейнера
        self.container.height = len(values) * 62 + 160
        self.add_widget(self.container)
        
        # Центрируем выбранное значение
        Clock.schedule_once(self._center_selected, 0.2)
    
    def _on_button_press(self, btn):
        """Обработка нажатия на кнопку"""
        self.selected_value = self.values[btn.index]
        if self.on_selected:
            self.on_selected(self.selected_value)
        # Прокручиваем к выбранной кнопке
        self._center_to_button(btn.index)
    
    def _center_to_button(self, index):
        """Центрирует скролл к выбранной кнопке"""
        if self.container.height <= self.height:
            return
        
        # Простой расчет: позиция = индекс * высота элемента
        item_height = 62  # 60 + 2 spacing
        # Целевая позиция (чтобы кнопка оказалась в центре)
        target = index * item_height + 80 - (self.height / 2) + 30
        # Нормализуем
        max_scroll = self.container.height - self.height
        scroll_y = target / max_scroll
        scroll_y = max(0, min(1, scroll_y))
        self.scroll_y = 1 - scroll_y
    
    def _center_selected(self, dt):
        """Центрирует скролл к выбранному значению"""
        try:
            index = self.values.index(self.selected_value)
            self._center_to_button(index)
        except ValueError:
            pass
    
    def set_selected(self, value):
        """Устанавливает выбранное значение"""
        try:
            index = self.values.index(value)
            self.selected_value = value
            self._center_to_button(index)
        except ValueError:
            pass

class ModernTimePicker(BoxLayout):
    """Современный TimePicker с прокруткой"""
    hour = NumericProperty(23)
    minute = NumericProperty(0)
    
    def __init__(self, **kwargs):
        kwargs.setdefault('spacing', -120)  # Умеренное отрицательное значение
        kwargs.setdefault('padding', [0, 0])
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 200
        
        # Часы (0-23)
        self.hours_list = list(range(00, 24))
        self.hours_picker = TimePickerColumn(self.hours_list)
        self.hours_picker.on_selected = self.on_hour_selected
        self.hours_picker.selected_value = self.hour
        
        # Разделитель ":"
        separator = Label(
            text=":",
            font_size="42sp",
            color=(0.7137, 0.5294, 0.5294, 1),
            size_hint_x=None,
            width=0,
            font_name="Gilroy-Medium"
        )
        
        # Минуты (00, 10, 20, 30, 40, 50)
        self.minutes_list = [00, 10, 20, 30, 40, 50]
        self.minutes_picker = TimePickerColumn(self.minutes_list)
        self.minutes_picker.on_selected = self.on_minute_selected
        self.minutes_picker.selected_value = self.minute
        
        # Одинаковая ширина
        self.hours_picker.size_hint_x = 0.5
        self.minutes_picker.size_hint_x = 0.5
        
        self.add_widget(self.hours_picker)
        self.add_widget(separator)
        self.add_widget(self.minutes_picker)
        
        # Устанавливаем начальные значения
        Clock.schedule_once(self._set_initial_values, 0.3)
    
    def on_hour_selected(self, value):
        self.hour = value
        print(f"Час выбран: {value}")
    
    def on_minute_selected(self, value):
        self.minute = value
        print(f"Минута выбрана: {value}")
    
    def _set_initial_values(self, dt):
        """Устанавливает начальные значения"""
        self.hours_picker.set_selected(self.hour)
        self.minutes_picker.set_selected(self.minute)
    
    def on_hour(self, instance, value):
        self.hours_picker.set_selected(value)
    
    def on_minute(self, instance, value):
        self.minutes_picker.set_selected(value)


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

    # Сохраняем данные о воде
        key = datetime.now().strftime("%Y-%m-%d")
        data = daily_store.get(key) if daily_store.exists(key) else {}
        data["water"] = self.water_amount
        daily_store.put(key, **data)

class StepsScreen(Screen):
    selected_steps = NumericProperty(0)

    def go_next(self):
        # если ввели вручную
        if self.ids.steps_input.text.isdigit():
            self.selected_steps = int(self.ids.steps_input.text)

    def choose_range(self, value):
        self.selected_steps = value
        self.ids.steps_input.text = str(value)

    def go_next(self):
        print("Шаги за сегодня:", self.selected_steps)
        # здесь переход дальше

        key = datetime.now().strftime("%Y-%m-%d")

        data = daily_store.get(key) if daily_store.exists(key) else {}
        data["steps"] = self.selected_steps

        daily_store.put(key, **data)

        print("Сохранены шаги:", self.selected_steps)

        App.get_running_app().go_to_sleep()

class SleepScreen(Screen):
    sleep_hour = NumericProperty(23)
    sleep_min = NumericProperty(0)
    wake_hour = NumericProperty(7)
    wake_min = NumericProperty(0)

    def on_enter(self):
        # Синхронизируем значения с TimePicker
        try:
            if hasattr(self.ids, 'sleep_time'):
                self.ids.sleep_time.hour = self.sleep_hour
                self.ids.sleep_time.minute = self.sleep_min
        except:
            pass

        try:
            if hasattr(self.ids, 'wake_time'):
                self.ids.wake_time.hour = self.wake_hour
                self.ids.wake_time.minute = self.wake_min
        except:
            pass

    def go_next(self):
        print("Сон:", f"{self.sleep_hour:02d}:{self.sleep_min:02d}", 
              "-", f"{self.wake_hour:02d}:{self.wake_min:02d}")
        app = App.get_running_app()
        app.go_to_mood()

from kivy.uix.relativelayout import RelativeLayout
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

class ResultWaterScreen(Screen):
    water = NumericProperty(0)
    goal = 1000

    def on_pre_enter(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if daily_store.exists(today):
            self.water = daily_store.get(today).get("water", 0)
            print(f"Загружена вода: {self.water}")  # Для отладки
        else:
            self.water = 0

class ResultStepsScreen(Screen):
    steps = NumericProperty(0)
    goal = 7000

    def on_pre_enter(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if daily_store.exists(today):
            self.steps = daily_store.get(today).get("steps", 0)

class ResultSleepScreen(Screen):
    sleep_hours = NumericProperty(0)

    def on_pre_enter(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if daily_store.exists(today):
            start = daily_store.get(today).get("sleep_start", "")
            end = daily_store.get(today).get("sleep_end", "")

            if start and end:
                self.sleep_hours = self.calc_sleep(start, end)

    def calc_sleep(self, start, end):
        t1 = datetime.strptime(start, "%H:%M")
        t2 = datetime.strptime(end, "%H:%M")

        if t2 <= t1:
            t2 = t2.replace(day=t2.day + 1)

        return round((t2 - t1).seconds / 3600, 1)

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
                    root.go_next()
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

<ModernTimePicker>:
    size_hint_y: None
    height: 200
    spacing: -120
    padding: [0, 0]

<PickerItem>:
    size_hint_y: None
    height: 60
    font_size: '38sp'
    font_name: 'Gilroy-Medium'
    color: (0.7137, 0.5294, 0.5294, 1)
    background_normal: ''
    background_color: (0, 0, 0, 0)

<TimePickerColumn>:
    bar_width: 0
    bar_color: (0, 0, 0, 0)
    bar_inactive_color: (0, 0, 0, 0)

<SleepScreen>:
    FloatLayout:
        # Фон
        Image:
            source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон для сна и эмоций.png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos

        # Заголовок
        Label:
            text: "Сон"
            font_name: "Gilroy-Medium"
            font_size: "36sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": -0.35, "y": 0.41}

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
            color: 0.7137, 0.5294, 0.5294, 1
            font_size: "20sp"
            pos_hint: {"x": 0.07, "y": 0.3}
            text_size: self.width, None

        # Карточка - Время для сна
        BoxLayout:
            id: sleep_card  # Добавлен id для карточки
            orientation: "vertical"
            size_hint: 0.9, None
            height: 280
            pos_hint: {"center_x": 0.5, "top": 0.75}
            padding: [10, 10]
            spacing: 5
            
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.8
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]
                Color:
                    rgba: 0.8, 0.7, 0.7, 0.6
                Line:
                    width: 1.0
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 25)

            Label:
                text: "Время для сна"
                font_name: "Gilroy-Medium"
                font_size: "20sp"
                color: 0.7137, 0.5294, 0.5294, 1
                size_hint_y: None
                height: 40

            ModernTimePicker:
                id: sleep_time
                hour: root.sleep_hour
                minute: root.sleep_min
                size_hint_y: None
                height: 180

            Label:
                text: ""
                size_hint_y: None
                height: 20

        # Карточка - Время пробуждения
        BoxLayout:
            id: wake_card
            orientation: "vertical"
            size_hint: 0.9, None
            height: 280
            pos_hint: {"center_x": 0.5, "top": 0.48}
            padding: [10, 10]
            spacing: 5
            
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.8
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]
                Color:
                    rgba: 0.8, 0.7, 0.7, 0.6
                Line:
                    width: 1.0
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 25)

            Label:
                text: "Время пробуждения"
                font_name: "Gilroy-Medium"
                font_size: "20sp"
                color: 0.7137, 0.5294, 0.5294, 1
                size_hint_y: None
                height: 40

            ModernTimePicker:
                id: wake_time
                hour: root.wake_hour
                minute: root.wake_min
                size_hint_y: None
                height: 180

            Label:
                text: ""
                size_hint_y: None
                height: 20

        #Норма сна
        Label:
            text: "Примерная норма в день\\n8 часов"
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": 0.09, "y": -0.35}  # Сдвинул влево (было 0.41)
            halign: "left"  # Текст по левому краю
            valign: "top"   # Выравнивание по вертикали
            text_size: self.width, None  # Ширина для переноса

        # Кнопка перехода
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
                background_color: (0, 0, 0, 0)
                color: 0.7137, 0.5294, 0.5294, 1
                size: self.parent.size
                pos: self.parent.pos
                on_release: app.go_to_mood()

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
                app.go_to_result_water()
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

#---------------- Блок рекомендаций ----------------
<ResultWaterScreen>:
    name: "result_water"

    FloatLayout:
        canvas.before:
            Rectangle:
                source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон для сна и эмоций.png"
                size: self.size
                pos: self.pos

        Label:
            text: "Результаты"
            font_size: "32sp"
            pos_hint: {"x": -0.3, "y": 0.4}
            color: 0.7,0.5,0.5,1

        Label:
            text: "01.11 пн"
            pos_hint: {"x": -0.4, "y": 0.35}
            color: 0.7,0.5,0.5,1

        # СТАКАН
        FloatLayout:
            size_hint: .5, .5
            pos_hint: {"center_x":0.5, "center_y":0.55}

            Image:
                source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/стакан.png"
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                size_hint: 1,1

            Label:
                text: f"{root.water}/1000 ml"
                pos_hint: {"center_x":0.5, "center_y":0.7}
                color: 0.7,0.5,0.5,1

        # ТЕКСТ
        # Label:
        #     text:
        #         "Вы прекрасно справились с водным балансом!"
        #         if root.water >= root.goal else
        #         "Вам стоит пить больше воды"
        #     size_hint: .8, .2
        #     pos_hint: {"center_x":0.5, "y":0.25}
        #     halign: "center"
        #     text_size: self.size
        #     color: 0.7,0.5,0.5,1

        # КАРТОЧКА
        Label:
            text: "Начните утро со стакана воды"
            size_hint: .8, .15
            pos_hint: {"center_x":0.5, "y":0.1}
            canvas.before:
                Color:
                    rgba: 1,1,1,0.8
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]

        Button:
            text: ">"
            pos_hint: {"right":0.95, "y":0.05}
            size_hint: None,None
            size: 60,60
            on_release: app.root.current = "result_steps"

<ResultStepsScreen>:
    name: "result_steps"

    FloatLayout:
        canvas.before:
            Rectangle:
                source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон для сна и эмоций.png"
                size: self.size
                pos: self.pos

        Label:
            text: "Результаты"
            font_size: "32sp"
            pos_hint: {"x": -0.3, "y": 0.4}
            color: 0.7,0.5,0.5,1

        # КРУГ
        Widget:
            size_hint: None, None
            size: 220, 220
            pos_hint: {"center_x":0.5, "center_y":0.6}

            canvas:
                # серый фон круга
                Color:
                    rgba: 0.9, 0.85, 0.8, 1
                Line:
                    width: 10
                    circle: (self.center_x, self.center_y, 100, 0, 360)

                # ПРОГРЕСС
                Color:
                    rgba: 1, 0.7, 0.4, 1
                Line:
                    width: 10
                    circle: (self.center_x, self.center_y, 100, 0, root.steps / 7000 * 360)

        Label:
            text: f"{root.steps}"
            pos_hint: {"center_x":0.5, "center_y":0.6}
            font_size: "32sp"
            color: 0.7,0.5,0.5,1

        Label:
            text: "шагов"
            pos_hint: {"center_x":0.5, "center_y":0.55}
            color: 0.7,0.5,0.5,1

        # Label:
        #     text:
        #         "Отличная активность!"
        #         if root.steps >= root.goal else
        #         "Попробуйте больше двигаться"
        #     size_hint: .8, .2
        #     pos_hint: {"center_x":0.5, "y":0.25}
        #     halign: "center"
        #     text_size: self.size
        #     color: 0.7,0.5,0.5,1

        Button:
            text: ">"
            pos_hint: {"right":0.95, "y":0.05}
            size_hint: None,None
            size: 60,60
            on_release: app.root.current = "result_sleep"

<ResultSleepScreen>:
    name: "result_sleep"

    FloatLayout:
        canvas.before:
            Rectangle:
                source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон для сна и эмоций.png"
                size: self.size
                pos: self.pos

        Label:
            text: "Результаты"
            font_size: "32sp"
            pos_hint: {"x": -0.3, "y": 0.4}
            color: 0.7,0.5,0.5,1

        Label:
            text: f"{root.sleep_hours} часов"
            font_size: "40sp"
            pos_hint: {"center_x":0.5, "center_y":0.6}
            color: 0.7,0.5,0.5,1

        # Label:
        #     text:
        #         "Отличный сон!"
        #         if root.sleep_hours >= 7 else
        #         "Недостаток сна влияет на здоровье"
        #     size_hint: .8, .2
        #     pos_hint: {"center_x":0.5, "y":0.25}
        #     halign: "center"
        #     text_size: self.size
        #     color: 0.7,0.5,0.5,1

        Button:
            text: ">"
            pos_hint: {"right":0.95, "y":0.05}
            size_hint: None,None
            size: 60,60
            on_release: app.root.current = "main"
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
        sm.add_widget(ResultWaterScreen(name="result_water"))
        sm.add_widget(ResultStepsScreen(name="result_steps"))
        sm.add_widget(ResultSleepScreen(name="result_sleep"))

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
    def go_to_result_water(self):
        self.root.current = "result_water"
    def go_to_result_steps(self):
        self.root.current = "result_steps"
    def go_to_result_sleep(self):
        self.root.current = "result_sleep"

if __name__ == '__main__':
    MainApp().run()

#"Если вы видите это сообщение, значит вы увидели изменение"
