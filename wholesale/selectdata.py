import pyodbc
server = 'wholesalesql.database.windows.net'
database = 'Wholesale DB'
username = 'Stanley'
password = 'Passwordforwholesalesql!'
driver= 'ODBC Driver 17 for SQL Server'
#driver= '/usr/lib/libtdsodbc.so.0.0.0'
conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
c = conn.cursor()
c.execute("SELECT * FROM dbo.Products")

#OPTION 2 - Fetch all results as a list
print(c.fetchall())
print(type(c.fetchall()))

conn.commit()
conn.close()