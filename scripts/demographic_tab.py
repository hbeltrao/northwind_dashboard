from bokeh.plotting import figure
from bokeh.models import (GeoJSONDataSource, LinearColorMapper, ColorBar,
                            TableColumn, DataTable, NumberFormatter, ColumnDataSource,
                            TapTool, Panel, Div, Tap)
from bokeh.layouts import column, row
from bokeh.palettes import Viridis8, Category10
from bokeh.events import Tap, Reset
from bokeh.transform import cumsum

from math import pi

import json


def demographic_tab(geodata, user_data, product_data, pie_data):

    def map_plot(data):

        plot_col = 'customer_share(%)'
        title = 'Customer Distribution by Country'

        tooltips = [('Country','@name'), 
            ('Tot Customers', "@tot_customers{0,0}"),
            ('Customer Share', '@{customer_share(%)}{0.0} %'),
            ('Revenue', '@brute_revenue{($ 0.00 a)}'),
            ('Revenue Share', '@{revenue_share(%)}{0.0} %')]

        palette = Viridis8
        palette = palette[::-1]

        
        color_mapper = LinearColorMapper(palette = palette)

        color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,
                border_line_color=None, orientation = 'vertical', title = "% of Clients")

        p = figure(title = title, plot_height = 600 , plot_width = 1150, tooltips = tooltips)
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        p.title.text_font_size = '20pt'

        patch_renderer = p.patches('xs','ys', source = data, fill_color = {'field' :plot_col, 'transform' : color_mapper},
                line_color = 'black', line_width = 0.25, fill_alpha = 1)

        p.add_layout(color_bar, 'right')


        tap_tool = TapTool(renderers=[patch_renderer])

        p.add_tools(tap_tool)

        return p
    

    def adjust_pie_data(pie_data):

        _pie_data = pie_data.groupby('category_name')['brute_revenue'].sum().reset_index()
        _pie_data.sort_values(by='brute_revenue', ascending=False, inplace=True)
        _pie_data['angle'] = _pie_data['brute_revenue']/_pie_data['brute_revenue'].sum()*2*pi
        _pie_data['color'] = Category10[len(_pie_data['category_name'])]
        _pie_data['revenue_share'] = 100*_pie_data['brute_revenue']/_pie_data['brute_revenue'].sum()

        return _pie_data



    def pie_chart(pie_source):

        pie = figure(height=600, title="Revenue by Product Category", toolbar_location=None,
           tools="hover", tooltips="@category_name :@revenue_share{0.0} %", x_range=(-0.5, 1.5))

        pie.annular_wedge(x=0.25, y=1, inner_radius=0.4, outer_radius=0.6,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='category_name', source=pie_source)

        pie.title.text_font_size = '20pt'
        pie.axis.axis_label = None
        pie.axis.visible = False
        pie.grid.grid_line_color = None

        return pie


    def user_table(table_source):

        columns = [
            TableColumn(field="customer_name", title="Customer Name"),
            TableColumn(field="customer_country", title="Customer Country"),
            TableColumn(field="brute_revenue", title="Revenue", formatter=NumberFormatter(format="$0,0.00")),
            TableColumn(field="tot_orders", title="Total Orders"),
            TableColumn(field="revenue_share(%)", title="Revenue Share (%)", formatter=NumberFormatter(format="0.00%")),
            TableColumn(field="freight_cost", title="Freight Cost", formatter=NumberFormatter(format="$0,0.00")),
            TableColumn(field="freight_weight(%)", title="Freight Weight (%)", formatter=NumberFormatter(format="0.00%")),  
        ]

        


        data_table = DataTable(source=table_source, columns = columns, autosize_mode = "fit_viewport")

        return data_table


    def products_table(table_source):

        columns = [
            TableColumn(field="product_name", title="Product Name"),
            TableColumn(field="origin_country", title="Origin Country"),
            TableColumn(field="customer_id", title="Customer Name"),
            TableColumn(field="ship_country", title="Customer Country"),
            TableColumn(field="revenue", title="Revenue", formatter=NumberFormatter(format="$0,0.00")),
            TableColumn(field="total_orders", title="Total Orders"),
            TableColumn(field="revenue_share(%)", title="Freight Cost", formatter=NumberFormatter(format="0.00%"))
        ]

        
        data_table = DataTable(source=table_source, columns = columns, autosize_mode = "fit_viewport")

        return data_table

    

    def update_table(PointEvent):

        try:

            selected_index = geosource.selected.indices[0]

            if selected_index:

                parsed_geojson = json.loads(geosource.geojson)
                features = parsed_geojson['features']
                series_key = features[selected_index ]['properties']['country']

                new_df_1 = user_data[user_data['customer_country']==series_key]
                new_df_2 = product_data[product_data['ship_country']==series_key]
                new_df_3 = pie_data[pie_data['destination_country']==series_key]
                new_pie_source = adjust_pie_data(new_df_3)

                
                table_1.source.data = ColumnDataSource.from_df(new_df_1)
                table_2.source.data = ColumnDataSource.from_df(new_df_2)
                pie_source.data = ColumnDataSource.from_df(new_pie_source)


            else :

                reset_tables()

        
        except IndexError:
            pass

    

    def reset_tables(PlotEvent):
        table_1.source.data = ColumnDataSource.from_df(user_data)
        table_2.source.data = ColumnDataSource.from_df(product_data)
        pie_source.data = ColumnDataSource.from_df(adjust_pie_data(pie_data))



    geosource = GeoJSONDataSource(geojson = geodata.to_json())
    user_source = ColumnDataSource(data=user_data)
    product_source = ColumnDataSource(data=product_data)
    pie_source = ColumnDataSource(data=adjust_pie_data(pie_data))
    

    p = map_plot(geosource)
    table_1 = user_table(user_source)
    table_2 = products_table(product_source)
    pie_graph = pie_chart(pie_source)

    table_1_title = Div(text="<b>Top Customers by revenue</b>", style={'font-size': '200%', 'color': 'black'}, align='center')
    table_2_title = Div(text="<b>Top Products Bought by revenue</b>", style={'font-size': '200%', 'color': 'black'}, align='center')

    
    p.on_event(Tap, update_table)
    p.on_event(Reset, reset_tables)


    # Create a row layout
    layout = column(row(p, pie_graph), row(column(table_1_title, table_1), column(table_2_title, table_2)))
	
	# Make a tab with the layout 
    tab = Panel(child=layout, title = 'Demographics')

    return tab



