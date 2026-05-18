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

# ===== ГРАФИКИ ДЛЯ СТАТИСТИКИ =====
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from math import*

Window.size = (390, 844)


#Регистрация шрифтов
LabelBase.register(name="Gilroy-MediumItalic", fn_regular="Gilroy-MediumItalic.otf")
LabelBase.register(name="Gilroy-Medium", fn_regular="Gilroy-Medium.otf")
LabelBase.register(name="Gilroy-RegularItalic", fn_regular="Gilroy-RegularItalic.otf")
LabelBase.register(name="Gilroy-Regular", fn_regular="Gilroy-Regular.otf")
LabelBase.register(name="Gilroy-SemiBold", fn_regular="Gilroy-SemiBold.otf")

store = JsonStore("user.json") # Для имени пользователя
daily_store = JsonStore("daily.json")# Для ежедневных данных

class MiniChart(Widget):
    """Мини-график для отображения данных за последние 7 дней"""
    data = ListProperty([])  # Список значений для отображения
    max_value = NumericProperty(100)  # Максимальное значение для нормализации
    bar_color = ListProperty([0.9, 0.7, 0.6, 1])  # Цвет столбцов
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(data=self._update_chart, 
                  max_value=self._update_chart,
                  pos=self._update_chart, 
                  size=self._update_chart)
        Clock.schedule_once(self._update_chart, 0.1)
    
    def _update_chart(self, *args):
        with self.canvas:
            self.canvas.clear()
            
            if not self.data or self.width <= 0 or self.height <= 0:
                return
            
            bar_count = len(self.data)
            spacing = 3
            available_width = self.width - spacing * (bar_count - 1)
            bar_width = max(2, available_width / bar_count)  # минимум 2px
            
            max_val = max(self.data) if self.data else 1
            if max_val <= 0:
                max_val = 1
            
            for i, value in enumerate(self.data):
                ratio = max(0.05, value / max_val)
                bar_height = ratio * max(10, self.height - 8)
                
                x = self.x + i * (bar_width + spacing)
                y = self.y + 4
                
                intensity = value / max_val
                Color(
                    self.bar_color[0] * (0.7 + 0.3 * intensity),
                    self.bar_color[1] * (0.7 + 0.3 * intensity),
                    self.bar_color[2] * (0.7 + 0.3 * intensity),
                    self.bar_color[3] * (0.6 + 0.4 * intensity)
                )
                
                Rectangle(pos=(x, y), size=(bar_width, bar_height))

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

    # Добавьте эти свойства для привязки к SleepScreen
    sleep_hour = NumericProperty(23)
    sleep_min = NumericProperty(0)
    
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
        self.parent_hour = value  # Обновляем родительское свойство
        print(f"Час выбран: {value}")
    
    def on_minute_selected(self, value):
        self.minute = value
        self.parent_minute = value  # Обновляем родительское свойство
        print(f"Минута выбрана: {value}")

    def _auto_save(self):
    # Автоматически сохраняем при изменении времени
        app = App.get_running_app()
        if app.root.current == "sleep":
            sleep_screen = app.root.get_screen("sleep")
            sleep_screen.sleep_hour = self.hour
            sleep_screen.sleep_min = self.minute
            # Здесь можно сразу сохранять
    
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
        self.load_day_data()
    
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
        print("=== НАЧАЛО ЗАГРУЗКИ ===")
        
        # 1. Получаем ключ (дату)
        app = App.get_running_app()
        key = app.selected_date
        print(f"Ключ (дата): {key}")
        
        # 2. Проверяем существование данных
        if daily_store.exists(key):
            data = daily_store.get(key)
            print(f"Данные из хранилища: {data}")
            
            # 3. Вытаскиваем значения
            water_value = data.get("water", 0)
            steps_value = data.get("steps", 0)
            
            print(f"Значение воды: {water_value}")
            print(f"Значение шагов: {steps_value}")
            
            # 4. Проверяем, существуют ли ID
            if hasattr(self.ids, 'water_value'):
                self.ids.water_value.text = f"{water_value} мл"
                print(f"water_value text установлен: {self.ids.water_value.text}")
            else:
                print("ОШИБКА: нет water_value в ids!")
                
            if hasattr(self.ids, 'steps_value'):
                self.ids.steps_value.text = f"{steps_value} шагов"
                print(f"steps_value text установлен: {self.ids.steps_value.text}")
            else:
                print("ОШИБКА: нет steps_value в ids!")
        else:
            print(f"НЕТ ДАННЫХ для ключа {key}")
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
        key = App.get_running_app().selected_date
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

        key = App.get_running_app().selected_date

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
        # Загружаем сохраненные значения для текущей даты
        app = App.get_running_app()
        key = app.selected_date

        self.ids.sleep_time.bind(hour=self.on_sleep_time_changed)
        self.ids.sleep_time.bind(minute=self.on_sleep_time_changed)

        self.ids.wake_time.bind(hour=self.on_wake_time_changed)
        self.ids.wake_time.bind(minute=self.on_wake_time_changed)
        
        if daily_store.exists(key):
            data = daily_store.get(key)
            # Загружаем сохраненное время сна, если есть
            if "sleep_start" in data:
                start = data["sleep_start"]
                self.sleep_hour = int(start.split(":")[0])
                self.sleep_min = int(start.split(":")[1])
            if "sleep_end" in data:
                end = data["sleep_end"]
                self.wake_hour = int(end.split(":")[0])
                self.wake_min = int(end.split(":")[1])

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

    def on_sleep_hour(self, instance, value):
        """При изменении часа сна обновляем TimePicker"""
        if hasattr(self.ids, 'sleep_time'):
            self.ids.sleep_time.hour = value
    
    def on_sleep_min(self, instance, value):
        """При изменении минуты сна обновляем TimePicker"""
        if hasattr(self.ids, 'sleep_time'):
            self.ids.sleep_time.minute = value
    
    def on_wake_hour(self, instance, value):
        """При изменении часа пробуждения обновляем TimePicker"""
        if hasattr(self.ids, 'wake_time'):
            self.ids.wake_time.hour = value
    
    def on_wake_min(self, instance, value):
        """При изменении минуты пробуждения обновляем TimePicker"""
        if hasattr(self.ids, 'wake_time'):
            self.ids.wake_time.minute = value

        # Добавьте для отладки
        app = App.get_running_app()
        print(f"SleepScreen: текущая selected_date = {app.selected_date}")

    def go_next(self):
        print("Сон:", f"{self.sleep_hour:02d}:{self.sleep_min:02d}", 
              "-", f"{self.wake_hour:02d}:{self.wake_min:02d}")
        app = App.get_running_app()
        key = app.selected_date
    
        # Проверяем, что значения не пустые
        print(f"sleep_hour = {self.sleep_hour}, sleep_min = {self.sleep_min}")
        print(f"wake_hour = {self.wake_hour}, wake_min = {self.wake_min}")
    
        # Сохраняем данные
        data = daily_store.get(key) if daily_store.exists(key) else {}
        print(f"Данные до сохранения: {data}")
    
        data["sleep_start"] = f"{self.sleep_hour:02d}:{self.sleep_min:02d}"
        data["sleep_end"] = f"{self.wake_hour:02d}:{self.wake_min:02d}"
    
        daily_store.put(key, **data)
    
        # Проверяем, что сохранилось
        saved_data = daily_store.get(key)
        print(f"Данные после сохранения: {saved_data}")
        print(f"sleep_start = {saved_data.get('sleep_start')}")
        print(f"sleep_end = {saved_data.get('sleep_end')}")
    
        app.go_to_mood()

    def on_sleep_time_changed(self, instance, value):
        # Обновляем свойства при изменении времени
        self.sleep_hour = self.ids.sleep_time.hour
        self.sleep_min = self.ids.sleep_time.minute
        print(f"Время сна обновлено: {self.sleep_hour}:{self.sleep_min}")

    def on_wake_time_changed(self, instance, value):
        self.wake_hour = self.ids.wake_time.hour
        self.wake_min = self.ids.wake_time.minute
        print(f"Время пробуждения обновлено: {self.wake_hour}:{self.wake_min}")

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image


class EmotionCarousel(RelativeLayout):
    index = NumericProperty(0)

    emotions = ListProperty([
        ("Ярость", "Ярость(2).png"),
        ("Раздражение", "Раздражение(1).png"),
        ("Безразличие", "Безразличие(1).png"),
        ("Счастье", "Счастье(1).png"),
        ("Спокойствие", "Спокойствие(1).png"),
        ("Смущение", "Смущение(1).png"),
        ("Грусть", "Грусть(1).png"),
    ])

    emotion_name = StringProperty("")
    emotion_image = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_emotion()

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

    def save_emotion(self):
        name, img = self.emotions[self.index]

        key = App.get_running_app().selected_date

        data = daily_store.get(key) if daily_store.exists(key) else {}
        data["mood"] = name
        data["mood_image"] = img   # ← сохраняем картинку тоже!

        daily_store.put(key, **data)

        print("Сохранено настроение:", name)
        
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
    sleep_start_time = StringProperty("00:00")  
    sleep_end_time = StringProperty("00:00")   

    def on_pre_enter(self):
        app = App.get_running_app()
        key = app.selected_date
    
        if daily_store.exists(key):
            data = daily_store.get(key)
        
            start = data.get("sleep_start", "")
            end = data.get("sleep_end", "")
        
            if start and end:
                self.sleep_hours = self.calc_sleep(start, end)
                self.sleep_start_time = start  
                self.sleep_end_time = end      
                print(f"Рассчитано часов сна: {self.sleep_hours}")
            else:
                self.sleep_hours = 0
                self.sleep_start_time = "00:00"
                self.sleep_end_time = "00:00"
        else:
            self.sleep_hours = 0
            self.sleep_start_time = "00:00"
            self.sleep_end_time = "00:00"

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


class ResultMoodScreen(Screen):
    mood = StringProperty("")
    mood_image = StringProperty("")
    mood_text = StringProperty("")

    def on_pre_enter(self):
        key = datetime.now().strftime("%Y-%m-%d")

        if daily_store.exists(key):
            data = daily_store.get(key)

            self.mood = data.get("mood", "Не задано")
            self.mood_image = data.get("mood_image", "")

        else:
            self.mood = "Не задано"
            self.mood_image = ""

        self.generate_text()

    def generate_text(self):
        if self.mood in ["Ярость", "Раздражение"]:
            self.mood_text = "Похоже, вы испытываете напряжение. Попробуйте отдохнуть и снизить нагрузку."
    
        elif self.mood in ["Грусть", "Безразличие"]:
            self.mood_text = "Сегодня стоит уделить внимание себе — прогулка или разговор могут помочь."

        elif self.mood in ["Смущение"]:
            self.mood_text = "Небольшая неуверенность — это нормально. Дайте себе время."

        elif self.mood in ["Спокойствие"]:
            self.mood_text = "Вы в стабильном состоянии. Отличный момент для продуктивного дня."

        elif self.mood in ["Счастье"]:
            self.mood_text = "Вы в хорошем эмоциональном состоянии. Так держать"

        else:
            self.mood_text = "Настроение не определено"

class FinalResultScreen(Screen):
    date = StringProperty("")
    water = NumericProperty(0)
    steps = NumericProperty(0)
    sleep_hours = NumericProperty(0)
    mood = StringProperty("")
    mood_image = StringProperty("")

    recommendation = StringProperty("")

    def on_pre_enter(self):
        key = App.get_running_app().selected_date
        self.date = key

        #значения по умолчанию
        self.water = 0
        self.steps = 0
        self.sleep_hours = 0
        self.mood = "Не задано"
        self.mood_image = ""

        if daily_store.exists(key):
            data = daily_store.get(key)

            self.water = data.get("water", 0)
            self.steps = data.get("steps", 0)

            sleep_start = data.get("sleep_start", "")
            sleep_end = data.get("sleep_end", "")

            if sleep_start and sleep_end:
                self.sleep_hours = self.calc_sleep(sleep_start, sleep_end)

            self.mood = data.get("mood", "РќРµ Р·Р°РґР°РЅРѕ")
            self.mood_image = data.get("mood_image", "")

        self.generate_recommendation()

    def calc_sleep(self, start, end):
        t0 = datetime.strptime(start, "%H:%M")
        t1 = datetime.strptime(end, "%H:%M")

        start_dt = datetime(2000,1,1,t0.hour,t0.minute)
        end_dt = datetime(2000,1,1,t1.hour,t1.minute)

        if end_dt <= start_dt:
            end_dt = end_dt.replace(day=2)

        hours = (end_dt - start_dt).total_seconds() / 3600
        return round(hours, 1)

    def generate_recommendation(self):
        text = ""

        #вода
        if self.water < 1000:
            text += "Пей больше воды\n"

        #шаги
        if self.steps < 7000:
            text += "Добавь активности\n"

        #сон
        if self.sleep_hours < 7:
            text += "Недостаточно сна\n"

        #настроение
        if self.mood in ["Ярость", "Раздражение"]:
            text += "Попробуй снизить стресс\n"
        elif self.mood in ["Грусть", "Безразличие"]:
            text += "Удели время себе\n"
        elif self.mood == "Счастье":
            text += "Отличное состояние\n"

        if text == "":
            text = "Ты в отличном состоянии! ПРодолжай в том же духе"

        self.recommendation = text

class SummaryScreen(Screen):
    steps = NumericProperty(0)
    water = NumericProperty(0)
    sleep_hours = NumericProperty(0)
    sleep_minutes = NumericProperty(0)
    mood = StringProperty("")
    mood_image = StringProperty("")

    def on_pre_enter(self):
        key = App.get_running_app().selected_date

        if daily_store.exists(key):
            data = daily_store.get(key)

            self.steps = data.get("steps", 0)
            self.water = data.get("water", 0)

            start = data.get("sleep_start", "")
            end = data.get("sleep_end", "")

            if start and end:
                hours = self.calc_sleep(start, end)
                self.sleep_hours = int(hours)
                self.sleep_minutes = int((hours % 1) * 60)

            self.mood = data.get("mood", "Не задано")
            self.mood_image = data.get("mood_image", "")

        # ✅ Отложенная загрузка графиков
        Clock.schedule_once(lambda dt: self.load_chart_data(), 0.25)
    
    def load_chart_data(self):
        """Загружает данные для мини-графиков"""
        app = App.get_running_app()
        
        charts_data = {
            'steps': [],
            'water': [],
            'sleep': []
        }
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")
            
            if daily_store.exists(date_key):
                data = daily_store.get(date_key)
                charts_data['steps'].append(data.get('steps', 0))
                charts_data['water'].append(data.get('water', 0))
                
                sleep_start = data.get('sleep_start', '')
                sleep_end = data.get('sleep_end', '')
                if sleep_start and sleep_end:
                    hours = self.calc_sleep(sleep_start, sleep_end)
                    charts_data['sleep'].append(hours)
                else:
                    charts_data['sleep'].append(0)
            else:
                charts_data['steps'].append(0)
                charts_data['water'].append(0)
                charts_data['sleep'].append(0)
        
        if hasattr(self.ids, 'steps_chart'):
            self.ids.steps_chart.data = charts_data['steps']
            self.ids.steps_chart.max_value = 10000
        
        if hasattr(self.ids, 'water_chart'):
            self.ids.water_chart.data = charts_data['water']
            self.ids.water_chart.max_value = 1000
        
        if hasattr(self.ids, 'sleep_chart'):
            self.ids.sleep_chart.data = charts_data['sleep']
            self.ids.sleep_chart.max_value = 12

    def calc_sleep(self, start, end):
        from datetime import datetime
        t0 = datetime.strptime(start, "%H:%M")
        t1 = datetime.strptime(end, "%H:%M")

        if t1 <= t0:
            t1 = t1.replace(day=2)

        return (t1 - t0).total_seconds() / 3600

# ===== Добавьте класс ActivityScreen =====
class ActivityScreen(Screen):
    steps = NumericProperty(0)
    goal = NumericProperty(7000)
    percentage = NumericProperty(0)
    
    # Данные для графика (день/неделя/месяц)
    daily_steps = ListProperty([])
    weekly_steps = ListProperty([])
    monthly_steps = ListProperty([])
    
    current_view = StringProperty("День")  # День / Неделя / Месяц

    # ✅ Новые свойства для позиции точки на круге
    dot_pos_x = NumericProperty(0)
    dot_pos_y = NumericProperty(0)
    
    def on_pre_enter(self):
        # Загружаем текущие шаги
        key = App.get_running_app().selected_date
        if daily_store.exists(key):
            data = daily_store.get(key)
            self.steps = data.get("steps", 0)
        else:
            self.steps = 0
        self.update_dot_position()
    
    def on_percentage(self, instance, value):
        """Обновляем позицию точки при изменении процента"""
        self.update_dot_position()
    
    def update_dot_position(self):
        """Вычисляем координаты точки на окружности"""
        # Центр круга (в координатах RelativeLayout размером 250x250)
        center_x, center_y = 125, 125
        radius = 100
        
        # Угол: 90° = верх, отсчёт против часовой стрелки
        angle = 90 - self.percentage * 3.6
        angle_rad = radians(angle)
        
        # Координаты точки
        self.dot_pos_x = center_x + radius * cos(angle_rad)
        self.dot_pos_y = center_y + radius * sin(angle_rad)
        
        # Считаем процент
        self.percentage = min(100, round(self.steps / self.goal * 100))
        
        # Загружаем данные для графиков
        self.load_chart_data()
    
    def load_chart_data(self):
        """Загружаем данные для всех трех режимов"""
        # День - почасовые данные (заглушка - равномерное распределение)
        self.daily_steps = [0, 0, 0, 0, self.steps]  # Упрощенно
        
        # Неделя - последние 7 дней
        week_data = []
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")
            if daily_store.exists(date_key):
                week_data.append(daily_store.get(date_key).get("steps", 0))
            else:
                week_data.append(0)
        self.weekly_steps = week_data
        
        # Месяц - последние 30 дней (агрегировано по неделям для простоты)
        month_data = []
        for i in range(3, -1, -1):
            week_sum = 0
            for j in range(7):
                date = datetime.now() - timedelta(days=i*7 + j)
                date_key = date.strftime("%Y-%m-%d")
                if daily_store.exists(date_key):
                    week_sum += daily_store.get(date_key).get("steps", 0)
            month_data.append(week_sum)
        self.monthly_steps = month_data
    
    def set_view(self, view):
        """Переключение между День/Неделя/Месяц"""
        self.current_view = view

class ActivityChart(Widget):
    data = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(data=self._draw_chart, pos=self._draw_chart, size=self._draw_chart)
        Clock.schedule_once(self._draw_chart, 0.1)
    
    def _draw_chart(self, *args):
        with self.canvas:
            self.canvas.clear()
            
            if not self.data or self.width <= 0:
                return
            
            bar_count = len(self.data)
            max_val = max(self.data) if self.data else 1
            if max_val == 0:
                max_val = 1
            
            # Линия цели (7000 шагов)
            goal_y = self.y + self.height * 0.8
            Color(0.9, 0.85, 0.8, 0.5)
            #Line(points=[self.x, goal_y, self.right, goal_y], width=1)
            
            # Рисуем столбцы
            spacing = 4
            bar_width = (self.width - spacing * (bar_count + 1)) / bar_count
            
            for i, value in enumerate(self.data):
                ratio = min(1.0, value / max_val)
                bar_height = ratio * self.height * 0.85
                
                x = self.x + spacing + i * (bar_width + spacing)
                y = self.y + 5
                
                # Градиент: последние дни ярче
                time_factor = 0.3 + 0.7 * (i / max(1, bar_count - 1))
                value_intensity = value / max_val if max_val > 0 else 0.5
                
                Color(
                    1.0 * (0.6 + 0.4 * value_intensity),
                    0.7 * (0.6 + 0.4 * value_intensity),
                    0.4 * (0.6 + 0.4 * value_intensity),
                    0.4 + 0.6 * time_factor
                )
                
                Rectangle(pos=(x, y), size=(bar_width, bar_height))

class SleepDetailScreen(Screen):
    sleep_hours = NumericProperty(0)
    sleep_minutes = NumericProperty(0)
    goal = NumericProperty(8)
    percentage = NumericProperty(0)
    
    sleep_start_time = StringProperty("00:00")
    sleep_end_time = StringProperty("00:00")
    
    # Данные для графика
    daily_sleep = ListProperty([])
    weekly_sleep = ListProperty([])
    monthly_sleep = ListProperty([])
    
    current_view = StringProperty("День")

    def on_pre_enter(self):
        # Загружаем данные
        key = App.get_running_app().selected_date
        if daily_store.exists(key):
            data = daily_store.get(key)
            start = data.get("sleep_start", "")
            end = data.get("sleep_end", "")
            
            if start and end:
                total_hours = self.calc_sleep(start, end)
                self.sleep_hours = int(total_hours)
                self.sleep_minutes = int((total_hours % 1) * 60)
                self.sleep_start_time = start
                self.sleep_end_time = end
                
                # Считаем процент от цели
                self.percentage = min(100, round(total_hours / self.goal * 100))
        
        self.load_chart_data()
    
    def load_chart_data(self):
        """Загружаем данные для графиков"""
        # День - упрощенно
        self.daily_sleep = [self.sleep_hours + self.sleep_minutes/60]
        
        # Неделя - последние 7 дней
        week_data = []
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")
            if daily_store.exists(date_key):
                data = daily_store.get(date_key)
                start = data.get("sleep_start", "")
                end = data.get("sleep_end", "")
                if start and end:
                    hours = self.calc_sleep(start, end)
                    week_data.append(hours)
                else:
                    week_data.append(0)
            else:
                week_data.append(0)
        self.weekly_sleep = week_data

        # Месяц - последние 4 недели
        month_data = []
        for i in range(3, -1, -1):
            week_sum = 0
            for j in range(7):
                date = datetime.now() - timedelta(days=i*7 + j)
                date_key = date.strftime("%Y-%m-%d")
                if daily_store.exists(date_key):
                    data = daily_store.get(date_key)
                    start = data.get("sleep_start", "")
                    end = data.get("sleep_end", "")
                    if start and end:
                        week_sum += self.calc_sleep(start, end)
            month_data.append(week_sum / 7)  # Среднее за неделю
        self.monthly_sleep = month_data
    
    def calc_sleep(self, start, end):
        t1 = datetime.strptime(start, "%H:%M")
        t2 = datetime.strptime(end, "%H:%M")
        if t2 <= t1:
            t2 = t2.replace(day=t2.day + 1)
        return round((t2 - t1).seconds / 3600, 2)
    
    def set_view(self, view):
        self.current_view = view


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
            source: "фон (1).png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos

        # ЛОГОТИП СВЕРХУ СПРАВА
        Image:
            source: "цветочек.png"
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
            source: "фон (1).png"
            allow_stretch: True
            keep_ratio: False
            size: self.parent.size
            pos: self.parent.pos

        Image:
            source: "цветочек.png"
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
            source: "фон2.png"
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
            source: "фон (1).png"
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
                source: "вода.png"
                size_hint_x: 0.18
            BoxLayout:
                orientation: "vertical"
                Label:
                    id: water_value
                    text: "0 мл"
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
                source: "шаги.png"
                size_hint_x: 0.18
            BoxLayout:
                orientation: "vertical"
                Label:
                    id:steps_value
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
                    source: "home.png"
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
                    source: "Статистика.png"
                    allow_stretch: True
                    keep_ratio: True
                    size: self.parent.size
                    pos: self.parent.pos
                
                Button:
                    background_normal: ""
                    background_color: (0, 0, 0, 0)
                    size: self.parent.size
                    pos: self.parent.pos
                    on_release: app.go_to_summary()

            # Аналогично для Результатов
            RelativeLayout:
                size_hint: None, None
                size: 45, 45
                pos_hint: {"center_x": 0.5, "center_y": 0.1}
                
                Image:
                    source: "Результаты.png"
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
                background_normal: "Начать.png"
                background_down: "Начать.png"
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
            source: "фон2.png"
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
            source: "фон для опроса.png"
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
            source: "стакан.png"
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
                background_normal: "Начать (2).png"
                background_down: "Начать (2).png"
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
            source: "фон для опроса.png"
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
            source: "фон для сна и эмоций.png"
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
                on_release: 
                    root.go_next()
                    app.go_to_mood()

<EmotionCarousel>:
    id: carousel
    canvas.before:
        Color:
            rgba: 0,0,0,0
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
            source: "фон для сна и эмоций.png"
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
            pos_hint: {"center_x": 0.5, "y": 0.3}

        EmotionCarousel:
            id: carousel
            size_hint: 1, 0.55
            pos_hint: {"center_x":0.5, "center_y":0.48}

            # Картинка эмоции
            Image:
                id: emoji_img
                source: carousel.emotion_image
                size_hint: None, None
                size: 200, 200
                pos_hint: {"center_x":0.5, "center_y":0.6}

            # Название эмоции
            Label:
                text: carousel.emotion_name
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
                size_hint: 0.7, 0.14
                pos_hint: {"center_x":0.5, "center_y":-0.02}
                font_name: "Gilroy-SemiBold"
                font_size: "18sp"
                color: 0.7137, 0.5294, 0.5294, 1
                background_normal: ""
                background_color: (0, 0, 0, 0)  # Белый фон
                border: (0, 0, 0, 0)

                on_release:
                    carousel.save_emotion()
                    app.go_to_share_2()

                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1  # Белый цвет
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [self.height / 2]  # Полукруглая форма

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
            source: "фон2.png"
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
                source: "фон для сна и эмоций.png"
                size: self.size
                pos: self.pos

        Label:
            text: "Результаты"
            font_name: "Gilroy-Medium"
            font_size: "32sp"
            pos_hint: {"x": -0.24, "y": 0.4}
            color: 0.7,0.5,0.5,1

        Label:
            text: app.selected_date
            font_name: "Gilroy-Medium"
            pos_hint: {"x": -0.36, "y": 0.36}
            color: 0.7,0.5,0.5,1

        # СТАКАН
        FloatLayout:
            size_hint: .5, .5
            pos_hint: {"center_x":0.5, "center_y":0.55}

            Image:
                source: "стакан.png"
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                size_hint: 1,1

            Label:
                text: f"{root.water}/1000 ml"
                font_name: "Gilroy-Medium"
                pos_hint: {"center_x":0.5, "center_y":0.75}
                color: 0.7,0.5,0.5,1
                font_size: "22sp"

        Label:
            text: "Вы прекрасно справились с водным балансом!"
            halign: "left"
            font_name: "Gilroy-Medium"
            font_size: "18sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": 0.062, "y": -0.15}
            text_size: self.width, None

        # КАРТОЧКА
        Label:
            text: "Начните утро со стакана воды - это простой\\nспособ задать тон дню."
            font_name: "Gilroy-Medium"
            size_hint: .8, .15
            pos_hint: {"center_x":0.5, "y":0.15}
            color: 0.7,0.5,0.5,1
            canvas.before:
                Color:
                    rgba: 1,1,1,0.8
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]

        # Круглый белый контейнер для кнопки перехода
        BoxLayout:
            size_hint: None, None
            width: 70
            height: 70
            pos_hint: {"right": 0.95, "y": 0.03}
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
                on_release: app.root.current = "result_steps"
        
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
                    source: "home.png"
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
                    source: "Статистика.png"
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
                    source: "Результаты.png"
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


<ResultStepsScreen>:
    name: "result_steps"

    FloatLayout:
        canvas.before:
            Rectangle:
                source: "фон для сна и эмоций.png"
                size: self.size
                pos: self.pos

        Label:
            text: "Результаты"
            font_name: "Gilroy-Medium"
            font_size: "32sp"
            pos_hint: {"x": -0.25, "y": 0.4}
            color: 0.7,0.5,0.5,1
        
        Label:
            text: app.selected_date
            font_name: "Gilroy-Medium"
            pos_hint: {"x": -0.36, "y": 0.36}
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
                    rgba: 1, 0.8, 0.6, 1
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
        
        # Белый контейнер-карточка с первым текстом внутри
        RelativeLayout:
            size_hint: 0.9, None
            height: 150
            pos_hint: {"center_x": 0.475, "y": 0.07}
                
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.9
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]
            
        # Текст 1 (внутри контейнера)
        Label:
            text: "Попробуйте завтра: выйти на одну остановку раньше."
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.7, 0.5, 0.5, 1
            size_hint_x: 0.9
            pos_hint: {"center_x": 0.5, "top": 0.7}
            halign: "center"
            text_size: self.width, None

        # Текст 2 (снаружи контейнера, поверх него)
        Label:
            text: "Сегодня у вас был не очень активный день."
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.7, 0.5, 0.5, 1
            size_hint_x: 0.9
            pos_hint: {"center_x": 0.49, "top": 0.9}  # Выше контейнера
            halign: "center"
            text_size: self.width, None
        
        # Круглый белый контейнер для кнопки перехода
        BoxLayout:
            size_hint: None, None
            width: 70
            height: 70
            pos_hint: {"right": 0.95, "y": 0.03}
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
                on_release: app.root.current = "result_sleep"

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
                    source: "home.png"
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
                    source: "Статистика.png"
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
                    source: "Результаты.png"
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

<ResultSleepScreen>:
    name: "result_sleep"

    FloatLayout:
        canvas.before:
            Rectangle:
                source: "фон для сна и эмоций.png"
                size: self.size
                pos: self.pos

        Label:
            text: "Результаты"
            font_size: "32sp"
            pos_hint: {"x": -0.25, "y": 0.4}
            color: 0.7,0.5,0.5,1
        
        # Дата
        Label:
            text: app.selected_date
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.7,0.5,0.5,1
            pos_hint: {"x": -0.36, "y": 0.36}

        Label:
            text: f"{root.sleep_hours} часов"
            font_size: "14sp"
            pos_hint: {"center_x":0.5, "center_y":0.6}
            color: 0.7,0.5,0.5,1
        
        Label:
            text: root.sleep_start_time
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.7, 0.5, 0.5, 1
            halign: "left"
            size_hint: None, None
            size: 60, 30
            pos_hint: {"center_x":0.16, "center_y":0.6}
        
        Label:
            text: root.sleep_end_time
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.7, 0.5, 0.5, 1
            halign: "right"
            size_hint: None, None
            size: 60, 30
            pos_hint: {"center_x":0.84, "center_y":0.6}

        # Текст рекомендации
        Label:
            text: "Ваш сон был короче рекомендованной\\nнормы. Недостаток отдыха может влиять\\nна настроение и концентрацию."
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.7, 0.5, 0.5, 1
            pos_hint: {"center_x": 0.5, "center_y": 0.45}
            halign: "center"
            text_size: self.width - 40, None
        
        # Шкала сна
        Image:
            source: "картинка для ResultSleepScreen.png"
            size_hint: 0.8, 0.58
            pos_hint: {"center_x": 0.5, "center_y": 0.65}
        
        # Белый блок с советом
        BoxLayout:
            orientation: "vertical"
            size_hint: 0.9, None
            height: 150
            pos_hint: {"center_x": 0.5, "y": 0.12}
            padding: [20, 15]
            spacing: 5
            
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.9
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]
            
            Label:
                text: "Сегодня постарайтесь лечь спать на 30 минут\\nраньше. Создайте ритуал: проветрите\\nкомнату, отложите гаджеты и почитайте книгу."
                font_name: "Gilroy-Medium"
                font_size: "15sp"
                color: 0.7, 0.5, 0.5, 1
                halign: "left"
                valign: "top"
                text_size: self.width, self.height

        # Круглый белый контейнер для кнопки перехода
        BoxLayout:
            size_hint: None, None
            width: 70
            height: 70
            pos_hint: {"right": 0.95, "y": 0.03}
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
                on_release: app.root.current = "result_mood"

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
                    source: "home.png"
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
                    source: "Статистика.png"
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
                    source: "Результаты.png"
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


<ResultMoodScreen>:
    name: "result_mood"

    FloatLayout:
        canvas.before:
            Rectangle:
                source: "фон для сна и эмоций.png"
                size: self.size
                pos: self.pos

        Label:
            text: "Результаты"
            font_size: "32sp"
            color: 0.7,0.5,0.5,1
            pos_hint: {"x": -0.24, "y": 0.42}
        
        Label:
            text: app.selected_date
            font_name: "Gilroy-Medium"
            pos_hint: {"x": -0.36, "y": 0.36}
            color: 0.7,0.5,0.5,1

        Image:
            source: root.mood_image
            size_hint: None, None
            size: 200, 200
            pos_hint: {"center_x": 0.5, "center_y": 0.6}

        # КАРТОЧКА
        BoxLayout:
            orientation: "vertical"
            size_hint: .85, .2
            pos_hint: {"center_x":0.5, "center_y":0.25}

            canvas.before:
                Color:
                    rgba: 1,1,1,0.8
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]

            Label:
                text:root.mood_text
                font_size: "16sp"
                halign: "center"
                text_size: self.width-40, None
                color: 0.7,0.5,0.5,1

        # КНОПКА ВПЕРЕД
        Button:
            text: ">"
            size_hint: None,None
            size: 70,70
            pos_hint: {"right":0.95, "y":0.03}
            background_normal: ""
            background_color: 0,0,0,0
            color: 0.7,0.5,0.5,1

            on_release:
                app.root.current = "final_result"

            canvas.before:
                Color:
                    rgba: 1,1,1,1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [self.height]
        
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
                    source: "home.png"
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
                    source: "Статистика.png"
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
                    source: "Результаты.png"
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

<FinalResultScreen>:
    name: "final_result"

    FloatLayout:
        canvas.before:
            Rectangle:
                source: "C:/Users/vbzai/OneDrive/Desktop/Sensa_project/фон для сна и эмоций.png"
                size: self.size
                pos: self.pos

        # ДАТА
        Label:
            text: root.date
            font_size: "16sp"
            color: 0.7,0.5,0.5,1
            pos_hint: {"center_x":0.5, "top":0.95}

        # ЗАГОЛОВОК
        Label:
            text: "Итог за день"
            font_size: "32sp"
            color: 0.7,0.5,0.5,1
            pos_hint: {"x": -0.3, "y": 0.42}

        # КАРТОЧКА
        BoxLayout:
            orientation: "vertical"
            size_hint: .9, .6
            pos_hint: {"center_x":0.5, "center_y":0.5}
            spacing: 10
            padding: 20

            canvas.before:
                Color:
                    rgba: 1,1,1,0.85
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]

            # ВОДА
            Label:
                text: f"Вода: {root.water} мл"
                color: 0.7,0.5,0.5,1

            # ШАГИ
            Label:
                text: f"Шаги: {root.steps}"
                color: 0.7,0.5,0.5,1

            # СОН
            Label:
                text: f"Сон: {root.sleep_hours} ч"
                color: 0.7,0.5,0.5,1

            # НАСТРОЕНИЕ
            Label:
                text: f"Настроение: {root.mood}"
                color: 0.7,0.5,0.5,1

            # КАРТИНКА НАСТРОЕНИЯ
            Image:
                source: root.mood_image
                size_hint: None, None
                size: 120,120
                pos_hint: {"center_x":0.5}

            # РЕКОМЕНДАЦИИ
            Label:
                text: root.recommendation
                halign: "center"
                text_size: self.width-40, None
                color: 0.7,0.5,0.5,1

        # КНОПКА НАЗАД
        Button:
            text: "На главную"
            size_hint: 0.6, 0.08
            pos_hint: {"center_x":0.5, "y":0.05}
            background_normal: ""
            background_color: 1,1,1,1
            color: 0.7,0.5,0.5,1
            on_release: app.go_to_home()

            canvas.before:
                Color:
                    rgba: 1,1,1,1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [self.height/2]

<SummaryScreen>:
    name: "summary"

    FloatLayout:
        canvas.before:
            Rectangle:
                source: "фон для сна и эмоций.png"
                size: self.size
                pos: self.pos

        # Заголовок
        Label:
            text: "Сводка"
            font_name: "Gilroy-Medium"
            font_size: "36sp"
            color: 0.7,0.5,0.5,1
            pos_hint: {"x": -0.3, "y": 0.42}

        # ===== АКТИВНОСТЬ (только шаги) =====
        Button:
            size_hint: .9, .12
            pos_hint: {"center_x":0.5, "top":0.75}
            background_normal: ""
            background_color: 0,0,0,0
            on_release: app.go_to_activity()
            
            canvas.before:
                Color:
                    rgba: 1,1,1,1 
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]
                Color:
                    rgba: 0.7137, 0.5294, 0.5294, 0.8
                Line:
                    width: 1.0
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 20)
            
            RelativeLayout:
                # Текст "Активность" вверху слева
                Label:
                    text: "Активность"
                    font_name: "Gilroy-Medium"
                    font_size: "15sp"
                    color: 0.7,0.5,0.5,1
                    size_hint: None, None
                    size: self.texture_size
                    pos_hint: {"x": 0.39, "top": 7.85}
                
                # Значение шагов внизу слева
                Label:
                    text: "[font=Gilroy-SemiBold]{} шагов[/font]".format(root.steps)
                    markup: True
                    font_size: "24sp"
                    color: 0.7,0.5,0.5,1
                    size_hint: None, None
                    size: self.texture_size
                    pos_hint: {"x": 0.39, "top": 7.15}

            # Правая часть с графиком
            RelativeLayout: 
                padding: [5, 0, 0, 0]
                    
                # График ТОЛЬКО для шагов
                MiniChart:
                    id: steps_chart
                    pos_hint: {"x": 3.42, "top": 7.75}
                    size_hint: 1, 1
                    bar_color: 0.9, 0.7, 0.6, 1
        
        # ===== ВОДА =====
        Button:
            size_hint: .9, .12
            pos_hint: {"center_x":0.5, "top":0.6}
            background_normal: ""
            background_color: 0,0,0,0
            
            canvas.before:
                Color:
                    rgba: 1,1,1,1 
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]
                Color:
                    rgba: 0.7137, 0.5294, 0.5294, 0.8
                Line:
                    width: 1.0
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 20)
            
            RelativeLayout:
                # Текст "Вода" вверху слева
                Label:
                    text: "Вода"
                    font_name: "Gilroy-Medium"
                    font_size: "15sp"
                    color: 0.7,0.5,0.5,1
                    size_hint: None, None
                    size: self.texture_size
                    pos_hint: {"x": 0.39, "top": 6.25}
                
                # Значение шагов внизу слева
                Label:
                    text: "[font=Gilroy-SemiBold]{} мл[/font]".format(root.water)
                    markup: True
                    font_size: "24sp"
                    color: 0.7,0.5,0.5,1
                    size_hint: None, None
                    size: self.texture_size
                    pos_hint: {"x": 0.39, "top": 5.55}

            # Правая часть с графиком
            RelativeLayout: 
                padding: [5, 0, 0, 0]
                    
                # График ТОЛЬКО для шагов
                MiniChart:
                    id: water_chart
                    pos_hint: {"x": 3.42, "top": 6.15}
                    size_hint: 1, 1
                    bar_color: 0.9, 0.7, 0.6, 1
        
        # ===== СОН =====
        Button:
            size_hint: .9, .12
            pos_hint: {"center_x":0.5, "top":0.45}
            background_normal: ""
            background_color: 0,0,0,0
            
            canvas.before:
                Color:
                    rgba: 1,1,1,1 
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]
                Color:
                    rgba: 0.7137, 0.5294, 0.5294, 0.8
                Line:
                    width: 1.0
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 20)
            
            on_release: app.go_to_sleep_detail()
            
            RelativeLayout:
                # Текст "Сон" вверху слева
                Label:
                    text: "Сон"
                    font_name: "Gilroy-Medium"
                    font_size: "15sp"
                    color: 0.7,0.5,0.5,1
                    size_hint: None, None
                    size: self.texture_size
                    pos_hint: {"x": 0.39, "top": 4.65}
                
                # Значение шагов внизу слева
                Label:
                    text: "[font=Gilroy-SemiBold]{} ч {} мин[/font]".format(root.sleep_hours,root.sleep_minutes)
                    markup: True
                    font_size: "24sp"
                    color: 0.7,0.5,0.5,1
                    size_hint: None, None
                    size: self.texture_size
                    pos_hint: {"x": 0.39, "top": 3.95}

            # Правая часть с графиком
            RelativeLayout: 
                padding: [5, 0, 0, 0]
                    
                # График ТОЛЬКО для шагов
                MiniChart:
                    id: sleep_chart
                    pos_hint: {"x": 3.42, "top": 4.55}
                    size_hint: 1, 1
                    bar_color: 0.9, 0.7, 0.6, 1
        
        # ===== НАСТРОЕНИЕ =====
        Button:
            size_hint: .9, .12
            pos_hint: {"center_x":0.5, "top":0.3}
            background_normal: ""
            background_color: 0,0,0,0
            color: 0.7137, 0.5294, 0.5294, 1 
            on_release:
                app.root.current = "stats_mood"

            canvas.before:
                Color:
                    rgba: 1,1,1,1 
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]
                Color:
                    rgba: 0.7137, 0.5294, 0.5294, 0.8
                Line:
                    width: 1.0
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 20)

            RelativeLayout:
                # Текст "Настроение" вверху слева
                Label:
                    text: "Настроение"
                    font_name: "Gilroy-Medium"
                    font_size: "15sp"
                    color: 0.7,0.5,0.5,1
                    size_hint: None, None
                    size: self.texture_size
                    pos_hint: {"x": 0.39, "top": 3.05}
                
                # Значение воды внизу слева
                Label:
                    text: "[font=Gilroy-SemiBold]{}[/font]".format(root.mood)
                    markup: True
                    font_size: "24sp"
                    color: 0.7,0.5,0.5,1
                    size_hint: None, None
                    size: self.texture_size
                    pos_hint: {"x": 0.39, "top": 2.35}
                
                # Картинка справа (закреплена к правому краю)
                Image:
                    source: root.mood_image
                    size_hint: None, None
                    size: 105, 105
                    pos_hint: {"x": 3.5, "top": 3.05}
        
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
                    source: "home.png"
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
                    source: "Статистика.png"
                    allow_stretch: True
                    keep_ratio: True
                    size: self.parent.size
                    pos: self.parent.pos
                
                Button:
                    background_normal: ""
                    background_color: (0, 0, 0, 0)
                    size: self.parent.size
                    pos: self.parent.pos
                    on_release: app.go_to_summary()

            # Аналогично для Результатов
            RelativeLayout:
                size_hint: None, None
                size: 45, 45
                pos_hint: {"center_x": 0.5, "center_y": 0.1}
                
                Image:
                    source: "Результаты.png"
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

# ===== Кастомный круговой прогресс =====
<CircularProgress>:
    size_hint: None, None
    size: 200, 200

# ===== ActivityScreen =====
<ActivityScreen>:
    name: "activity"
    
    FloatLayout:
        canvas.before:
            Rectangle:
                source: "фон для сна и эмоций.png"
                size: self.size
                pos: self.pos
        
        # Заголовок
        Label:
            text: "Активность"
            font_name: "Gilroy-Regular"
            font_size: "36sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"x": -0.18, "top": 1.39}
        
        # Кнопка назад
        Button:
            text: "<"
            size_hint: None, None
            size: 44, 44
            pos_hint: {"right": 0.92, "top": 0.91}
            background_normal: ""
            background_color: 1, 1, 1, 0.5
            color: 0.7137, 0.5294, 0.5294, 1
            font_size: "24sp"
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Ellipse:
                    pos: self.pos
                    size: self.size
            on_release: app.root.current = "summary"
        
        # Процент от цели
        Label:
            text: "{}% от сегодняшней цели!".format(root.percentage)
            font_name: "Gilroy-Medium"
            font_size: "20sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"center_x": 0.5, "top": 1.28}
        
        # Круговой прогресс
        RelativeLayout:
            size_hint: None, None
            size: 250, 250
            pos_hint: {"center_x": 0.5, "center_y": 0.58}
            
            # Фоновый круг
            Widget:
                canvas:
                    Color:
                        rgba: 0.95, 0.85, 0.75, 0.3
                    Line:
                        width: 12
                        circle: (self.center_x, self.center_y, 100, 0, 360)
            
            # Прогресс-дуга
            Widget:
                canvas:
                    Color:
                        rgba: 1.0, 0.7, 0.4, 1.0
                    Line:
                        width: 12
                        circle: (self.center_x, self.center_y, 100, 90, 90 - root.percentage * 3.6)
            
            # Точка на конце дуги
            Widget:
                canvas:
                    Color:
                        rgba: 1, 1, 1, 1
                    Ellipse:
                        pos: root.dot_pos_x - 6, root.dot_pos_y - 6
                        size: 12, 12
            
            # Иконка шагов (ножки)
            Label:
                text: "👣"  # Можно заменить на Image с вашей иконкой
                font_size: "32sp"
                pos_hint: {"center_x": 0.5, "center_y": 0.65}
            
            # Значение шагов
            Label:
                text: "{}".format(root.steps)
                font_name: "Gilroy-SemiBold"
                font_size: "36sp"
                color: 0.7137, 0.5294, 0.5294, 1
                pos_hint: {"center_x": 0.5, "center_y": 0.52}
            
            Label:
                text: "шагов"
                font_name: "Gilroy-Medium"
                font_size: "18sp"
                color: 0.7137, 0.5294, 0.5294, 1
                pos_hint: {"center_x": 0.5, "center_y": 0.42}
        
        # Блок с графиком
        BoxLayout:
            orientation: "vertical"
            size_hint: 0.9, 0.32
            pos_hint: {"center_x": 0.5, "y": 0.05}
            padding: [15, 15]
            spacing: 10
            
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.9
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]
            
            # Переключатели День/Неделя/Месяц
            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: 40
                spacing: 10
                padding: [5, 5]
                
                Button:
                    text: "День"
                    background_normal: ""
                    background_color: (1.0, 0.9, 0.8, 1) if root.current_view == "День" else (0, 0, 0, 0)
                    color: 0.7137, 0.5294, 0.5294, 1
                    font_name: "Gilroy-Medium"
                    font_size: "16sp"
                    canvas.before:
                        Color:
                            rgba: (1, 0.9, 0.8, 0.5) if root.current_view == "День" else (0, 0, 0, 0)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [20]
                    on_release: root.set_view("День")
                
                Button:
                    text: "Неделя"
                    background_normal: ""
                    background_color: (1.0, 0.9, 0.8, 1) if root.current_view == "Неделя" else (0, 0, 0, 0)
                    color: 0.7137, 0.5294, 0.5294, 1
                    font_name: "Gilroy-Medium"
                    font_size: "16sp"
                    canvas.before:
                        Color:
                            rgba: (1, 0.9, 0.8, 0.5) if root.current_view == "Неделя" else (0, 0, 0, 0)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [20]
                    on_release: root.set_view("Неделя")
                
                Button:
                    text: "Месяц"
                    background_normal: ""
                    background_color: (1.0, 0.9, 0.8, 1) if root.current_view == "Месяц" else (0, 0, 0, 0)
                    color: 0.7137, 0.5294, 0.5294, 1
                    font_name: "Gilroy-Medium"
                    font_size: "16sp"
                    canvas.before:
                        Color:
                            rgba: (1, 0.9, 0.8, 0.5) if root.current_view == "Месяц" else (0, 0, 0, 0)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [20]
                    on_release: root.set_view("Месяц")
            
            # Цель
            Label:
                text: "Цель\\n" + str(root.goal)
                font_name: "Gilroy-Medium"
                font_size: "14sp"
                color: 0.7137, 0.5294, 0.5294, 1
                size_hint: None, None
                size: 60, 40
                pos_hint: {"x": 0, "top": 1}
                halign: "left"
            
            # График шагов
            ActivityChart:
                size_hint: 1, 0.6
                data: root.weekly_steps if root.current_view == "Неделя" else (root.monthly_steps if root.current_view == "Месяц" else root.daily_steps)
            
            # Текущее значение внизу
            Label:
                text: "{} шагов".format(root.steps)
                font_name: "Gilroy-SemiBold"
                font_size: "28sp"
                color: 0.7137, 0.5294, 0.5294, 1
                size_hint_y: None
                height: 40

# ===== График для ActivityScreen =====
<ActivityChart>:
    data: []
    
    canvas:
        # Горизонтальная линия цели
        Color:
            rgba: 0.9, 0.85, 0.8, 0.5
        Line:
            points: [self.x, self.y + self.height * 0.8, self.right, self.y + self.height * 0.8]
            width: 1
        
        # Столбцы
        # (реализация через Python)
       
<SleepDetailScreen>:
    name: "sleep_detail"
    
    FloatLayout:
        canvas.before:
            Rectangle:
                source: "фон для сна и эмоций.png"
                size: self.size
                pos: self.pos

        # Заголовок
        Label:
            text: "Сон"
            font_name: "Gilroy-Medium"
            font_size: "32sp"
            pos_hint: {"x": -0.35, "y": 0.4}
            color: 0.7,0.5,0.5,1

        # Кнопка назад
        Button:
            text: "<"
            size_hint: None, None
            size: 44, 44
            pos_hint: {"right": 0.92, "top": 0.91}
            background_normal: ""
            background_color: 1, 1, 1, 0.5
            color: 0.7137, 0.5294, 0.5294, 1
            font_size: "24sp"
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Ellipse:
                    pos: self.pos
                    size: self.size
            on_release: app.root.current = "summary"

        # Процент от цели
        Label:
            text: "{}% от сегодняшней цели!".format(root.percentage)
            font_name: "Gilroy-MediumItalic"
            font_size: "20sp"
            color: 0.7137, 0.5294, 0.5294, 1
            pos_hint: {"center_x": 0.5, "top": 1.28}

        Label:
            text: f"{root.sleep_hours} часов"
            font_size: "14sp"
            pos_hint: {"center_x":0.5, "center_y":0.6}
            color: 0.7,0.5,0.5,1
        
        Label:
            text: root.sleep_start_time
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.7, 0.5, 0.5, 1
            halign: "left"
            size_hint: None, None
            size: 60, 30
            pos_hint: {"center_x":0.16, "center_y":0.6}
        
        Label:
            text: root.sleep_end_time
            font_name: "Gilroy-Medium"
            font_size: "16sp"
            color: 0.7, 0.5, 0.5, 1
            halign: "right"
            size_hint: None, None
            size: 60, 30
            pos_hint: {"center_x":0.84, "center_y":0.6}

        # Шкала сна
        Image:
            source: "картинка для ResultSleepScreen.png"
            size_hint: 0.8, 0.58
            pos_hint: {"center_x": 0.5, "center_y": 0.65}
        
        # ===== БЛОК С ГРАФИКОМ =====
        BoxLayout:
            orientation: "vertical"
            size_hint: 0.9, 0.35
            pos_hint: {"center_x": 0.5, "y": 0.05}
            padding: [15, 15]
            spacing: 10
            
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.9
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]
            
            # Переключатели День/Неделя/Месяц
            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: 40
                spacing: 10
                padding: [5, 5]

                Button:
                    text: "День"
                    background_normal: ""
                    background_color: (1.0, 0.9, 0.8, 1) if root.current_view == "День" else (0, 0, 0, 0)
                    color: 0.7137, 0.5294, 0.5294, 1
                    font_name: "Gilroy-Medium"
                    font_size: "16sp"
                    canvas.before:
                        Color:
                            rgba: (1, 0.9, 0.8, 0.5) if root.current_view == "День" else (0, 0, 0, 0)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [20]
                    on_release: root.set_view("День")
                
                Button:
                    text: "Неделя"
                    background_normal: ""
                    background_color: (1.0, 0.9, 0.8, 1) if root.current_view == "Неделя" else (0, 0, 0, 0)
                    color: 0.7137, 0.5294, 0.5294, 1
                    font_name: "Gilroy-Medium"
                    font_size: "16sp"
                    canvas.before:
                        Color:
                            rgba: (1, 0.9, 0.8, 0.5) if root.current_view == "Неделя" else (0, 0, 0, 0)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [20]
                    on_release: root.set_view("Неделя")
                
                Button:
                    text: "Месяц"
                    background_normal: ""
                    background_color: (1.0, 0.9, 0.8, 1) if root.current_view == "Месяц" else (0, 0, 0, 0)
                    color: 0.7137, 0.5294, 0.5294, 1
                    font_name: "Gilroy-Medium"
                    font_size: "16sp"
                    canvas.before:
                        Color:
                            rgba: (1, 0.9, 0.8, 0.5) if root.current_view == "Месяц" else (0, 0, 0, 0)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [20]
                    on_release: root.set_view("Месяц")
            
            # График
            RelativeLayout:
                size_hint: 1, 1
                
                # Линия цели
                Widget:
                    size_hint: None, None
                    size: root.width - 30, 2
                    pos: 15, root.height * 0.7
                    pos_hint: {"center_x": 0.5, "y": 0.05}
                    canvas:
                        Color:
                            rgba: 0.9, 0.85, 0.8, 0.5
                        Rectangle:
                            pos: self.pos
                            size: self.size
                
                # Текст "Цель 8 часов"
                Label:
                    text: "Цель\\n{} часов".format(root.goal)
                    font_name: "Gilroy-Medium"
                    font_size: "12sp"
                    color: 0.7, 0.5, 0.5, 1
                    halign: "left"
                    size_hint: None, None
                    size: 60, 40
                    pos: 15, root.height * 0.72
                    pos_hint: {"x": 0, "y": 0.75}
                
                # Столбец графика
                Widget:
                    size_hint: None, None
                    size: 60, root.height * 0.65
                    pos: root.width - 100, root.y + 60
                    canvas:
                        # Фон столбца (светлый)
                        Color:
                            rgba: 1.0, 0.8, 0.6, 0.3
                        Rectangle:
                            pos: self.pos
                            size: self.size
                        
                        # Заполненный столбец
                        Color:
                            rgba: 1.0, 0.7, 0.4, 0.9
                        Rectangle:
                            pos: self.x, self.y
                            size: self.width, self.height * (root.percentage / 100)
                
                # Значение часов
                Label:
                    text: "{}".format(root.sleep_hours)
                    font_name: "Gilroy-SemiBold"
                    font_size: "48sp"
                    color: 0.7137, 0.5294, 0.5294, 1
                    size_hint: None, None
                    size: 80, 60
                    pos: root.width - 180, root.y + 20
                
                Label:
                    text: "часов"
                    font_name: "Gilroy-Medium"
                    font_size: "16sp"
                    color: 0.7, 0.5, 0.5, 1
                    size_hint: None, None
                    size: 60, 30
                    pos: root.width - 140, root.y + 35
'''

class MainApp(App):
    selected_date = StringProperty(datetime.now().strftime("%Y-%m-%d"))
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
        sm.add_widget(ResultMoodScreen(name="result_mood"))
        sm.add_widget(FinalResultScreen(name="final_result"))
        sm.add_widget(SummaryScreen(name="summary"))
        sm.add_widget(Screen(name="stats_steps"))
        sm.add_widget(Screen(name="stats_water"))
        sm.add_widget(Screen(name="stats_sleep"))
        sm.add_widget(Screen(name="stats_mood"))
        sm.add_widget(ActivityScreen(name="activity"))
        sm.add_widget(SleepDetailScreen(name="sleep_detail"))
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

        #key = datetime.now().strftime("%Y-%m-%d")
        key = App.get_running_app().selected_date

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
    def go_to_result_mood(self):
        self.root.current = "result_mood"
    def go_to_final_result(self):
        self.root.current = "final_result"
    def go_to_summary(self):
        self.root.current = "summary"
    def go_to_activity(self):
        # Обновляем данные перед переходом
        screen = self.root.get_screen("activity")
        screen.on_pre_enter()
        self.root.current = "activity"
    def go_to_sleep_detail(self):
        screen = self.root.get_screen("sleep_detail")
        screen.on_pre_enter()
        self.root.current = "sleep_detail"

if __name__ == '__main__':
    MainApp().run()

#"Если вы видите это сообщение, значит вы увидели изменение"
