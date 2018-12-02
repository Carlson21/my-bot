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

bot = telebot.TeleBot('624431408:AAEMRUTdMwx_xJg7EFemgFn-wdrAQ0hb6tc')

titles = []
brands = []
full_prices = []
ratings = []
sellerss = []
links = []


@bot.message_handler(commands=['start'])
def command_c(message):
    if message.text == '/start':
        #print("qqq")
        bot.send_message(message.from_user.id, 'Input URL')
        @bot.message_handler(content_types='text')

        def input_text(message):
            

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
                    pages = soup.find("div", id="pagn").find("span", class_="pagnDisabled").text
                except:
                    pages = soup.find("div", id="pagn").find("span", class_="pagnLink").text

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
                    print(sys.exc_info())

            def main():
                try:
                    bot.send_message(message.from_user.id, 'Alright, wait please')
                    url = message.text
                    print(url)
                    page = r'page=\d'
                    all_pages = get_total_pages(get_html(url))
                    start = re.findall('\d', str((re.findall(page, url))))
                    if start:
                        for p in range(int(start[0]), int(all_pages) + 1):
                            new_url = re.sub(page, 'page=' + str(p), url)
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


bot.polling(none_stop=True, interval=0)
