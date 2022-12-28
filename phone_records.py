import os, pandas as pd

class PhoneRecords:

    def __init__(self, file_root):

        self.file_root = file_root

        self.verizon_billed_filename = "Verizon Sample Call detail report billed calls.csv"
        self.verizon_unbilled_filename = "Verizon Sample Current Unbilled Usage Report_.xls"
        self.contacts_filename = "Sample contacts master list.xlsx"

    
    def preprocess_files(self):

        self.__preprocess_contacts_file()
        self.__preprocess_verizon_files()
        self.__preprocess_client_files()
    
    def __preprocess_contacts_file(self):

        df_contacts = pd.read_excel(os.path.join(self.file_root, self.contacts_filename))
        df_contacts.columns = [str.capitalize(x) for x in df_contacts.columns]

        df_contacts.Number = df_contacts.Number.map(lambda x: pd.NA if pd.isna(x) else str(int(x)))
        df_contacts = df_contacts.replace({" ": pd.NA}).dropna(how="all", axis=1)

        self.df_contacts = df_contacts

    def __preprocess_verizon_billed(self):

        df_verizonb = pd.read_csv(os.path.join(self.file_root, self.verizon_billed_filename), skiprows=13)

        df_verizonb.Date = df_verizonb.Date.map(lambda x: x.strip())
        latter_index = df_verizonb[df_verizonb.Date == "Total"].index[0]

        df_verizonb = df_verizonb.loc[:latter_index-1]

        def remove_loc_whitespace(x):
            return (
                pd.NA if pd.isna(x) 
                else ' '.join([y for y in x.split(" ") if y])
                )

        df_verizonb.Destination = df_verizonb.Destination.map(lambda x: remove_loc_whitespace(x))

        df_verizonb = (
            df_verizonb
            .rename(columns={
                "In/Out number": "Number",
            })
            [["Date", "Time", "Number", "Duration", "Destination"]]
        )

        df_verizonb["billed"] = True

        self.df_verizonb = df_verizonb

    def __preprocess_verizon_unbilled(self):

        df_verizonu = pd.read_excel(os.path.join(self.file_root, self.verizon_unbilled_filename), skiprows=3)

        df_verizonu = (
            df_verizonu.rename(columns={
                "Minutes": "Duration",
                "Description": "Destination"
            })
        )

        df_verizonu["billed"] = False

        self.df_verizonu = df_verizonu

    def __preprocess_verizon_files(self):

        if self.verizon_billed_filename and self.verizon_unbilled_filename:

            self.__preprocess_verizon_billed()
            self.__preprocess_verizon_unbilled()
            self.df_verizon = pd.concat([self.df_verizonb, self.df_verizonu])

        elif self.verizon_billed_filename:

            self.__preprocess_verizon_billed()
            self.df_verizon = self.df_verizonb.copy()

        elif self.verizon_unbilled_filename:

            self.__preprocess_verizon_unbilled()
            self.df_verizon = self.df_verizonu.copy()

        else:
            assert False, "No verizon file listed"

    def __preprocess_client_files(self):

        client_filenames = [x for x in os.listdir(self.file_root) if x.startswith("_")]

        df_client = pd.concat([self.__read_clean_client_file(x) for x in client_filenames])
        df_client.Duration = df_client.Duration.astype(int)

        self.df_client = df_client

    def __read_clean_client_file(self, x):

        df_client = pd.read_excel(os.path.join(self.file_root, x), header=None)

        df_client.columns = [
            "Date", "Time", "Number", "Origination",
            "Destination", "Duration", "Name 0"
        ]

        def duration_is_numeric(x):
            try:
                return str.isnumeric(str(int(x)))
            except:
                return False

        df_client = (
            df_client[
                df_client.Duration.map(
                    lambda x: duration_is_numeric(x)
                    )
                ]
            .reset_index(drop=True)
            )

        df_client.Date = pd.to_datetime(df_client.Date)

        def strip_client_name(x):
            return x.strip("_").replace(".xlsx", "")

        df_client["client name"] = strip_client_name(x)

        return df_client

if __name__ == "__main__":

    file_root = "./sample files/"
    verizon_billed_filename = "Verizon Sample Call detail report billed calls.csv"
    verizon_unbilled_filename = "Verizon Sample Current Unbilled Usage Report_.xls"
    contacts_filename = "Sample contacts master list.xlsx"

    phone_records = PhoneRecords(file_root)
    phone_records.preprocess_files()