#
import pandas as pd
import geopandas as gpd




def geodata_fixer(users, revenue, codes, map):


    # Definindo uma função para mapear e inserir o código ISO-3 nos datasets
    def get_country_code(country):

        if country in codes['LABEL EN'].unique():
            code = codes.loc[codes['LABEL EN']==country, 'ISO3 CODE'].iloc[0]

        else:
            code = ""
            
        return code

    # Juntando os dados de clientes com os dados de receitas por país
    user_data_by_country = users.merge(revenue, how='left',
                                                      left_on='country', right_on='ship_country')

    user_data_by_country.drop('ship_country', axis=1, inplace=True)

    # Usando o método apply() para mapear a função get_country_codes() no dataset e adicionar os códigos ISO-3
    user_data_by_country['ISO_code'] = user_data_by_country['country'].apply(lambda x: get_country_code(x))

    # ajustando manualmente os códigos faltantes
    user_data_by_country.loc[user_data_by_country['country']=='USA', 'ISO_code'] = 'USA'
    user_data_by_country.loc[user_data_by_country['country']=='UK', 'ISO_code'] = 'GBR'
    user_data_by_country.loc[user_data_by_country['country']=='Venezuela', 'ISO_code'] = 'VEN'

    # juntando os dados geograficos com os dados de clientes
    full_country_data_with_geodata = map.merge(user_data_by_country, how='left',
                                                    right_on='ISO_code', left_on='iso_a3')
    
    return full_country_data_with_geodata

        