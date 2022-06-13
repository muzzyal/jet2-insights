import csv
import os
import pathlib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
import pickle
from re import A
import pandas as pd
from googleapiclient.discovery import build

f=open("email-setup/emailaddress.txt","r")
lines=f.readlines()
sender=lines[0]
path_to_pickle = "token.pickle"

def getService(path):
    with open(rf'{path}', 'rb') as token:
        creds = pickle.load(token)
    service = build('gmail', 'v1', credentials=creds)
    return service

service = getService(path_to_pickle)

def attachmentsList(csvPath):
    attachmentsList = os.listdir(csvPath)
    attachments = []
    
    for csvs in attachmentsList:
        attachments.append(os.path.join(csvPath, csvs))
    
    return attachments

def sendEmail(recipient, csvPath, year, category, dataset):

    attachments = attachmentsList(csvPath)

    if len(attachments) > 1:
        compiledCsvDf = pd.concat(
            map(pd.read_csv, attachments), ignore_index=True)

        compiledCsvDf = compiledCsvDf.iloc[:, 1:]

        csvFilePath = os.path.join(csvPath, f"{category}-{dataset}-{year}-compiled.csv")
        compiledCsvDf.to_csv(csvFilePath, encoding='utf-8')

        for a in attachments:
            if "compiled" not in a:
                os.remove(a)

    attachments = attachmentsList(csvPath)

    if "airlines" in attachments[0]:
        jet2Df = compiledCsvDf[compiledCsvDf.isin(["JET2.COM LTD"]).any(axis=1)]
        emailMsg = 'Hello, This is an automated email containing your requested airlines data file. Below you can find the JET2 data from the attached file.'
    else:
        jet2Df = compiledCsvDf[compiledCsvDf.isin(["BELFAST CITY (GEORGE BEST)", "BRISTOL", "BIRMINGHAM", "EAST MIDLANDS INTERNATIONAL", "EDINBURGH", "GLASGOW", "LEEDS BRADFORD", "STANSTED", "MANCHESTER", "NEWCASTLE"]).any(axis=1)]
        emailMsg = 'Hello, This is an automated email containing your requested airport data file. Below you can find the data of ten airports JET2 operates from, from the attached file.'

    emailHTML = """\
        <html>
        <head></head>
        <body>
            {0}
        </body>
        </html>
        """.format(jet2Df.to_html())

    csvFilePath = os.path.join(csvPath, f"JET2-Summary-{dataset}-{year}-compiled.csv")
    jet2Df.to_csv(csvFilePath, encoding='utf-8') 
    # create email message
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = recipient
    mimeMessage['subject'] = 'Jet2 Insights Programme'
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))
    mimeMessage.attach(MIMEText(emailHTML, 'html'))
    # Attach files
    for attachment in attachments:
        content_type, encoding = mimetypes.guess_type(attachment)
        main_type, sub_type = content_type.split('/', 1)
        file_name = os.path.basename(attachment)
    
        f = open(attachment, 'rb')
    
        myFile = MIMEBase(main_type, sub_type)
        myFile.set_payload(f.read())
        myFile.add_header('Content-Disposition', 'attachment', filename=file_name)
        encoders.encode_base64(myFile)
    
        f.close()
    
        mimeMessage.attach(myFile)
    
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
    
    message = service.users().messages().send(
        userId='me',
        body={'raw': raw_string}).execute()