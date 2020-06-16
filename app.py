#!/usr/bin/python3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from random import randint
from os import path
import time

# Global variables and methods
class App:
    def __init__(self):
        self.restart = 0
        self.email = ''
        self.password = ''
        self.types_of_images = 0
        self.names_of_images = []
        self.max_amount_of_images = []
        self.words_of_images = []

    def restart_app(self, message):
        try:
            error = str(message)
        except Exception:
            error = 'Critical error.'
        
        print(error + 'Rebooting script! \n')
        time.sleep(10)
        self.restart = 1

        self.write_log(error)

        time.sleep(2)
        self.main()

    def write_log(self, message):

        if path.exists('app_log.txt'):
            write_mode = 'a'
        else:
            write_mode = 'w'

        with open('app_log.txt', write_mode) as f:
            error_log = '** '
            error_log += str(time.ctime(time.time()))
            error_log += ' ' + message + ' **\n'
            f.write(error_log)

    def get_options_from_file(self):
        
        # Example options file:
        #
        # myemail@test.com                  // The username/email of a facebook account 
        # supersecretpassword               // The password of the same facebook account
        # g.13410024292743428291            // mobile.facebook.com - G number*
        # 2                                 // The number of image types that you want the program to send
        # dog_image 204 dog hound           // Specifies the type of images sent after a predefined message has been seen by the bot.**
        # cat_image 724 cat kitty :)) :((   // Same as above, just a different type of images.**
        # 
        # // - is just a note that isn't supposed to be included in the file
        # * - The G number can be found in the url of mobile.fb.com after (...)/messages/read/
        # ** - The first word is the type of images you want the bot to send.
        # ** - The second number is the amount of all the images of the same type.
        # ** - The last few words are triggers for the bot to activate.
        # ** - Words are separated by a single space.

        with open('options.txt', 'r') as f:
            print('Reading options file..')

            try:
                content = f.read()
                content = content.split('\n')
                self.email, self.password, self.g_number, self.types_of_images  = content[0], content[1], content[2], int(content[3])

                try:
                    for i in range(4, 4 + self.types_of_images): # From the 4-th line of the options file
                        line = content[i].split()
                        self.names_of_images.append(line.pop(0))
                        self.max_amount_of_images.append(int(line.pop(0)))
                        self.words_of_images.append(tuple(line))
                except Exception:
                    APP.write_log('Error with images-words lines in options file.')
                    exit('Error with images-words lines in options file.')

                try:
                    self.facebook_url = 'https://mobile.facebook.com/messages/read/?tid=cid.' + self.g_number
                    self.facebook_url_send_image = ('https://mobile.facebook.com/messages/photo/?ids&tids%5B0%5D=cid.'
                        + self.g_number
                        + '&message_text&cancel=https%3A%2F%2Fmobile.facebook.com%2Fmessages%2Fread%2F%3Ftid%3Dcid.' 
                        + self.g_number)
                except Exception:
                    APP.write_log('Error with url g-number in options file.')
                    exit('Error with  url g-number in options file.')

            except Exception:
                APP.write_log('Error with options file')
                exit('Error with options file.')
            else:
                if ((self.email != None or self.email != '')
                and (self.password != None or self.password != '')
                and (self.g_number != None or self.g_number != '')
                and (self.types_of_images > 0)
                and (len(self.names_of_images) == self.types_of_images)
                and (len(self.max_amount_of_images) == self.types_of_images)):
                    print('Complete! \n')
                else:
                    APP.write_log('Error with options file')
                    exit('Error with options file.')

    def main(self):
        bot = Bot(APP.email, APP.password)
        bot.login()

        self.restart = 0
        
        while self.restart == 0:
            bot.listen_values()
            time.sleep(2)


class Bot:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.last_messages = []
        self.listening = 99
        self.failed = 0
        
        options = Options()
        options.headless = True

        print('Opening browser and logging in.. ')

        try:
            bot = self.bot = webdriver.Firefox(options=options,executable_path="./geckodriver")
        except Exception:
            APP.restart_app('Error with running browser.')

        try:
            bot.get(APP.facebook_url)
            bot.refresh()
        except Exception:
            APP.restart_app('Error with getting facebook url.')

        time.sleep(30)

    def login(self):
        bot = self.bot
        email = self.email
        password = self.password

        try:
            login_field = bot.find_element_by_css_selector('input[name="email"]')
            password_field = bot.find_element_by_css_selector('input[name="pass"]')
            enter_login_button = bot.find_element_by_css_selector('input[name="login"]')
        except Exception:
            APP.restart_app('Error with getting html content.')

        try:
            login_field.clear()
            password_field.clear()

            login_field.send_keys(email)
            password_field.send_keys(password)
            enter_login_button.click() # Enter to login
        except Exception:
            print('Failed logging or already logged in!')

        time.sleep(30)
        print('Complete! \n')

    def listen_values(self):
        bot = self.bot
        last_messages = self.last_messages
        
        try:
            bot.find_element_by_css_selector('a.bo').click() # Refresh page
            time.sleep(1)

            messages = bot.find_elements_by_css_selector('.bu>div>span')
            messages.reverse() #Sorts messages from newest to oldest

            if messages != None: #Notify the user that the script is running without errors
                self.listening += 1
                if self.listening % 100 == 0:
                    print('Listening.. ' + str(time.ctime(time.time())))
                    self.listening = 1

            if len(last_messages) < 2:
                [last_messages.append(messages[i].text) for i in range(3)]

            for i in range(3):
                if i <= len(messages):
                    self.failed = 0 # Reset failure counter
                    
                    if messages[i] != None and messages[i].text != '':
                        text = messages[i].text
                        text = text.lower()
                        if not text in last_messages:
                            last_messages.append(text)
                            if len(last_messages) > 5:
                                last_messages.pop(0)

                            for i in range(APP.types_of_images):
                                for word in APP.words_of_images[i]:
                                    if word in text:
                                        print(f'Reacting to message: {str(text)}+ with {str(APP.names_of_images[i])} image')
                                        try:
                                            self.send_image(APP.names_of_images[i], APP.max_amount_of_images[i])
                                        except Exception:
                                            print(f'Failed with sending image..')

                    time.sleep(0.2)
                else:
                    self.failed += 1 # Bot hasn't found enough messages
                    
        except Exception:
            self.listening = 99 # Resets the counter to quickly show the user that the program is running without errors
            self.failed += 1
            if self.failed >= 5:
                APP.restart_app('Too many failtures with reading messages.')
            print(f'Failed reading messages for {str(self.failed)}. time..')

    def send_image(self, image_name, max_amount_of_image):
        bot = self.bot

        print('Getting random path to dog image..')
        path_to_random_image = ("/home/admin/bot/images/"
                                + str(image_name)
                                + str(randint(1, max_amount_of_image))
                                + '.jpg')

        bot.get(APP.facebook_url_send_image)
        time.sleep(1)

        try:
            input_file = bot.find_element_by_css_selector('input[name="file1"]')
            input_file.send_keys(path_to_random_image)

            time.sleep(1)

            bot.find_element_by_css_selector('input[type="submit"]').click()
            time.sleep(1)

            print('Send image: ' + str(path_to_random_image))
        except Exception:
            print('Error with sending file')
            APP.write_log('Error with sending file')

def init_values():
    print('\nStarting running script!\n')
    
    global APP
    APP = App()
    
    APP.write_log('Script started running.')

    APP.get_options_from_file()
    APP.main()


if __name__ == "__main__":
    init_values()
