from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


#doen jisdfdf
app=Flask(__name__)

@app.route('/',methods=['GET'])
def home():
	return "Welcome to CodeUtsava 2.0 . ATeamWithNoName :-)!!"


@app.route('/get_suggestions',methods=['GET'])
def get_suggestions():
	if request.method == 'GET':
		temp_age=request.args.get("age")
		#i
		temp_gender=request.args.get("gender")
		#j

		k=7
		l=request.args.get("symptoms")


		#condition if any of the params is missing
		if temp_age==None or temp_gender==None or k==None or l==None :
			return jsonify({'error':'one of the parameter is missing!!','age':temp_age,'gender':temp_gender,'region':k,'symptoms':l}),400

		if int(temp_age) < 1:
			i = 2
		elif int(temp_age) <= 5:
			i = 3
		elif int(temp_age) <= 12:
			i = 10
		elif int(temp_age) <= 16:
			i = 4
		elif int(temp_age) <= 29:
			i = 7
		elif int(temp_age) <= 39:
			i = 5
		elif int(temp_age) <= 49:
			i = 8
		elif int(temp_age) <= 64:
			i = 9
		else :
			i = 6

		if temp_gender == "male":
			j = 2
		else:
			j = 1
		#print("going to start the souce lab")
		#starting the webdriver
		SAUCE_USERNAME = 'breakit12345'
		SAUCE_ACCESS_KEY = 'd0778173-13b3-42fb-a11d-972b09847356'

		print("starting the session")
		driver = webdriver.Remote(
	    	desired_capabilities=webdriver.DesiredCapabilities.FIREFOX,
	    	command_executor='http://%s:%s@ondemand.saucelabs.com:80/wd/hub' %
	    	(SAUCE_USERNAME, SAUCE_ACCESS_KEY)
			)

		driver.get('https://symptomchecker.isabelhealthcare.com/suggest_diagnoses_advanced/landing_page')
		id = driver.session_id
		

		#get the page and scrap it
		age=Select(driver.find_element_by_id('query_age'))
		region=Select(driver.find_element_by_id('query_region_name'))
		submit_button=driver.find_element_by_class_name('search_query_button')

		#putting the input back
		if int(i)>=1 and int(i)<=10:
			age.select_by_value(str(i))
		else:
			return jsonify({'error':'invalid age input'}),400

		#input for male and female
		if int(j)==1:
			sex=driver.find_elements_by_class_name('new_radio2')
		elif int(j)==2:
			sex=driver.find_elements_by_class_name('new_radio')
		else:
			return jsonify({'error':'unknown sex type'}),400
		sex[0].click()

		#input for region
		if int(k)>=1 and int(k)<=17:
			region.select_by_value(str(k))
		else:
			return jsonify({'error':'invalid region type'}),400

		#input for symptoms
		sl=str(l).split(',')
		for x in range(min(len(sl),5)):
			x+=1
			symp=driver.find_element_by_id('query_text_' + str(x))
			symp.send_keys(str(sl[x-1]))
			#write here to increase the box size

		#click on submit
		submit_button.click()
		submit_button.click()
		timeout = 10
		try:
		    element_present = EC.presence_of_element_located((By.ID, 'common_rare'))
		    WebDriverWait(driver, timeout).until(element_present)
		except TimeoutException:
		    return jsonify({'error':'internal error'}),500

		#click on the common tab of disease
		driver.find_element_by_xpath("//a[@id='common_rare']").click()

		time.sleep(2)


		#scrap to get the results
		final_page=driver.page_source
		final_soup=BeautifulSoup(final_page,'html5lib')
		tables=final_soup.findAll("table", {"class": "putBorderForPrint"})

		driver.quit()
		#store all the results in list of dict sorted
		#in the order of flag
		final=[]
		for i in range(1,11):
			dic={}
			dic['flag']=int(len(tables[i].findAll("img", {"alt": "F"})))
			dic['name']=str(tables[i].tbody.tr.td.div.span.a.text)
			final.append(dic)
		final=sorted(final,key=lambda x:x['flag'])

		#click to logout
		#driver.find_element_by_xpath("//a[@href='/login/logout']").click()

		#close the driver
		driver.quit()

		#return the final output :)
		return jsonify(final),200



if __name__=="__main__":
	app.run(port=8000,use_reloader=True,debug=True)
