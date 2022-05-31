import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_DOC_URL
from outputs import control_output
from utils import get_response
from utils import find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    # response = session.get(whats_new_url)
    # response.encoding = 'utf-8'
    response = get_response(session, whats_new_url)
    if response is None:
        # Если страница не загрузится, программа перейдёт к следующей ссылке.
        return

    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'div', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version = section.find('a')
        href = version['href']
        version_link = urljoin(whats_new_url, href)
        # Загрузите все страницы со статьями. Используйте кеширующую сессию.
        response = session.get(version_link)
        response.encoding = 'utf-8'  # Укажите кодировку utf-8.
        soup = BeautifulSoup(response.text, 'lxml')  # Сварите "супчик".
        h1 = find_tag(soup, 'h1')  # Найдите в "супе" тег h1.
        dl = find_tag(soup, 'dl')  # Найдите в "супе" тег dl.
        # Добавьте в вывод на печать текст из тегов h1 и dl.
        dl_text = dl.text.replace('\n', ' ')
        # На печать теперь выводится переменная dl_text — без пустых строчек.
        tup = (version_link, h1.text, dl_text)
        results.append(tup)
    # Печать списка с данными.
    return results


def latest_versions(session):
    # response = session.get(MAIN_DOC_URL)
    # response.encoding = 'utf-8'
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    # Перебор в цикле всех найденных списков.
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for ul in ul_tags:
        # Проверка, есть ли искомый текст в содержимом тега.
        if 'All versions' in ul.text:
            # Если текст найден, ищутся все теги <a> в этом списке.
            a_tags = ul.find_all('a')
            # Остановка перебора списков.
            break
    # Если нужный список не нашёлся,
    # вызывается исключение и выполнение программы прерывается.
    else:
        raise Exception('Ничего не нашлось')
    # print(a_tags)
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern,  a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    # response = session.get(downloads_url)
    # response.encoding = 'utf-8'
    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def peps_download(session):
    response = get_response(session, PEP_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'index-by-category'})
    section = main_div.find_all('section')
    results = [('Статус', 'Количество')]
    for tbody in section:
        body = find_tag(tbody, 'tbody')
        for index in tqdm(body):
            td = index.find_next('td', attrs={'class': 'num'})
            pep = find_tag(td, 'a')
            href = pep['href']
            status_link = urljoin(PEP_DOC_URL, href)
            response = session.get(status_link)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            status = soup.find(string='Status').findNext('dd').contents[0]
            dl_text = status.string.replace('\n', ' ')
            tup = (status_link, dl_text)
            results.append(tup)
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'peps-download': peps_download
}


def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')
    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    # Считывание аргументов из командной строки.
    args = arg_parser.parse_args()
    # Получение из аргументов командной строки нужного режима работы.
    session = requests_cache.CachedSession()
    if args.clear_cache:
        # Очистка кеша.
        session.cache.clear()
    parser_mode = args.mode
    # Поиск и вызов нужной функции по ключу словаря.
    results = MODE_TO_FUNCTION[parser_mode](session)
    # Если из функции вернулись какие-то результаты,
    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()


# p
