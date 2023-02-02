# Telegram bot assistent


Telegram bot accesses the API of the Practicum.Homework and find out the status of homework (whether the homework was taken to review, whether it was checked, and if it was checked, then the reviewer accepted it or returned it for revision).

## What does bot do?
- request to API of the Homework service once every 10 minutes and check the status of homework submitted for review
- analyze updated status using API response 
- send corresponding notification in Telegram about updated status
- add logging and inform about important problems with a Telegram message

TODO: add picture