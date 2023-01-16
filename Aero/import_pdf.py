import PyPDF2
import pandas as pd
import re


def scrape_pdf(pdf):
    # Open the PDF file
    with open(pdf, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)

        # Initialize an empty list to store the data
        data = []

        # Iterate through each page of the PDF
        for page in range(len(pdf.pages)):
            text = pdf.pages[page].extract_text()
            # Split the text into rows
            rows = text.split('\n')

            append_from_top = False
            hold_data = ''
            for i in range(4, len(rows), 1):

                try:
                    if len(re.split(' {2,}', rows[i].strip())) == 7:
                        even = re.split(' {2,}', rows[i].strip())
                        odd = re.sub(' {2,}', ', ', rows[i + 1].strip())
                        even[2] += ', ' + odd
                        data.append(even)
                    elif len(re.split(' {2,}', rows[i].strip())) == 2 and append_from_top == False:
                        pass
                    elif len(re.split(' {2,}', rows[i].strip())) == 2 and append_from_top == True:
                        odd = re.sub(' {2,}', ', ', rows[i].strip())
                        hold_data[2] += ', ' + odd
                        data.append(hold_data)
                    elif len(re.split(' {2,}', rows[i].strip())) == 3:
                        even = re.split(' {2,}', rows[i].strip())
                        data.append(even)
                except:
                    if len(re.split(' {2,}', rows[i].strip())) == 7:
                        even = re.split(' {2,}', rows[i].strip())
                        hold_data = even
                        append_from_top = True
                    else:
                        print(i)

        # Convert the data into a DataFrame
        columns = ["Registrant", "N-Nbr", "Mailing Address", "MMS", "Cert Date", "Type-R", "Year-Mfr"]

        df = pd.DataFrame(data, columns=columns)
        df.to_csv('scraped_plane_data.csv')
    return df
