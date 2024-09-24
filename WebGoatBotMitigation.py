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
        # {
        #     'exercise': '/SqlInjectionMitigations/attack10a',
        #     'data': {
        #         'field1': 'getConnection',
        #         'field2': 'PreparedStatement statement',
        #         'field3': 'prepareStatement',
        #         'field4': '?',
        #         'field5': "?",
        #         'field6': "statement.setString(1, 'Smith')",
        #         'field7': "statement.setString(1, 'John')",
        #     }
        # },
        # {
        #     'exercise': '/SqlInjectionMitigations/attack10b',
        #     'data': {
        #         'editor': """try {
        #             Connection conn = DriverManager.getConnection(DBURL, DBUSER, DBPW);
        #
        #             PreparedStatement statement = conn.prepareStatement("SELECT status FROM  users WHERE name=? AND mail=?");
        #             statement.setString(1, "Smith");
        #             statement.setString(1, "Smith");
        #             statement.setString(2, "John");
        #
        #             ResultSet results = statement.executeQuery();
        #         } catch (Exception e) {
        #             System.out.println("Oops. Something went wrong!");
        #         }"""
        #     }
        # },
        # {
        #     'exercise': '/SqlOnlyInputValidation/attack',
        #     'data': {
        #         'userid_sql_only_input_validation': "Smith';/**/select/**/*/**/from/**/user_system_data;--"
        #     }
        # },
        {
            'exercise': '/SqlInjectionMitigations/attack12a',
            'data': {
                'ip': "104.130.219.202"
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