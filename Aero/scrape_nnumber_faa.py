from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd


def scrape_nnumber(df):
    # start Firefox browser
    driver = webdriver.Firefox()
    final_df = pd.DataFrame()
    invalid_nnumbers = []
    for n in df['N-Nbr'].unique():
        try:
            # navigate to the page

            driver.get("https://registry.faa.gov/aircraftinquiry/Search/NNumberInquiry")

            enter_nnumber = driver.find_element("name", "NNumbertxt")
            enter_nnumber.send_keys(f'{n}')
            driver.find_elements(By.CSS_SELECTOR, "button.primary.default[type='submit']")[0].click()
            table = driver.find_element("xpath", "//table[@class='devkit-table']")
            rows = table.find_elements("tag name", "tr")
            data = []
            for row in rows:
                cols = row.find_elements("tag name", "td")

                cols = [col.text for col in cols]
                data.append(cols)

            df = pd.DataFrame(data)
            df_test1 = df[[0, 1]].T.reset_index(drop=True)
            df_test2 = df[[2, 3]].T.reset_index(drop=True)
            df_test = pd.concat([df_test1, df_test2], axis=1)
            df_test.columns = df_test.iloc[0]
            df_test = df_test[1:]
            final_df = pd.concat([final_df, df_test])
        except:
            invalid_nnumbers.append(n)
    driver.quit()
    final_df.to_csv('faainquiryold.csv')
    return final_df