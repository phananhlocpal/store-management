from ui.ui_home import*
from lib import *
import mainProgram

class Role():
    def __init__(self):
        super(Role,self).__init__
        self.update_db()
    
    def update_db(self):
        self.raw_role = db.execute("SELECT * FROM Role")
        self.roleTable = self.raw_role.fetchall()

class Users(Role):
    def __init__(self):
        Role().__init__()
        self.update_db()

    def update_db(self):
        self.raw_user = db.execute("SELECT * FROM Users")
        self.userTable = self.raw_user.fetchall()

    def createUser(self, name, phone, address, email, role):
        # Check condition
        check = True
        displayTest = ""
        homeTask = mainProgram.home()
        if name == "" or phone == "" or address == "" or email == "":
            check = False
            displayTest += "You must filed all the information\n"
        else:
            if (len(phone) >= 10):
                if not phone.isdigit():
                    displayTest += "The phone number must be the sequence of numbers.\n"
                    check = False
            else: 
                displayTest += "The phone number must have more 9 numbers.\n"
                check = False
            if email != "":
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if re.match(pattern, email) is None:
                    displayTest += "The email you entered is not valid.\n"
                    check = False
                try:
                    if db.execute("SELECT * FROM Users WHERE Email = ?", email).fetchone():
                        displayTest += "Email already exists. Pleaser choose another email"
                except ValueError:
                    homeTask.noti("Value Error!")
                except Exception as e:
                    homeTask.noti(f"Error: {e}")
        
        if check == False:
            displayTest += "Please re-input!"
            homeTask.noti(displayTest)
        else: 
            userName, domain = str(email).split("@")
            roleId = db.execute("SELECT Id FROM Role WHERE RoleName = ?", role).fetchone()[0]
            try:
                db.execute("INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (len(self.userTable) + 1001, name, int(phone), address, str(email), int(roleId), 11111111, userName, True))
                db.commit()
                homeTask.noti("User is created succesfully!")
                
                sender = 'anhloc280@gmail.com'
                password = 'zvloronmuhyqocjv'
                recipient = str(email)
                subject = 'WELCOME TO PAL STORE! We give you the user information to login the system.'
                body = f"""

                Hi {name},

                Welcome to our company!
                Your username: {userName}
                Your Password: 11111111

                Have a nice day!
                Best Regards./.
                Pal
                """
                self.send_email(sender, password, recipient, subject, body)
            except ValueError:
                homeTask.noti("Cant send email!")
            except Exception:
                homeTask.noti("Cant send email")

    def send_email(self, sender, password, recipient, subject, body):
            # create MIMEText with email content
            message = MIMEMultipart()
            message['From'] = sender
            message['To'] = recipient
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            # connect to server email and login with account and password 
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)

            # Gửi email
            text = message.as_string()
            server.sendmail(sender, recipient, text)
            server.quit()

class Unit():
    def __init__(self):
        super(Unit, self).__init__
        self.update_db()
        
    def update_db(self):
        #Import raw values in supplier table
        self.rawUnit = db.execute("SELECT * FROM Unit")
        self.unitTable = self.rawUnit.fetchall()
   
class Supplier():
    def __init__(self):
        super(Supplier, self).__init__()    
        self.notiWindow = None
        self.displayText = ""
        self.update_db()
        
    def update_db(self):
        #Import raw values in supplier table
        self.raw_supplier = db.execute("SELECT * FROM Suplier")
        self.supplierTable = self.raw_supplier.fetchall()

    def createSuppliers(self, name, address, phone: str, email):
        self.homeTask = mainProgram.home()
        noti_display = ""
        check = True
        #Check condition
            # 1. The cells is not none except description 
        if phone == ""  or name == "" or address == "" or email == "":
            noti_display += "(You must fill all the information.\n"
            check = False
            # 2. Phone must be a number > 6 
        elif (len(phone) < 7):
            noti_display += "( Phone number must be greater than 6 characters.\n"
            check = False
        elif not phone.isdigit():
            noti_display += f"(Phone number must be a sequence of numbers greater than 6 characters.\n"
            check = False
            # 3. email must be valid
        if email != "":
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if re.match(pattern, email) is None:
                noti_display += f"(The email you entered is not valid.\n"
                check = False
        # Display the notification and create item
        if check == False:
            noti_display += "\nPlease re-iput"
            self.homeTask.noti(noti_display)
        else:
            #If the condition == true, do:
            try:
                db.execute("INSERT INTO Suplier VALUES (?, ?, ?, ?, ?)", (len(self.supplierTable) + 1001, name, address, phone, email))
                db.commit()
                self.update_db()
                #Notify the message: "Input sucessfully"
                self.displayText = 'Vendor imported successfully!'
                self.homeTask = mainProgram.home()
                self.homeTask.noti(self.displayText)
                self.homeTask.default_createSupplier()
            except ValueError:
                #Notify the message: "Input sucessfully"
                self.homeTask = mainProgram.home()
                self.homeTask.noti("Your data is invalid!")    
            except Exception:
                self.homeTask.noti("Have error! Pleaser try again!")

class Item(Supplier, Unit):
    def __init__(self):
        Supplier().__init__()
        Unit().__init__()
        self.notiWindow = None
        self.displayText = ""
        self.update_db()
    
    def update_db(self):
        #Import raw values in supplier table
        self.rawItem = db.execute("SELECT * FROM Item")
        self.itemTable = self.rawItem.fetchall()
    
    def createItems(self, itemName: str, itemDescription: str, itemLabel: str, itemPrice: str, itemUnitName: str, itemSupplierName: str):
        self.homeTask = mainProgram.home()
        noti_display = ""
        index = 1
        check = True
        # The input values
        unitId = int(db.execute("SELECT Id FROM Unit WHERE Name = ?", itemUnitName).fetchone()[0])
        supplierID = int(db.execute("SELECT Id FROM Suplier WHERE Name = ?", itemSupplierName).fetchone()[0])
        # Check Condition
            # 1. The cells is not none except description 
        if itemName == ""  or itemPrice == "":
            noti_display += f"({index}) Name Item and Price must be not None.\n"
            index +=1
            check = False
            # 2. Price must a number be greater than 1,000
        if itemPrice.isdigit():
            if int(itemPrice) < 1000:
                noti_display += f"({index}) Item price must be greater than 1,000đ.\n"
                index += 1
                check = False
        else: 
            noti_display += f"({index}) Item price must be a number.\n"
            index += 1
            check = False
        # Display the notification and create item
        if check == False:
            noti_display += "\nPlease re-iput"
            self.homeTask.noti(noti_display)
        else:
            try:
                db.execute("INSERT INTO Item VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (len(self.itemTable) + 10001, itemName, itemDescription, itemLabel,  unitId,supplierID, int(itemPrice), True))
                db.commit()
                self.update_db()
                self.homeTask.noti("Input item successfully!")
            except ValueError:
                self.homeTask.noti("Your data is invalid!")
            except Exception as e:
                self.homeTask.noti(f" {e} Have Error. Please try again!")

class BE(Users, Supplier):
    def __init__(self):
        Users().__init__()
        Supplier().__init__()
        #self.BERun = mainProgram.home("")
        self.update_db()
        
    
    def update_db(self):
        #Import raw values in BE table
        self.raw_BE = db.execute("SELECT * FROM BE")
        self.BETable = self.raw_BE.fetchall()
    
    def inputItem(self, item_id, item_name, createBETable, count):
        # Check if the item is already in the table
        for i in range(createBETable.rowCount()):
            if createBETable.item(i, 0).text() == item_id:
                # If the item is already in the table, update the spinbox value
                spinbox = createBETable.cellWidget(i, 2)
                spinbox.setValue(spinbox.value() + 1)
                return
        
        # If the item is not in the table, add it to the end
        row_position = createBETable.rowCount()
        createBETable.insertRow(row_position)
        createBETable.setItem(row_position, 0, QTableWidgetItem(item_id))
        createBETable.setItem(row_position, 1, QTableWidgetItem(item_name))
        
        spinbox = QSpinBox(createBETable)
        spinbox.setRange(1, 999)
        spinbox.setValue(1)
        createBETable.setCellWidget(row_position, 2, spinbox)
        
    def createBE(self, BEId, userId):
        homeTask = mainProgram.home()
        current_datetime = QDateTime.currentDateTime().toString('dd/MM/yyyy HH:mm:ss')
        try:
            db.execute("INSERT INTO BE VALUES (?, ?, ?, ?, ?, ?)", (int(BEId), datetime.datetime.strptime(current_datetime, '%d/%m/%Y %H:%M:%S'), int(userId), False, 0, ""))
            db.commit()
            self.update_db()
        except ValueError:
            homeTask.noti("Value Error!")
        except Exception as e:
            homeTask.noti(f"Error: {e}")

    def confirmBuyingEntry(self, BEId, totalInvoice, itemId_tList: list):
        homeTask = mainProgram.home()
        stockTask = Stock()
        current_datetime = QDateTime.currentDateTime().toString('dd/MM/yyyy HH:mm:ss')
        try:
            db.execute(f"UPDATE BE SET Status = ? WHERE Id = ?", True, int(BEId))
            db.execute(f"UPDATE BE SET TotalInvoice = ? WHERE Id = ?", int(totalInvoice), int(BEId))
            db.execute(f"UPDATE BE SET ReceivedDate = ? WHERE Id = ?", datetime.datetime.strptime(current_datetime, '%d/%m/%Y %H:%M:%S'), int(BEId))
            db.commit()
        except ValueError:
            homeTask.noti("Value Error!")
        except Exception as e:
            homeTask.noti(f"Error: {e}")

        #Update real amount
        BE_DetailTask = BE_Detail()
        BE_DetailTask.updateBE_Detail_afterCF(BEId, itemId_tList)    
                
class BE_Detail(BE, Item):
    def __init__(self):
        BE().__init__()
        Item().__init__()
        self.update_db()

    def update_db(self):
        #Import raw values in BE_Detail Table
        self.raw_BE_Detail = db.execute("SELECT * FROM BE_Detail")
        self.BE_DetailTable = self.raw_BE_Detail.fetchall()

    def createBE_Detail(self, BEId, itemId, amount):
        homeTask = mainProgram.home()
        try:
            db.execute("INSERT INTO BE_Detail VALUES (?, ?, ?)", (int(BEId), int(itemId), int(amount)))
            db.commit()
            self.update_db()
        except ValueError:
            homeTask.noti("Value Error!")
        except Exception as e:
            homeTask.noti(f"Erorr: {e}")
            
    def updateBE_Detail_afterCF(self, BEId, itemId_tList: list):
        listStock = []
        homeTask = mainProgram.home()
        try:
            for i in range(len(itemId_tList)):
                itemId = itemId_tList[i]["ItemId"]
                realAmount = itemId_tList[i]["RealAmount"]
                db.execute("UPDATE BE_Detail SET Amout = ? WHERE BEId = ? AND itemId = ?", (int(realAmount), int(BEId), int(itemId)))
                db.commit()
                listStock_dict = {"itemId": itemId_tList[i]["ItemId"], "deviation": itemId_tList[i]["RealAmount"]}
                listStock.append(listStock_dict)

            #Update Stock
            stockTask = Stock()
            stockTask.updateStock(listStock)
        except ValueError:
            homeTask.noti("Value Error!")
        except Exception as e:
            homeTask.noti(f"Error: {e}")

class Stock(Item, BE):
    def __init__(self):
        Item().__init__()
        BE().__init__()
        self.update_db
        self.raw_stock = db.execute("SELECT * FROM STOCK")
        self.stockTable = self.raw_stock.fetchall()
    
    def update_db(self):
        #Import raw values in BE_Detail Table
        self.raw_stock = db.execute("SELECT * FROM STOCK")
        self.stockTable = self.raw_stock.fetchall()
    
    def updateStock(self, listStock: list):
        #listStock = [{itemId: ?? ; deviation: ??}]
        #defin itemId location in stockTable
        homeTask = mainProgram.home()
        try: 
            for i in range(len(listStock)):
                for j in range (len(self.stockTable)):
                    if self.stockTable[j][0] == listStock[i]["itemId"]:
                        amount = self.stockTable[j][1] + listStock[i]["deviation"]
                        db.execute("UPDATE STOCK SET amount = ? WHERE itemId = ?", (amount, listStock[i]["itemId"]))
                        db.commit()
        except ValueError:
            homeTask.noti("Your data is invalid")
        except Exception as e:
            homeTask.noti(f"Error: {e}")

class Customer():
    def __init__(self):
        super(Customer, self).__init__()
        self.update_db()
        self.raw_customer = db.execute("SELECT * FROM Customer")
        self.customerTable = self.raw_customer.fetchall()

    def update_db(self):
        #Import raw values in BE_Detail Table
        self.raw_customer = db.execute("SELECT * FROM Customer")
        self.customerTable = self.raw_customer.fetchall()
    
    def createCustomers(self, name, phone, email, address):
        self.homeTask = mainProgram.home()
        noti_display = ""
        index = 1
        check = True
        #Check condition
            # 1. The cells is not none except description 
        if phone == ""  or name == "":
            noti_display += f"({index}) Customer name and phone number must be not None.\n"
            index +=1
            check = False
            # 2. Phone must be a number > 6 
        elif (len(phone) < 7):
            noti_display += f"({index}) Phone number must be greater than 6 characters.\n"
            index +=1
            check = False
        elif not phone.isdigit():
            noti_display += f"({index}) Phone number must be a sequence of numbers greater than 6 characters.\n"
            index +=1
            check = False
            # 3. email must be valid
        if email != "":
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if re.match(pattern, email) is None:
                noti_display += f"({index}) The email you entered is not valid.\n"
                index +=1
                check = False
        # Display the notification and create item
        if check == False:
            noti_display += "\nPlease re-iput"
            self.homeTask.noti(noti_display)
        else:
            try:
                db.execute("INSERT INTO Customer VALUES (?, ?, ?, ?, ?)", (len(self.customerTable) + 1001, name, int(phone), email, address))
                db.commit()
                self.homeTask.noti("Input customer user successfully!")
                self.homeTask.defaut_createCustomer
            except ValueError:
                self.homeTask.noti("Your data is invalid!")
            except Exception as e:
                self.homeTask.noti(f"Error: {e}")

class Invoice(Users):
    def __init__(self):
        Users().__init__()
        self.update_db()
        #Import raw values in BE_Detail Table
        self.raw_invoice = db.execute("SELECT * FROM Invoice")
        self.invoiceTable = self.raw_invoice.fetchall()
    
    def update_db(self):
        #Import raw values in BE_Detail Table
        self.raw_invoice = db.execute("SELECT * FROM Invoice")
        self.invoiceTable = self.raw_invoice.fetchall()
    
    def inputItem(self, item_id, item_name, itemInvoice, count):
        # Check if the item is already in the table
        for i in range(itemInvoice.rowCount()):
            if itemInvoice.item(i, 0).text() == item_id:
                # If the item is already in the table, update the spinbox value
                spinbox = itemInvoice.cellWidget(i, 2)
                spinbox.setValue(spinbox.value() + 1)
                return
        
        # If the item is not in the table, add it to the end
        row_position = itemInvoice.rowCount()
        itemInvoice.insertRow(row_position)
        itemInvoice.setItem(row_position, 0, QTableWidgetItem(item_id))
        itemInvoice.setItem(row_position, 1, QTableWidgetItem(item_name))

        
        spinbox = QSpinBox(itemInvoice)
        spinbox.setRange(1, 999)
        spinbox.setValue(1)
        itemInvoice.setCellWidget(row_position, 2, spinbox)

    def createInvoice(self,invoiceId,  payment, totalPrice, customerId, userId):
        current_datetime = QDateTime.currentDateTime().toString('dd/MM/yyyy HH:mm:ss')
        if customerId == "":
            customerId = 0
        homeTask = mainProgram.home()
        try:
            db.execute("INSERT INTO Invoice VALUES (?, ?, ?, ?, ?, ?)", (int(invoiceId), datetime.datetime.strptime(current_datetime, '%d/%m/%Y %H:%M:%S'), payment, int(totalPrice), int(customerId), int(userId) ))
            db.commit()
            self.update_db()
        except ValueError:
            homeTask.noti("Your data is invalid!")
        except Exception as e:
            homeTask.noti(f"Error: {e}")

class InvoiceDetail(Invoice, Item):
    def __init__(self):
        Invoice().__init__()
        Item().__init__()
        self.update_db
    
    def update_db(self):
        #Import raw values in BE_Detail Table
        self.raw_invoice_detail = db.execute("SELECT * FROM InvoiceDetail")
        self.invoiceDetailTable = self.raw_invoice_detail.fetchall()
    
    def createInvoice_Detail(self,invoiceId, itemId, amount, total):
        homeTask = mainProgram.home()
        invoice_label = Invoice()
        invoice_label.update_db()
        try: 
            db.execute("INSERT INTO InvoiceDetail VALUES (?, ?, ?, ?)", (int(invoiceId), int(itemId), int(amount), int(total)))
            db.commit()
            self.update_db()
        except ValueError:
            homeTask.noti("Value Error!")
        except Exception as e:
            homeTask.noti(f"Value Error: {e}")

    
    def updateStock_afterSELL(self, invoiceId, itemInvoice_list):        
        #Update Stock
        stockTask = Stock()
        stockTask.updateStock(itemInvoice_list)
     
class show_chart(FigureCanvasQTAgg):
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)

        plt.ion()
    

