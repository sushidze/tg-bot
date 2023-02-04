# Telegram bot assistent


Telegram bot accesses the API of the Practicum.Homework and find out the status of homework (whether the homework was taken to review, whether it was checked, and if it was checked, then the reviewer accepted it or returned it for revision).

## What does bot do?
- request to API of the Homework service once every 10 minutes and check the status of homework submitted for review
- analyze updated status using API response 
- send corresponding notification in Telegram about updated status
- add logging and inform about important problems with a Telegram message

![image_2023-02-02_22-57-30](https://user-images.githubusercontent.com/106175866/216470179-affe3e36-d6a8-4bbf-9cf3-ce513c44ad6a.png)
