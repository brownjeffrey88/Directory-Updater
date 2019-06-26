from exchangelib import *
import re
import time
from datetime import date, datetime, timedelta
import os
from Data import catalog
import FileManip

images_Directory = "C:\\Users\\jbrown\\Desktop\\directory psd files"
replacements_Directory = "C:\\Users\\jbrown\\Desktop\\directory psd files\\blanks"
# pulls all image files and dates to the images dict from the data.py file
images = catalog

# variables
failed_body = "There was an error fulfilling your request. be sure to check the formatting of your " \
              "subject line and that the date is not passed or improperly formatted. Format should be date in XX/XX/XXXX" \
              "\nExample: 02/12/2099" \
              "\n\nFor list of files and their names, send a message or reply to this message with the subject line 'files'\n" \
              "If the file youre attempting to update is not in that list of files it cannot be added or updated at this time."
update_success = "The requested changes have been made"
noAttachment_body = "There was an error fulfilling your request. There was no attached image to update."

# exchangelib login's
credentials = ServiceAccount(username='NCEE\\directorymain', password='NCee1914')
account = Account(primary_smtp_address='directorymain@nceent.com', credentials=credentials,
                  autodiscover=True, access_type=DELEGATE)


# send messages...
def sendMessage(recipient, subject, body):
    try:
        m = Message(
            account=account,
            folder=account.sent,
            subject=subject,
            body=body,
            to_recipients=[Mailbox(email_address=recipient)]
        )
    except Exception as e:
        print("\nfailed sending email.\n", str(e))
    m.send_and_save()


# reply to messages...
def replyMessage(recipient, messageToRespondTo, body):
    try:
        m = account.inbox.get(subject=messageToRespondTo)
        m.reply(
            subject='Re: ' + messageToRespondTo,
            body=body,
            to_recipients=[recipient]
        )
    except Exception as e:
        print("\nfailed replying to email. ", messageToRespondTo, "\n", str(e))


# check messages... need to delete message after its been read and executed
def checkMessages():
    try:
        account.inbox.refresh()
        if (account.inbox.unread_count > 0):
            print("new messages:")
            for x in account.inbox.all().order_by('datetime_received'):
                sender = str(x.sender.email_address)
                subject = str(x.subject)
                z = checkFormat(subject, x)
                if z == None:
                    replyMessage(sender, subject, noAttachment_body)
                if z == 1:
                    files = ""
                    for i in images:
                        files += i + "\n"
                    print(files)
                    replyMessage(sender, subject, files)
                if z == 2:
                    try:
                        downloaded, attachedName = downloadAttachment(x)
                        if downloaded:
                            FileManip.replaceFile(attachedName, attachedName)
                            FileManip.setDate(attachedName, subject)
                            replyMessage(sender, subject, update_success)
                    except Exception as e:
                        print("\nfailed to download email attachment\n", str(e))
                if z == 3:
                    replyMessage(sender, subject, failed_body)
                print("this message returned ", z, subject, sender, "\n")
                x.delete()
        else:
            print("No new messages")
    except Exception as e:
        print("\nFailed to retrieve emails.\n", str(e))


# reads the subject line, returns true if the message is formatting to specification
def checkFormat(subject, message):
    filesRequest = re.search("files$", subject)
    updateRequest = re.search("^([0-9]|0[1-9]|1[0-2])(.|-|/)([0-9]|1[0-9]|2[0-9]|3[0-1])(.|-|/)20[0-9][0-9]$", subject)
    try:
        if filesRequest:
            return 1
        elif updateRequest:
            for attachment in message.attachments:
                if isinstance(attachment, FileAttachment):
                    todaysDate = time.strptime((str(date.today().strftime("%m/%d/%Y"))), "%m/%d/%Y")
                    futureDate = time.strptime(subject, "%m/%d/%Y")
                    if futureDate > todaysDate:
                        return 2
        else:
            return 3
    except Exception as e:
        print("\nfailed checking the format of the message. \n", str(e))


# download file attachment, save to the replacements directory
def downloadAttachment(message):
    try:
        for attachment in message.attachments:
            if isinstance(attachment, FileAttachment):
                local_path = os.path.join(replacements_Directory, attachment.name)
                with open(local_path, 'wb') as f:
                    f.write(attachment.content)
                    f.close()
                return True, str(attachment.name)
            else:
                return False, str("no attachment")
    except Exception as e:
        print("\nfailed downloading attachment.\n", str(e))
