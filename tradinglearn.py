import requests, json, sys
from tradeof import Ui_Dialog
from bs4 import BeautifulSoup
from PyQt5 import QtCore, QtGui, QtWidgets

app = QtWidgets.QApplication(sys.argv)

Dialog = QtWidgets.QDialog()
ui = Ui_Dialog()
ui.setupUi(Dialog)
Dialog.show()


#Hook loop
#Current balance
def printCurrent():
	currentCat = ''
	for i in account:
		currentCat += i if i != 'name' else 'Имя' 
		currentCat += ' : ' + str(account[i]) + '; '
	ui.label_5.setText(currentCat.replace('chet', 'Счет'))

#Login or singup
def createAccount():
	global account, data
	send = ui.lineEdit_5.text()

	try:
		with open("accounts.json", "r") as read_file:
			data = json.load(read_file)
	except FileNotFoundError:
		#if there is no file accounts.json
		data = {}

	if not send in data:
		#signup
		data[send] = {'name':send, 'chet':1000.0}
		account = data[send]
		ui.label_6.setText('Ты создал новый аккаунт, бро: ' + account['name'])
	else:
		#login
		account = data[send]
		ui.label_6.setText('Приветствуем, ' + account['name'])
	#write to file
	with open('accounts.json', 'w') as file:
		json.dump(data, file, indent=2, ensure_ascii=False)
	printCurrent()

def getPriceToLabel():
	global acPrice, res, send, acName
	send = ui.lineEdit.text()
	res = getPrice(send)
	if res == 'Error':
	    ui.label.setText('Нет такого))')
	    return
	acPrice = float(res[0].replace(",","."))
	acName = res[1]
	ui.label.setText('Акция от ' + res[1] + ' стоит ' + res[0].replace(",",".") + ' USD.\nСколько хотите купить?')
	#Enable buy tabs
	ui.lineEdit_3.setEnabled(True)
	ui.pushButton_2.setEnabled(True)


def getPrice(send):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'}
    url = 'https://www.google.com/search?q=акция ' + send
    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.content, 'html.parser')
    #price
    convert = soup.findAll("span", {"class":"IsqQVc NprOob"})
    #name of share
    acName = soup.findAll("div", {"class":"oPhL2e"})
    
    try:
    	return convert[0].text, acName[0].text
    except IndexError:
        return 'Error'


def buy():
	global account, send
	#disable buy tabs
	ui.lineEdit_3.setEnabled(False)
	ui.pushButton_2.setEnabled(False)

	sendCount = int(ui.lineEdit_3.text())
	
	if acPrice * sendCount > account['chet']:
		ui.label_4.setText('У тебя ж денег нет столько))')
		ui.label.setText('')
		return

	account['chet'] = round(account['chet'] - acPrice * sendCount, 2)
	try:
		account[send] += sendCount
	except KeyError:
		account[send] = sendCount
	ui.label_4.setText('Вы купили: ' + str(sendCount) + ' акцию(й) от\n' + acName)
	ui.label.setText('')

	with open('accounts.json', 'w') as file:
		json.dump(data, file, indent=2, ensure_ascii=False)
	printCurrent()


def findSell():
	global account, acPrice, res, send, acName
	send = ui.lineEdit_2.text()
	try:
		account[send] = account[send]
	except KeyError:
		ui.label_2.setText('Пффф... Такого нет у тебя.')
		return
	res = getPrice(send)
	acPrice = float(res[0].replace(",","."))
	acName = res[1]
	ui.label_2.setText('1 Акция сейчас стоит: ' + str(acPrice) + '\n' + 'Сколько акций хочешь продать?(у тебя их ' + str(account[send]) + ' )')
	ui.lineEdit_4.setEnabled(True)
	ui.pushButton_4.setEnabled(True)
	ui.label_4.setText('')

def sell():
	global send, acPrice, account
	ui.lineEdit_4.setEnabled(False)
	ui.pushButton_4.setEnabled(False)
	sendCount = int(ui.lineEdit_4.text())
	if sendCount > account[send]:
		ui.label_3.setText('У тебя пока маловато акций))')
		ui.label_2.setText('')
		return
	account[send] -= sendCount
	if account[send] == 0:
		account.pop(send)
	account['chet'] = round(account['chet'] + acPrice * sendCount, 2)
	with open('accounts.json', 'w') as file:
		json.dump(data, file, indent=2, ensure_ascii=False)
	printCurrent()
	ui.label_3.setText('Ты продал: ' + str(sendCount) + ' акцию(й) от\n' + acName)
	ui.label_2.setText('')

ui.pushButton.clicked.connect(getPriceToLabel)
ui.pushButton_2.clicked.connect(buy)
ui.pushButton_3.clicked.connect(findSell)
ui.pushButton_4.clicked.connect(sell)
ui.pushButton_5.clicked.connect(createAccount)



#exit
sys.exit(app.exec_())

