import csv
import yfinance as yf
'''
def readStocks():
    # Open the source CSV file (NSE500.csv) for reading
    with open('NSE500.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        
        # Open the destination CSV file in append mode
        with open('Indian stock names.csv', 'a', newline='') as outfile:
            writer = csv.writer(outfile)
            
            # Loop through the rows in the source file
            for row in reader:
                stock_symbol = row[2]
                try:
                    stock_symbol = stock_symbol + '.NS'
                    yf.download(stock_symbol, progress=False)
                    writer.writerow([stock_symbol])
                except:
                    print(stock_symbol+": Stock Not available")

# Call the function to perform the operation
readStocks()
'''

def readStocks():
    # Open the source CSV file (NSE500.csv) for reading
    with open('sp500.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        
        # Open the destination CSV file in append mode
        with open('US.csv', 'a', newline='') as outfile:
            writer = csv.writer(outfile)
            
            # Loop through the rows in the source file
            for row in reader:
                stock_symbol = row[1]
                try:
                    yf.download(stock_symbol, progress=False)
                    writer.writerow([stock_symbol])
                except:
                    print(stock_symbol+": Stock Not available")

# Call the function to perform the operation
readStocks()