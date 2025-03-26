'''
-----------------------------------------------------------
    Program Title: Task2_ExpenseTracker.py
    Description:Expense tracker is a python program designed 
                to help users manage and monitor their expenses. 
                By inputting data about their spending, users 
                can categorize expenses, track their financial 
                habits, and make informed decisions to better 
                manage their budgets in the future.
    Features:   User login to system to use expense tracker system
                User management
                    - Allow users to add a new expense with details 
                    such as description, amount, category, and date/time.
                    - Allow users to update the record.
                    - Allow users to delete the record.
                View all expenses
                Display a list of all recorded expenses and categories
                Search expense by category or date/time
    Additions:  Create detailed reports of expenses, optionally saving them to a file.
                Set a budget limit and track expenses against it, alerting when limits are approached or exceeded.
                Support multiple users, each with their own expense data.
    Author: David Rogers
    Date Created: 4/12/2024
    Last Modified: 11/01/2025
    Version: 1.0 - Add pseudocode and test database connectivity
             1.1 - Add date/time string manipulation to be more readable
             1.2 - Add initial menu structure and login page
             2.0 - Add ability to login and set a budget
             2.1 - Add ability to create users
             2.2 - Add abiltiy to add new transactions
             2.3 - Add ability to search transactions by category
             2.4 - Add ability to update transactions and fix date formats 
             2.5 - Add ability to delete transactions and fix Amount formats
                 - Update code documentation!
             2.6 - Add ability to Add, Update and Delete Categories
             2.7 - Add Budget monitoring, fix delete of transaction and
                 - neaten up code for long string lines
             3.0 - Start adding Reports
             3.1 - Finish adding Reports and testing
             3.2 - Finish adding Search By Date and Search By Time
             3.3 - Clean up interface
             3.4 - Improve code reuse with more function abstractions
             3.5 - Update transaction lists to tabulate reports
             3.6 - Fix up code documentation - function descriptions
             4.0 - Testing + Added error checking to get/set Data functions
             4.1 - Testing and fixing empty database conditions
             4.2 - Testing and update addTrans to offer new category
             4.3 - Allow user to save report as custom filename
             4.4 - Testing - fix blank catID in addCat()
             4.5 - Extract Report 'save to file' as seperate function
             4.6 - Testing and fix updateCat and minor interface fixes
-----------------------------------------------------------
'''

# import modules
import pyodbc
from datetime import datetime
from art import logo
import getpass
import re
from tabulate import tabulate
import msvcrt
import sys
import os
import time


# global variables
userID = ""


def clrScreen():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        Description:    Makes an OS call to clear the terminal screen
        Args:           nil
        Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    os.system('cls')
    return


def isValidName(name):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Takes a name string and trys to match it against a
                    regular expression set of valid characters for a 
                    person's name.
    Args:           name: a persons name as a string
    Returns:        True: It is a valid name
                    False: name contains invalid characters
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Define the pattern for a valid name: only alphabetic characters, spaces, and hyphens
    pattern = r'^[A-Za-z\s\-]+$'
    
    # Check if the name matches the regular expression pattern
    if re.match(pattern, name):
        return True
    else:
        return False


def isValidDate(dateString, dateFormat="%d-%m-%Y"):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Takes a date string and trys to parse it into a
                    datetime object. If no error occurs, it is a
                    valid date in the correct format.
    Args:           dateString (string): Any date string
                    dateFormat (string): The desired date format
    Returns:        True: It is a valid date
                    False: It is not a valid date
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    try:
        # Try to parse the date string into a datetime object
        datetime.strptime(dateString, dateFormat)
        # If no error occurs, the date is valid
        return True  
    except ValueError:
        # If an error occurs, the date is invalid
        return False  


def isValidTime(timeString, timeFormat="%H:%M"):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Takes a time string and trys to parse it into a
                    datetime object. If no error occurs, it is a
                    valid time.
    Args:           timeString (string): Any time string
                    timeFormat (string): The desired time format
    Returns:        True: It is a valid time
                    False: It is not a valid time
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    try:
        # Try to parse the time string into a datetime object
        datetime.strptime(timeString, timeFormat)
        # If no error occurs, the time is valid
        return True  
    except ValueError:
        # If an error occurs, the time is invalid
        return False  


def hasTwoDecimalPlaces(value):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Takes a numeric value (float) and compares it to a 
                    regular expression pattern to determine if the
                    value has only 2 decimal places
    Args:           value (float): a float value
    Returns:        True: It does have 2 decimal places
                    False: It does not have 2 decimal places
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Regular expression to match numbers with exactly two decimal places
    pattern = r'^\d+\.\d{2}$'
    return bool(re.match(pattern, value))


def getData (sql):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Connects to an Azure SQL database (within a max
                    of 5 retries), gets data from the database based
                    on a supplied SQL statement and then closes the
                    connection.
    Args:           sql (string): a valid SELECT SQL statement
    Returns:        row: database records as a list of tuples 
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Connection string
    connectionString = f'Driver={{ODBC Driver 18 for SQL Server}};' \
                         'Server=tcp:djr040.database.windows.net,1433;' \
                         'Database=Exp_Tracker;' \
                         'Uid=djr040;Pwd=;' \
                         'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    
    # Set connection retries before giving up
    maxRetries = 5
    retries = 0
    
    # Connect to the SQL Server
    while retries < maxRetries:
        try:
            conn = pyodbc.connect(connectionString)
            break

        # Check for database connectivity issues
        except pyodbc.OperationalError as e:
            print ('Waiting on Azure Database Server to spin up...')
            retries += 1

        except pyodbc.InterfaceError as e:
            print (f"InterfaceError: {e}. Unable to connect to the database.")
            return None  # Exit early if there's an issue with the database interface

        except pyodbc.Error as e:
            print (f"Database connection error: {e}. Retrying... ({retries + 1}/{maxRetries})")
            retries += 1
    
        except Exception as e:
            print (f"An unexpected error occurred: {e}.")
            return None  # Exit early on any other unexpected errors

    # If the connection fails after max retries, return None
    if retries == maxRetries:
        print (f"Failed to connect to the database after {maxRetries} retries.")
        return None

    try:
        # Create a cursor object to interact with the database
        cursor = conn.cursor()
        cursor.execute(sql) 
        rows = cursor.fetchall()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Return rows 
        return (rows)

    except pyodbc.Error as e:
        print (f"Error executing the query: {e}")
        return None


def setData (sql):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Connects to an Azure SQL database, sets data in 
                    the database based on a supplied SQL statement
                    (either UPDATE, INSERT INTO or DELETE) and then 
                    closes the connection.
    Args:           sql (string): a valid UPDATE, INSERT INTO or DELETE SQL 
                    statement.
    Returns:        Nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Connection string
    connectionString = f'Driver={{ODBC Driver 18 for SQL Server}};' \
                         'Server=tcp:djr040.database.windows.net,1433;' \
                         'Database=Exp_Tracker;' \
                         'Uid=djr040;Pwd=;' \
                         'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        
    # Set connection retries before giving up
    maxRetries = 5
    retries = 0

    while retries < maxRetries:
        try:
            # Connect to the SQL Server
            conn = pyodbc.connect(connectionString)
            break

        # Check for database connectivity issues
        except pyodbc.OperationalError as e:
            print (f"OperationalError: {e}. Retrying... ({retries + 1}/{maxRetries})")
            retries += 1
            time.sleep(2)  # Wait for 2 seconds before retrying

        except pyodbc.InterfaceError as e:
            print (f"InterfaceError: {e}. Unable to connect to the database.")
            return  # Exit early if there's an issue with the database interface

        except pyodbc.Error as e:
            print (f"Database connection error: {e}. Retrying... ({retries + 1}/{maxRetries})")
            retries += 1
            time.sleep(2)  # Wait for 2 seconds before retrying

        except Exception as e:
            print (f"An unexpected error occurred: {e}.")
            return  # Exit early on any other unexpected errors

    # If the connection fails after max retries, return
    if retries == maxRetries:
        print (f"Failed to connect to the database after {maxRetries} retries.")
        return

    try:
        # Create a cursor object to interact with the database
        cursor = conn.cursor()
        cursor.execute(sql) 
        
        # Committ the transaction
        conn.commit()
    
    except pyodbc.Error as e:
        print (f"Error executing SQL statement: {e}")
        
        # Rollback any changes if the transaction fails
        conn.rollback()  
        print ("Expense transaction rolled back due to error.")

    # Close the connection
    cursor.close()
    conn.close()
     
    return


def pause():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Asks the user to 'Press any key to continue'. 
                    This allows the user to review information on 
                    the screen before continuing
    Args:           Nil
    Returns:        Nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    print("Press any key to continue...")
    # Wait for a key press
    msvcrt.getch()  
    return


def isValidFilename(filename):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Tests if a filename is valid under Windows
    Args:           filename: a string
    Returns:        True: the filename is valid under Windows
                    False: the filename is invalid under Windows
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    invalidCharacters = r'["/\\:*?<>|]'  # Windows invalid characters
    reservedNames = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'LPT1', 'LPT2', 'LPT3'}

    # Check if filename contains invalid characters
    if re.search(invalidCharacters, filename):
        print(f"\nError: Filename contains invalid characters.")
        return False

    # Check for reserved filenames (for Windows)
    baseName = os.path.basename(filename).upper()  # case insensitive comparison
    fName, ext = os.path.splitext(baseName) # split into filename and extension
    if fName in reservedNames:
        print(f"\nError: Filename is a reserved name.")
        return False
    
    # Check if filename is blank
    if filename == '':
        print(f"\nError: Filename cannot be blank.")
        return False
    
    # Check if the filename has an extension and if the extension is exactly 3 characters long
    _, ext = os.path.splitext(filename)  # Split into filename and extension
    if not ext:  # If there's no extension
        print(f"\nError: Filename must have an extension.")
        return False

    if len(ext) != 4:  # Extension should be 3 characters + the dot (i.e., '.txt', '.csv', etc.)
        print(f"\nError: Extension must be exactly 3 characters long (e.g., .txt, .csv).")
        return False
    
    # If no issues, the filename is considered valid
    return True


def showCats():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Connect to the database and return a list of the
                    current categories. Display the list of current
                    categories, if available.
    Args:           Nil
    Returns:        validCats: A list of valid Category ID's
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    validCats = []
    cats = getData('SELECT * FROM categories;')

    if cats == []:
        return (validCats)    
    else:
        # Display the current list of categories
        print ('ID \tCategory')
        for cat in cats:
            catRow = (cat[0] + '\t' + cat[1])
            validCats.append(cat[0]) # Create a list of valid category ID's
            print (catRow)
        return (validCats)


def fixDate(dateToFix):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Recieve a date in format yyyy-mm-dd and return
                    it in the format dd-mm-yyyy
    Args:           dateToFix: A date to convert
    Returns:        fixedDate: A date converted from yyyy-mm-dd to dd-mm-yyyy
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # convert the date string to a datetime object
    getDate = datetime.strptime(str(dateToFix),'%Y-%m-%d')
    
    # amend the new datetime object to the correct format
    fixedDate = datetime.strftime(getDate, '%d-%m-%Y')
    return(fixedDate)


def convertDate(dateToFix):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Recieve a date in format dd-mm-yyyy and return
                    it in the format yyyy-mm-dd for submission to
                    SQL
    Args:           dateToFix : A date to convert
    Returns:        convertedDate : A date converted from dd-mm-yyyy to
                    yyyy-mm-dd
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Convert the string 'dateToFix' to a datetime object
    getDate = datetime.strptime(dateToFix, "%d-%m-%Y")
    
    # Convert the datetime object to the SQL format (yyyy-mm-dd)
    convertedDate = getDate.strftime("%Y-%m-%d")
    return (convertedDate)


def fixAmt(amtToFix):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Recieve a string amount and format it to have 
                    2 decimal places and a dollar sign
    Args:           amtToFix: An string to be converted to $0.00
    Returns:        fixedAmt: An amount converted to currency with 2 
                    decimal places
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # format amtToFix to be 2 decimal places and have a $ sign
    fixedAmt = "$" + "{:.2f}".format(amtToFix)
    
    return(fixedAmt)


def buildTrans(trans):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Recieve a list of transactions, fix the date and
                    amounts in each row and display a simple report
                    of the transactions
    Args:           trans: a list of transactions
    Returns:        validTranIDs: a list of transaction IDs presented
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    validTranIDs = []
    if trans != []:
        for tran in trans:
            # cycle through the transactions and fix the date and amount formats
            tran[1]=fixDate(tran[1])
            tran[5]=fixAmt(tran[5])    
            # build a list of current valid transaction ID's to return
            validTranIDs.append(tran[0])
        
        # Output a report of transactions using the tabulate module
        headers = ['TranID', 'Date', 'Time', 'Category', 'Description', 'Amount']    
        report = (tabulate(trans, headers, tablefmt="simple", colalign=("right", "right", "right", "center", "left", "right")))
        print (report)
    else:
        return (validTranIDs)
        
    return (validTranIDs)


def loginUser ():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Asks the user to enter their login information
                    (password is supressed) and check these details
                    against the users table in the database. It will
                    give the user 4 attempts to enter their correct
                    login information. 
    Args:           Nil
    Returns:        Nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Import the current userID
    global userID
    validUser = False
    retries = 0
    # Repeat request for user details until valid user received or retries > 3
    while not validUser and retries < 3:
        uID = input('Please enter your user ID: ') 
        pwd = getpass.getpass('Please enter your password: ')
        
        print ()
        print ('Please wait while I validate your credentials')
        
        # Check these details against the database
        rows = getData ("SELECT * FROM users WHERE userID='" + uID + "'")
        
        # If the database request returns rows of data
        if rows != []:
            for row in rows:
                userID = row[0]
                password = row[1]

                # Check the password entered is correct
                # and welcome the user
                if pwd == password.strip():
                    print ()
                    print ('Welcome ' + row[2])
                    pause ()
                    validUser = True
                    return # To Main 
                else:
                    print ('Incorrect Password. Please try again.')
        else:
            print ('That is not a valid user ID. Please try again.')
            retries += 1
    if retries >= 3:
        print ('Login Attemps exceeded. Sorry you are not allowed entry to this system.')
        quit ()
    else:
        return # To Main


def createUser ():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Creates a new unique UserID and requests the 
                    user provide their information (First/Last Name,
                    Password, Budget Amount) and uploads these details
                    to the database.
    Args:           Nil
    Returns:        Nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    print ()
    print ("Accessing the database to create your new user entry")
    
    # Create a new unique UserID starting at 1001 if the database is new
    lastUserID = getData("SELECT MAX(userID) FROM users")
    
    if lastUserID[0][0] == None:
        newUserID = 1001
    else:
        # Extract the lastUserID from the database returned list of tuples
        lastUserID = ''.join(map(str, lastUserID[0]))
        newUserID = int(lastUserID) + 1
    
    # Advise the user of their new UserID
    print ('Your UserID will be ' + str(newUserID))
    
    # Ask the user for their details (test for validitiy)
    # Password, First Name, Last Name and Budget Amount
    validPwd = False
    while not validPwd:
        # user enters their new password (supressed)
        newPwd = getpass.getpass('Please enter your password: ')
        if newPwd == '' or len(newPwd) > 20:
            print ('Your password cannot be blank and must be less than 20 characters.')
        else:
            validPwd = True
    validFName = False
    while not validFName:
        newFName = input('Please enter your First Name: ')
        if newFName == '' or len(newFName) > 15 or not isValidName(newFName):
            print ('That is not a valid First Name. Please Try again.')
        else:
            validFName = True
    validLName = False
    while not validLName:
        newLName = input('Please enter your Last Name: ')
        if newLName == '' or len(newLName) > 15 or not isValidName(newLName):
            print ('That is not a valid last name. Please try again.')
        else:
            validLName = True
    validBudget = False
    while not validBudget:
        newBudget = input('Please enter you budget limit (in 0.00 format): $')
        if newBudget == '' or float(newBudget) <= 0 or not hasTwoDecimalPlaces(newBudget):
            print ('That is not a valid budget amount. Please try again.')
        else:
            validBudget = True
    
    # Insert the new UserID and the user's information into the database
    sql = "INSERT INTO users (userID, userPwd, fName, lName, userBudget) " \
          "VALUES (" + str(newUserID) + ", '" + newPwd + "', '" + newFName + "', '" + newLName + "', " + str(newBudget) + ")"
    setData(sql)
    
    pause ()
    clrScreen ()

    return # To login screen


def addTrans ():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Provides User with a list of available Categories
                    and asks User to enter (validated) details about 
                    the new transaction (Date, Time, Category, 
                    Description and Amount). Creates a new unique
                    Transction ID and uploads the information to the
                    transactions table. Takes the current global UserID
                    and updates the userTransactions table with
                    userID and tranID to maintain m2m relationship.
    Args:           Nil
    Returns:        Nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Import the current userID
    global userID
    clrScreen()
    print ()
    print ("========================================================================")
    print ("\t \t ADD A NEW EXPENSE TRANSACTION")
    print ("========================================================================")
    print ()
    print ('Here are the available categories:')
    print ()

    # Get a list of current categories from the database and
    # display the list for the user
    validCats = showCats()
    print ()

    # Check if any of these categories is suitable for the new transaction
    validAns = False
    while not validAns:
        suitableCat = input ('Is there a suitable category for your Expense Transaction (y/n)?: ')
        if suitableCat.lower() == 'y':
            validAns = True
        elif suitableCat.lower() == 'n':
            validAns = True
            # Add a category and return here
            addCat()
            # Clear the screen and replay the menu title
            clrScreen()
            print ()
            print ("========================================================================")
            print ("\t \t ADD A NEW EXPENSE TRANSACTION")
            print ("========================================================================")
            print ()
            print ('Here are the available categories:')
            print ()
            # Display the current categories and return a list of valid category ID's
            validCats = showCats()
            print()
        else:
            print ('That is not a valid answer. Please Try Again.')
    
    # Ask the user to select a current category and validate
    validCategory = False
    while not validCategory:    
        catID = input('Please enter the Category ID for your expense transaction: ')
        if catID in validCats:
            break
        else:
            print ('That is not an available Category ID. Please try again.')

    # Ask the user to enter transaction information and validate
    validDate = False
    while not validDate:
        tranDate = input('Please enter the expense transaction date in dd-mm-yyyy format: ')
        if isValidDate(tranDate):
            validDate = True
        else:
            print('That is not a valid date. Please try again.')
    validTime = False
    while not validTime:
        tranTime = input('Please enter the time of the transaction in hh:mm format: ')
        if isValidTime(tranTime):
            validTime = True
        else:
            print('That is not a valid time. Please try again.')
    validDesc = False
    while not validDesc:
        tranDesc = input('Please enter the expense transaction description in 50 characters or less: ')
        if len(tranDesc) <= 50 and tranDesc != '':
            validDesc = True
        else:
            print('That is not a valid description. Please try again.')
    validAmt = False
    while not validAmt:
        tranAmt = input('Please enter the expense transaction amount in 0.00 format: $')
        if hasTwoDecimalPlaces(tranAmt) and float(tranAmt) > 0:
            validAmt = True
        else:
            print('That is not a valid amount. Please try again.')
    
    # Create a new unique TranID by adding 1 to the current maximum TranID
    tranID = []
    trans = getData ("SELECT MAX(tranID) FROM transactions")
    
    if trans[0][0] != None:
        for tran in trans:
            tranID = tran[0]
        tranID = int(tranID) + 1
    else:
        # if this is the first transaction use tranID 1000
        tranID = 1000
    
    # Build a SQL statement to INSERT the collected tranaction details
    # into the tranactions table in the database.
    sql = ("SET DATEFORMAT dmy;"\
           "INSERT INTO transactions (tranID, tranDate, tranTime, catID, tranDescription, tranAmount) "\
           "VALUES ('" + str(tranID) + "','" + str(tranDate) + "', '" + str(tranTime) + "', '" + str(catID) + "', '" + tranDesc + "', '" + str(tranAmt) + "')")
    setData (sql)

    # Build a SQL statement to INSERT the current UserID and new TranID
    # into the userTransactions table in the database.
    sql = ("INSERT INTO userTransactions (userID, tranID) "\
           "VALUES ('" + str(userID) + "', '" + str(tranID) + "')")
    setData(sql)

    print ()
    print ('Expense transaction added successfully.')
    print ()

    # Do a budget check after the new transaction has been added
    checkBud()
    pause ()
    
    return # To transMenu


def getTranByCat():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Search the database for all the transactions for the
                    requested category for the current user and return a 
                    list of valid TranID's
    Args:           Nil
    Returns:        validTranIDs: a list of tranID's found
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # import the current UserID 
    global userID

    clrScreen()
    print ()
    print ("========================================================================")
    print ("\t   SEARCH FOR AN EXPENSE TRANSACTION BY CATEGORY")
    print ("========================================================================")
    print ()
    print ('Here are the available categories:')
    print ()
    
    # Search the database for current list of valid categories
    # Print out a table of valid categories for the user to select
    validCats = showCats()
    print ()

    if validCats != []:
        # Ask the user which category they wish to search for tranactions 
        validCategory = False
        while not validCategory:    
            catID = input('Please enter a Category ID to find Expense Transactions for: ')
            if catID in validCats:
                break
            else:
                print ('That is not a currently available Category ID. Please try again.')
    else:
        return
    
    print ()
    
    # Build a SQL SELECT statement to return transactions for the selected category
    # that relate to the current User
    sql = ("SELECT transactions.tranID, tranDate, tranTime, categories.catName, tranDescription, tranAmount "\
            "FROM userTransactions "\
            "INNER JOIN transactions on transactions.tranID = userTransactions.tranID "\
            "INNER JOIN users on users.userID = userTransactions.userID "\
            "INNER JOIN categories on transactions.catID = categories.catID "\
            "WHERE users.userID=" + str(userID) + " "\
            "AND categories.catID=" + str(catID) + " "\
            "ORDER BY tranDate;")
    trans = getData(sql)

    # Build a list of transactions with correctly formatted dates and amounts and display the list 
    validTranIDs = buildTrans(trans)
    
    # return a list of valid Transaction ID's 
    return (validTranIDs)


def getTranByDate(tranDate):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Recieve a valid date, search the database for
                    transactions from that date for the current user, 
                    display the list of transactions and return a 
                    list of valid Transaction ID's 
    Args:           tranDate (dd-mm-yyyy)
    Returns:        validTranIDs: a list of tran ID's
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # import the current UserID 
    global userID

    clrScreen()
    print ()
    print ("========================================================================")
    print ("\t    SEARCH FOR AN EXPENSE TRANSACTION BY DATE")
    print ("========================================================================")
    print ()

    # Build a SQL SELECT statement to return transactions for the selected date
    # that relate to the current User
    sql = ("SELECT transactions.tranID, tranDate, tranTime, categories.catName, tranDescription, tranAmount "\
            "FROM userTransactions "\
            "INNER JOIN transactions on transactions.tranID = userTransactions.tranID "\
            "INNER JOIN users on users.userID = userTransactions.userID "\
            "INNER JOIN categories on transactions.catID = categories.catID "\
            "WHERE users.userID=" + str(userID) + " "\
            "AND tranDate = '" + convertDate(str(tranDate)) + "' "\
            "ORDER BY tranDate;")
    trans = getData(sql)

    # If there are transactions returned then
    # Build a list of transactions with correctly formatted dates and amounts and display the list 
    if trans != []:
        validTranIDs = buildTrans(trans)
    else:
        print ('You have no expense transactions with that date.')
        pause ()
        validTranIDs = []

    # return a list of valid Transaction ID's 
    return (validTranIDs)


def getTranByTime(tranTime):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Recieve a valid time, search the database for
                    transactions from that time for the current user, 
                    display the list of transactions and return a 
                    list of valid Transaction ID's 
    Args:           tranTime (hh:mm)
    Returns:        validTranIDs: a list of tran ID's   
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # import the current UserID 
    global userID

    clrScreen()
    print ()
    print ("========================================================================")
    print ("\t    SEARCH FOR AN EXPENSE TRANSACTION BY TIME")
    print ("========================================================================")
    print ()

    # Build a SQL SELECT statement to return transactions for the selected time
    # that relate to the current User
    sql = ("SELECT transactions.tranID, tranDate, tranTime, categories.catName, tranDescription, tranAmount "\
            "FROM userTransactions "\
            "INNER JOIN transactions on transactions.tranID = userTransactions.tranID "\
            "INNER JOIN users on users.userID = userTransactions.userID "\
            "INNER JOIN categories on transactions.catID = categories.catID "\
            "WHERE users.userID=" + str(userID) + " "\
            "AND tranTime = '" + tranTime + "' "\
            "ORDER BY tranDate;")
    trans = getData(sql)

    # If there are transactions returned then
    # Build a list of transactions with correctly formatted dates and amounts and display the list 
    if trans != []:
        validTranIDs = buildTrans(trans)
    else:
        validTranIDs = []
    
    # return a list of valid Transaction ID's if available 
    return (validTranIDs)


def updateByTranID(tranID):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Update the elements of a transaction with a given
                    tranID. Display the existing transaction and ask
                    the user which element they want to update. Issue
                    a SQL UPDATE statement to make the changes in 
                    the database.
    Args:           tranID (string): a transaction ID
    Returns:        Nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """    
    
    clrScreen()
    print ()
    print ("========================================================================")
    print ("\t \t UPDATE AN EXPENSE TRANSACTIONS DETAILS ")
    print ("========================================================================")
    print ()

    # Build a SQL statement to return the current details of 
    # the transaction
    sql = ("SELECT tranID, tranDate, tranTime, categories.catName, tranDescription, tranAmount "\
          "FROM transactions "\
          "INNER JOIN categories on transactions.catID = categories.catID "\
          "WHERE tranID=" + str(tranID))

    trans = getData(sql)

    # Build a list of transactions with correctly formatted dates and amounts and display the list 
    buildTrans(trans)
    
    # Provide user with a list of elements to update
    # Or return to the previous menu
    print ()
    print ('\t (1) DATE')
    print ('\t (2) TIME')
    print ('\t (3) CATEGORY')
    print ('\t (4) DESCRIPTION')
    print ('\t (5) AMOUNT')
    print ('\t (R)ETURN')
    print ()
    
    # Get a valid tranaction element to work with
    validSelection = False
    while not validSelection:
        fieldToUpdate = input('Press a number to update a field for expense transaction ' + tranID + ': ')
        
        # Change the transactions date
        if fieldToUpdate == '1':
            validSelection = True
            validDate = False
            while not validDate:
                newDate = input('Please enter a new date (dd-mm-yyyy): ')
                if isValidDate(newDate):
                    validDate = True
                    # Build the SQL String to UPDATE the tranDate
                    sql = "UPDATE transactions "\
                          "SET tranDate='" + str(convertDate(newDate)) + "' "\
                          "WHERE tranID=" + str(tranID)
                else:
                    print ('This is not a valid date. Please try again.')

        # Change a transactions time
        elif fieldToUpdate == '2':
            validSelection = True
            validTime = False
            while not validTime:
                newTime = input('Please enter a new time (hh:mm): ')
                if isValidTime(newTime):
                    validTime = True
                    # Build a SQL String to UPDATE the tranTime
                    sql = "UPDATE transactions "\
                          "SET tranTime='" + str(newTime) + "' "\
                          "WHERE tranID=" + str(tranID)
                else:
                    print ('This is not a valid time. Please try again.')

        # Change a transactions Category
        elif fieldToUpdate == '3':
            validSelection = True
            print ('Here are the available categories:')
            print ()
            # Display the list of current Categories to the user
            validCats = showCats()
            print ()
            
            # Get a valid new category to make the transaction a part of
            validCat = False
            while not validCat:
                newCat = input('Enter the Category you want to change to: ')
                if newCat in validCats:
                    # Build a SQL UPDATE statement to update the tranID's 
                    # Category in the database
                    sql = "UPDATE transactions "\
                          "SET catID='" + str(newCat) + "' "\
                          "WHERE tranID=" + str(tranID)
                    validCat = True
                else:
                    print ('That is not a valid existing category. Please try again.')

        # Change a transactions description            
        elif fieldToUpdate == '4':
            validSelection = True
            validDesc = False
            while not validDesc:
                newDesc = input('Please enter the new description: ')
                if newDesc != '' and len(newDesc) <= 50:
                    validDesc = True
                    # Build a SQL UPDATE statement to update the transactions description
                    sql = "UPDATE transactions "\
                          "SET tranDescription='" + str(newDesc) + "' "\
                          "WHERE tranID=" + str(tranID)
                else:
                    print ('That is not a valid description. Please try again.')
        
        # Change a transactions amount
        elif fieldToUpdate == '5':
            validSelection = True
            validAmt = False
            while not validAmt:
                newAmt = input('Please enter the new amount in 0.00 format: $')
                if hasTwoDecimalPlaces(newAmt) and float(newAmt) > 0:
                    validAmt = True
                    # Builde a SQL UPDATE statement to update the transactions amount    
                    sql = "UPDATE transactions "\
                          "SET tranAmount=" + str(newAmt) + " "\
                          "WHERE tranID=" + str(tranID)
                else:
                    print('This is not a valid amount. Please try agin.')

        # Return to the previous menu
        elif fieldToUpdate.lower() == 'r':
            validSelection = True
            return
        else:
            print ('That is not a valid selection. Please try again.') 
    
    # Send the created SQL statement to the database to update
    setData(sql)
    
    # Confirm with the user that the record has been updated successfully
    print ()
    print ('Expense Transaction Record updated successfully!')
    print ('Here is the new record -:')
    print ()
    
    # Build a SQL statement to return the newly update transaction
    sql = ("SELECT tranID, tranDate, tranTime, categories.catName, tranDescription, tranAmount "\
          "FROM transactions "\
          "INNER JOIN categories on transactions.catID = categories.catID "\
          "WHERE tranID=" + str(tranID))
    trans = getData(sql)

    # Build a list of transactions with correctly formatted dates and amounts and display the list 
    buildTrans(trans)
    
    # Do a budget check now that a transaction has been updated
    print ()
    checkBud()
    pause ()
    
    return
    

def deleteByTranID(tranID):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Takes a valid tranID and builds a DELETE SQL 
                    statement. Connects to the database and executes
                    the DELETE statements
    Args:           tranID (string): A valid transaction ID
    Returns:        Nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    clrScreen()
    print ()
    print ("========================================================================")
    print ("\t \t   DELETE AN EXPENSE TRANSACTION")
    print ("========================================================================")
    print ()
    
    # Build a SQL statment to return the current transactions details from
    # the database.
    sql = ("SELECT tranID, tranDate, tranTime, categories.catName, tranDescription, tranAmount "\
          "FROM transactions "\
          "INNER JOIN categories on transactions.catID = categories.catID "\
          "WHERE tranID=" + str(tranID))
    trans = getData(sql)

    # Build a list of transactions with correctly formatted dates and amounts and display the list 
    buildTrans(trans)
    
    # Print a warning to the user
    print ()
    print ('Please note: The Action CANNOT be undone')
    print ()

    # Confirm the user wants to DELETE the current transaction
    validAns = False
    while not validAns:
        ans = input ("Please confirm that you wish to DELETE transaction number " + tranID + " (y/n): ")
        if ans.lower() == 'y':
            # Build the SQL DELETE statement to delete the user/trans record from userTransactions table
            sql = ("DELETE FROM userTransactions WHERE tranid='" + tranID + "';")
            setData (sql)            
            # Build the SQL DELETE statement to delete the current transaction record from transactions table
            sql = ("DELETE FROM transactions WHERE tranid='" + tranID + "';")
            validAns = True
            # Send the SQL DELETE request to the database
            setData (sql)
            print ("Expense Transaction Successfully DELETED")
        elif ans.lower() == 'n':
            break
        else:
            print ('That is not a valid answer. Please try again.')
    
    # Do a budget check now that a transaction has been deleted
    print()
    checkBud()
    pause ()
    
    return


def addCat():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Function Name:  addCat
    Description:    Add a new valid category to the database. The
                    Category ID and Name must not already exist and
                    must not be blank.
    Args:           nil
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    clrScreen()
    print ()
    print ("========================================================================")
    print ('\t                   ADD A NEW CATEGORY')
    print ("========================================================================")
    print ()
    print ('Current Categories:')
    print ()

    # Display a list of current categories
    validCatIDs = []
    validCatNames = []
    rows = getData('SELECT * FROM categories;')
    if rows != []:
        print ('ID \tCATEGORY')
        for row in rows:
            catRow = (row[0] + '\t' + row[1])
            validCatIDs.append(row[0])
            validCatNames.append(row[1])
            print (catRow)
    else:
        print ('There are no current categories.')
    
    print()

    # Get details of the new category from the user
    # Get a valid Category ID
    validID = False
    while not validID:
        newCatID = input ('Please enter a new Category ID between 1000 and 9999: ')
        if newCatID != '':
            if int(newCatID) > 9999 or int(newCatID) < 1000 or newCatID in validCatIDs:
                print ('That ID is not valid. Please try again.')
                print ('Valid category IDs are between 1000 and 9999 and cannot have been already used')
            else:
                # Exit the loop and move on to Category Name
                validID = True
        else:
             print ('That ID is not valid. Please try again.')
             print ('Valid category IDs are between 1000 and 9999 and cannot have been already used')
    
    # Get a valid Category Name
    validCatName = False
    while not validCatName:
        newCatName = input ('Please enter a name for the new Category: ')
        if len(newCatName) < 31 and newCatName != '' and newCatName not in validCatNames:
            validCatName = True
        else:
            print ('That is not a valid Category Name. Please try again.')

    # Build a SQL statement to INSERT INTO categories table new Category details
    sql = "INSERT INTO categories (catID, catName) " \
          "VALUES (" + newCatID + ",'" + newCatName + "')"
    # Update the database
    setData (sql)
    
    # Confirm new category created
    print ()
    print ('New Category Created')
    print ('Here is the new list of Categories:')
    print ()
    # Display the current categories
    showCats()
    print ()
    pause ()

    # Clear the screen and return to a previous menu
    clrScreen()
    return #To previous menu


def updateCat():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Present the user with a list of the current 
                    categories and allow them to update a category
                    name.
    Args:           nil
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    clrScreen()
    print ()
    print ("========================================================================")
    print ('                    UPDATE A CATEGORY')
    print ("========================================================================")
    print ()
    print ('Current Categories:')
    
    # Display a list of current categories
    validCatIDs = []
    validCatNames = []
    rows = getData('SELECT * FROM categories;')
    if rows != []:
        print ('ID \tCATEGORY')
        for row in rows:
            catRow = (row[0] + '\t' + row[1])
            validCatIDs.append(row[0])
            validCatNames.append(row[1])
            print (catRow)
    else:
        print ('There are no categories available.')
        print ('Return to the previous menu and use (A)DD to add a Category')
        print ()
        pause ()
        return # To catMenu
        
    print()

    # Get a valid Category ID to update
    validCatID = False
    while not validCatID:
        catID = input ('What is the Category ID you wish to update?: ')
        if catID in validCatIDs:
            validCatID = True
        else:
            print ('This is not a valid Category ID. Please try again.')

    # Get a valid Category Name for the update
    validCatName = False
    while not validCatName:
        newCatName = input ('What name do you want this category to be?: ')
        if newCatName not in validCatNames and newCatName !='' and len(newCatName) <= 30:
            validCatName = True
        else:
            print ('That is not a valid category name. Please try again.')

    sql = ("UPDATE categories "\
           "SET catName='" + newCatName + "' "\
           "WHERE catID=" + catID)
    setData (sql)

    # Confirm new category created
    print ()
    print ('Category Name Updated')
    print ()
    print ('Here is the updated list of Categories:')
    print ()
    # Display the current categories
    showCats()
    print ()
    pause ()
    
    # Clear the screen and return to a previous menu
    clrScreen()
    return # To catMenu


def deleteCat():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Present the user a with a list of the current
                    categories. Ask which Category they wish to 
                    delete. Ensure there are no transactions 
                    associated with that category and delete the
                    category record.
    Args:           nil 
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    clrScreen()
    print ()
    print ("========================================================================")
    print ('                        DELETE A CATEGORY')
    print ("========================================================================")
    print ()
    print ('Current Categories:')

    # Display a list of current categories
    validCatIDs = []
    validCatIDs = showCats()
    print()

    if validCatIDs == []:
        print ('There are no Categories to Delete.')
        print ()
        pause ()
        return # To catMenu

    # Get a valid Category ID to delete
    validCatID = False
    while not validCatID:
        catID = input ('What is the Category ID you wish to delete?: ')
        if catID in validCatIDs:
            validCatID = True
        else:
            print ('This is not a valid Category ID. Please try again.')
    
    # Test if there are any TranIDs with that CatID
    tranIDs = []
    sql = ("SELECT * FROM transactions WHERE catID=" + catID)
    tranIDs = getData(sql)
    if tranIDs != []:
        print()
        print('You cannot delete that Category - there are expense transactions associated with it.')
        print('The administrator will first need to delete all the existing transactions from all users.')
        print()
        pause()
        return # To catMenu
    else:
        sql=("DELETE FROM categories WHERE catID='" + catID + "';")
        setData(sql)
        print ('Category Deleted successfully')

    # Display an updated list of Categories
    print()
    showCats()
    print()

    pause()
    # Clear the screen and return to a previous menu
    clrScreen()
    return # To catMenu


def getBud():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Get the budget amount for the current
                    User and return it with 2 decimal places
    Args:           Nil
    Returns:        budget (float): Amount with 2 decimal places
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Import the current userID
    global userID
    
    # Get the current budget amount for the current user from the database
    bud = getData("SELECT userBudget FROM users WHERE userID=" + userID)
    
    # Extract the Budget amount from database returned list of tuples
    # and fix it to be a float with 2 decimal places
    bud = ''.join(map(str, bud[0]))
    budget = float(bud)
    budget = "{:.2f}".format(budget)
    
    # return the current budget amount
    return (budget)


def updateBud():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Update the budget amount for the current user in
                    the database.
    Args:           nil
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Import the current userID
    global userID
    validInput = False
    while not validInput:
        bud = input ('What would you like your budget to be (In 0.00 format): $')
        
        # Validate the new budget amount
        if hasTwoDecimalPlaces(bud) and bud != '' and float(bud) > 0:
            # Send UPDATE SQL statement to the database to update users table with
            # new budget amount
            setData("UPDATE users SET userBudget=" + bud +" WHERE userID=" + userID)
            print ('Your budget is now set to $',bud)
            validInput = True
        else:
            print ('Please enter a valid amount for your budget.')
    
    pause()
    # Clear the screen and return to a previous menu
    clrScreen()
    return # To budMenu


def checkBud():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Update the budget amount for the current user in
                    the database.
    Args:           nil
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # use the current logged in userID
    global userID
    totalTranAmt = 0
    
    # Get the users current budget amount
    userBudget = getBud()
    
    # fix the amount format to currency with 2 decimal places
    userBudget = float(userBudget)
    fixBudAmt = fixAmt(userBudget)

    # Get the total of all transaction amounts for the current user
    sql = ("SELECT tranAmount " \
           "FROM userTransactions " \
           "INNER JOIN transactions on transactions.tranID = userTransactions.tranID " \
           "INNER JOIN users on users.userID = userTransactions.userID " \
           "WHERE users.userID=" + str(userID))
    tranAmts = getData(sql)
    for tranAmt in tranAmts:
        totalTranAmt += tranAmt[0]

    # fix the amount format to currency with 2 decimal places
    totalTranAmt = float(totalTranAmt)
    fixTranAmt = fixAmt(totalTranAmt)
    
    print ()
    print ('All your expenses currently total ' + str(fixTranAmt))
    print ('Your budget is currently set to ' + str(fixBudAmt))
    print ()
    
    # Check if the total transactions are now Under Budget, Within 90% of the Budget, Over Budget.
    if float(totalTranAmt) < (float(userBudget) * 0.9):
        print ('UNDER BUDGET: Your total tranactions are less than 90% of your Budget Amount.')
    elif (float(totalTranAmt) < float(userBudget)) and (float(totalTranAmt) > (float(userBudget) * 0.9)):
        print ('UNDER BUDGET Note: You have reached 90% of your current budget.')
    else:
        print ("OVER BUDGET: You have now exceeded your current budget.")
    
    print ()
    
    return


def saveToFile (repHead, report):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Accepts a report header and report content, requests
                    a filename from the user and saves the report header,
                    the report and budget information to an external
                    file.
    Args:           repHead: string (The report header)
                    report: string (The report to save) 
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """

    filePath = "./Reports/"
    # Check if ./Reports/ folder exists, if not, create it
    os.makedirs(filePath, exist_ok=True)
    # Get a valid filename to save file to
    validFilename = False
    while not validFilename:
        fName = input ('\nEnter a filename for the report: ')
        # test if this is a valid filename
        if isValidFilename(fName):
            validFilename = True
        else:
            print ('That is not a valid filename in Windows. Please try again.')
    # Build the full file path
    fPathName = filePath + fName
    # Overwrite (or create) the file with the latest report
    # Write the heading
    with open(fPathName, "w") as file:
        file.write(repHead)
    # Append the report data to the heading
    with open(fPathName, "a") as file:
        file.write(report)
    # Append the output from checkBud() to the report    
    with open(fPathName, "a") as file:
        # Redirect stdout to the file
        sys.stdout = file  
        checkBud()  
        # Restore stdout to normal
        sys.stdout = sys.__stdout__
    print ('\nYour Report has been written to ' + str(fPathName))
    return



def currTranRep():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Builds a report to output to the screen all
                    the users current tranactions. Offer the user
                    the ability to save report to an external file.
    Args:           nil 
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Import the current userID
    global userID
    clrScreen ()
    print ()
    print ("========================================================================")
    print ("\t \t     ALL EXPENSES REPORT")
    print ("========================================================================")
    print ()

    print ('This is a report of all your expenses to date:')
    print ()

    # Build a SQL SELECT statement to return all this users transactions
    sql = ("SELECT tranDate, tranTime, categories.catName, tranDescription, tranAmount "\
            "FROM userTransactions "\
            "INNER JOIN transactions on transactions.tranID = userTransactions.tranID "\
            "INNER JOIN users on users.userID = userTransactions.userID "\
            "INNER JOIN categories on transactions.catID = categories.catID "\
            "WHERE users.userID=" + str(userID) + " "\
            "ORDER BY tranDate;")

    # Request the data from the database
    reportData = getData(sql)

    # Cycle through the reportData list and fix date and amount format 
    for data in reportData:
        # fix the date format to read dd-mm-yyyy
        data[0] = fixDate(data[0])
        # fix the amount format to be currency with 2 decimal places
        data[4] = fixAmt(data[4])

    if reportData != []:
        # Build the report for the user
        headers = ['Date', 'Time', 'Category', 'Description', 'Amount']
        report = tabulate(reportData, headers, tablefmt="pretty", colalign=("right", "right", "center", "left", "right"))
        # Provide the user with their Report and Budget information
        print (report)
        checkBud ()
        pause ()

        # Offer the user the option of saving the report to a file
        clrScreen ()
        print ()
        print ("========================================================================")
        print ("\t \t     SAVE THE ALL EXPENSES REPORT")
        print ("========================================================================")
        print ()
        print (report)
        print ()
        repHead = "========================================================================" \
                  + "\n" + "\t \t \t \t   ALL EXPENSES REPORT" + "\n" \
                  + "========================================================================" \
                  + "\n"
        
        validSelection = False
        while not validSelection:
            writeToFile = input('Would you like to save this report to a file? (y/n): ')
            if writeToFile == 'y':
                validSelection = True
                # write the Report header and report to a file
                saveToFile (repHead, report)
            elif writeToFile == 'n':
                validSelection = True
                break
            else:
                print('That is not a valid selection. Please try again.')
        print()
    else:
        print ('There are no expenses to report.')
    
    print()
    pause()

    # Clear the screen and return to a previous menu
    clrScreen()
    return # To repMenu


def tranByCatRep():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Builds a report to output to the screen all
                    the users tranactions for a requested Category. 
                    Offer the user the ability to save report to an 
                    external file.
    Args:           Nil  
    Returns:        Nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Import the current userID
    global userID
    clrScreen()
    print ()
    print ("========================================================================")
    print ("\t \t \t CATEGORIES REPORT")
    print ("========================================================================")
    print ()

    print ('This report will provide you with all your expenses for a requested category.')
    print ()

    # Get a list of current categories from the database
    validCats = showCats()
    
    if validCats == []:
        print ('There are no Categories to report on.')
        print ()
        pause ()
        return # To repMenu

    # Ask the user to select a current category and validate
    validCategory = False
    while not validCategory:    
        catID = input('Please enter the Category ID to report on: ')
        if catID in validCats:
            break
        else:
            print ('That is not an available Category ID. Please try again.')
    
    # Build a SQL SELECT statement to return transactions for this user under the
    # requested Category
    sql = ("SELECT tranDate, tranTime, categories.catName, tranDescription, tranAmount "\
            "FROM userTransactions "\
            "INNER JOIN transactions on transactions.tranID = userTransactions.tranID "\
            "INNER JOIN users on users.userID = userTransactions.userID "\
            "INNER JOIN categories on transactions.catID = categories.catID "\
            "WHERE users.userID=" + str(userID) + " "\
            "AND categories.catID=" + str(catID) + " "\
            "ORDER BY tranDate;")

    # Request the data from the database
    reportData = getData(sql)
    
    totalTrans = 0
    
    # Cycle through the reportData list and fix date and amount format 
    for data in reportData:
        # Get a running total of the transaction amounts for this category
        totalTrans += data[4]
        # fix the date format to read dd-mm-yyyy
        data[0] = fixDate(data[0])
        # fix the amount format to be currency with 2 decimal places
        data[4] = fixAmt(data[4])

    if reportData != []:
        # Build the report and its total using Tabulate module 
        totalTrans = fixAmt(totalTrans)   
        headers = ['Date', 'Time', 'Category', 'Description', 'Amount']
        report = (tabulate(reportData, headers, tablefmt="pretty", colalign=("right", "right", "center", "left", "right")) \
                + ('\n\n')\
                + ('Your Expenses under this category total: ' + str(totalTrans)))

        # Clear the screen and provide the user with their Report 
        # and Budget information
        clrScreen ()
        print (report)
        print()
        checkBud()
        pause()

        # Offer the user the option of saving the report to a file
        clrScreen ()
        print ()
        print ("========================================================================")
        print ("\t \t     SAVE THE CATEGORIES REPORT")
        print ("========================================================================")
        print ()
        print (report)
        print ()
        repHead = "========================================================================" \
                  + "\n" + "\t \t \t   EXPENSES BY CATEGORY REPORT" + "\n" \
                  + "========================================================================" \
                  + "\n"
        validSelection = False
        while not validSelection:
            writeToFile = input('Would you like to save this report to a file? (y/n): ')
            if writeToFile == 'y':
                validSelection = True
                # Write the report header and report to a file
                saveToFile (repHead, report)
            elif writeToFile == 'n':
                validSelection = True
                break
            else:
                print('That is not a valid selection. Please try again.')
    else:
        print('There are no expenses to report on under this Category.')

    print()
    pause()
    
    # Clear the screen and return to a previous menu
    clrScreen()
    return # To repMenu


def tranByDateRep():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Builds a report to output to the screen of
                    the users tranactions between dates entered. 
                    Offer the user the ability to save report to an 
                    external file.
    Args:           nil 
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Import the current userID
    global userID
    clrScreen ()
    print ()
    print ("========================================================================")
    print ("\t \t    EXPENSES BY DATE REPORT")
    print ("========================================================================")
    print ()

    print ('This report will provide your expenses between 2 specified dates.')
    print ()

    # Ask the user for report dates and validate
    validDate = False
    while not validDate:
        firstTranDate = input ('First Date (dd-mm-yyyy): ')
        secTranDate = input ('Second Date (dd-mm-yyyy): ')
        if (firstTranDate > secTranDate) or not isValidDate (firstTranDate) or not isValidDate (secTranDate):
            print ('These are not valid dates. Please try again.')
        else:
            validDate = True

    # Build a SQL SELECT Statement to find transactions for this user between the given dates
    sql = ("SET DATEFORMAT dmy;"\
           "SELECT tranDate, tranTime, categories.catName, tranDescription, tranAmount "\
            "FROM userTransactions "\
            "INNER JOIN transactions on transactions.tranID = userTransactions.tranID "\
            "INNER JOIN users on users.userID = userTransactions.userID "\
            "INNER JOIN categories on transactions.catID = categories.catID "\
            "WHERE users.userID=" + str(userID) + " "\
            "AND tranDate BETWEEN '" + str(firstTranDate) + "' AND '" + str(secTranDate) + "' "\
            "ORDER BY tranDate;")

    # Request the data from the database
    reportData = getData(sql)
    totalTrans = 0
    
    # Cycle through the reportData list and fix date and amount format 
    for data in reportData:
        # Get a running total of the transaction amounts for this category
        totalTrans += data[4]
        # fix the date format to read dd-mm-yyyy
        data[0] = fixDate(data[0])
        # fix the amount format to be currency with 2 decimal places
        data[4] = fixAmt(data[4])

    if reportData != []:
        # Build the report and its total using Tabulate module
        totalTrans = fixAmt(totalTrans)    
        headers = ['Date', 'Time', 'Category', 'Description', 'Amount']    
        report = (tabulate(reportData, headers, tablefmt="pretty", colalign=("right", "right", "center", "left", "right")) \
                + ('\n\n')\
                + ('Your Expenses between these dates total: ' + str(totalTrans)))

        # Clear the screen and provide the user with their Report and Budget information
        clrScreen ()
        print (report)
        checkBud()
        pause ()

        # Offer the user the option of saving the report to a file
        clrScreen ()
        print ()
        print ("========================================================================")
        print ("\t \t     SAVE THE EXPENSES BY DATE REPORT")
        print ("========================================================================")
        print ()
        print (report)
        print ()
        repHead = "========================================================================" \
                  + "\n" + "\t \t \t   EXPENSES BY DATE REPORT" + "\n" \
                  + "========================================================================" \
                  + "\n"
        validSelection = False
        while not validSelection:
            writeToFile = input('Would you like to save this report to a file? (y/n): ')
            if writeToFile == 'y':
                validSelection = True
                # Write the report header and report to a file
                saveToFile (repHead, report)
            elif writeToFile == 'n':
                validSelection = True
                break
            else:
                print('That is not a valid selection. Please try again.')
    else: 
        print ('There are no expense transactions between those dates.')

    print()
    pause()
 
    # Clear the screen and return to a previous menu
    clrScreen()
    return # To repMenu


def tranByTimeRep():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Ask the user for a date and a time range on that
                    date. Present a report of all tranactions that
                    occured for the current user. Offer the user the 
                    ability to save the report to a file.
    Args:           nil
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    # Import the current userID
    global userID
    clrScreen ()
    print ()
    print ("========================================================================")
    print ("\t \t \t  EXPENSES BY TIME REPORT")
    print ("========================================================================")
    print ()

    print ('This report will provide your expenses between 2 specified times on ')
    print ('a particular date.')
    print ()

    # Ask the user for report date and times and validate
    validDate = False
    while not validDate:
        tranDate = input ('Please enter the date you wish to search (dd-mm-yyyy): ')
        firstTranTime = input ('Please enter the starting time (hh:mm): ')
        secTranTime = input ('Please enter the ending time (hh:mm): ')
        if (firstTranTime > secTranTime) or not isValidTime (firstTranTime) or not isValidTime (secTranTime) or not isValidDate (tranDate):
            print ('These are not valid date/times. Please try again.')
        else:
            validDate = True

    # Build a SQL SELECT Statement to find transactions for this user between the given dates
    sql = ("SET DATEFORMAT dmy;"\
           "SELECT tranDate, tranTime, categories.catName, tranDescription, tranAmount "\
            "FROM userTransactions "\
            "INNER JOIN transactions on transactions.tranID = userTransactions.tranID "\
            "INNER JOIN users on users.userID = userTransactions.userID "\
            "INNER JOIN categories on transactions.catID = categories.catID "\
            "WHERE users.userID=" + str(userID) + " "\
            "AND tranDate='" + str(tranDate) + "' "\
            "AND tranTime BETWEEN '" + str(firstTranTime) + "' AND '" + str(secTranTime) + "' "\
            "ORDER BY tranDate;")

    # Request the data from the database
    reportData = getData(sql)
    totalTrans = 0
    
    # Cycle through the reportData list and fix date and amount format 
    for data in reportData:
        # Get a running total of the transaction amounts for this category
        totalTrans += data[4]
        # fix the date format to read dd-mm-yyyy
        data[0] = fixDate(data[0])
        # fix the amount format to be currency with 2 decimal places
        data[4] = fixAmt(data[4])

    if reportData != []:
        # Build the report and its total using Tabulate module
        totalTrans = fixAmt(totalTrans)    
        headers = ['Date', 'Time', 'Category', 'Description', 'Amount']    
        report = (tabulate(reportData, headers, tablefmt="pretty", colalign=("right", "right", "center", "left", "right")) \
                + ('\n\n')\
                + ('Your Expenses between these times total: ' + str(totalTrans)))

        # Clear the screen and provide the user with their Report and Budget information
        clrScreen ()
        print (report)
        checkBud()
        pause ()

        # Offer the user the option of saving the report to a file
        clrScreen ()
        print ()
        print ("========================================================================")
        print ("\t \t     SAVE THE EXPENSES BY TIME REPORT")
        print ("========================================================================")
        print ()
        print (report)
        print ()
        repHead = "========================================================================" \
                  + "\n" + "\t \t \t   EXPENSES BY TIME REPORT" + "\n" \
                  + "========================================================================" \
                  + "\n"
        validSelection = False
        while not validSelection:
            writeToFile = input('Would you like to save this report to a file? (y/n): ')
            if writeToFile == 'y':
                validSelection = True
                # Write the report header and report to a file
                saveToFile (repHead, report)
            elif writeToFile == 'n':
                validSelection = True
                break
            else:
                print('That is not a valid selection. Please try again.')
    else:
        print('There are no expense transactions between those times on that date.')

    print()
    pause()

    # Clear the screen and return to a previous menu
    clrScreen()
    return # To repMenu



def topLevelMenu():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Display the main menu
    Args:           Nil
    Returns:        Nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    validChoice = False
    while not validChoice:
        clrScreen()
        print ()
        print ("========================================================================")
        print ("\t \t \t     MAIN MENU")
        print ("========================================================================")
        
        # Display the menu options
        print ("\n")
        print ('Press:')
        print ("\t (T)RANSACTIONS")
        print ('\t (C)ATEGORIES')
        print ('\t (B)UDGET')
        print ('\t (R)EPORTS')
        print ('\t (Q)UIT')
        print ()

        # Get a valid menu choice from the user
        menuChoice = input('What would you like to do?: ')
        if menuChoice.lower() == 't':
            transMenu()
        elif menuChoice.lower() == 'c':
            catMenu()
        elif menuChoice.lower() == 'b':
            budMenu()
        elif menuChoice.lower() == 'r':
            repMenu()
        elif menuChoice.lower() == 'q':
            validChoice = True
            print ()
            print ('Goodbye')
            exit()
        else:
            print ('Invalid Choice. Please try again.')


def transMenu():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    A sub level menu allowing users to Search by
                    Transaction ID or Add a new Transaction
    Args:           nil 
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    validChoice = False
    while not validChoice:
        clrScreen()
        print ()
        print ("========================================================================")
        print ("\t \t EXPENSE TRANSACTION MENU")
        print ("========================================================================")
        # Display the menu options
        print ("\n")
        print ('Press:')
        print ("\t (A)DD a new expense transaction")
        print ('\t (S)EARCH your expense transactions')
        print ('\t (R)ETURN to previous menu')
        print ()
        
        # Get a valid choice from the user
        menuChoice = input('What would you like to do?: ')
        if menuChoice.lower() == 'a':
            addTrans()
        elif menuChoice.lower() == 's':
            searchTransMenu()
        elif menuChoice.lower() == 'r':
            break
        else:
            print ('Invalid Choice. Please try again.')
    
    # Clear Screen and Return to the previous menu
    clrScreen()
    return # To topLevelMenu


def searchTransMenu():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    A sub-sub-level menu allowing the user to choose
                    the element by which they want to seach for
                    transactions, e.g. by Category, Date, or Time.
    Args:           Nil
    Returns:        Nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    validChoice = False
    while not validChoice:
        clrScreen()
        print ()
        print ("========================================================================")
        print ("\t \t  SEARCH EXPENSE TRANSACTION MENU")
        print ("========================================================================")
        # Display the menu options
        print ("\n")
        print ('Press letter to search by:')
        print ("\t (C)ATEGORY")
        print ('\t (D)ATE of the expense transaction')
        print ('\t (T)IME of the expense transaction')
        print ('\t (R)ETURN to previous menu')
        print ()
        
        # Get a valid choice from the user
        menuChoice = input('What would you like to do?: ')
        if menuChoice.lower() == 'c':
            searchByCatMenu()
        elif menuChoice.lower() == 'd':
            searchByDateMenu()
        elif menuChoice.lower() == 't':
            searchByTimeMenu()            
        elif menuChoice.lower() == 'r':
            break
        else:
            print ('Invalid Choice. Please try again.')
    
    # Clear Screen and Return to the previous menu
    clrScreen()
    return # To transMenu


def searchByDateMenu():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Search for transactions based on a date and
                    allow user to Update or Delete one of the 
                    transactions if desired
    Args:           nil
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    clrScreen()
    print ()
    print ("========================================================================")
    print ("\t \t \t DATE SEARCH MENU")
    print ("========================================================================")
    print ()     
    print ()
    # Get a date to search on from the user and validate
    validDate = False
    while not validDate:
        dateToSearch = input('Enter the date of the expense transactions you wish to search for (dd-mm-yyyy): ')
        if isValidDate(dateToSearch):
            validDate = True
            # Get transactions that match the valid date
            validTranIDs = getTranByDate (dateToSearch)
        else:
            print ('That is not a valid date. Please try again.')
    print()
    
    # Check if there were any transactions returned
    if validTranIDs == []:
        print ('You have no Expense transactions with that Date.')
        return # To searchTransMenu

    # Ask user if they want to amend any of the listed transactions
    validAns = False
    while not validAns:
        updateTrans = input('Do you wish to UPDATE or DELETE one of these expense transactions? (y/n): ')
        if updateTrans.lower() == 'y':
            validAns = True
        elif updateTrans.lower() == 'n':
            validAns = True
            return # To searchTransMenu
        else:
            print ('That is not a valid response. Please try again.')

    # From the list of Tranactions presented, ask user for one they want to adjust
    validTranID = False
    while not validTranID:
        tranID = input('Enter the Expense Transaction ID you wish to adjust: ')
        if tranID in validTranIDs:
            validTranID = True
        else:
            print ('That is not an available Expense Transaction ID for this search. Please try again.')
    
    print ()
    print ('Press letter to change expense transaction ' + str(tranID) + ':')
    print ()
    print ('\t (U)PDATE an expense transaction')
    print ('\t (D)ELETE an expense transaction')
    print ('\t (R)ETURN to previous menu')
    print ()
    validChoice = False
    while not validChoice:
        menuChoice = input('What would you like to do?: ')
        if menuChoice.lower() == 'u':
            updateByTranID(tranID)
            validChoice = True
        elif menuChoice.lower() == 'd':
            deleteByTranID(tranID)
            validChoice = True            
        elif menuChoice.lower() == 'r':
            break
        else:
            print ('Invalid Choice. Please try again.')
    
    # Clear Screen and Return to the previous menu
    clrScreen()
    return # To searchTransMenu


def searchByTimeMenu():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Search for transactions based on a time and 
                    allow users to Update or Delete one of the 
                    transactions
    Args:           nil
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    clrScreen()
    print ()
    print ("========================================================================")
    print ("\t \t \t TIME SEARCH MENU")
    print ("========================================================================")
    print ()
    # Get a date to search on from the user and validate
    validTime = False
    while not validTime:
        timeToSearch = input('Enter the time of the expense transactions you wish to search for (hh:mm): ')
        if isValidTime(timeToSearch):
            validTime = True
            # Get transactions that match the valid date
            validTranIDs = getTranByTime (timeToSearch)
        else:
            print ('That is not a valid time. Please try again.')
    print()
    
    # Check if there were any transactions returned
    if validTranIDs == []:
        print ('You have no Expense Transactions with that time.')
        print ()
        pause ()
        return # To searchTransMenu

    # Ask user if they want to amend any of the listed transactions
    validAns = False
    while not validAns:
        updateTrans = input('Do you wish to UPDATE or DELETE one of these expense transactions? (y/n): ')
        if updateTrans.lower() == 'y':
            validAns = True
        elif updateTrans.lower() == 'n':
            validAns = True
            return # To searchTransMenu
        else:
            print ('That is not a valid response. Please try again.')

    # From the list of Tranactions presented, ask user for one they want to adjust
    validTranID = False
    while not validTranID:
        tranID = input('Enter the Expense Transaction ID you wish to adjust: ')
        if tranID in validTranIDs:
            validTranID = True
        else:
            print('That is not an available Expense Transaction ID for this search. Please try again.')
    print()
    print ('Press letter to change expense transaction ' + str(tranID) + ':')
    print ()
    print ('\t (U)PDATE an expense transaction')
    print ('\t (D)ELETE an expense transaction')
    print ('\t (R)ETURN to previous menu')
    print ()
    validMenuChoice = False
    while not validMenuChoice:
        menuChoice = input('What would you like to do?: ')
        if menuChoice.lower() == 'u':
            validMenuChoice = True
            updateByTranID(tranID)
        elif menuChoice.lower() == 'd':
            validMenuChoice = True
            deleteByTranID(tranID)            
        elif menuChoice.lower() == 'r':
            break
        else:
            print ('Invalid Choice. Please try again.')
    
    # Clear Screen and Return to the previous menu
    clrScreen()
    return # To searchTransMenu


def searchByCatMenu():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Allow the user to search for transactions based
                    on a valid category ID. Ask the user if they
                    wish to UPDATE or DELETE one of the listed 
                    transactions.
    Args:           nil
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    clrScreen()
    print ()
    print ("========================================================================")
    print ("\t \t \t CATEGORY SEARCH MENU")
    print ("========================================================================")
    print ()
    
    # Get a list of valid transactions based on a category
    validTranIDs = getTranByCat()
    print ()
        
    # Check if there were any transactions returned
    if validTranIDs == []:
        print ('You have no Expense Transactions with that Category.')
        print ()
        pause ()
        return # To searchTransMenu
    elif validTranIDs == None:
        print ('There are currently no Categories. Please use the Category menu to create some.')
        print ()
        pause ()
        return # To searchTransMenu
    
    # Ask user if they want to amend any of the listed transactions
    validAns = False
    while not validAns:
        updateTrans = input('Do you wish to UPDATE or DELETE one of these expense transactions? (y/n): ')
        if updateTrans.lower() == 'y':
            validAns = True
        elif updateTrans.lower() == 'n':
            validAns = True
            return # To searchTransMenu
        else:
            print ('That is not a valid response. Please try again.')

    # Get the tranID the user wants to amend
    validTranID = False
    while not validTranID:
        tranID = input('Enter the Expense Transaction ID you wish to adjust: ')
        if tranID in validTranIDs:
            validTranID = True
        else:
            print("That is not one of the available Expense Transactions. Please try again.")

    # Present a menu selection allowing users to UPDATE or DELETE a transaction
    validChoice = False
    while not validChoice:   
        print ()
        print ('Press letter to change expense transaction ' + str(tranID) + ':')
        print ()
        print ('\t (U)PDATE an expense transaction')
        print ('\t (D)ELETE an expense transaction')
        print ('\t (R)ETURN to previous menu')
        print ()
         
        menuChoice = input('What would you like to do?: ')
        
        if menuChoice.lower() == 'u':
            # send the current tranID to be updated
            updateByTranID(tranID)
            validChoice = True
        elif menuChoice.lower() == 'd':
            # send the current tranID to be deleted
            deleteByTranID(tranID) 
            validChoice = True           
        elif menuChoice.lower() == 'r':
            # return to the previous menu
            break
        else:
            print ('Invalid Choice. Please try again.')
            clrScreen()
    
    # Clear Screen and Return to the previous menu
    clrScreen()
    return # To searchTransMenu


def catMenu():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Present a sub-menu to the user that allows them
                    to UPDATE, ADD, or DELETE a Category
    Args:           nil
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    validChoice = False
    while not validChoice:
        clrScreen()
        print ()
        print ("========================================================================")
        print ("\t \t \t CATEGORIES MENU")
        print ("========================================================================")
        # Display the menu options
        print ("\n")
        print ('Press:')
        print ("\t (A)DD a new category")
        print ('\t (U)PDATE a category name')
        print ('\t (D)ELETE a category (if empty)')
        print ('\t (R)ETURN to previous menu')
        print ()
        menuChoice = input('What would you like to do?: ')
        if menuChoice.lower() == 'a':
            addCat()
        elif menuChoice.lower() == 'u':
            updateCat()
        elif menuChoice.lower() == 'd':
            deleteCat()
        elif menuChoice.lower() == 'r':
            break
        else:
            print ('Invalid Choice. Please try again.')
    
    # Clear Screen and Return to the previous menu
    clrScreen()
    return # To topLevelMenu


def budMenu():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Present a sub-menu to the user showing their current
                    budget amount and allowing them to request an
                    UPDATE of the budget amount.
    Args:           nil
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    validChoice = False
    while not validChoice:
        clrScreen()
        print ()
        print ("========================================================================")
        print ("\t \t \t BUDGET MENU")
        print ("========================================================================")
        # Display the users current budget and the menu options
        print ("\n")
        print ('Your current budget is $', getBud())
        print ()
        print ('Press:')
        print ('\t (C)HECK your budget against your total expense transactions')
        print ('\t (U)PDATE your budget amount')
        print ('\t (R)ETURN to previous menu')
        print ()
        menuChoice = input('What would you like to do?: ')
        if menuChoice.lower() == 'u':
            updateBud()
        elif menuChoice.lower() == 'c':
            checkBud()
            pause()
        elif menuChoice.lower() == 'r':
            break
        else:
            print ('Invalid Choice. Please try again.')
            clrScreen ()
    
    # Clear Screen and Return to the previous menu
    clrScreen()
    return # To topLevelMenu


def repMenu():
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:    Presents the user with a sub-menu of Reporting
                    options
    Args:           nil
    Returns:        nil
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    validChoice = False
    while not validChoice:
        clrScreen()
        print ()
        print ("========================================================================")
        print ("\t \t \t REPORT MENU")
        print ("========================================================================")
        # Display the menu options
        print ("\n")
        print ('Press:')
        print ('\t (1) Report on your current expenses')
        print ('\t (2) Report on your expenses by category')
        print ('\t (3) Report on your expenses by date')
        print ('\t (4) Report on your expenses by time of day')
        print ('\t (R)ETURN to previous menu')
        print ()
        menuChoice = input('What would you like to do?: ')
        if menuChoice.lower() == '1':
            #validChoice = True
            currTranRep()
        elif menuChoice.lower() == '2':
            #validChoice = True
            tranByCatRep()
        elif menuChoice.lower() == '3':
            #validChoice = True
            tranByDateRep()
        elif menuChoice.lower() == '4':
            #validChoice = True
            tranByTimeRep()
        elif menuChoice.lower() == 'r':
            break
        else:
            print ('Invalid Choice. Please try again.')
            clrScreen()
    
    # Clear Screen and Return to the previous menu
    clrScreen()
    return # To topLevelMenu


# Main

validLogin = False
while not validLogin:
    # Display the imported logo
    clrScreen()
    print (logo)
    print ("========================================================================")
    # Display the menu options
    print ("\n")
    print ('Press:')
    print ("\t (L)OGIN to Expense Tracker")
    print ('\t (C)REATE a new user')
    print ('\t (Q)UIT')
    print ()
    login = input ("What would you like to do?: ")
    if login.lower() == 'l':
        currentUserID = loginUser()
        validLogin = True
    elif login.lower() == 'c':
        currentUserID = createUser()
    elif login.lower() == 'q':
        validLogin = True
        print("Goodbye !")
        exit()
    else:
        print ('Invalid Selection. Please try again.')

# Display the Top Level Menu of the system
topLevelMenu()

