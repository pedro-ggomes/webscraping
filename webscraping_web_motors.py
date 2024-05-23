from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import json
import re
from time import sleep

def normalize_str(text:str) ->str:
    text = re.sub(r'[^a-zA-Z0-9]+', '', text.lower())
    return text


def choose_browser(browser):
    match browser:
        case "Chrome":
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--incognito")
            driver = webdriver.Chrome(options=chrome_options)
        case "Firefox":
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.add_argument("--incognito")
            driver = webdriver.Firefox(options=firefox_options)
        case "Edge":
            ## Edge may not work, try to enable HyperVisor
            edge_options = webdriver.EdgeOptions()
            edge_options.add_argument("--incognito")
            driver = webdriver.Edge(options=edge_options)
        case _:
            KeyError("Specified browser not available, Options: Firefox, Chrome, Edge")
    return driver

js_code = """const vehicleCards = document.querySelectorAll('[data-qa^="vehicle_card_"]');

const vehicles = [];

vehicleCards.forEach((vehicleCard, index) => {

  const title = vehicleCard.querySelector('.Vropq').textContent;
  const description = vehicleCard.querySelector('.fQZoiO').textContent;
  const price = vehicleCard.querySelector('.sc-cJSrbW').textContent;
  const location = vehicleCard.querySelector('.XBFev').textContent;

  const imageSrc = vehicleCard.querySelector('.PhotoSlider--container img').getAttribute('src');

  const link = vehicleCard.querySelector('.sc-kfGgVZ.sc-esjQYD.fDhTTc').getAttribute('href');

  const vehicleObject = {
    title: title.trim(),
    description: description.trim(),
    price: price.trim(),
    location: location.trim(),
    imageSrc: imageSrc.trim(),
    link: link.trim()
  };

  vehicles.push(vehicleObject);
});

const jsonContent = JSON.stringify(vehicles, null, 2);

const blob = new Blob([jsonContent], { type: 'application/json' });

const a = document.createElement('a');
a.href = URL.createObjectURL(blob);
a.download = 'vehicles.json';

a.click();

URL.revokeObjectURL(a.href);"""

def get_basic_car_info(url:str,xpath:str,browser:str="Chrome"):
    ## Cicle through different browser if one happens to be blocked (Edge may not work)
    driver = choose_browser(browser)

    driver.get(url)

    """
    This block retrieves basic car info from the card: Title, Description and price
    then saves it to a file "cars_json" on local dir
    """
    car_cards = driver.find_elements(by=By.XPATH,value=xpath)
    cars_json = []
    for card in car_cards:
        try:
            info = []
            var = card.text.split('\n')
            for i in range(0,len(var),7):
                info.append(var[i:i+7])
            for u in info:
                cars_json.append({
                "title":u[0],
                "description":u[1],
                "price":u[2],
                "image":[],
                "link":""
            })
        except Exception as e:
            print(e)
    with open('cars_json.json', 'w') as fp:
        json.dump(cars_json, fp)

    driver.quit()

def get_image_urls(page_url:str,search_value:str,by:str=By.XPATH,browser:str="Chrome"):
    ## Cicle through different browser if one happens to be blocked (Edge may not work)
    driver = choose_browser(browser)
    driver.get(page_url)
    elems = driver.find_elements(by=by,value=search_value)
    cars_json = None

    urls = [url.get_attribute('src') for url in elems]
    print(urls)
    # urls = [x.split('/') for x in urls
    with open('cars_json.json','r') as f:
        cars_json = json.load(f)
    new_car_json = []
    for car in cars_json:
        car['concated'] = car['title'] + " " + car['description']
        car_images = []
        for url in urls:
            print(url)
            try:
                normal_url = normalize_str(url[8])
                normal_car_name = normalize_str(car['concated'])
                print(normal_url,normal_car_name)
                if normal_url == normal_car_name:
                    car_images.append(url)
            except IndexError:
                continue
        car['image'] = car_images
        new_car_json.append(car)
    
    with open('cars.json','w') as fp:
        json.dump(new_car_json,fp)

def execute_js_script(js_script:str,url:str,browser:str='Firefox'):
    driver = None
    driver = choose_browser(browser)
    driver.get(url)
    sleep(5)
    WebDriverWait(driver)
    test = driver.execute_script(js_script)
    print(test)


if __name__ == "__main__":
    url = "https://www.webmotors.com.br/carros/estoque/?idrevendedor=3916424&idcmpint=t1:c17:m07:webmotors:ver-estoque-vendedor"
    card_xpath = '/html/body/div[1]/main/div[1]/div[3]/div[2]/div/div[1]/div'
    # get_basic_car_info(url,xpath)
    # get_image_urls(url,search_value='img',by=By.TAG_NAME,browser='Firefox')
    execute_js_script(js_code,url,'Firefox')

    exit()