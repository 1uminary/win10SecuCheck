# -*- coding: utf-8 -*

import os
import xlrd #conda install -c auto xlrd
import docx #pip install python-docx
import PyPDF2 #pip install PyPDF2

#exts = ['.xls', '.xlsx', '.doc', '.docx', '.ppt', '.pptx']

def docuSearch(drive):
    exts =['.xls', 'xlsx']
    docuList = []
    for(path, dir, files) in os.walk(drive):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            for extname in exts:
                if ext == extname:
                    docuList.append("%s/%s" % (path, filename))
    return docuList

def readXls(filename):
    workBook = xlrd.open_workbook(filename)
    sheetNames = workBook.sheet_names()
    rowVal = []
    for sheetName in sheetNames:
        workSheet = workBook.sheet_by_name(sheetName)
        numRows = workSheet.nrows
        for rowNum in range(numRows):
            rowVal.append(workSheet.row_values(rowNum))
    return rowVal

def readDocx(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

def readPDF(filename):
    f = open(filename, 'rb')
    pdf = PyPDF2.PdfFileReader(f)
    n = pdf.numPages
    fullText = []
    while n > -1:
        n = n - 1
        page = (pdf.getPage(n)).extractText()
        page = page.encode('UTF-8')
        fullText.append(page)
    return fullText
        
def searchSocialNum(fullText):



d = docuSearch("C:/Users/luminary/Downloads/")
print(d)
pdf = readPDF(d[0])
print(pdf)