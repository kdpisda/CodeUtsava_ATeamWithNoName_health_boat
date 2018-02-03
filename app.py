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
	return "Health Boat by Team : ATeamWithNoName"


@app.route('/get_suggestions',methods=['GET'])
def get_suggestions():
	response = {}
	try:
		if request.method == 'GET':
			i=request.args.get("age")
			j=request.args.get("sex")
			l=request.args.get("symptoms")


			#condition if any of the params is missing
			if i==None or j==None or l==None :
				return jsonify({'error':'one of the parameter is missing!!','age':i,'sex':j,'region':k,'symptoms':l, success:False}),400

			#print("going to start the souce lab")
			#starting the webdriver

			SAUCE_USERNAME = 'testkd'
			SAUCE_ACCESS_KEY = '275592fe-1b16-4a74-bc04-ce551c1bd940'

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
				return jsonify({'error':'invalid age input', success:False}),400

			#input for male and female
			if int(j)==1:
				sex=driver.find_elements_by_class_name('new_radio2')
			elif int(j)==2:
				sex=driver.find_elements_by_class_name('new_radio')
			else:
				return jsonify({'error':'unknown sex type', success:False}),400
			sex[0].click()

			#input for region
			# Hardcoding region for South Asia only
			region.select_by_value("10")

			#input for symptoms
			sl=str(l).split(',')
			for x in range(min(len(sl),2)):
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
			    return jsonify({'error':'internal error', success:False}),500

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
				arr=dic['name'].split()
				add=str()
				final.append(dic)
			final=sorted(final,key=lambda x:x['flag'])

			#close the driver
			driver.quit()
			#return the final output :)

			response['success'] = True
			response['data'] = final
	except Exception as e:
		response['success'] = False
		response['description'] = "Sorry an error occured"
		
	return jsonify(response),200

if __name__=="__main__":
	app.run(port=8000,use_reloader=True,debug=True)
