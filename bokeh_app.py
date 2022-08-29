# Imports

import pandas as pd
import geopandas as gpd

from os.path import dirname, join


from scripts.geodata_fixer import geodata_fixer
from scripts.demographic_tab import demographic_tab
from scripts.financial_tab import financial_tab


from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models.widgets import Tabs


#####

# Loading all data necessary



# Loading data for tab 1
# Data for world map
customers_by_country = pd.read_csv(join(dirname(__file__), "data", "customers_by_country.csv"), sep=";", decimal='.')
revenue_by_country = pd.read_csv(join(dirname(__file__), "data", "revenue_by_country.csv"), sep=";", decimal='.')
country_codes = pd.read_csv(join(dirname(__file__), "data", "countries-codes.csv"), delimiter=';')
world_map = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
customer_country_data_with_geodata = geodata_fixer(customers_by_country, revenue_by_country, country_codes, world_map)

# Data for DataTables
customers_info = pd.read_csv(join(dirname(__file__), "data", "customers_info.csv"), sep=";", decimal='.')
products_info = pd.read_csv(join(dirname(__file__), "data", "clients_per_product.csv"), sep=";", decimal='.')

# Data for Pie chart
pie_data = pd.read_csv(join(dirname(__file__), "data", "category_revenue_with_customer_country.csv"), sep=";", decimal='.')


# end of tab 1 data loading
#####################################################################################################################################


# Loading data for tab 2
global_income_data = pd.read_csv(join(dirname(__file__), "data", "category_revenue_with_customer_country.csv"), sep=";", decimal='.')

average_tiket_data = pd.read_csv(join(dirname(__file__), "data", "average_ticket_monthly_per_customer.csv"), sep=";", decimal='.')

suppliers_data = pd.read_csv(join(dirname(__file__), "data", "revenue_per_supplier_country.csv"), sep=";", decimal='.')

# end of tab 2 data loading
#####################################################################################################################################



# Calling all tabs scripts
tab_1 = demographic_tab(customer_country_data_with_geodata, customers_info, products_info, pie_data)

tab_2 = financial_tab(global_income_data, average_tiket_data, customers_info, suppliers_data)

# Put all the tabs into one application
tabs = Tabs(tabs = [tab_1, tab_2])

curdoc().add_root(tabs)
