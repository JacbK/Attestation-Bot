from twilio.rest import Client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import sqlite3
from flask import Flask, request
from twilio import twiml
from twilio.twiml.messaging_response import Message, MessagingResponse
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Twilio API Variables
account_sid = "fill in"
auth_token  = "fill in"
twilio_number = "fill in"

# Cloudinary API Variables
cloudinary.config(
  cloud_name = 'fill in',
  api_key = 'fill in',
  api_secret = 'fill in'
)

#Be sure after running and texting your number once, to comment out the table creation method on line 145

CHROMEDRIVER_PATH = '/root/chromedriver'
WINDOW_SIZE = "828,1792"
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument('--no-sandbox')

client = Client(account_sid, auth_token)

def fillForm(email, first, last):
    web = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                              chrome_options=chrome_options
                             )
    web.get('https://wsipcbts.sjc1.qualtrics.com/jfe/form/SV_a3NhKAwg8Uo1itL?e=105&sd=39119&s=2388&c=S')
    time.sleep(2)
    web.implicitly_wait(10)

    NextOne = web.find_element_by_xpath('//*[@id="NextButton"]')
    NextOne.click()
    time.sleep(2)
    web.implicitly_wait(10) 

    emailField = web.find_element_by_xpath('//*[@id="QR~QID22~1"]')
    emailField.send_keys(str(email))

    firstField = web.find_element_by_xpath('//*[@id="QR~QID24~1"]')
    firstField.send_keys(str(first))

    lastField = web.find_element_by_xpath('//*[@id="QR~QID24~2"]')
    lastField.send_keys(str(last))
    time.sleep(2)
    web.implicitly_wait(10)

    NextTwo = web.find_element_by_xpath('//*[@id="NextButton"]')
    NextTwo.click()
    time.sleep(6)
    web.implicitly_wait(10)


    l2= web.find_elements_by_xpath('//*[@id="QID21-1-label"]')
    s2 = len(l2)

    if s2 > 0:

        YesOne = web.find_element_by_xpath('//*[@id="QID21-1-label"]')
        YesOne.click()
        time.sleep(5)
        web.implicitly_wait(10)

        NextThree = web.find_element_by_xpath('//*[@id="NextButton"]')
        NextThree.click()
        time.sleep(5)
        web.implicitly_wait(10)

    else:
        return('User already completed survey.')

    l= web.find_elements_by_xpath('//*[@id="QID11-1-label"]')
    s = len(l)

    if s > 0:

        print('Running true if statement.')
        YesTwo = web.find_element_by_xpath('//*[@id="QID11-1-label"]')
        YesTwo.click()
        time.sleep(5)
        web.implicitly_wait(10)

        NextFour = web.find_element_by_xpath('//*[@id="NextButton"]')
        NextFour.click()
        time.sleep(5)
        web.implicitly_wait(10)


        NoneOfAbove = web.find_element_by_xpath('//*[@id="QID34-19-label"]')
        NoneOfAbove.click()
        time.sleep(5)
        web.implicitly_wait(10)
    else:
        print('Running false else statement.')
        NoneOfAbove = web.find_element_by_xpath('//*[@id="QID34-19-label"]')
        NoneOfAbove.click()
        time.sleep(5)
        web.implicitly_wait(10)

    NextFive = web.find_element_by_xpath('//*[@id="NextButton"]')
    NextFive.click()
    time.sleep(5)
    web.implicitly_wait(10)

    NoneOfAboveTwo = web.find_element_by_xpath('//*[@id="QID38-19-label"]')
    NoneOfAboveTwo.click()
    time.sleep(5)
    web.implicitly_wait(10)

    NextSix = web.find_element_by_xpath('//*[@id="NextButton"]')
    NextSix.click()


    time.sleep(4)
    web.execute_script("document.body.style.zoom='180%'")
    time.sleep(1)
    web.get_screenshot_as_file("screenshot.png")
    web.close()
    uploadList = cloudinary.uploader.upload("screenshot.png")
    imageLink = uploadList["url"]
    return(str(imageLink))

app = Flask(__name__)

@app.route('/sms', methods=['GET', 'POST'])
def sms():
    conn = sqlite3.connect('students.db')

    c = conn.cursor()
    numberSentFrom = str(request.form['From'])
    c.execute("""CREATE TABLE students (
                first text,
                last text,
                email text,
                phone text
                )""")

    conn.commit()
    numberSentFrom = str(request.form['From'])
    message_body = str(request.form['Body'])
    #Gets phone number that was used to send

    try:
        c.execute("SELECT * FROM students WHERE phone=?", (numberSentFrom,))
        dblist = c.fetchone()
        firstN, lastN, listEmail, listPhone = dblist
        print('Detected existing phone number.')

        if(message_body == 'form' or message_body == 'Form' or message_body == 'form ' or message_body == 'Form '):
            message = client.messages \
                .create(
                     body='Please wait, it could take up to two minutes.',
                     from_=twilio_number,
                     to=numberSentFrom
                 )
            imageLinkFunction = fillForm(listEmail, firstN, lastN)
            print(imageLinkFunction)
            print('Sending message')
            if imageLinkFunction.startswith('http') == True:
                message = client.messages \
                    .create(
                         body='Here is your form:',
                         media_url=imageLinkFunction,
                         from_=twilio_number,
                         to=numberSentFrom
                     )
            else:
                message = client.messages \
                    .create(
                         body='A form was already filled out with your information today.',
                         from_=twilio_number,
                         to=numberSentFrom
                     )
        elif message_body == 'DELETE' or message_body == 'Delete' or message_body == 'DELETE ' or message_body == 'Delete ' or message_body == 'delete 'or message_body == 'delete':
            c.execute("DELETE FROM students WHERE phone=?", (numberSentFrom,))
            conn.commit()
            message = client.messages \
                .create(
                     body='Your information has been deleted. Thank you for using Attestation Bot. Text this number again if you wish to reregister.',
                     from_=twilio_number,
                     to=numberSentFrom
                 )
            return('Deleted data from database.')

        else:
            message = client.messages \
                .create(
                     body='Bot Usage:\n"Form" - Fills out an attestation form.\n"Delete" - Remove your data from the bot.',
                     from_=twilio_number,
                     to=numberSentFrom
                 )

        return('Detected existing phone number.')

    except TypeError:

        if message_body.startswith(':') == True:
            varForSplitting = message_body[1:]
            newdblist = varForSplitting.split()
            newdblist.append(numberSentFrom)
            try:
                newFirst, newLast, newEmail, newPhone = newdblist

                c.execute("INSERT INTO students VALUES (:first, :last, :email, :phone)", {'first': newFirst, 'last': newLast, 'email': newEmail, 'phone': newPhone})
                conn.commit()

                message = client.messages \
                    .create(
                         body='You are now registered under this phone number - '+ str(numberSentFrom) + '.\n\nWhen you are ready to have a form filled out, send the word, "Form" to this number and the rest will be taken care of for you!\n\nIf you would like to remove your information from the database, text the word "Delete".',
                         from_=twilio_number,
                         to=numberSentFrom
                     )
                return('Completed Registration. Sent usage instructions.')


            except ValueError:
                message = client.messages \
                    .create(
                         body='Incorrect registration format. If you would like to register, respond with your information in this format:\n\n:FirstName LastName Email\n\nDo not forget the ":".',
                         from_=twilio_number,
                         to=numberSentFrom
                     )
                return('Incorrect format.')
                print('Incorrect format.')

        else:
            message = client.messages \
                .create(
                     body='Hello there, your phone number is not currently registered for the Attestation Bot - made by Jacob K. If you would like to register, respond with your information in this format:\n\n:FirstName LastName Email\n\nDo not forget the ":" before your information and use your Selah email.',
                     from_=twilio_number,
                     to=numberSentFrom
                 )
            return('Sent registration instructions.')
            print('Sent registration instructions.')

if __name__ == '__main__':
    app.run(debug=True)
