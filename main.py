import requests
import os
from dotenv import load_dotenv
from math import ceil
from terminaltables import AsciiTable


HH_AREA_ID = 1
SEARCH_VACANCY_PERIOD = 1
HH_RU_API_HOST = 'https://api.hh.ru'
SUPER_JOB_API_HOST = 'https://api.superjob.ru/2.0'
TECHNOLOGIES =[
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


def get_technology_salary_hh(technology: str) -> dict:
    params = {
        'area': HH_AREA_ID,
        'only_with_salary': True,
        'period': SEARCH_VACANCY_PERIOD,
        'text': technology
    }
    tech_stat = {}
    tech_stat['vacancies_processed'] = 0
    total_salary_amount = 0
    page = 0
    pages_number = 1
    while page < pages_number:
        params['page'] = page
        response = requests.get(f'{HH_RU_API_HOST}/vacancies', params=params)
        response.raise_for_status()
        vacancies = response.json()
        pages_number = vacancies['pages']
        for vacancy in vacancies.get('items'):
            vacancy_salary = predict_rub_salary_hh(vacancy=vacancy)
            if vacancy_salary:
                tech_stat['vacancies_processed'] += 1
                total_salary_amount += vacancy_salary   
        page += 1
    if tech_stat['vacancies_processed'] > 0:
        tech_stat['average_salary'] = int(total_salary_amount / tech_stat['vacancies_processed'])
    else:
        tech_stat['average_salary'] = 0
    tech_stat['vacancies_found'] = vacancies['found']
    return tech_stat


def get_technology_salary_sj(technology: str, headers: dict) -> dict:
    records_count = 50
    params = {
        'keyword': technology,
        'town': 'Москва',
        'count': {records_count},
    }
    tech_stat = {}
    tech_stat['vacancies_processed'] = 0
    total_salary_amount = 0
    page = 0
    pages_number = 1
    while page < pages_number:
        params['page'] = page
        response = requests.get(f'{SUPER_JOB_API_HOST}/vacancies', params=params, headers=headers)
        response.raise_for_status()
        vacancies = response.json()
        pages_number = ceil(vacancies['total'] / records_count)
        for vacancy in vacancies.get('objects'):
            vacancy_salary = predict_rub_salary_sj(vacancy=vacancy)
            if vacancy_salary:
                tech_stat['vacancies_processed'] += 1
                total_salary_amount += vacancy_salary    
        page += 1
    if tech_stat['vacancies_processed'] > 0:
        tech_stat['average_salary'] = int(total_salary_amount / tech_stat['vacancies_processed'])
    else:
        tech_stat['average_salary'] = 0
    tech_stat['vacancies_found'] = vacancies['total']
    return tech_stat


def print_stats(title: str, salary_data: list) -> None:
    vacancies_stats_table = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for salary in salary_data:
        vacancies_stats_table.append(salary)
    table_instance = AsciiTable(vacancies_stats_table, title)
    print(table_instance.table)


if __name__ == '__main__':
    load_dotenv()
    headers_sj = {
        'X-Api-App-Id':os.getenv('SUPER_JOB_SECRET_KEY')
    }
    vacancies_stats_hh = []
    vacancies_stats_sj = []
    for technology in TECHNOLOGIES:
        technology_stats_hh = get_technology_salary_hh(technology=technology)
        technology_stats_sj = get_technology_salary_sj(technology=technology, headers=headers_sj)
        vacancies_stats_hh.append(
            [
                technology, 
                technology_stats_hh['vacancies_found'], 
                technology_stats_hh['vacancies_processed'],
                technology_stats_hh['average_salary']
            ]
        )
        vacancies_stats_sj.append(
            [
                technology, 
                technology_stats_sj['vacancies_found'], 
                technology_stats_sj['vacancies_processed'],
                technology_stats_sj['average_salary']
            ]
        )        
    print_stats(title='HeadHunter Moscow', salary_data=vacancies_stats_hh)
    print_stats(title='SuperJob Moscow', salary_data=vacancies_stats_sj)
