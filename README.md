# Attestation-Bot

A bot created to fill out my high school's attestation form for COVID. 🦠

Made with Python, Twilio, Selenium, Cloudinary, SQLite.

All interaction done with users is through the Twilio API. Users register by texting, and their data is stored in a SQLite database, using their phone number as an identification number. From there, users can message the bot to fill a form, and the bot does it for them using selenium. Once screenshot is taken it uploads the file using the Cloudinary API to be sent to the user via Twilio. Other interactions with the users are available such as the 'DELETE' command to remove their data from the database.

This is definitely a beginner project, and I am hoping for advisory on how to improve the organization and practicality of my code. 😊
