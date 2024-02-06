from lib import *
import classTask

class login(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loginPage = ui.ui_login.Ui_MainWindow()
        self.loginPage.setupUi(self) 
        self.loginPage.loginButton.clicked.connect(self.comeHome)
        self.user_label = classTask.Users()
        self.loginUserId = loginUserId

    def comeHome(self):
        if self.loginPage.username.text() == "" or self.loginPage.username.text() == "":
            print("Invalid!")
        else:
            check = False
            for i in range(len(self.user_label.userTable)):
                if self.loginPage.username.text() == self.user_label.userTable[i][7] and self.loginPage.password.text() == self.user_label.userTable[i][6]:
                    check = True
                    loginUserId = db.execute("SELECT Id FROM Users WHERE Username = ?",self.loginPage.username.text()).fetchone()[0]
            if check == False:
                homeTask = home()                 
                homeTask.noti("Username or Password is incorrect! Please re-input.")
            else:
                # Truyền giá loginUserId đến tất cả các class
                comeHome = home()
                widget.addWidget(comeHome)
                widget.setCurrentIndex(widget.currentIndex()+1)

class confirmBEWindow(QMainWindow):
    closed = pyqtSignal()
    def __init__(self, BEId: int):
        super(confirmBEWindow, self).__init__()    
        self.confirmBEWindow = ui.ui_confirmBE.Ui_MainWindow()
        self.confirmBEWindow.setupUi(self) 
        self.BE_label = classTask.BE()
        self.BE_Detail_label = classTask.BE_Detail()
        self.user_label = classTask.Users()
        self.supplier_label = classTask.Supplier()
        self.item_label = classTask.Item()
        self.customer_label = classTask.Customer()
        self.BEId = BEId
        self.completer_user_list = []

        #Design the element
        requesterId = db.execute("SELECT UserId from BE WHERE Id = ?", BEId).fetchone()[0]
        requesterName = db.execute("SELECT Name FROM Users WHERE Id = ?", int(requesterId)).fetchone()[0]
        createDate = db.execute("SELECT CreateDate FROM BE WHERE Id = ?", BEId).fetchone()[0]

        self.confirmBEWindow.Requester.setText(f"{requesterId} - {requesterName}")
        self.confirmBEWindow.creationDate.setText(f"{createDate}")
        current_datetime = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss")
        self.confirmBEWindow.duedate.setText(f"{current_datetime}")
        self.confirmBEWindow.BEId.setText(f"{BEId}")

        #Design the recommended box
        for i in range (len(self.user_label.userTable)):
            self.completer_user_list.append(f"{self.user_label.userTable[i][0]} - {self.user_label.userTable[i][1]}")
        self.completer_user = QCompleter(self.completer_user_list, self)
        self.completer_user.setCaseSensitivity(Qt.CaseInsensitive)
        self.confirmBEWindow.staff.setCompleter(self.completer_user)

        #Design table
        for i in range(len(self.BE_Detail_label.BE_DetailTable)):
            if self.BE_Detail_label.BE_DetailTable[i][0] == self.BEId:
                rowPosition = self.confirmBEWindow.ItemTable.rowCount()
                self.confirmBEWindow.ItemTable.insertRow(rowPosition)
                self.confirmBEWindow.ItemTable.setItem(rowPosition, 0, QTableWidgetItem(str(self.BE_Detail_label.BE_DetailTable[i][1])))
                name = db.execute("SELECT Name FROM Item WHERE Id = ?", self.BE_Detail_label.BE_DetailTable[i][1]).fetchone()[0]
                self.confirmBEWindow.ItemTable.setItem(rowPosition, 1, QTableWidgetItem(str(name)))
                self.confirmBEWindow.ItemTable.setItem(rowPosition, 2, QTableWidgetItem(str(self.BE_Detail_label.BE_DetailTable[i][2])))
        
        # interact with button
        self.confirmBEWindow.confirmButton.clicked.connect(self.confirmBE)
    
    def confirmBE(self):
        # Check condition  
        notiDisplay = ""
        check = True
        # 1. Staff must have in staff list with form Id - name
        # 1.1. Check if it has " - "
        if not " - " in self.confirmBEWindow.staff.text():
            notiDisplay += "Staff information is invalid.\n"
            check = False
        else:
            staffId, staffName = str(self.confirmBEWindow.staff.text()).split(" - ")
            # 1.2. Does the ID exist?
            check_exist = False
            for i in range (len(self.user_label.userTable)):
                if int(staffId) == self.user_label.userTable[i][0]:
                    check_exist = True
                    break
            if check_exist == False:
                notiDisplay += "Staff information is invalid.\n"
                check = False
            else:
                # 1.3. ID and Name are been one person in staff list?
                staffID_test = db.execute("SELECT Id FROM Users WHERE Name = ?", staffName).fetchone()[0]
                if int(staffId) != staffID_test:
                    notiDisplay += "Staff information is invalid.\n"
                    check = False
        # 2. Check realAmount
        # 2.1. All row of realAmount col must be filled 
        check_filled = True
        for i in range (self.confirmBEWindow.ItemTable.rowCount()):
            if self.confirmBEWindow.ItemTable.item(i, 3) is None:
                check_filled = False
                break
        if check_filled == False:
                notiDisplay += "All row off \"Real Amount\" column must be filled.\n"
                check = False
        else:
            check_filled = True
            for i in range (self.confirmBEWindow.ItemTable.rowCount()):
                if self.confirmBEWindow.ItemTable.item(i, 3).text() == "":
                    check_filled = False
                    break
            if check_filled == False:
                notiDisplay += "All row off \"Real Amount\" column must be filled.\n"
                check = False
            else: 
                # 2.2. The value must a number
                check_number = True
                for i in range (self.confirmBEWindow.ItemTable.rowCount()):
                    text = str(self.confirmBEWindow.ItemTable.item(i, 3).text())
                    if not text.isdigit():
                        check_number = False
                        break
                if check_number == False:
                    notiDisplay += "The value of real amount must be a number.\n"
                    check = False
                else:
                    # 2.3. The number must be greater than 0
                    check_number = True
                    for i in range (self.confirmBEWindow.ItemTable.rowCount()):
                        text = int(self.confirmBEWindow.ItemTable.item(i, 3).text())
                        if text < 0:
                            check_number = False
                            break
                    if check_number == False:
                        notiDisplay += "The value of real amount must be greater than 0.\n"
                        check= False
        # 3. Check invoice total
        # 2.1. invoice total must be filled 
        if self.confirmBEWindow.invoiceTotal.text() == "":
            notiDisplay += "The invoice total must be filled.\n"
            check = False
        else: 
            # 2.2. The invoice total must a number
            text = str(self.confirmBEWindow.invoiceTotal.text())
            if not text.isdigit():
                notiDisplay += "The value of invoice total must be a number.\n"
                check = False
            else:
                try:
                    text = int(self.confirmBEWindow.invoiceTotal.text())
                except ValueError:
                    text = "0"
                if text < 0:
                    notiDisplay += "The value of invoice total must be greater than 0.\n"
                    check= False
        homeTask = home()
        if check == True:
            itemId_tList = []
            for i in range(self.confirmBEWindow.ItemTable.rowCount()):
                itemId_tdict= {"ItemId": int(self.confirmBEWindow.ItemTable.item(i,0).text()), "RealAmount": int(self.confirmBEWindow.ItemTable.item(i,3).text())}
                itemId_tList.append(itemId_tdict)
            self.BE_label.confirmBuyingEntry(self.BEId, self.confirmBEWindow.invoiceTotal.text(), itemId_tList)
            notiDisplay += "Confirmed successfully!"
            homeTask.noti(notiDisplay)
        else: homeTask.noti(notiDisplay)
    
    def closeEvent(self, event):
        super().closeEvent(event)
        self.closed.emit()
        
class editItem(QMainWindow):
    closed = pyqtSignal()
    def __init__(self, itemId: int):
        super(editItem, self).__init__()    
        self.editItem = ui.ui_editItem.Ui_MainWindow()
        self.editItem.setupUi(self) 
        self.itemId = itemId
        itemName = db.execute("SELECT Name FROM Item WHERE Id = ?", itemId).fetchone()[0]
        itemPrice = db.execute("SELECT Price FROM Item WHERE Id = ?", itemId).fetchone()[0]
        itemStatus = int(db.execute("SELECT Status FROM Item WHERE Id = ?", itemId).fetchone()[0])
        self.editItem.EditItemName.setText(f"{itemName}")
        self.editItem.EditItemPrice.setText(f"{itemPrice}")
        if itemStatus == 1:
            self.editItem.EditItemStatus.setCurrentText("Available")
        else: self.editItem.EditItemStatus.setCurrentText("Not available")
        self.editItem.EditItemChange.clicked.connect(self.changeIteminfo)

    def changeIteminfo(self):
        homeTask = home()
        try:
            db.execute("UPDATE Item SET Name = ? WHERE Id = ?", (str(self.editItem.EditItemName.text()), self.itemId))
            db.execute(f"UPDATE Item SET Price = {int(self.editItem.EditItemPrice.text())} WHERE Id = {self.itemId}")
            if self.editItem.EditItemStatus.currentText() == "Available":
                db.execute(f"UPDATE Item SET Status = 1 WHERE Id = {self.itemId}")
            else: db.execute(f"UPDATE Item SET Status = 0 WHERE Id = {self.itemId}")
            db.commit()
            self.close()
            homeTask.noti('Item updated successfully!')
            homeTask.item_label.update_db()
        except ValueError:
            homeTask.noti("Value Error!")
        
    def closeEvent(self, event):
        super().closeEvent(event)
        self.closed.emit()
  
class EditStaff(QMainWindow):
    def __init__(self, userId: int):
        super(EditStaff, self).__init__()
        self.editStaff = ui.ui_EditUser.Ui_MainWindow()
        self.editStaff.setupUi(self)
        self.userId = userId 
        self.user_label = classTask.Users()
        self.role_label = classTask.Role()

        # Design the Combo box
        for i in range (len(self.role_label.roleTable)): 
            self.editStaff.ESRole.addItem(str(self.role_label.roleTable[i][1]))

        self.editStaff.ESName.setText(db.execute("SELECT Name FROM Users WHERE Id = ?", self.userId).fetchone()[0])
        self.editStaff.ESPhone.setText(str(db.execute("SELECT Phone FROM Users WHERE Id = ?", self.userId).fetchone()[0]))
        self.editStaff.ESAddress.setText(db.execute("SELECT Address FROM Users WHERE Id = ?", self.userId).fetchone()[0])
        self.editStaff.ESEmail.setText(db.execute("SELECT Email FROM Users WHERE Id = ?", self.userId).fetchone()[0])
        esrole = db.execute("SELECT RoleName FROM Role JOIN Users ON Role.Id = Users.RoleId WHERE Users.RoleId = ?", self.userId).fetchone()[0]
        self.editStaff.ESRole.setCurrentText(esrole)
        if self.user_label.userTable[i][8] == True: 
            self.editStaff.ESStatus.setCurrentText("Available")
        else: self.editStaff.ESStatus.setCurrentText("Not available")
        self.editStaff.ESUsername.setText(db.execute("SELECT Username FROM Users WHERE Id = ?", self.userId).fetchone()[0])
        self.editStaff.ESPassword.setText(db.execute("SELECT Password FROM Users WHERE Id = ?", self.userId).fetchone()[0])
    
        self.editStaff.ESButton.clicked.connect(self.changeInfo)

    def changeInfo(self):
        homeTask = home()
        try:
            db.execute("UPDATE Users SET Name = ? WHERE Id = ?", self.editStaff.ESName.text(), self.userId)
            db.execute("UPDATE Users SET Phone = ? WHERE Id = ?", int(self.editStaff.ESPhone.text()),self.userId)
            db.execute("UPDATE Users SET Address = ? WHERE Id = ?", self.editStaff.ESAddress.text(), self.userId)
            db.execute("UPDATE Users SET Email = ? WHERE Id = ?", self.editStaff.ESEmail.text(),self.userId)
            role_new = int(db.execute("SELECT Id FROM Role WHERE RoleName = ?",self.editStaff.ESRole.currentText()).fetchone()[0])
            db.execute("UPDATE Users SET RoleId = ? WHERE Id = ?", role_new, self.userId)
            db.execute("UPDATE Users SET Username = ? WHERE Id = ?", self.editStaff.ESUsername.text(), self.userId)
            db.execute("UPDATE Users SET Password = ? WHERE Id = ?", self.editStaff.ESPassword.text(), self.userId)
            if self.editStaff.ESStatus.currentText() == "Available":
                db.execute("UPDATE Users SET Status = 1 WHERE Id = ?", self.userId)
            else: db.execute("UPDATE Users SET Status = 0 WHERE Id = ?", self.userId)
            db.commit()
            homeTask =home()
            homeTask.format_list_staff()
            homeTask.noti("Update the user information sucessfully")
            self.close()
        except ValueError:
            homeTask.noti("Vale Error!")
        except Exception as e:
            homeTask.noti(f"Error: {e}")

class ChangePassword(QMainWindow):
    def __init__(self, loginUserId):
        super(ChangePassword, self).__init__()
        self.changePassword = ui.ui_changePassword.Ui_MainWindow()
        self.changePassword.setupUi(self)
        self.changePassword.pushButton.clicked.connect(self.update)
        self.user_label = classTask.Users()
        self.loginUserId = loginUserId
    
    def update(self):
        #Check condition
        check = True
        displayTest = ""
        homeTask = home()
        if self.changePassword.lineEdit.text() == "" or self.changePassword.lineEdit_2.text() == "":
            check = False
            displayTest += "You must fill all the information.\n"
        elif self.changePassword.lineEdit.text() != self.changePassword.lineEdit_2.text():
            check = False
            displayTest += "Your re-input password is not as password.\n"
        if check == False:
            displayTest += "Please re-input."
            homeTask.noti("displayTest")
        else: 
            try:
                db.execute("UPDATE Users SET Password = ? WHERE Id = ?", (self.changePassword.lineEdit.text(), self.loginUserId))
                db.commit()
                self.user_label.update_db()
                homeTask.noti("Update password successfully!")
            except ValueError:
                homeTask.noti("Value error!")
            except Exception:
                homeTask.noti("Something wrong. Please re-input!")

class home(QMainWindow):
    def __init__(self):
        super().__init__()
        # Display the screen
        self.homePage = ui.ui_home.Ui_StoreManagementSystem()
        self.homePage.setupUi(self) 
        self.homePage.stackedWidget.setCurrentWidget(self.homePage.Home)
        self.loginUserId = 1000
        self.loginRoleId = db.execute("SELECT RoleID FROM Users WHERE Id = ?", self.loginUserId).fetchone()[0]
        self.loginRole = db.execute("SELECT RoleName FROM Role WHERE Id = ?", self.loginRoleId).fetchone()[0]

        # Declare list, dict, class from classTask
        self.completer_item_list = []
        self.completer_user_list = []
        self.completer_customer_list = []
        self.product_counts = {}
        self.item_label = classTask.Item()
        self.unit_label = classTask.Unit()
        self.supplier_label = classTask.Supplier()
        self.user_label = classTask.Users()
        self.customer_label = classTask.Customer()
        self.BE_label = classTask.BE()
        self.BE_Detail_label = classTask.BE_Detail()
        self.stock_label = classTask.Stock()
        self.invoice_label = classTask.Invoice()
        self.invoiceDetail_label = classTask.InvoiceDetail()
        self.role_label = classTask.Role()
        self.spinboxes = []
        # connect the valueChanged signal of each spinbox to the updateTotal slot
        for spinbox in self.spinboxes:
            spinbox.valueChanged.connect(self.updateTotal)
        
        #Update database
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.item_label.update_db())
        self.timer.timeout.connect(self.format_list_staff)
        self.timer.timeout.connect(lambda: self.BE_label.update_db())
        self.timer.timeout.connect(lambda: self.customer_label.update_db())
        self.timer.timeout.connect(lambda: self.stock_label.update_db())
        self.timer.start(5000)

        # Call design and connect functions
        self.designComboBox()
        self.designRecommendBox()
        self.connect()
        self.designChart()
    
    def connect(self):
        # Connect to stackedWidget
        # 1. Home
        self.homePage.actionHome.triggered.connect(lambda: self.homePage.stackedWidget.setCurrentWidget(self.homePage.Home))
        # 2. Item
        self.homePage.actionPrint_Price_Tags.setVisible(False)
        if self.loginRole == "Manager":
            self.homePage.actionCreate_an_items.triggered.connect(lambda: (self.homePage.stackedWidget.setCurrentWidget(self.homePage.CreateItems), self.designRecommendBox()))
        else: self.homePage.actionCreate_an_items.setVisible(False)
        self.homePage.actionList_Itesm.triggered.connect(lambda: (self.homePage.stackedWidget.setCurrentWidget(self.homePage.ListItems), self.middleman_listItem(), self.designRecommendBox()))
        self.homePage.actionPrint_Price_Tags.triggered.connect(lambda: self.homePage.stackedWidget.setCurrentWidget(self.homePage.PrintPriceTag))
        # 3. Customer
        self.homePage.actionCreate_Customer_Users.triggered.connect(lambda: self.homePage.stackedWidget.setCurrentWidget(self.homePage.CreateCustomerUsers))
        self.homePage.actionList_Customers.triggered.connect(lambda: (self.homePage.stackedWidget.setCurrentWidget(self.homePage.ListCustomer), self.format_list_customer(self.customer_label.customerTable), self.designRecommendBox()))
        # 4. Sale Entry
        self.homePage.actionCreate_an_invoice.triggered.connect(lambda: (self.homePage.stackedWidget.setCurrentWidget(self.homePage.CreateAnInvoice), self.defaut_createInvoice(), self.designRecommendBox()))
        self.homePage.actionList_invoices.triggered.connect(lambda _, filterInvoice=self.invoice_label.invoiceTable: (self.format_list_invoice(filterInvoice), self.homePage.stackedWidget.setCurrentWidget(self.homePage.ListInvoices), self.default_listInvoice()))
        # 5. Buying Entry
        if self.loginRole == "Manager":
            self.homePage.actionCreate_a_buying_entry.triggered.connect(lambda: (self.homePage.stackedWidget.setCurrentWidget(self.homePage.CreateBE), self.defaut_createBE(), self.designRecommendBox()))
        else: self.homePage.actionCreate_a_buying_entry.setVisible(False)
        self.homePage.actionConfirm_Buying_Entry.triggered.connect(lambda: (self.homePage.stackedWidget.setCurrentWidget(self.homePage.ComfirmBE), self.format_list_uncf_BE()))
        self.homePage.actionList_Buying_Entry.triggered.connect(lambda _, filterBE=self.BE_label.BETable: (self.format_list_BE(filterBE), self.homePage.stackedWidget.setCurrentWidget(self.homePage.ListBE), self.default_listBE()))
        if self.loginRole == "Manager":
            self.homePage.actionCreate_Suppliers.triggered.connect(lambda: self.homePage.stackedWidget.setCurrentWidget(self.homePage.CreateSupplier))
        else: self.homePage.actionCreate_Suppliers.setVisible(False)
        # 6. Stock
        self.homePage.actionStock_Map.triggered.connect(lambda _, filterStock=self.item_label.itemTable: (self.format_stock(filterStock), self.homePage.stackedWidget.setCurrentWidget(self.homePage.StockMap), self.designComboBox()))
        if self.loginRole == "Manager":
            self.homePage.actionUpdate_Stock.triggered.connect(lambda: (self.homePage.stackedWidget.setCurrentWidget(self.homePage.UpdateStock), self.designRecommendBox()))
        else: self.homePage.actionUpdate_Stock.setVisible(False)
        # 7. User
        self.homePage.actionInformation.triggered.connect(lambda: (self.homePage.stackedWidget.setCurrentWidget(self.homePage.UserInfo), self.default_userInformation()))
        if self.loginRole == "Manager":
            self.homePage.actionCreate_user.triggered.connect(lambda: (self.homePage.stackedWidget.setCurrentWidget(self.homePage.CreateUser), self.default_createUser))
        else: self.homePage.actionCreate_user.setVisible(False)
        self.homePage.actionList_Staff.triggered.connect(lambda: self.homePage.stackedWidget.setCurrentWidget(self.homePage.ListStaff))
        self.homePage.actionLog_out.triggered.connect(lambda: self.return_loginPage())
        
        # Interact in the stackedWidget
            # 1. Click the button
        self.homePage.SupplierCreateButton.clicked.connect(lambda: self.middleman_createSupplier()) # Click "Create Supplier Button" in page "Create Supplier"
        self.homePage.BECreateButton.clicked.connect(lambda: self.createBE()) # Click "Create BE Button" in page "Create BE"
        self.homePage.CreateItemButton.clicked.connect(lambda: (self.middleman_createItem(), self.default_createItem()))
        self.homePage.CUCreateButton.clicked.connect(lambda: self.middleman_createCustomer())
        self.homePage.paymentButton.clicked.connect(lambda: (self.createInvoice()))
        self.homePage.LIFilterButton.clicked.connect(lambda: self.middleman_filterListItem())
        self.homePage.LIshowAllButton.clicked.connect(lambda: self.format_list_item(self.item_label.itemTable, "all"))
        self.homePage.FindItemButton.clicked.connect(lambda: self.middleman_findItem())
        self.homePage.LCFilterButton.clicked.connect(lambda: self.middleman_filterListCustomer())
        self.homePage.LCShowAllButton.clicked.connect(lambda _, list=self.customer_label.customerTable: (self.format_list_customer(list)))
        self.homePage.FindCustomerInvoice.clicked.connect(lambda: self.middleman_findInvoice())
        self.homePage.InvoiceFilter.clicked.connect(lambda: self.middleman_filterListInvoice())
        self.homePage.InvoiceShowAll.clicked.connect(lambda: self.format_list_invoice(self.invoice_label.invoiceTable))
        self.homePage.LBFilter.clicked.connect(lambda: self.middleman_filterListBE())
        self.homePage.createInvoice_subButton.clicked.connect(lambda: (self.homePage.stackedWidget.setCurrentWidget(self.homePage.CreateAnInvoice), self.defaut_createInvoice()))
        self.homePage.stockMap_subButton.clicked.connect(lambda _, filterStock=self.item_label.itemTable: (self.format_stock(filterStock), self.homePage.stackedWidget.setCurrentWidget(self.homePage.StockMap)))
        self.homePage.LBShowAll.clicked.connect(lambda: self.format_list_BE(self.BE_label.BETable))
        self.homePage.stockShowAllButton.clicked.connect(lambda: (self.format_stock(self.item_label.itemTable), self.default_stock))
        self.homePage.stockFilterButton.clicked.connect(lambda: self.middleman_filterStock())
        self.homePage.stockFindButton.clicked.connect(lambda: self.middleman_findItemStock())
        self.homePage.UpdateStockButton.clicked.connect(lambda: self.updateStock())
        self.homePage.CraeteUserButton.clicked.connect(lambda: (self.middleman_createUser(), self.default_createUser()))
        self.homePage.ChangePassButton.clicked.connect(lambda: self.open_changePassword())
            # 2. Press enter line edit
        self.homePage.BEInputItem.returnPressed.connect(lambda: self.middleman_inputItemBE())
        self.homePage.findItemInvoice.returnPressed.connect(lambda: self.middleman_inputItemInvoice())
        self.homePage.UpdateStockFind.returnPressed.connect(lambda: self.middleman_inputItemUpdateStock())
        self.homePage.findCustomerInvoiceInput.returnPressed.connect(self.customerDisplay)
    
    #================================================================================================================================================
    # MIDDLEMAN METHOD
    def middleman_listItem(self):
        self.item_label.update_db()
        filterItem=self.item_label.itemTable
        self.format_list_item(filterItem, "filter")
        
    def middleman_findItem(self):
        itemfilter = self.FindItem()
        self.format_list_item(itemfilter, "find")
    def middleman_findInvoice(self):
        invoicefilter = self.findInvoice()
        self.format_list_invoice(invoicefilter)
    def middleman_filterListCustomer(self):
        customerFilter = self.LCFilter()
        self.format_list_customer(customerFilter)
    def middleman_filterListItem(self):
        itemfilter=self.LIFilter()
        self.format_list_item(itemfilter, "filter")
    def middleman_filterListInvoice(self):
        invoiceFilter = self.invoiceFilter()
        self.invoiceFilter()
        self.format_list_invoice(invoiceFilter)
    def middleman_filterListBE(self): 
        BEFilter = self.BEFilter()
        self.BEFilter()
        self.format_list_BE(BEFilter)
    def middleman_filterStock(self):
        stockfilter=self.stockFilter()
        self.format_stock(stockfilter)
    def middleman_findItemStock(self):
        stockfilter = self.FindItemStock()
        self.format_stock(stockfilter)
    def middleman_createUser(self):
        name=self.homePage.User_Name.text()
        phone=self.homePage.User_Phone.text()
        address=self.homePage.User_Address.text()
        email=self.homePage.User_Email.text()
        role=self.homePage.User_RoleCB.currentText()
        self.user_label.createUser(name, phone, address, email, role)
        self.user_label.update_db()
    def middleman_createSupplier(self):
        name=str(self.homePage.NameSupplier.text())
        address=str(self.homePage.AddressSupplier.text())
        phone=str(self.homePage.PhoneSupplier.text())
        email=str(self.homePage.EmailSupplier.text())
        self.supplier_label.createSuppliers(name,address,phone,email)
        self.supplier_label.update_db()
    def middleman_createItem(self):
        name=self.homePage.NameItem.text()
        description=self.homePage.descriptionItem.text()
        inputItem=self.homePage.label_input_Items.currentText()
        price=self.homePage.priceItem.text()
        unit=self.homePage.unitItemCB.currentText()
        supplier = self.homePage.supplierItemCB.currentText()
        self.item_label.createItems(name,description,inputItem,price,unit,supplier)
        self.item_label.update_db()

    def middleman_createCustomer(self):
        name=self.homePage.CUName.text()
        phone=self.homePage.CUPhone.text()
        email=self.homePage.CUEmail.text()
        address=self.homePage.CUAddress.text()
        self.customer_label.createCustomers(name, phone, email, address)
        self.customer_label.update_db()
    def middleman_inputItemInvoice(self):
        table=self.homePage.itemInvoice
        inputItem=self.homePage.findItemInvoice
        task="Invoice"
        self.pre_addTable(table, inputItem, task)
    def middleman_inputItemBE(self):
        table=self.homePage.CreateBETable
        inputItem=self.homePage.BEInputItem
        task="CreateBE"
        self.pre_addTable(table, inputItem, task)
    def middleman_inputItemUpdateStock(self):
        table=self.homePage.UpdateStockTable
        inputItem=self.homePage.UpdateStockFind
        task="UpdateStock"
        self.pre_addTable(table, inputItem, task)
    #================================================================================================================================================
    #  DESIGN
    # 0. Chart
    def designChart(self):
        self.invoice_label.update_db()
        self.homePage.Notification.setText("WEEKLY REVENUE CHART OF THE STORE")
        # Tạo các giá trị ngày tháng bằng đối tượng datetime.date
        date_to = datetime.date.today()
        date_from = date_to - datetime.timedelta(days=7)
        
        revenue = []
        # Lặp qua các ngày và tính tổng doanh thu cho từng ngày
        for i in range((date_to - date_from).days + 1):
            sum = 0
            for j in range(len(self.invoice_label.invoiceTable)):
                invoice_date = self.invoice_label.invoiceTable[j][1].date()
                if invoice_date == date_from + datetime.timedelta(days=i):
                    sum += self.invoice_label.invoiceTable[j][3]
            revenue.append(sum)
        date = []
        # Tạo danh sách các giá trị ngày tháng dạng chuỗi để sử dụng cho trục x
        for i in range((date_to - date_from).days + 1):
            date.append((date_from + datetime.timedelta(days=i)).strftime('%Y-%m-%d'))
        
        # Create chart
        fig = Figure()
        ax = fig.add_subplot(111)
        ax.plot(date, revenue, color ="black",linewidth=2)
        ax.set_xlabel("Date")
        ax.set_ylabel("Revenue")
        # Chia số tiền cho 1 triệu và hiển thị dưới dạng nhãn trên trục tung
        yticks = ax.get_yticks() * 1e-6
        yticklabels = [f"{tick:.1f}" for tick in yticks]
        ax.set_yticklabels(yticklabels)

        formatter = ticker.StrMethodFormatter("{x:,.0f}")
        ax.yaxis.set_major_formatter(formatter)

        canvas = FigureCanvasQTAgg(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.homePage.layoutChart.addWidget(canvas)
    # 1. ComboBox
    def designComboBox(self):
        #update data
        self.unit_label.update_db()
        self.item_label.update_db()
        self.supplier_label.update_db()
        #Clear old data
        self.homePage.unitItemCB.clear()
        self.homePage.supplierItemCB.clear()
        self.homePage.SMSupplier.clear()
        self.homePage.SMSupplier.addItems([str("All")])
        self.homePage.LISupplier.clear()
        self.homePage.LISupplier.addItems([str("All")])
        self.homePage.User_RoleCB.clear()

        # Design the Combo box
        for i in range (len(self.unit_label.unitTable)): #Unit Combo box  
            self.homePage.unitItemCB.addItems([str(self.unit_label.unitTable[i][1])])                  
        for i in range (len(self.supplier_label.supplierTable)): #Supplier Combo box
            self.homePage.supplierItemCB.addItems([str(self.supplier_label.supplierTable[i][1])])     
            self.homePage.SMSupplier.addItems([str(self.supplier_label.supplierTable[i][1])])
            self.homePage.LISupplier.addItems([str(self.supplier_label.supplierTable[i][1])])
        for i in range (len(self.role_label.roleTable)):
            self.homePage.User_RoleCB.addItems([str(self.role_label.roleTable[i][1])])
    # 2. RecommendBox
    def designRecommendBox(self):
        #Update data
        self.item_label.update_db() 
        self.user_label.update_db()
        self.customer_label.update_db()
        # 1. Item recommended box   
        for i in range (len(self.item_label.itemTable)):
            self.completer_item_list.append(f"{self.item_label.itemTable[i][0]} - {self.item_label.itemTable[i][1]}")
        self.completer_item = QCompleter(self.completer_item_list, self)
        self.completer_item.setCaseSensitivity(1)
        self.homePage.BEInputItem.setCompleter(self.completer_item)
        self.homePage.SMFindItem.setCompleter(self.completer_item)
        self.homePage.findItemInvoice.setCompleter(self.completer_item)
        self.homePage.LIFindItem.setCompleter(self.completer_item)
        self.homePage.UpdateStockFind.setCompleter(self.completer_item)

        # 2. User recommended box
        self.format_list_staff()
        for i in range (len(self.user_label.userTable)):
            self.completer_user_list.append(f"{self.user_label.userTable[i][0]} - {self.user_label.userTable[i][1]}")
        self.completer_user = QCompleter(self.completer_user_list, self)
        self.completer_user.setCaseSensitivity(1)
        self.homePage.BECreateUserId.setCompleter(self.completer_user)
        
        # 3. Customer recommended box
        self.customer_label.update_db()
        for i in range (len(self.customer_label.customerTable)):
            self.completer_customer_list.append(f"{self.customer_label.customerTable[i][0]} - {self.customer_label.customerTable[i][1]}")
        self.completer_customer = QCompleter(self.completer_customer_list, self)
        self.completer_customer.setCaseSensitivity(1)
        self.homePage.LCFindCustomer.setCompleter(self.completer_customer)
        self.homePage.findCustomerInvoiceInput.setCompleter(self.completer_customer)
        self.homePage.listInvoiceFindInput.setCompleter(self.completer_customer)
    # 3. Table
    #<===> 3.1 List Item Table
    def format_list_item(self, itemfilter: list, task):
        self.item_label.update_db()
        if itemfilter == []:
            self.homePage.LITable.setRowCount(0)
        else:
            self.homePage.LITable.setRowCount(0)
            for i in range(len(itemfilter)):
                rowPosition = self.homePage.LITable.rowCount()
                self.homePage.LITable.insertRow(rowPosition)
                for j in range(4):
                    self.homePage.LITable.setItem(rowPosition, j, QTableWidgetItem(str(itemfilter[i][j])))
                self.homePage.LITable.setItem(rowPosition, 4, QTableWidgetItem(str(db.execute(f"SELECT Name FROM Unit WHERE Id = {itemfilter[i][4]}").fetchone()[0])))
                self.homePage.LITable.setItem(rowPosition, 5, QTableWidgetItem(str(db.execute(f"SELECT Name FROM Suplier WHERE Id = {itemfilter[i][5]}").fetchone()[0])))
                self.homePage.LITable.setItem(rowPosition, 6, QTableWidgetItem(str(itemfilter[i][6])))
                if itemfilter[i][7] == 1:
                    self.homePage.LITable.setItem(rowPosition, 7, QTableWidgetItem(str("Available")))
                else: self.homePage.LITable.setItem(rowPosition, 7, QTableWidgetItem(str("Not available")))
            if self.loginRole == "Manager":
                for row in range(self.homePage.LITable.rowCount()):
                    button = QPushButton("Edit")
                    self.homePage.LITable.setCellWidget(row, 8, button)
                    button.clicked.connect(lambda _, itemId= int(self.homePage.LITable.item(row,0).text()): self.open_edit_item_window(itemId, itemfilter, task))
    #<===> 3.2. List Staff Table
    def format_list_staff(self):
        self.user_label.update_db()
        self.homePage.LSTable.setRowCount(0)

        for i in range(len(self.user_label.userTable)):
            rowPosition = self.homePage.LSTable.rowCount()
            self.homePage.LSTable.insertRow(rowPosition)
            for j in range(3):
                self.homePage.LSTable.setItem(rowPosition, j, QTableWidgetItem(str(self.user_label.userTable[i][j])))
            self.homePage.LSTable.setItem(rowPosition, 3, QTableWidgetItem(str(db.execute(f"SELECT RoleName FROM Role JOIN Users ON Role.Id = Users.RoleId WHERE Users.RoleId = {self.user_label.userTable[i][5]}").fetchone()[0])))
            if self.user_label.userTable[i][8] == 1: 
                self.homePage.LSTable.setItem(rowPosition, 4, QTableWidgetItem(str("Available")))
            else: self.homePage.LSTable.setItem(rowPosition, 4, QTableWidgetItem(str("Not available")))
        if self.loginRole == "Manager":
            for row in range(self.homePage.LSTable.rowCount()):
                button = QPushButton("Edit")
                self.homePage.LSTable.setCellWidget(row, 5, button)
                button.clicked.connect(lambda _, userEditId= int(self.homePage.LSTable.item(row,0).text()): self.open_edit_staff_window(userEditId))
    #<===> 3.3. List BE Table
    def format_list_BE(self, BEFilter: list):
        self.BE_label.update_db()
        if BEFilter == []:
            self.noti("No BE match your filter.")
        else:
            self.homePage.listBETable.setRowCount(0)
            if self.homePage.statusBECB.currentText() == "Not Confirmed":
                    compareStatus = 0
            elif self.homePage.statusBECB.currentText() == "Confirmed":
                    compareStatus = 1
            else: compareStatus = 2
            if compareStatus == 1 or compareStatus  == 0:
                for i in range(len(BEFilter)):
                    #ID, Date, Staff, Status
                    if BEFilter[i][4] == compareStatus:
                        rowPosition = self.homePage.listBETable.rowCount()
                        self.homePage.listBETable.insertRow(rowPosition)
                        self.homePage.listBETable.setItem(rowPosition, 0, QTableWidgetItem(str(BEFilter[i][0])))
                        self.homePage.listBETable.setItem(rowPosition, 1, QTableWidgetItem(str(BEFilter[i][1])))
                        self.homePage.listBETable.setItem(rowPosition, 2, QTableWidgetItem(str(BEFilter[i][5])))
                        self.homePage.listBETable.setItem(rowPosition, 3, QTableWidgetItem(str(BEFilter[i][2])))
                        self.homePage.listBETable.setItem(rowPosition, 4, QTableWidgetItem(str(BEFilter[i][4])))
                        self.homePage.listBETable.setItem(rowPosition, 5, QTableWidgetItem(str(BEFilter[i][3])))
            else: 
                for i in range(len(BEFilter)):
                    rowPosition = self.homePage.listBETable.rowCount()
                    self.homePage.listBETable.insertRow(rowPosition)
                    self.homePage.listBETable.setItem(rowPosition, 0, QTableWidgetItem(str(BEFilter[i][0])))
                    self.homePage.listBETable.setItem(rowPosition, 1, QTableWidgetItem(str(BEFilter[i][1])))
                    self.homePage.listBETable.setItem(rowPosition, 2, QTableWidgetItem(str(BEFilter[i][5])))
                    self.homePage.listBETable.setItem(rowPosition, 3, QTableWidgetItem(str(BEFilter[i][2])))
                    self.homePage.listBETable.setItem(rowPosition, 4, QTableWidgetItem(str(BEFilter[i][4])))
                    self.homePage.listBETable.setItem(rowPosition, 5, QTableWidgetItem(str(BEFilter[i][3])))
    #<===> 3.4. List unconfirm BE Table
    def format_list_uncf_BE(self):
        self.BE_label.update_db()
        self.BE_Detail_label.update_db()
        self.stock_label.update_db()
        self.homePage.CfBETable.setRowCount(0)
        for i in range(len(self.BE_label.BETable)):
            if (self.BE_label.BETable[i][3] == 0):
                rowPosition = self.homePage.CfBETable.rowCount()
                self.homePage.CfBETable.insertRow(rowPosition)
                self.homePage.CfBETable.setItem(rowPosition, 0, QTableWidgetItem(str(self.BE_label.BETable[i][0])))
                self.homePage.CfBETable.setItem(rowPosition, 1, QTableWidgetItem(self.BE_label.BETable[i][1].strftime('%d/%m/%Y')))
                userId = db.execute("SELECT UserId FROM BE WHERE Id = ?", self.BE_label.BETable[i][0]).fetchone()[0]
                userName = db.execute("SELECT Name FROM Users WHERE Id = ?", int(userId)).fetchone()[0]
                Name = f"{userId} - {userName}"
                self.homePage.CfBETable.setItem(rowPosition, 2, QTableWidgetItem(str(userName)))
        for row in range(self.homePage.CfBETable.rowCount()):
            button = QPushButton("Confirm")
            self.homePage.CfBETable.setCellWidget(row, 3, button)
            button.clicked.connect(lambda _, BEId = int(self.homePage.CfBETable.item(row,0).text()): self.open_confirm_BE_window(BEId))
    #<===> 3.5. List customer Table
    def format_list_customer(self, customerfilter):
        self.customer_label.update_db()
        if customerfilter == []:
            self.noti("No products match your filter.")
        else:
            self.homePage.LCTable.setRowCount(0)
            for i in range(len(customerfilter)):
                rowPosition = self.homePage.LCTable.rowCount()
                self.homePage.LCTable.insertRow(rowPosition)
                for j in range(5):
                    self.homePage.LCTable.setItem(rowPosition, j, QTableWidgetItem(str(customerfilter[i][j])))
    #<===> 3.6. List invoice Table
    def format_list_invoice(self, invoicefilter: list):
        self.invoice_label.update_db()
        if invoicefilter == []:
            
            self.noti("The system doesnt have any invoice.")
        else:
            self.homePage.listInvoiceTable.setRowCount(0)
            for i in range(len(invoicefilter)):
                rowPosition = self.homePage.listInvoiceTable.rowCount()
                self.homePage.listInvoiceTable.insertRow(rowPosition)
                for j in range(4):
                    self.homePage.listInvoiceTable.setItem(rowPosition, j, QTableWidgetItem(str(invoicefilter[i][j])))
                customerName = db.execute("SELECT Name FROM Customer WHERE Id = ?", invoicefilter[i][4]).fetchone()[0]
                staffName = db.execute("SELECT Name FROM Users WHERE Id = ?", invoicefilter[i][5]).fetchone()[0]
                self.homePage.listInvoiceTable.setItem(rowPosition, 4, QTableWidgetItem(f"{invoicefilter[i][4]} - {customerName}"))
                self.homePage.listInvoiceTable.setItem(rowPosition, 5, QTableWidgetItem(f"{invoicefilter[i][5]} - {staffName}"))
            for row in range(self.homePage.listInvoiceTable.rowCount()):
                button = QPushButton("See more detail")
                self.homePage.listInvoiceTable.setCellWidget(row, 6, button)
                button.clicked.connect(lambda _, invoiceId= int(self.homePage.listInvoiceTable.item(row,0).text()): self.open_see_detail_invoice(invoiceId))
    #<===> 3.7. Stock Table
    def format_stock(self, stockFilter):
        self.stock_label.update_db()
        if stockFilter == []:
            self.noti("No products match your filter.")
        else:
            self.homePage.SMTable.setRowCount(0)
            for i in range(len(stockFilter)):
                rowPosition = self.homePage.SMTable.rowCount()
                self.homePage.SMTable.insertRow(rowPosition)
                for j in range(4):
                    self.homePage.SMTable.setItem(rowPosition, j, QTableWidgetItem(str(stockFilter[i][j])))
                self.homePage.SMTable.setItem(rowPosition, 4, QTableWidgetItem(str(db.execute(f"SELECT Name FROM Unit WHERE Id = {stockFilter[i][4]}").fetchone()[0])))
                self.homePage.SMTable.setItem(rowPosition, 5, QTableWidgetItem(str(db.execute(f"SELECT Name FROM Suplier WHERE Id = {stockFilter[i][5]}").fetchone()[0])))
                self.homePage.SMTable.setItem(rowPosition, 6, QTableWidgetItem(str(stockFilter[i][6])))
                self.homePage.SMTable.setItem(rowPosition, 7, QTableWidgetItem(str(db.execute(f"SELECT amount FROM STOCK WHERE itemID = {stockFilter[i][0]}").fetchone()[0])))
                if stockFilter[i][7] == 1:
                    self.homePage.SMTable.setItem(rowPosition, 8, QTableWidgetItem(str("Available")))
                else: self.homePage.SMTable.setItem(rowPosition, 8, QTableWidgetItem(str("Not available")))


    #================================================================================================================================================
    # DEFAUT PAGE
    # 1. Create Item
    def default_createItem(self):
        self.homePage.NameItem.setText("")
        self.homePage.descriptionItem.setText("")
        self.homePage.priceItem.setText("")
    # 2. Create an invoice
    def defaut_createInvoice(self):
        self.homePage.findCustomerInvoiceInput.setText("")
        self.homePage.findItemInvoice.setText("")
        self.homePage.itemInvoice.setRowCount(0)
        self.homePage.totalInvoice.setText("")
        self.homePage.customerInfo.setText("")
        self.spinboxes.clear() 
    # 3. Create BE
    def defaut_createBE(self):
        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("dd/MM/yyyy HH:mm:ss")
        self.homePage.BECreateDate.setText(f"{formatted_datetime}")
        self.homePage.BECreateId.setText(f"{len(self.BE_label.BETable) + 10001}")
        self.homePage.CreateBETable.setRowCount(0)
        self.homePage.BECreateUserId.setText("")
        self.homePage.BEInputItem.setText("")
    # 4. Create Customer
    def defaut_createCustomer(self):
        self.homePage.CUName.setText("")
        self.homePage.CUPhone.setText("")
        self.homePage.CUEmail.setText("")
        self.homePage.CUAddress.setText("")
    # 5. List Invoice
    def default_listInvoice(self):
        self.homePage.LCFindCustomer.setText("")
        current_datetime = QDateTime.currentDateTime()
        self.homePage.dateInvoiceTo.setDateTime(current_datetime)
        self.homePage.dateInvoiceTo.setDisplayFormat('dd/MM/yyyy')

        DateFrom_datetime = current_datetime.addMonths(-2)
        self.homePage.dateInvoiceFrom.setDateTime(DateFrom_datetime)
        self.homePage.dateInvoiceFrom.setDisplayFormat('dd/MM/yyyy')
    # 6. List BE
    def default_listBE(self):
        current_datetime = QDateTime.currentDateTime()
        self.homePage.CredateBETo.setDateTime(current_datetime)
        self.homePage.CredateBETo.setDisplayFormat('dd/MM/yyyy')

        DateFrom_datetime = current_datetime.addMonths(-2)
        self.homePage.CredateBEFrom.setDateTime(DateFrom_datetime)
        self.homePage.CredateBEFrom.setDisplayFormat('dd/MM/yyyy')
    # 7. Update Stock
    def default_updateStock(self):
        self.homePage.UpdateStockReason.setText("")
        self.homePage.UpdateStockFind.setText("")
        self.homePage.UpdateStockTable.setRowCount(0)
    # 8. User Information
    def default_userInformation(self):
        id = self.loginUserId
        name = db.execute("SELECT Name FROM Users WHERE Id = ?", id).fetchone()[0]
        phone = db.execute("SELECT Phone FROM Users WHERE Id = ?", id).fetchone()[0]
        address = db.execute("SELECT Address FROM Users WHERE Id = ?", id).fetchone()[0]
        email = db.execute("SELECT Email FROM Users WHERE Id = ?", id).fetchone()[0]
        roleId = db.execute("SELECT RoleID FROM Users WHERE Id = ?", id).fetchone()[0]
        role = db.execute("SELECT RoleName FROM Role WHERE Id = ?", roleId).fetchone()[0]
        username = db.execute("SELECT Username FROM Users WHERE Id = ?", id).fetchone()[0]
        password = db.execute("SELECT Password FROM Users WHERE Id = ?", id).fetchone()[0]

        self.homePage.InfoID.setText(f"{id}")
        self.homePage.InfoName.setText(f"{name}")
        self.homePage.InfoPhone.setText(f"{phone}")
        self.homePage.InfoAddress.setText(f"{address}")
        self.homePage.InfoEmail.setText(f"{email}")
        self.homePage.InfoRole.setText(f"{role}")
        self.homePage.InfoUsername.setText(f"{username}")
        self.homePage.InfoPassword.setText(f"{password}")

    # 9. Create User 
    def default_createUser(self):
        self.homePage.User_Name.setText("")
        self.homePage.User_Phone.setText("")
        self.homePage.User_Address.setText("")
        self.homePage.User_Email.setText("")
    # 10. Stock
    def default_stock(self):
        self.homePage.SMLabel.setCurrentText("All")
        self.homePage.SMSupplier.setCurrentText("All")
        self.homePage.SMStatus.setCurrentText("All")
    # 11. Create Supplier
    def default_createSupplier(self):
        self.homePage.NameSupplier.setText("")
        self.homePage.AddressSupplier.setText("")
        self.homePage.PhoneSupplier.setText("")
        self.homePage.EmailSupplier.setText("")
    
    #================================================================================================================================================
    # FUNCTION TO CREATE SOMETHING
    # 1. Create BE (BE and BE_detail)
    def createBE(self):
        if self.homePage.BECreateUserId.text() == "":
            self.noti("You must input UserId!")
        else:
            try:
                userId, userName = str(self.homePage.BECreateUserId.text()).split(" - ")
                self.BE_label.createBE(self.homePage.BECreateId.text(), userId)
                for i in range (self.homePage.CreateBETable.rowCount()):
                    self.BE_Detail_label.createBE_Detail(int(self.homePage.BECreateId.text()),int(self.homePage.CreateBETable.item(i,0).text()),int(self.homePage.CreateBETable.cellWidget(i,2).value()))
                self.noti('Buying Entry imported successfully!')
                self.defaut_createBE() 
            except ValueError:
                self.noti('Value Error!')
            except Exception as e:
                self.noti(f'Have error: {e}!')
    # 2. Create Invoice (Invoice and Invoice_detail)
    def createInvoice(self):
        itemInvoice_list = []
        if self.homePage.itemInvoice.rowCount == 0:
            self.noti("You must input item before creating invoices!")
        else:
            if self.homePage.findCustomerInvoiceInput.text() == "":
                customerId = ""
            else: customerId, customerName = str(self.homePage.findCustomerInvoiceInput.text()).split(" - ")
            invoiceId = len(self.invoice_label.invoiceTable) + 10001
            totalDisplay = self.totalDisplay()
            self.invoice_label.createInvoice(invoiceId, self.homePage.methodInvoice.currentText(), int(totalDisplay), customerId, "1000")
            for i in range (self.homePage.itemInvoice.rowCount()):
                spinBox = self.homePage.itemInvoice.cellWidget(i, 3)
                value = spinBox.value()
                itemInvoice_dict = {"itemId": int(self.homePage.itemInvoice.item(i, 0).text()), "deviation": -int(value)}
                itemInvoice_list.append(itemInvoice_dict)
                self.invoiceDetail_label.createInvoice_Detail(invoiceId, int(self.homePage.itemInvoice.item(i, 0).text()), int(value), int(self.homePage.itemInvoice.item(i, 4).text()))
            self.invoiceDetail_label.updateStock_afterSELL(invoiceId, itemInvoice_list)
            self.noti("Create invoice successfully!")
            self.defaut_createInvoice()
    

    #===============================================================================================================================================
    # FUNCTION TO FILTER
    # 1. List Items
    def LIFilter(self):
        Itemfilter = []
        # Get the selected label, supplier, and status values
        label_value = self.homePage.LILabel.currentText()
        supplier_value = self.homePage.LISupplier.currentText()
        status_value = self.homePage.LIStatus.currentText()
        # Check if "All" is selected for any of the filters
        if label_value == "All":
            label_value = None
        if supplier_value == "All":
            supplier_value = None
        if status_value == "All":
            status_value = None
        # Generate the filter based on the selected values
        if label_value is not None and supplier_value is not None and status_value is not None:
            Itemfilter = list(filter(lambda x: x[3] == label_value and x[5] == int(db.execute(f"SELECT Id FROM Suplier WHERE Name = '{supplier_value}'").fetchone()[0]) and x[7] == (1 if status_value == "Available" else 0), self.item_label.itemTable))
        elif label_value is not None and supplier_value is not None and status_value is None:
            Itemfilter = list(filter(lambda x: x[3] == label_value and x[5] == int(db.execute(f"SELECT Id FROM Suplier WHERE Name = '{supplier_value}'").fetchone()[0]), self.item_label.itemTable))
        elif label_value is not None and supplier_value is None and status_value is not None:
            Itemfilter = list(filter(lambda x: x[3] == label_value and x[7] == (1 if status_value == "Available" else 0), self.item_label.itemTable))
        elif label_value is not None and supplier_value is None and status_value is None:
            Itemfilter = list(filter(lambda x: x[3] == label_value, self.item_label.itemTable))
        elif label_value is None and supplier_value is not None and status_value is not None:
            Itemfilter = list(filter(lambda x: x[5] == int(db.execute(f"SELECT Id FROM Suplier WHERE Name = '{supplier_value}'").fetchone()[0]) and x[7] == (1 if status_value == "Available" else 0), self.item_label.itemTable))
        elif label_value is None and supplier_value is not None and status_value is None:
            Itemfilter = list(filter(lambda x: x[5] == int(db.execute(f"SELECT Id FROM Suplier WHERE Name = '{supplier_value}'").fetchone()[0]), self.item_label.itemTable))
        elif label_value is None and supplier_value is None and status_value is not None:
            Itemfilter = list(filter(lambda x: x[7] == (1 if status_value == "Available" else 0), self.item_label.itemTable))
        else:
            Itemfilter = self.item_label.itemTable

        return Itemfilter
    # 2. List Customers
    def LCFilter(self):
        self.customer_label.update_db()
        customerfilter = []
        text = str(self.homePage.LCFindCustomer.text())
        if " - " in text:
            customerId, customerName = text.split(" - ")
            phone = db.execute(f"SELECT Phone FROM Customer WHERE Id = {customerId}").fetchone()[0]
            email = db.execute(f"SELECT Email FROM Customer WHERE Id = {customerId}").fetchone()[0]
            address = db.execute(f"SELECT Address FROM Customer WHERE Id = {customerId}").fetchone()[0]
            customerfilter = [(customerId, customerName, phone, email, address)]
        return customerfilter
    # 3. List Invoices
    def invoiceFilter(self):
        self.invoice_label.update_db()
        invoiceFilter = []
        displayTest = ""
        check = True
        text = str(self.homePage.listInvoiceFindInput.text())
        if text != "":
            if " - " in text:
                customerId, customerName = text.split(" - ")
                customerId_test = db.execute("SELECT * FROM Customer WHERE Id = ?", customerId).fetchone()[0]
                customerName_test = db.execute("SELECT Name FROM Customer WHERE Id = ?", customerId).fetchone()[0]
                if not customerId_test or not customerName_test:
                    check = False
                    displayTest += "The customer information input is invalid.\n"
        date_to = self.homePage.dateInvoiceTo.dateTime().toPyDateTime()
        date_from = self.homePage.dateInvoiceFrom.dateTime().toPyDateTime()
        if date_from > date_to:
            check = False
            displayTest += "Start date must be before end date.\n"
        if check == False:
            displayTest += "Please re-input!"
            self.noti(displayTest)
        else:
            for i in range (len(self.invoice_label.invoiceTable)):
                date_str = db.execute("SELECT BuyingDate FROM Invoice WHERE Id = ?", (self.invoice_label.invoiceTable[i][0])).fetchone()[0]
                date_obj = datetime.datetime.strptime(date_str.strftime('%d/%m/%Y'), '%d/%m/%Y')
                if text == "":
                    if self.invoice_label.invoiceTable[i][1].date() >= date_from.date() and self.invoice_label.invoiceTable[i][1].date() <= date_to.date():
                        invoiceFilter.append(self.invoice_label.invoiceTable[i])
                else:
                    if int(customerId) == self.invoice_label.invoiceTable[i][4]:
                        if self.invoice_label.invoiceTable[i][1] >= date_from and self.invoice_label.invoiceTable[i][1] <= date_to:
                            invoiceFilter.append(self.invoice_label.invoiceTable[i])
        return invoiceFilter
    # 4. List BE
    def BEFilter(self):
        self.BE_label.update_db()
        listBEFilter = []
        draft = []
        displayTest = ""
        check = True
        cre_date_to = self.homePage.CredateBETo.dateTime().toPyDateTime()
        cre_date_from = self.homePage.CredateBEFrom.dateTime().toPyDateTime()
        if self.homePage.statusBECB.currentText() == "Confirmed":
            status = 1
        elif self.homePage.statusBECB.currentText() == "Not confirmed":
            status = 0
        else: status = 2
        if cre_date_from > cre_date_to:
            check = False
            displayTest += "With creation day, start date must be before end date.\n"
        if check == False:
            displayTest += "Please re-input!"
            self.noti(displayTest)
            
        else:
            
            for i in range (len(self.BE_label.BETable)):
                if status == 2:
                    if self.BE_label.BETable[i][1].date() >= cre_date_from.date() and self.BE_label.BETable[i][1].date() <= cre_date_to.date():
                        listBEFilter.append(self.BE_label.BETable[i])
                else:
                    if self.BE_label.BETable[i][1].date() >= cre_date_from.date() and self.BE_label.BETable[i][1].date() <= cre_date_to.date() and self.BE_label.BETable[i][3] == status:
                        draft.append(self.BE_label.BETable[i])
                    listBEFilter = list(filter(lambda x: x[3] == status, draft))
        return listBEFilter
    # 5. Stock
    def stockFilter(self):
        stockFilter = []
        # Get the selected label, supplier, and status values
        label_value = self.homePage.SMLabel.currentText()
        supplier_value = self.homePage.SMSupplier.currentText()
        status_value = self.homePage.SMStatus.currentText()
        # Check if "All" is selected for any of the filters
        if label_value == "All":
            label_value = None
        if supplier_value == "All":
            supplier_value = None
        if status_value == "All":
            status_value = None
        # Generate the filter based on the selected values
        if label_value is not None and supplier_value is not None and status_value is not None:
            stockFilter = list(filter(lambda x: x[3] == label_value and x[5] == int(db.execute(f"SELECT Id FROM Suplier WHERE Name = '{supplier_value}'").fetchone()[0]) and x[7] == (1 if status_value == "Available" else 0), self.item_label.itemTable))
        elif label_value is not None and supplier_value is not None and status_value is None:
            stockFilter = list(filter(lambda x: x[3] == label_value and x[5] == int(db.execute(f"SELECT Id FROM Suplier WHERE Name = '{supplier_value}'").fetchone()[0]), self.item_label.itemTable))
        elif label_value is not None and supplier_value is None and status_value is not None:
            stockFilter = list(filter(lambda x: x[3] == label_value and x[7] == (1 if status_value == "Available" else 0), self.item_label.itemTable))
        elif label_value is not None and supplier_value is None and status_value is None:
            stockFilter = list(filter(lambda x: x[3] == label_value, self.item_label.itemTable))
        elif label_value is None and supplier_value is not None and status_value is not None:
            stockFilter = list(filter(lambda x: x[5] == int(db.execute(f"SELECT Id FROM Suplier WHERE Name = '{supplier_value}'").fetchone()[0]) and x[7] == (1 if status_value == "Available" else 0), self.item_label.itemTable))
        elif label_value is None and supplier_value is not None and status_value is None:
            stockFilter = list(filter(lambda x: x[5] == int(db.execute(f"SELECT Id FROM Suplier WHERE Name = '{supplier_value}'").fetchone()[0]), self.item_label.itemTable))
        elif label_value is None and supplier_value is None and status_value is not None:
            stockFilter = list(filter(lambda x: x[7] == (1 if status_value == "Available" else 0), self.item_label.itemTable))
        else:
            stockFilter = self.item_label.itemTable

        return stockFilter

    #================================================================================================================================================
    # FUNCTON TO FIND THE INFORMATION
    # 1. Item
    def FindItem(self):
        itemfilter = []
        text = str(self.homePage.LIFindItem.text())
        if " - " in text:
            itemId, itemName = text.split(" - ")
            try:
                description = db.execute(f"SELECT Description FROM Item WHERE Id = {itemId}").fetchone()[0]
                label = db.execute(f"SELECT Label FROM Item WHERE Id = {itemId}").fetchone()[0]
                price = db.execute(f"SELECT Price FROM Item WHERE Id = {itemId}").fetchone()[0]
                status = db.execute(f"SELECT Status FROM Item WHERE Id = {itemId}").fetchone()[0]
                unitId = db.execute(f"SELECT UnitId FROM Item WHERE Id = {itemId}").fetchone()[0]
                supplierId = db.execute(f"SELECT SupplierId FROM Item WHERE Id = {itemId}").fetchone()[0]
                itemfilter = [(itemId, itemName, description, label, unitId, supplierId, price, status)]
            except ValueError:
                self.noti("Value Error!")
            except Exception as e:
                self.noti(f"Error: {e}")
        return itemfilter
    # 2. Invoice (from inputting customer information)
    def findInvoice(self):
        invoiceFilter = []
        text = str(self.homePage.listInvoiceFindInput.text())
        if " - " in text:
            customerId, customerName = text.split(" - ")
            for i in range(len(self.invoice_label.invoiceTable)):
                invoice_draft = ()
                if self.invoice_label.invoiceTable[i][4] == int(customerId):
                    invoice_draft = (self.invoice_label.invoiceTable[i][0], self.invoice_label.invoiceTable[i][1], self.invoice_label.invoiceTable[i][2], self.invoice_label.invoiceTable[i][3], self.invoice_label.invoiceTable[i][4], self.invoice_label.invoiceTable[i][5])
                    invoiceFilter.append(invoice_draft)
        return invoiceFilter
    # 3. Stock
    def FindItemStock(self):
        stockFilter = []
        text = str(self.homePage.SMFindItem.text())
        if " - " in text:
            itemId, itemName = text.split(" - ")
            try:
                description = db.execute(f"SELECT Description FROM Item WHERE Id = {itemId}").fetchone()[0]
                label = db.execute(f"SELECT Label FROM Item WHERE Id = {itemId}").fetchone()[0]
                price = db.execute(f"SELECT Price FROM Item WHERE Id = {itemId}").fetchone()[0]
                status = db.execute(f"SELECT Status FROM Item WHERE Id = {itemId}").fetchone()[0]
                unitId = db.execute(f"SELECT UnitId FROM Item WHERE Id = {itemId}").fetchone()[0]
                supplierId = db.execute(f"SELECT SupplierId FROM Item WHERE Id = {itemId}").fetchone()[0]
                stockFilter = [(itemId, itemName, description, label, unitId, supplierId, price, status)]
            except ValueError:
                self.noti("Value Error!")
            except Exception as e:
                self.noti(f"Error: {e}")
        return stockFilter

    #================================================================================================================================================
    # UPDATE DATA
    # 1. Spinboxes data
    def update_spinboxes(self):
        for spinbox in self.spinboxes:
            spinbox.valueChanged.connect(self.updateTotal)
    # 2. Total Price each item when update amount
    def updateTotal(self):
        # get the spinbox that triggered the signal
        spinbox = self.sender()
        # get the row and column index of the spinbox in the table
        row = self.homePage.itemInvoice.indexAt(spinbox.pos()).row()
        column = self.homePage.itemInvoice.indexAt(spinbox.pos()).column()
        # calculate the new total value based on the spinbox value and price
        price = int(self.homePage.itemInvoice.item(row, 2).text())
        amount = spinbox.value()
        total = price * amount
        # update the total value in the table
        self.homePage.itemInvoice.setItem(row, 4, QTableWidgetItem(str(total)))
        self.totalDisplay()
    # 3. Stock Data
    def updateStock(self):
        check = True
        displayTest = ""
        # 3.1. Check the condition
        if self.homePage.UpdateStockTable.rowCount() == 0:
            check = False
            displayTest += "You haven't inputted any product to update yet.\n"
        if self.homePage.UpdateStockReason == "":
            check = False
            displayTest += "You haven't inputted reason to update yet.\n"
        if check == False:
            displayTest += "Please re-input."
            self.noti(displayTest)
        else:
            try:
                for i in range (self.homePage.UpdateStockTable.rowCount()):
                    amount = int(self.homePage.UpdateStockTable.item(i,2).text())
                    itemId= int(self.homePage.UpdateStockTable.item(i,0).text())
                    try:
                        db.execute("UPDATE STOCK SET amount = ? WHERE itemId = ?", (amount, itemId))
                        db.commit()
                    except ValueError:
                        self.noti("Value Error!")
                    except Exception as e:
                        self.noti(f"Error: {e}")
            except ValueError:
                self.noti("Value Error!")
            except Exception as e:
                self.noti(f"Error: {e}")
            self.default_updateStock()
            self.noti("Updated successfully!")

    #================================================================================================================================================
    # DISPLAY SOMETHING INFORMATION ON THE SCREEN 
    # 1. Display Customer information when enter find the customer in "CREATE AN INVOICE"
    def customerDisplay(self):
        customerID, customerName = str(self.homePage.findCustomerInvoiceInput.text()).split(" - ")
        try:
            customerPhone = db.execute("SELECT Phone FROM Customer WHERE Id = ?", customerID).fetchone()[0]
            customerEmail = db.execute("SELECT Email FROM Customer WHERE Id = ?", customerID).fetchone()[0]
            self.homePage.customerInfo.setText(f"1. Customer ID: {customerID}\n2. Customer Name: {customerName}\n3. Customer Phone Number: {customerPhone}\n4. Customer Email: {customerEmail}")
        except ValueError:
            self.noti("Value Error!")
        except Exception as e:
            self.noti(f"Error: {e}")
    # 2. Display the total when user input the item in "CREATE AN INVOICE"
    def totalDisplay(self):
        totalPrice = 0
        for i in range(self.homePage.itemInvoice.rowCount()):
            totalPrice += int(self.homePage.itemInvoice.item(i, 4).text())
            totalPrice_display = locale.currency(totalPrice, grouping=True).replace(",00", "")
        self.homePage.totalInvoice.setText(str(totalPrice_display))
        return totalPrice

    #================================================================================================================================================    
    # FUNCTION TO ADD ITEM INTO THE TABLE
    def deleteLineInput(self, lineInput: QLineEdit):
        lineInput.setText("")
        
    def pre_addTable(self, table: QTableWidgetItem, lineInput: QLineEdit, task):
        # Get the selected text from the completer
        
        if lineInput.text() == "":
            self.noti("You must input the item id!")
        else:
            # Split the selected text into Item ID and name
            item_id, item_name = str(lineInput.text()).split(" - ")

            # Define the amount cell
            if item_id in self.product_counts:
                self.product_counts[item_id] += 1
            else:
                self.product_counts[item_id] = 1

            if task == "CreateBE": 
                self.addTable_detail_BE(table,  item_id, item_name)
            elif task == "Invoice":
                self.addTable_detail_Invoice(table,  item_id, item_name)
            elif task == "UpdateStock":
                self.addTable_detail_UpdateStock(table, item_id, item_name)
        self.deleteLineInput(lineInput)
    # 1. Add to "Create BE" Table      
    def addTable_detail_BE(self, table: QTableWidgetItem, item_id, item_name):
        # If the item is not in the table, add it to the end
        check = False
        for i in range(table.rowCount()):
            if table.item(i, 0).text() == item_id:  
                amount = table.cellWidget(i, 2).value() + 1
                table.cellWidget(i, 2).setValue(amount)
                check = True
        
        if check == False:    
            row_position = table.rowCount()
            table.insertRow(row_position)
            table.setItem(row_position, 0, QTableWidgetItem(item_id))
            table.setItem(row_position, 1, QTableWidgetItem(item_name))
            spinbox = QSpinBox(table) # Create spinBox for amount value
            spinbox.setRange(1, 999)
            spinbox.setValue(1)
            table.setCellWidget(row_position, 2, spinbox)
    # 2. Add to "Create an invoice" Table
    def addTable_detail_Invoice(self, table: QTableWidgetItem, item_id, item_name):
        # If the item is not in the table, add it to the end
        check = False
        for i in range(table.rowCount()):
            if table.item(i, 0).text() == item_id:  
                amount = table.cellWidget(i, 3).value() + 1
                table.cellWidget(i, 3).setValue(amount)
                total = int(table.cellWidget(i, 3).value()) * int(table.item(i, 2).text())
                table.setItem(i,4, QTableWidgetItem(str(total)))
                check = True
        
        if check == False:
            row_position = table.rowCount()
            table.insertRow(row_position)
            table.setItem(row_position, 0, QTableWidgetItem(item_id))
            table.setItem(row_position, 1, QTableWidgetItem(item_name))
            price = db.execute(f"SELECT Price FROM Item WHERE Id = {item_id}").fetchone()[0]
            table.setItem(row_position, 2, QTableWidgetItem(str(price)))
            spinbox = QSpinBox(table) # Create spinBox for amount value
            spinbox.setRange(1, 999)
            spinbox.setValue(1)
            self.spinboxes.append(spinbox)
            table.setCellWidget(row_position, 3, spinbox)
            total = int(table.cellWidget(row_position, 3).value()) * int(table.item(row_position, 2).text())
            table.setItem(row_position,4, QTableWidgetItem(str(total)))
            self.update_spinboxes()
        
        self.totalDisplay()
    # 3. Add to "Update Stock Modifier" Table
    def addTable_detail_UpdateStock(self, table: QTableWidgetItem, item_id, item_name):
        #check if the item is not in table, create new row
        check = False
        for i in range(table.rowCount()):
            if table.item(i, 0).text() == item_id:  
                check = True
        if check == False:
            row_position = table.rowCount()
            table.insertRow(row_position)
            table.setItem(row_position, 0, QTableWidgetItem(item_id))
            table.setItem(row_position, 1, QTableWidgetItem(item_name))
  
    #================================================================================================================================================
    # OPEN OTHER WINDOW
    # 1. Notification Screen  
    def noti(self, displayTest): 
        self.notiWindow = QtWidgets.QMainWindow()
        self.notiUI = ui.ui_notiWindow.Ui_MainWindow()
        self.notiUI.setupUi(self.notiWindow)
        self.notiUI.lineEdit.setText(displayTest)
        self.notiWindow.show()
    # 2. Confirm BE Screen
    def open_confirm_BE_window(self, BEId: int):
        self.confirm_BE_window = confirmBEWindow(BEId)
        self.confirm_BE_window.show()
        self.confirm_BE_window.closed.connect(lambda: self.format_list_uncf_BE)
    # 3. Edit Item Screen
    def open_edit_item_window(self,itemId, itemfilter, task):
        self.edit_item_window = editItem(itemId)
        self.edit_item_window.show()
        self.edit_item_window.closed.connect(lambda: self.update_main_window(itemfilter, task))
    def update_main_window(self, itemfilter, task):
        self.item_label.update_db()
        if task == "filter":
            itemfilter = self.LIFilter()
        elif task == "find":
            itemfilter = self.FindItem()
        else: 
            itemfilter = self.item_label.itemTable
        self.format_list_item(itemfilter, task)
    # 4. Edit Staff Screen
    def open_edit_staff_window(self, userId):
        self.edit_staff_window = EditStaff(userId)
        self.edit_staff_window.show()
    def open_see_detail_invoice(self, invoiceId):
        pass
    def open_changePassword(self):
        userId = self.homePage.InfoID.text()
        self.changePassword = ChangePassword(userId)
        self.changePassword.show()
    def return_loginPage(self):
        loginPage = login()
        widget.resize(800,600)
        widget.addWidget(loginPage)
        widget.setCurrentIndex(widget.currentIndex()+1)
    

if __name__ == "__main__":
    loginUserId =None
    app = QApplication(sys.argv)
    window = login(loginUserId)
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(window)
    widget.resize(800,600)
    widget.show()
    sys.exit(app.exec())

