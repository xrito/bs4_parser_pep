# Парсер документации PEP
### Hi there 👋, Dmitrii

#### Программа для парсинга документации со страницы https://peps.python.org/

### Парсеры
- whats-new   
Информация о релизах Python
```
py main.py whats-new [arg]
```
- latest_versions   
Статусы версий Python
```
py main.py latest-versions [arg]
```
- download   
Парсер скачивающий zip архив с документацией python в pdf формате.
```
py main.py download [arg]
```
- pep   
Вывод сводной информации о статусах всех PEP
```
py main.py pep [arg]
```
В проекте есть встроенная подсказка по использованию аргументов командной строки:
```
python main.py -h
```
=======>
```
usage: main.py [-h] [-c] [-o {pretty,file}]
               {whats-new,latest-versions,download,pep}
Парсер документации Python
positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера
optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
     
```
Skills: Python / BS4

[<img src='https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/github.svg' alt='github' height='40'>](https://github.com/xrito)  
