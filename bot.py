import telebot
from bs4 import BeautifulSoup
import requests
import urllib.request
import sys
import re
import csv
import pandas as pd
import string
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from PIL import Image
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater
from telebot import types
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


upd = Updater(TOKEN, workers=32)

@run_async

@bot.message_handler(commands=['start'])
def command_c(message):
    if message.text == '/start':
        #print("qqq")
        bot.send_message(message.from_user.id, 'Input URL')
   
        @bot.message_handler(content_types='text')

        def input_text(message):
            titles = []
            brands = []
            full_prices = []
            ratings = []
            sellerss = []
            links = []

            def write_csv(data):
                name = ''
                leters = string.ascii_lowercase
                num_s = string.digits
                for i in range(8):
                    name += random.choice(leters)
                    name += random.choice(num_s)
                print(name)
                # Сделать в parse глобальные списки и передавать их сюда за 1 раз
                df = pd.DataFrame(data, columns=['title', 'brand', 'price', 'rating', 'sellers', 'link'])
                writer = pd.ExcelWriter(name + '.xlsx')
                df.to_excel(writer, name)
                writer.save()
                try:
                    file = open(name + '.xlsx', 'rb')
                    #print(name)
                    bot.send_document(message.from_user.id, file)
                except:
                    print(sys.exc_info())

            def get_html(url):
                r = urllib.request.Request(url,
                                           data=None,
                                           headers={
                                               'User-Agent': 'Mozilla/5.0'
                                           }
                                           )
                f = urllib.request.urlopen(r)
                return f.read().decode("utf-8")

            def get_total_pages(html):
                soup = BeautifulSoup(html, "lxml")
                try:
                    try:
                        pages = soup.find("div", id="pagn").find("span", class_="pagnDisabled").text
                    except:
                        pages = soup.find("div", id="pagn").find("span", class_="pagnLink").text
                except:
                    pages = 1

                return int(pages)

            def parse(html):
                soup = BeautifulSoup(html, "lxml")
                search = r"\d+"
                slash = "^/"
                usedof = r"\d+ used offers"
                used_new = r"\d+ used &amp new offers"
                newest = r"\d+ new offers"
                number = r"\d+"

                try:
                    firstresult = soup.find("div", id="mainResults").find("ul").contents[0].get("id")
                    print(firstresult)
                    begin = re.findall(search, firstresult)
                    start = int(begin[0])

                    lastresult = soup.find("div", id="mainResults").find("ul").contents[-1].get("id")
                    print(lastresult)
                    stop = re.findall(search, lastresult)
                    finish = int(stop[0])

                except:
                    firstresult = soup.find("div", id="resultsCol").find("li").get("data-result-rank")
                    print(firstresult)
                    start = int(firstresult)

                    lastresult = soup.find("div", id="resultsCol").find_all("li")
                    print(len(lastresult) + start)
                    finish = len(lastresult)

                    global res, full_price, sellers, rating, cent, link, title, brand
                for n in range(start, finish + start):
                    try:
                        table = soup.find("li", id="result_" + str(n))#.find_all("div", class_="s-item-container")
                        for item in table:
                            # title brand link rating price used_offers

                            try:
                                title = item.find("div", class_="a-row a-spacing-mini").find("a").get("title")
                                titles.append(str(title))
                                print(title)
                            except:
                                title = item.find("div", class_="a-row a-spacing-small").find("a").get("title")
                                titles.append(str(title))
                                print(title)

                            try:
                                brand = item.find("span", class_="a-size-small a-color-secondary").next_sibling.text
                                brands.append(str(brand))
                                print(brand)
                            except:
                                brands.append(str(brand))
                                print(brand)

                            try:
                                link = item.find("div", class_="a-row a-spacing-mini").find("a").get("href")
                                if re.findall(slash, link):
                                    print("https://www.amazon.com" + link)
                                    new_link = "https://www.amazon.com" + str(link)
                                    links.append(str(new_link))
                                else:
                                    links.append(str(link))
                                    print(link)

                            except:
                                link = item.find("div", class_="a-row a-spacing-small").find("a").get("href")
                                if re.findall(slash, link):
                                    print("https://www.amazon.com" + link)
                                    new_link = "https://www.amazon.com" + str(link)
                                    links.append(str(new_link))
                                else:
                                    links.append(str(link))
                                    print(link)

                            try:
                                rating = item.find("span", class_="a-icon-alt").text
                                ratings.append(str(rating))
                                print(rating)

                            except:
                                rating = "No rating"
                                ratings.append(str(rating))
                                print(rating)

                            try:
                                try:
                                    price = item.find("span", class_="sx-price sx-price-large").find("span").text

                                    cent = item.find("span", class_="sx-price sx-price-large").find("sup",
                                                                                                    class_="sx-price-fractional").text
                                except:
                                    price = item.find("span", class_="a-size-base a-color-base").text

                                full_price = ("$" + price + "." + cent)
                                full_prices.append(str(full_price))
                                cent = ''
                                print(full_price)

                            except:
                                full_price = "No price"
                                print(full_price)
                                full_prices.append(str(full_price))
                                # print((sys.exc_info()))

                            try:
                                counter = 0
                                try:
                                    sellers = item.contents[5]
                                except:
                                    sellers = item.contents[4]
                                # print(sellers.text)
                                used = re.findall(usedof, sellers.text)
                                used_and_new = re.findall(used_new, sellers.text)
                                new = re.findall(newest, sellers.text)
                                if used:
                                    res = re.findall(number, str(used))
                                    sellerss.append(str(res[0]))
                                    print(res[0])
                                    counter += 1

                                if used_and_new:
                                    res = re.findall(number, str(used_and_new))
                                    sellerss.append(str(res[0]))
                                    print(res[0])
                                    counter += 1

                                if new:
                                    res = re.findall(number, str(new))
                                    sellerss.append(str(res[0]))
                                    print(res[0])
                                    counter += 1

                                if counter == 0:
                                    res = "0"
                                    sellerss.append(str(res))
                                    print(res)

                                print(counter)

                            except:
                                res = '0'
                                print(res)
                                sellerss.append(str(res))

                    except:
                        continue

            def write():
                print(len(titles))
                print(len(full_prices))
                print(len(ratings))
                print(len(brands))
                print(len(sellerss))
                print(len(links))

                try:
                    data = {"title": titles,  # Доделать append если возможно
                            "price": full_prices,
                            "rating": ratings,
                            "brand": brands,
                            "sellers": sellerss,
                            "link": links}
                    write_csv(data)
                except:
                    bot.send_message(message.from_user.id, 'Something wrong, try again')
                    print(sys.exc_info())

            def main():
                try:
                    url = message.text
                    print(url)                    
                    page = r'page=\d'
                    all_pages = get_total_pages(get_html(url))
                    start = re.findall('\d', str((re.findall(page, url))))
                    bot.send_message(message.from_user.id, 'Alright, wait please')
                    if start:
                        for p in range(int(start[0]), int(all_pages) + 1):
                            new_url = re.sub(page, 'page=' + str(p), url)
                            print(new_url)
                            parse(get_html(new_url))
                        write()
                    else:
                        keywords = re.findall('keywords', url)
                        if keywords:
                            for p in range(1, int(all_pages) + 1):
                                new_url = re.sub('keywords', 'page=' + str(p) + '&keywords', url)
                                print(new_url)
                                parse(get_html(new_url))
                            write()
                        else:
                            for p in range(1, int(all_pages) + 1):
                                new_url = re.sub('&bbn', '&page=' + str(p) + '&bbn', url)
                                print(new_url)
                                parse(get_html(new_url))
                            write()
                except:
                    bot.send_message(message.from_user.id, 'Try Again')
                    print(sys.exc_info())


            if __name__ == '__main__':
                main()

@bot.message_handler(commands=['statistics'])
def command(message):
    mess = message
    @bot.message_handler(content_types='text')
    def input_msg(message):
        global c
        msg = message.text
        print(msg)

        if msg == '/statistics':
            c = 0

        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        file = [['Kids Home Store',
                 'Kitchen & Dining',
                 'Bedding'],
                ['Bath',
                 'Furniture',
                 'Home Decor'],
                ['Wall Art',
                 'Lighting & Ceiling Fans',
                 'Seasonal Decor'],
                ['Event & Party Supplies',
                 'Heating, Cooling & Air Quality',
                 'Irons & Steamers'],
                ['Vacuums & Floor Care',
                 'Storage & Organization',
                 'Cleaning Supplies'],
                ['Painting, Drawing & Art Supplies',
                 'Beading & Jewelry Making',
                 'Crafting'],
                ['Fabric',
                 'Fabric Decorating',
                 'Knitting & Crochet'],
                ['Needlework',
                 'Organization, Storage & Transport',
                 'Printmaking'],
                ['Scrapbooking & Stamping',
                 'Sewing',
                 'Party Decorations & Supplies'],
                ['Gift Wrapping Supplies',
                 'Action Figures & Statues',
                 'Arts & Crafts'],
                ['Baby & Toddler Toys',
                 'Building Toys',
                 'Dolls & Accessories'],
                ['Dress Up & Pretend Play',
                 'Kids Electronics',
                 'Games'],
                ['Grown-Up Toys',
                 'Hobbies',
                 'Kids Furniture, Decor & Storage'],
                ['Learning & Education',
                 'Novelty & Gag Toys',
                 'Party Supplies'],
                ['Puppets',
                 'Puzzles',
                 'Sports & Outdoor Play'],
                ['Stuffed Animals & Plush Toys',
                 'Toy Remote Control & Play Vehicles',
                 'Tricycles, Scooters & Wagons'],
                ['Video Games',
                 'Tools & Home Improvement',
                 'Appliances'],
                ['Building Supplies',
                 'Electrical',
                 'Hardware'],
                ['Kitchen & Bath Fixtures',
                 'Light Bulbs',
                 'Lighting & Ceiling Fans'],
                ['Measuring & Layout Tools',
                 'Painting Supplies & Wall Treatments',
                 'Power & Hand Tools'],
                ['Rough Plumbing',
                 'Safety & Security',
                 'Storage & Home Organization']]
        left = '←'
        right = '→'
        firs_b, second_b, third_b = file[0]

        if msg == '→' or msg == '←':
            if msg == '→':
                c += 1
                #print(c)
                if c == 20:
                    c = 0
            else:
                c -= 1
                #print(c)
                if c == -20:
                    c = -1
            firs_b, second_b, third_b = file[c]

        need = file[c].count(msg)

        #print(need)

        if need > 0:
            print('Yes')
            driver = webdriver.Firefox()
            driver.get('https://trends.google.ru/trends/?geo=US')
            try:
                search_line = driver.find_element_by_id('input-254')
            except:
                search_line = driver.find_element_by_id('input-24')
            search_line.click()
            search_line.send_keys(str(msg))
            driver.implicitly_wait(2)
            try:
                helper = driver.find_element_by_id('ul-254').find_element_by_tag_name('li')
                helper.click()
            except:
                pass
            date_popup = driver.find_element_by_tag_name('custom-date-picker')
            date_popup.click()
            date_pick = driver.find_element_by_id('select_option_19')
            date_pick.click()
            time.sleep(2)
            leters = string.ascii_lowercase
            name = ''
            for leter in range(5):
                name += random.choice(leters)
            name = name + '.png'
            driver.get_screenshot_as_file(str(name))
            img = Image.open(name)
            pos = (65, 339, 1139, 672)
            cropped = img.crop(pos)
            cropped.save(name)
            photo = open(name, 'rb')
            bot.send_photo(message.from_user.id, photo)

        keyboard.row(left, firs_b, second_b, third_b, right)
        bot.send_message(message.from_user.id,reply_markup=keyboard,text='--')

    if __name__=='__main__':
        input_msg(message)

bot.polling(none_stop=True, interval=0)
