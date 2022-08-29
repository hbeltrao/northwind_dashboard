# Imports
from bokeh.plotting import figure
from bokeh.models import (NumeralTickFormatter, Range1d, LinearAxis, HoverTool, 
                            TableColumn, DataTable, NumberFormatter, ColumnDataSource,
                            TapTool, Panel, Div, Tap)
from bokeh.layouts import column, row
from bokeh.palettes import Viridis8, Category10
from bokeh.models.widgets import Select

import datetime as dt
import pandas as pd


###

def financial_tab(income_data, avg_ticket_data, customer_by_country_data, suppliers_data):

    def income_plot(data_source, title):

        # creating and configuring the income plot figure
        p = figure(title=title, x_axis_label="Year-Month", y_axis_label="Revenue",
                        plot_width=900, plot_height=400, tools="", toolbar_location=None, x_axis_type='datetime')


        #  Ajusting axis and title
        p.title.align = 'center'
        p.title.text_font_size='12pt'
        p.xaxis.ticker.desired_num_ticks = len(set(data_source.data['date']))
        p.yaxis.formatter=NumeralTickFormatter(format="($ 0.00 a)")
        p.xaxis.major_label_orientation = "vertical"
        p.border_fill_color = "whitesmoke"
        p.min_border_left = 80


        # lineplot of brute revenue per year-month
        a=p.line(x='year_months', y='brute_revenue', source = data_source, color= 'red', line_width=2,
                legend_label="Monthly revenue")


        # creating an extra y-axis to compute number of orders
        p.extra_y_ranges = {"Orders" : Range1d(start=0, end=data_source.data['tot_orders'].max()*1.1)}
        p.add_layout(LinearAxis(y_range_name="Orders", axis_label="Total Orders"), 'right')


        # bar plot of total orders per year-month
        b=p.vbar(x='year_months', top='tot_orders', source=data_source, 
                width=dt.timedelta(days=15), alpha=0.3, color= 'blue',
                legend_label="Total Orders", y_range_name="Orders")



        # Adding hovertool to the plot
        p.add_tools(HoverTool(
            tooltips=[
                ( 'date',   '@date'),
                ( 'Revenue', '@brute_revenue{($ 0.00 a)}'),
                ( 'Orders', '@tot_orders')
            ],

            mode='vline',
            renderers=[a]
        ))

        # Adjusting axis colors to match each plot
        p.yaxis[0].axis_line_color = "red"
        p.yaxis[0].major_label_text_color = "red"
        p.yaxis[0].major_tick_line_color = "red"
        p.yaxis[0].minor_tick_line_color = "red"
        p.yaxis[0].axis_label_text_color="red"

        p.yaxis[1].axis_line_color = "blue"
        p.yaxis[1].major_label_text_color = "blue"
        p.yaxis[1].major_tick_line_color = "blue"
        p.yaxis[1].minor_tick_line_color = "blue"
        p.yaxis[1].axis_label_text_color="blue"

        # Adding legends outside the plot rea
        p.add_layout(p.legend[0], 'right')

        return p
    


    def date_fixing(dataframe):

        fixed_dataset = dataframe

        # Converting year_months column to datetype to correctly display on axis graph
        fixed_dataset['year_months'] = pd.to_datetime(fixed_dataset['year_months'],
                                                            format='%Y%m').dt.to_period('M')

        # creating a copy of year_months column as string to better fit the hover tooltip
        fixed_dataset['date'] = fixed_dataset['year_months'].astype('str')

        return fixed_dataset

  

    def update_selector_options(attr, old, new):

        option = revenue_plot_selector.value

        if option == 'Global':

            revenue_plot_sub_selector.options = []
            data_source.data = ColumnDataSource.from_df(full_data)
            income_graph.extra_y_ranges['Orders'].update(end=data_source.data['tot_orders'].max()*1.1)
            income_graph.title.text = "Revenue Evolution of Northwind"
        

        if option == 'Category':

            revenue_plot_sub_selector.options = list(set(category_data["category_name"]))
        

        if option == 'Product':

            revenue_plot_sub_selector.options = list(set(product_data["product_name"]))
        

  
    def update_plots(attr, old, new):

        option = revenue_plot_selector.value
        option2 = revenue_plot_sub_selector.value

        if option == 'Category':
            
            filtered_data = category_data[category_data['category_name']==option2]
            data_source.data = ColumnDataSource.from_df(filtered_data)
            income_graph.extra_y_ranges['Orders'].update(end=data_source.data['tot_orders'].max()*1.1)
            income_graph.title.text = "Revenue Evolution of Northwind" + " Category: "+option2

        
        if option == 'Product':

            filtered_data = product_data[product_data['product_name']==option2]
            data_source.data = ColumnDataSource.from_df(filtered_data)
            income_graph.extra_y_ranges['Orders'].update(end=data_source.data['tot_orders'].max()*1.1)
            income_graph.title.text = "Revenue Evolution of Northwind" + " Poduct: "+option2
            


    def make_avg_ticket_plot(source, title):
        
        plot = figure(title=title, x_axis_label="Year-Months", y_axis_label="Average Ticket",
                    plot_width=900, plot_height=400, x_axis_type='datetime')
        

        #  Configuring title and axis
        plot.title.align = 'left'
        plot.title.text_font_size='12pt'
        plot.y_range = Range1d(start=0, end=source.data['average_ticket'].max()*1.1)
        plot.yaxis.formatter=NumeralTickFormatter(format="($ 0.00 a)")
        plot.xaxis.ticker.desired_num_ticks = 23
        plot.xaxis.major_label_orientation = "vertical"
        plot.border_fill_color = "whitesmoke"
        plot.min_border_left = 80

            
        #  lineplot with average ticket per year_month
        plot.line(x='year_months', y='average_ticket', source = source,
                color= 'blue', line_width=2, legend_label="Average Ticket")


        # Adding hovertool to the plot
        plot.add_tools(HoverTool(
                tooltips=[
                    ( 'date',   '@date'),
                    ( 'Average Ticket', '@average_ticket{($ 0.00 a)}'),
                    ( 'Total Orders', '@orders')
                ],

                mode='vline'
            ))


        # Adding legend outside plot area
        plot.add_layout(plot.legend[0], 'right')

        return plot
        

    def update_avg_ticket_plot(attr, old, new):
        
        selector = individual_selector.value     
        new_df = avg_ticket_source[avg_ticket_source['company_name']==selector]
        avg_ticket_plot.title.text = "Ticket Médio: " + selector   
        avg_ticket_source_filtered.data = ColumnDataSource.from_df(new_df) 
        avg_ticket_plot.y_range.end = avg_ticket_source_filtered.data['average_ticket'].max()*1.1

        
    def fix_avg_ticket_data(data):
            
        _data = data.pivot(index=['year_months'],columns= ['company_name'], values=['average_ticket', 'orders'])\
        .fillna(0).stack().reset_index()

        _data['date'] = _data['year_months'].astype('str')

        return _data
    

    def revenue_per_country_plot(source,  title):

        # Defining the figure to draw the plots
        p = figure(title=title, x_axis_label="State", y_axis_label="Days",
                    plot_width=990, plot_height=400, tools="", toolbar_location=None, x_range=source.data['country'].tolist())
        
        #  Configuring title and axis
        p.title.align = 'left'
        p.title.text_font_size='12pt'
        p.y_range = Range1d(start=0, end=source.data['brute_revenue'].max()*1.1)
        p.border_fill_color = "whitesmoke"
        p.xaxis.major_label_orientation = "vertical"
        p.min_border_left = 80

        # Creating the line plot of the average delay for each year-month
        p.line(x='country', y='brute_revenue', source = source,
                color= 'red', line_width=2, legend_label="Brute Revenue")

        # Creating the second y axis and adding it to the figure
        p.extra_y_ranges = {"Tot_Orders" : Range1d(start=0, end=source.data['tot_orders'].max()*1.1)}
        p.add_layout(LinearAxis(y_range_name="Tot_Orders", axis_label="Number of Orders"), 'right')

        # bar plot of total orders per year-month
        b=p.vbar(x='country', top='tot_orders', source=source, 
                width=0.5, alpha=0.3, color= 'blue',
                legend_label="Number of Orders", y_range_name="Tot_Orders")
        

        # Adding hovertool to the plot
        p.add_tools(HoverTool(
                tooltips=[
                    ( 'Country',   '@country'),
                    ( 'Brute Revenue', '@brute_revenue{($ 0.00 a)}'),
                    ( 'Total Orders', '@tot_orders')
                ],

                mode='vline',
                renderers=[b]
            ))        

        # Adjusting axis colors to match each plot
        p.yaxis[0].axis_line_color = "red"
        p.yaxis[0].major_label_text_color = "red"
        p.yaxis[0].major_tick_line_color = "red"
        p.yaxis[0].minor_tick_line_color = "red"
        p.yaxis[0].axis_label_text_color="red"

        p.yaxis[1].axis_line_color = "blue"
        p.yaxis[1].major_label_text_color = "blue"
        p.yaxis[1].major_tick_line_color = "blue"
        p.yaxis[1].minor_tick_line_color = "blue"
        p.yaxis[1].axis_label_text_color="blue"


        # Adding legend outside the plot
        p.add_layout(p.legend[0], 'right')

        return p


        

    
    ############################################################################################################################            
    # code for calling and controlling the income graph
    
    revenue_plot_selector = Select(title = 'Filter by:', options = ['Global', 'Category', 'Product'], value = 'Global')
    revenue_plot_sub_selector = Select(title = 'Select:', options = [], value = 'Global')

    _income_data = date_fixing(income_data)

    full_data = _income_data.groupby('year_months').agg({'brute_revenue':'sum', 'order_id':"count", 'date':'max'})\
        .reset_index().rename(columns={'order_id':'tot_orders'})
    
    category_data = _income_data.groupby(['year_months','category_name']).agg({'brute_revenue':'sum', 'order_id':"count", "date":'max'})\
        .reset_index().rename(columns={'order_id':'tot_orders'})

    product_data = _income_data.groupby(['year_months','product_name']).agg({'brute_revenue':'sum', 'order_id':"count", "date":'max'})\
        .reset_index().rename(columns={'order_id':'tot_orders'})


    data_source = ColumnDataSource(full_data)
    income_graph = income_plot(data_source, "Revenue Evolution of Northwind")


    revenue_plot_selector.on_change("value", update_selector_options)
    revenue_plot_sub_selector.on_change("value", update_plots)

    # end of income graph specifics code
    #########################################################################################################################################

    #########################################################################################################################################            
    # code for calling and controlling the average ticket graph
    
    customer="Alfreds Futterkiste"
    
    avg_ticket_source = fix_avg_ticket_data(date_fixing(avg_ticket_data))

    individual_selector = Select(title="Individual:", value="Alfreds Futterkiste", 
                                 options=avg_ticket_source['company_name'].unique().tolist())

    
    avg_ticket_source_filtered = ColumnDataSource(data=avg_ticket_source[avg_ticket_source['company_name']==customer])

    avg_ticket_plot = make_avg_ticket_plot(avg_ticket_source_filtered, "Ticket Médio: " + customer)

    individual_selector.on_change('value', update_avg_ticket_plot)

    # end of average ticket graph specifics code
    #########################################################################################################################################

    #########################################################################################################################################            
    # code for calling and controlling the income by country and supplier graph
    
    _customer_country_data = customer_by_country_data.rename(columns = {'customer_country':'country'})
    customer_country_data = ColumnDataSource(_customer_country_data.groupby('country')[['brute_revenue', 'tot_orders']].sum().reset_index()
                                                .sort_values(by='brute_revenue', ascending=False))
    customer_country_revenue_plot = revenue_per_country_plot(customer_country_data, "Revenue Per Customer Country")

    supplier_data_source = ColumnDataSource(suppliers_data.sort_values(by='brute_revenue', ascending=False))

    suppliers_country_revenue_plot = revenue_per_country_plot(supplier_data_source, "Revenue Per Supplier Country")



    # end of income by country graph specifics code
    #########################################################################################################################################

    # Create a row layout
    layout = row(column(row(revenue_plot_selector, revenue_plot_sub_selector), income_graph, customer_country_revenue_plot),
                 column(individual_selector, avg_ticket_plot, suppliers_country_revenue_plot))
	
	# Make a tab with the layout 
    tab = Panel(child=layout, title = 'Financial')

    return tab