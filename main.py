from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from database import Database

# Initialize Database
db = Database()
db.create_tables()  # Ensure tables exist

# ------------------ Kivy Screens -------------------

class LoginScreen(Screen):
    def login_user(self):
        username = self.ids.username.text
        password = self.ids.password.text

        user = db.login_user(username, password)
        if user:
            popup = Popup(title="Login Success",
                          content=Label(text=f"Welcome {user['first_name']}!"),
                          size_hint=(0.7, 0.3))
            popup.open()
            self.manager.current = 'main'
            self.manager.get_screen('main').current_user = user
        else:
            popup = Popup(title="Login Failed",
                          content=Label(text="Invalid username or password."),
                          size_hint=(0.7, 0.3))
            popup.open()


class RegisterScreen(Screen):
    def register_user(self):
        first_name = self.ids.first_name.text
        last_name = self.ids.last_name.text
        phone = self.ids.phone.text
        email = self.ids.email.text
        nid = self.ids.nid.text
        username = self.ids.username.text
        password = self.ids.password.text
        role = self.ids.role.text

        success = db.register_user(first_name, last_name, phone, email, nid, username, password, role)

        if success:
            popup = Popup(title="Success",
                          content=Label(text="Registration successful!"),
                          size_hint=(0.7, 0.3))
            popup.open()
            self.manager.current = 'login'
        else:
            popup = Popup(title="Error",
                          content=Label(text="Username already exists or invalid data."),
                          size_hint=(0.7, 0.3))
            popup.open()


class MainScreen(Screen):
    current_user = None

    def submit_report(self):
        if not self.current_user:
            popup = Popup(title="Error",
                          content=Label(text="No user logged in."),
                          size_hint=(0.7, 0.3))
            popup.open()
            return

        problem = self.ids.problem.text
        description = self.ids.description.text
        location = self.ids.location.text

        success = db.submit_report(self.current_user['id'], problem, description, location)

        if success:
            popup = Popup(title="Success",
                          content=Label(text="Report submitted successfully!"),
                          size_hint=(0.7, 0.3))
            popup.open()
            self.ids.problem.text = ""
            self.ids.description.text = ""
            self.ids.location.text = ""
        else:
            popup = Popup(title="Error",
                          content=Label(text="Failed to submit report."),
                          size_hint=(0.7, 0.3))
            popup.open()


# ------------------ Screen Manager -------------------

class WindowManager(ScreenManager):
    pass


# ------------------ Load KV Layout -------------------

kv = Builder.load_file("design.kv")


# ------------------ Main App -------------------

class CitizenApp(App):
    def build(self):
        self.title = "Citizen Help Portal"
        sm = WindowManager(transition=FadeTransition())
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(MainScreen(name='main'))
        return kv


if __name__ == "__main__":
    CitizenApp().run()
