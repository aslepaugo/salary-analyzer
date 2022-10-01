import requests
import os
from dotenv import load_dotenv
from math import ceil
from terminaltables import AsciiTable


load_dotenv()
HH_RU_API_HOST = 'https://api.hh.ru'
SUPER_JOB_API_HOST = 'https://api.superjob.ru/2.0'
popular_technologies =[
    'Java',
    'C++',
    'Python',
    'JavaScript',
    'Go',
    'C#',
    'Ruby',
    'Kotlin',
    'PHP',
    'Swift',
]

HEADHUNTER, SUPERJOB = range(2)


def predict_rub_salary(salary_from: int, salary_to: int) -> float:
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8
    return None


def predict_rub_salary_hh(vacancy: str) -> float:
    if vacancy.get('salary').get('currency') == 'RUR':
        return predict_rub_salary(vacancy.get('salary')['from'], vacancy.get('salary')['to'])
    return None


def predict_rub_salary_sj(vacancy: str) -> float:
    if vacancy.get('currency') == 'rub':
        return predict_rub_salary(vacancy.get('payment_from'), vacancy.get('payment_to'))
    return None


def get_technology_salary(technology: str, source: int) -> dict:
    if source == HEADHUNTER:
        return get_technology_salary_hh(technology)
    if source == SUPERJOB:
        return get_technology_salary_sj(technology)
    return None



def get_technology_salary_hh(technology: str) -> dict:
    params = {
        'area': 1,
        'only_with_salary': True,
        'period': 30,
        'text': technology
    }
    tech_stat = {}
    tech_stat['vacancies_processed'] = 0
    total_salary_amount = 0
    page = 0
    pages_number = 1
    while page < pages_number:
        params['page'] = page
        vacancies = requests.get(f'{HH_RU_API_HOST}/vacancies', params=params).json()
        pages_number = vacancies['pages']
        for vacancy in vacancies.get('items'):
            vacancy_salary = predict_rub_salary_hh(vacancy=vacancy)
            if vacancy_salary:
                tech_stat['vacancies_processed'] += 1
                total_salary_amount += vacancy_salary   
        page += 1
    tech_stat['average_salary'] = int(total_salary_amount / tech_stat['vacancies_processed'])
    tech_stat['vacancies_found'] = vacancies['found']
    return tech_stat


def get_technology_salary_sj(technology: str) -> dict:
    records_count = 50
    params = {
        'keyword': technology,
        'town': 'Москва',
        'count': {records_count},
    }
    headers = {
        'X-Api-App-Id':os.getenv('SUPER_JOB_SECRET_KEY')
    }
    tech_stat = {}
    tech_stat['vacancies_processed'] = 0
    total_salary_amount = 0
    page = 0
    pages_number = 1
    while page < pages_number:
        params['page'] = page
        vacancies = requests.get(f'{SUPER_JOB_API_HOST}/vacancies', params=params, headers=headers).json()
        pages_number = ceil(vacancies['total'] / records_count)
        for vacancy in vacancies.get('objects'):
            vacancy_salary = predict_rub_salary_sj(vacancy=vacancy)
            if vacancy_salary:
                tech_stat['vacancies_processed'] += 1
                total_salary_amount += vacancy_salary    
        page += 1
    tech_stat['average_salary'] = int(total_salary_amount / tech_stat['vacancies_processed'])
    tech_stat['vacancies_found'] = vacancies['total']
    return tech_stat


def print_stats(source: int) -> None:
    table_header = ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    table_data = []
    table_data.append(table_header)
    for technology in popular_technologies:
        stats = get_technology_salary(technology, source)
        if stats is None:
            break
        table_row = [technology]
        table_row.append(stats['vacancies_found'])
        table_row.append(stats['vacancies_processed'])
        table_row.append(stats['average_salary'])
        table_data.append(table_row)
    if source == SUPERJOB:
        title = 'SuperJob Moscow'
    if source == HEADHUNTER:
        title = 'HeadHunter Moscow'
    table_instance = AsciiTable(table_data, title)
    print(table_instance.table)


if __name__ == '__main__':
    print()
    print_stats(HEADHUNTER)
    print()
    print_stats(SUPERJOB)
