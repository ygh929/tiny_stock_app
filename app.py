from flask import Flask, render_template, request, redirect
import requests, pandas
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.charts import TimeSeries
from bokeh.resources import INLINE
from bokeh.templates import RESOURCES
import os
app = Flask(__name__)
app_vars={}
value_option={u'Close':4,u'Adj. Close':11,u'Volume':5}
colors=['blue','red','green']
widths=[1.5,1,1]


@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/check_plot',methods=['GET','POST'])
def check_plot():
    if request.method=='POST':
        app_vars['ticker_name']=request.form['ticker_name']
        app_vars['ticker_var']=request.form.getlist('ticker_var')
    url='https://www.quandl.com/api/v3/datasets/WIKI/'+app_vars['ticker_name']+'.json'
    time_value=requests.get(url)
    
    error=[]
    if len(app_vars['ticker_var'])==0:
        error.append('No variables were selected!')
    if time_value.status_code!=200:
        error.append('The ticker name can\'t be found in the database!')
    if error:
        return render_template('error.html',error_message=' '.join(error))
    else:
        tv_df=pandas.DataFrame(time_value.json()[u'dataset'][u'data'])
        tv_df.columns=time_value.json()[u'dataset'][u'column_names']
        select_var=app_vars['ticker_var']
        select_ind=[value_option[v] for v in select_var]
        df_use=tv_df.ix[:,select_ind]
        plot = figure(x_axis_type="datetime")
        time_ind=tv_df.ix[:,0].map(pandas.to_datetime)
        for i in range(len(select_var)):
            plot.line(time_ind,df_use.ix[:,i],legend=select_var[i],line_color=colors[i],
                     line_width=widths[i])
        plot.xaxis.axis_label="Date"
        plot.title="Data from Quandl WIKI dataset"
        script, div = components(plot)
        
        return render_template('show_plot.html',ticker_name=app_vars['ticker_name'],
                               script_=script,div_=div)

if __name__ == '__main__':
  app.run(port=33507)
