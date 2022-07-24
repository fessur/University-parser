import requests
from bs4 import BeautifulSoup
import csv


def get_html(url):
    r = requests.get(url)
    return r.text


def code_form(data):
    if data == "Заочная":
        return "З"
    if data == "Очно-заочная":
        return "ОЗ"
    if data == "Очная":
        return "О"


def main():
    rows = []
    for p in range(1, 3):
        p = str(p)
        url = "https://vuzopedia.ru/vuzfilter?vuz=&city%5B%5D=50&mat=68&rus=78&fiz=&obshe=&ist=&biol=&inform=78&him=&liter=&georg=&inyaz&page=" + p
        base_url = "https://vuzopedia.ru"
        html = get_html(url)
        with open("index.html", "w", encoding="utf-8") as file:
            file.write(html)
        soup = BeautifulSoup(html, 'lxml')
        vuzes = soup.find_all("div", class_="itemVuz")
        for vuz in vuzes:
            vuz_url = base_url + vuz.find("a").get("href") + "/programs/bakispec"
            vuz_html = get_html(vuz_url)
            vuz_soup = BeautifulSoup(vuz_html, "lxml")
            vuz_option = [i.get("class")[1] for i in vuz_soup.find("div", class_="vuzOpiton").find_all("i")]
            vuz_name = vuz.find("a").text.strip()
            vuz_shortname = vuz_soup.find("h1", class_="mainTitle").text.split(":")[0].strip()
            vuz_name += " (" + vuz_shortname + ")"
            if vuz_option[0] == "vuzok" and vuz_option[1] == "vuzok" and vuz_option[3] == "vuzok" and vuz_option[4] == "vuzok":
                i = 1
                p_url = vuz_url + "/?ege=egemat;egerus;egeinform;&&&&&&page="
                while True:
                    progs_soup = BeautifulSoup(get_html(p_url + str(i)), 'lxml')
                    progs = progs_soup.find_all("div", class_="shadowForItem")
                    if len(progs) == 0:
                        break
                    for prog in progs:
                        try:
                            score = prog.find_all("div", class_="col-md-4")[1].find("a").contents[0][3:]
                            if score == "-":
                                score = "Бюджет только с этого года"
                                total = -1
                            else:
                                total = int(score)

                        except:
                            score = "Нет"
                            total = 1000

                        if total <= 224:
                            names = prog.find("div", class_="itemSpecAllinfo").find_all("div")
                            prog_name = names[0].text.strip()
                            number, spec_name = [x.strip() for x in names[1].text.split('|')]
                            places = prog.find_all("div", class_="col-md-4")[1].find_all("a")[2].contents[0].split()[0].strip()
                            price = prog.find_all("div", class_="col-md-4")[0].find("a").contents[0][3:].strip()
                            min_score = prog.find_all("div", class_="col-md-4")[2].find("a").text[3:6].strip()
                            prog_url = base_url + prog.find("a", class_="spectittle").get("href")
                            prog_soup = BeautifulSoup(get_html(prog_url), 'lxml')
                            prog_options = prog_soup.find("div", class_="podrInfo").find_all("div")
                            qual = prog_options[2].contents[1].strip()[:-1]
                            try:
                                form = prog_options[3].contents[1].strip()[:-1].split("; ")
                                form = ", ".join(sorted([code_form(x) for x in form]))
                            except:
                                form = "Возможно, программа закрыта"
                            row = [vuz_name, number, spec_name, prog_name, score, "МИР", places, price, min_score, form]
                            if qual == "Специалитет":
                                row.append(qual)
                            print(row)
                            rows.append(row)
                    i += 1
    with open("data.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)
        print(rows)


if __name__ == "__main__":
    main()
